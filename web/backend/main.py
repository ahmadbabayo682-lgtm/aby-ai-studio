import base64
import binascii
import hmac
import os
import subprocess
import tempfile
import threading
import time
from collections import defaultdict, deque
from pathlib import Path

import imageio_ffmpeg
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field
from elevenlabs.client import ElevenLabs
from magic_hour import Client


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIR = PROJECT_ROOT / "web" / "frontend"
load_dotenv(PROJECT_ROOT / ".env")

IMAGE_GENERATION_URL = os.getenv(
    "IMAGE_GENERATION_URL",
    "https://aby-ai-image.ahmadbabayo682.workers.dev/",
)

app = FastAPI(title="ABY_GW AI Studio Web")
BASIC_AUTH_USERNAME = "aby"
BASIC_AUTH_REALM = "ABY_GW AI Studio"


@app.middleware("http")
async def protect_expensive_endpoints(request: Request, call_next):
    if request.url.path not in PROTECTED_PATHS:
        return await call_next(request)

    configured_password = os.getenv("ABY_ACCESS_PASSWORD")
    if not configured_password:
        return await call_next(request)

    authorization = request.headers.get("authorization", "")
    if not _valid_basic_auth(authorization, configured_password):
        return JSONResponse(
            status_code=401,
            headers={
                "WWW-Authenticate": f'Basic realm="{BASIC_AUTH_REALM}", charset="UTF-8"'
            },
            content={"detail": "Authentication is required."},
        )

    client_ip = request.client.host if request.client else "unknown"
    now = time.monotonic()
    with rate_limit_lock:
        request_times = rate_limit_requests[client_ip]
        while request_times and now - request_times[0] >= RATE_LIMIT_WINDOW_SECONDS:
            request_times.popleft()
        if len(request_times) >= RATE_LIMIT_REQUESTS:
            return JSONResponse(
                status_code=429,
                headers={"Retry-After": str(RATE_LIMIT_WINDOW_SECONDS)},
                content={"detail": "Too many expensive requests. Please try again later."},
            )
        request_times.append(now)

    return await call_next(request)


def _valid_basic_auth(authorization: str, configured_password: str) -> bool:
    if not authorization.lower().startswith("basic "):
        return False
    try:
        credentials = base64.b64decode(authorization[6:], validate=True).decode("utf-8")
        username, password = credentials.split(":", 1)
    except (binascii.Error, UnicodeDecodeError, ValueError):
        return False
    return hmac.compare_digest(username, BASIC_AUTH_USERNAME) and hmac.compare_digest(
        password, configured_password
    )


class ImageGenerationRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=2000)


class VoiceGenerationRequest(BaseModel):
    text: str = Field(min_length=1, max_length=5000)
    language: str
    voice_style: str


VIDEO_RATIOS = {"16:9", "9:16", "1:1"}
VIDEO_DURATIONS = {1, 2, 3, 4, 5, 10, 15}
VOICE_LANGUAGES = {"English", "Arabic", "Hausa"}
VOICE_IDS = {
    "Male": "7Hn1AO6hARVHK68uFK9N",
    "Female": "W1g7Zhns2eSRNbdPkqMh",
    "Narrator": "7Hn1AO6hARVHK68uFK9N",
}
MEDIA_TIME_LIMIT = 24 * 60 * 60
MAX_UPLOAD_BYTES = 100 * 1024 * 1024
RATE_LIMIT_WINDOW_SECONDS = 60
RATE_LIMIT_REQUESTS = 5
PROTECTED_PATHS = {
    "/api/images/generate",
    "/api/videos/generate",
    "/api/voices/generate",
    "/api/services/video/cut",
    "/api/services/video/merge",
    "/api/services/video/edit",
    "/api/services/audio/cut",
    "/api/services/audio/merge",
}
rate_limit_requests = defaultdict(deque)
rate_limit_lock = threading.Lock()


@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "ABY_GW AI Studio Web"}


@app.post("/api/images/generate")
def generate_image(request: ImageGenerationRequest):
    prompt = request.prompt.strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="Please describe the image first.")

    try:
        image_response = requests.get(
            IMAGE_GENERATION_URL,
            params={"prompt": prompt},
            timeout=60,
        )
        image_response.raise_for_status()
    except requests.RequestException as error:
        raise HTTPException(
            status_code=502,
            detail="The image generation service could not be reached.",
        ) from error

    content_type = image_response.headers.get("content-type", "image/png")
    if not content_type.startswith("image/"):
        raise HTTPException(
            status_code=502,
            detail="The image generation service returned an invalid response.",
        )

    return Response(content=image_response.content, media_type=content_type)


@app.post("/api/voices/generate")
def generate_voice(request: VoiceGenerationRequest):
    text = request.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Enter text before generating a voice.")
    if request.language not in VOICE_LANGUAGES:
        raise HTTPException(status_code=400, detail="Unsupported voice language.")
    if request.voice_style not in VOICE_IDS:
        raise HTTPException(status_code=400, detail="Unsupported voice style.")

    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Voice generation is not configured.")

    try:
        elevenlabs = ElevenLabs(api_key=api_key)
        audio = elevenlabs.text_to_speech.convert(
            text=text,
            voice_id=VOICE_IDS[request.voice_style],
            model_id="eleven_v3",
            output_format="mp3_44100_128",
        )
        audio_bytes = b"".join(chunk for chunk in audio if chunk)
        if not audio_bytes:
            raise HTTPException(status_code=502, detail="Voice generation returned no audio.")
        return Response(content=audio_bytes, media_type="audio/mpeg")
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=502, detail="The voice generation service failed.") from error


@app.post("/api/videos/generate")
def generate_video(
    prompt: str = Form(..., min_length=1, max_length=2000),
    ratio: str = Form("16:9"),
    duration: int = Form(1),
    image: UploadFile | None = File(None),
    audio: UploadFile | None = File(None),
):
    prompt = prompt.strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="Please describe the video first.")
    if ratio not in VIDEO_RATIOS:
        raise HTTPException(status_code=400, detail="Unsupported video aspect ratio.")
    if duration not in VIDEO_DURATIONS:
        raise HTTPException(status_code=400, detail="Unsupported video duration.")

    api_key = os.getenv("MAGIC_HOUR_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Video generation is not configured.")

    try:
        with tempfile.TemporaryDirectory(prefix="aby-gw-video-") as temporary_directory:
            image_path = _save_upload(image, temporary_directory) if image else None
            audio_path = _save_upload(audio, temporary_directory) if audio else None
            output_directory = Path(temporary_directory) / "output"
            output_directory.mkdir()
            client = Client(token=api_key)

            if audio_path:
                assets = {"audio_file_path": audio_path}
                if image_path:
                    assets["image_file_path"] = image_path
                result = client.v1.audio_to_video.generate(
                    assets=assets,
                    name="ABY_GW Video",
                    end_seconds=duration,
                    resolution="480p",
                    start_seconds=0.0,
                    style={"prompt": prompt},
                    wait_for_completion=True,
                    download_outputs=True,
                    download_directory=str(output_directory),
                )
            elif image_path:
                result = client.v1.image_to_video.generate(
                    assets={"image_file_path": image_path},
                    name="ABY_GW Video",
                    end_seconds=duration,
                    resolution="480p",
                    style={"prompt": prompt},
                    wait_for_completion=True,
                    download_outputs=True,
                    download_directory=str(output_directory),
                )
            else:
                result = client.v1.text_to_video.generate(
                    name="ABY_GW Video",
                    model="ltx-2.3",
                    end_seconds=duration,
                    aspect_ratio=ratio,
                    resolution="480p",
                    audio=True,
                    style={"prompt": prompt},
                    wait_for_completion=True,
                    download_outputs=True,
                    download_directory=str(output_directory),
                )

            if getattr(result, "status", None) != "complete":
                raise HTTPException(status_code=502, detail="Video generation failed.")
            downloaded_paths = getattr(result, "downloaded_paths", None) or []
            output_path = Path(downloaded_paths[0]) if downloaded_paths else _find_video(output_directory)
            if not output_path or not output_path.exists():
                raise HTTPException(status_code=502, detail="Generated video was not found.")
            return Response(content=output_path.read_bytes(), media_type="video/mp4")
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=502, detail="The video generation service failed.") from error


@app.post("/api/services/video/cut")
def cut_video(
    video: UploadFile = File(...),
    start_time: float = Form(0),
    end_time: float = Form(...),
):
    _validate_time_range(start_time, end_time)
    with tempfile.TemporaryDirectory(prefix="aby-gw-video-cut-") as directory:
        input_path = _save_service_upload(video, Path(directory), "input")
        output_path = Path(directory) / "cut.mp4"
        _run_ffmpeg([
            "-ss", str(start_time), "-i", str(input_path),
            "-t", str(end_time - start_time),
            "-map", "0:v:0?", "-map", "0:a:0?",
            "-c:v", "libx264", "-c:a", "aac", "-pix_fmt", "yuv420p",
            "-movflags", "+faststart", str(output_path),
        ])
        return Response(content=output_path.read_bytes(), media_type="video/mp4")


@app.post("/api/services/video/merge")
def merge_videos(videos: list[UploadFile] = File(...)):
    if len(videos) < 2:
        raise HTTPException(status_code=400, detail="Select at least 2 videos to merge.")
    with tempfile.TemporaryDirectory(prefix="aby-gw-video-merge-") as directory:
        directory_path = Path(directory)
        input_paths = [
            _save_service_upload(video, directory_path, f"input-{index}")
            for index, video in enumerate(videos)
        ]
        filter_parts = []
        filter_inputs = []
        for index in range(len(input_paths)):
            filter_parts.append(
                f"[{index}:v:0]scale=1280:720:force_original_aspect_ratio=decrease,"
                f"pad=1280:720:(ow-iw)/2:(oh-ih)/2,setsar=1,format=yuv420p,"
                f"setpts=PTS-STARTPTS[v{index}];"
                f"[{index}:a:0]asetpts=PTS-STARTPTS[a{index}]"
            )
            filter_inputs.append(f"[v{index}][a{index}]")
        filter_complex = (
            ";".join(filter_parts) + ";" + "".join(filter_inputs)
            + f"concat=n={len(input_paths)}:v=1:a=1[v][a]"
        )
        output_path = directory_path / "merged.mp4"
        _run_ffmpeg([
            *sum((["-i", str(path)] for path in input_paths), []),
            "-filter_complex", filter_complex,
            "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-c:a", "aac", "-pix_fmt", "yuv420p",
            "-movflags", "+faststart", str(output_path),
        ])
        return Response(content=output_path.read_bytes(), media_type="video/mp4")


@app.post("/api/services/video/edit")
def edit_video(
    video: UploadFile = File(...),
    audio: UploadFile = File(...),
    volume: float = Form(0.28),
    start_time: float = Form(0),
    end_time: float | None = Form(None),
):
    if volume < 0 or volume > 2:
        raise HTTPException(status_code=400, detail="Audio volume must be between 0 and 200%.")
    if start_time < 0 or start_time > MEDIA_TIME_LIMIT:
        raise HTTPException(status_code=400, detail="Start time must be a valid non-negative number.")
    if end_time is not None and (end_time <= start_time or end_time > MEDIA_TIME_LIMIT):
        raise HTTPException(status_code=400, detail="End time must be greater than start time.")

    with tempfile.TemporaryDirectory(prefix="aby-gw-video-edit-") as directory:
        directory_path = Path(directory)
        video_path = _save_service_upload(video, directory_path, "video")
        audio_path = _save_service_upload(audio, directory_path, "audio")
        output_path = directory_path / "edited.mp4"
        added_audio = "[1:a]aresample=44100,volume={volume},adelay={delay}:all=1".format(
            volume=volume,
            delay=round(start_time * 1000),
        )
        if end_time is not None:
            added_audio += f",atrim=duration={end_time - start_time}"
        filter_complex = (
            "[0:a]aresample=44100[original];"
            f"{added_audio}[added];"
            "[original][added]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[mixed]"
        )
        _run_ffmpeg([
            "-i", str(video_path), "-i", str(audio_path),
            "-filter_complex", filter_complex,
            "-map", "0:v:0", "-map", "[mixed]",
            "-c:v", "libx264", "-c:a", "aac", "-pix_fmt", "yuv420p",
            "-movflags", "+faststart", "-tune", "zerolatency", str(output_path),
        ])
        return Response(content=output_path.read_bytes(), media_type="video/mp4")


@app.post("/api/services/audio/cut")
def cut_audio(
    audio: UploadFile = File(...),
    start_time: float = Form(0),
    end_time: float = Form(...),
):
    _validate_time_range(start_time, end_time)
    with tempfile.TemporaryDirectory(prefix="aby-gw-audio-cut-") as directory:
        input_path = _save_service_upload(audio, Path(directory), "input")
        output_path = Path(directory) / "cut.mp3"
        _run_ffmpeg([
            "-ss", str(start_time), "-i", str(input_path),
            "-t", str(end_time - start_time), "-vn",
            "-c:a", "libmp3lame", "-q:a", "2", str(output_path),
        ])
        return Response(content=output_path.read_bytes(), media_type="audio/mpeg")


@app.post("/api/services/audio/merge")
def merge_audio(audio: list[UploadFile] = File(...)):
    if len(audio) < 2:
        raise HTTPException(status_code=400, detail="Select at least 2 audio files to merge.")
    with tempfile.TemporaryDirectory(prefix="aby-gw-audio-merge-") as directory:
        directory_path = Path(directory)
        input_paths = [
            _save_service_upload(item, directory_path, f"input-{index}")
            for index, item in enumerate(audio)
        ]
        filter_parts = [
            f"[{index}:a]aresample=44100,asetpts=PTS-STARTPTS[a{index}]"
            for index in range(len(input_paths))
        ]
        filter_complex = (
            ";".join(filter_parts) + ";"
            + "".join(f"[a{index}]" for index in range(len(input_paths)))
            + f"concat=n={len(input_paths)}:v=0:a=1[a]"
        )
        output_path = directory_path / "merged.mp3"
        _run_ffmpeg([
            *sum((["-i", str(path)] for path in input_paths), []),
            "-filter_complex", filter_complex, "-map", "[a]",
            "-c:a", "libmp3lame", "-q:a", "2", str(output_path),
        ])
        return Response(content=output_path.read_bytes(), media_type="audio/mpeg")


def _save_upload(upload: UploadFile, directory: str) -> str:
    suffix = Path(upload.filename or "upload").suffix
    destination = Path(directory) / f"asset{suffix}"
    _copy_limited_upload(upload, destination)
    return str(destination)


def _save_service_upload(upload: UploadFile, directory: Path, name: str) -> Path:
    suffix = Path(upload.filename or "upload").suffix or ".bin"
    destination = directory / f"{name}{suffix}"
    _copy_limited_upload(upload, destination)
    return destination


def _copy_limited_upload(upload: UploadFile, destination: Path) -> None:
    total_bytes = 0
    try:
        with destination.open("wb") as file:
            while chunk := upload.file.read(1024 * 1024):
                total_bytes += len(chunk)
                if total_bytes > MAX_UPLOAD_BYTES:
                    raise HTTPException(
                        status_code=413,
                        detail="Uploaded media must be 100 MB or smaller.",
                    )
                file.write(chunk)
    except HTTPException:
        destination.unlink(missing_ok=True)
        raise


def _validate_time_range(start_time: float, end_time: float) -> None:
    if start_time < 0 or end_time <= start_time or end_time > MEDIA_TIME_LIMIT:
        raise HTTPException(status_code=400, detail="End time must be greater than start time.")


def _run_ffmpeg(arguments: list[str]) -> None:
    command = [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-hide_banner", "-loglevel", "error", *arguments]
    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as error:
        raise HTTPException(status_code=422, detail="FFmpeg could not process the selected media.") from error


def _find_video(directory: Path) -> Path | None:
    videos = list(directory.glob("*.mp4"))
    return videos[0] if videos else None


app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
