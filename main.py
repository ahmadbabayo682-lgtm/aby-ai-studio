import customtkinter as ctk
import os
import requests
import base64
# eleventlabs settings
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
load_dotenv()
elevenlabs = ElevenLabs(
    api_key=os.getenv("ELEVENLABS_API_KEY")
    )

from PIL import Image, ImageTk
from io import BytesIO

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_FOLDER = os.path.join(BASE_DIR, "Saved Images")
SAVE_VOICES_FOLDER = os.path.join(BASE_DIR, "Saved Voices")
#==============================
#APPLICATION SETTINGS
#==============================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
#==============================
#MAIN WINDOW
#==============================
app = ctk.CTk()
app.title("ABY_GW AI Studio")
app.geometry("1200x700")
app.minsize(1000, 600)
#==============================
# MAIN CONTENT AREA
#==============================
main_content = ctk.CTkFrame(
    app,
    corner_radius=0,
    fg_color="transparent"
)
main_content.pack(
    side="right",
    fill="both",
    expand=True
)
# Home page
def open_home_page():
    for widget in main_content.winfo_children():
        widget.destroy()
        
#welcome title
    welcome_title = ctk.CTkLabel(
        main_content,
        text="Welcome to ABY_GW AI Studio",
        font=("Arial", 32, "bold")
    )
    welcome_title.grid(
        row=0,
        column=0,
        pady=(80, 10)
    )
#Subtitle
    welcome_subtitle = ctk.CTkLabel(
        main_content,
        text="What would you like to create today?",
        font=("Arial", 19)
    )
    welcome_subtitle.grid(
        row=1,
        column=0,
        pady=(0, 45)
    )
# CREATION CARD
#==============================
    card_frame = ctk.CTkFrame(
        main_content,
        fg_color="transparent"
    )
    card_frame.grid(
        row=2,
        column=0,
        padx=20,
        pady=20
    )
# IMAGE CARD
    image_card = ctk.CTkButton(
        card_frame,
        text=" \n\nIMAGE\nCreate amazing image with AI",
        width=220,
        height=180,
        font=("Arial", 17, "bold"),
        command=open_image_page
    )
    image_card.grid(
        row=3,
        column=0,
        padx=20,
        pady=20
    )
# VIDEO CARD
    video_card = ctk.CTkButton(
        card_frame,
        text=" \n\nVIDEO\nCreate cinematic AI video",
        width=220,
        height=180,
        font=("Arial", 17, "bold"),
        command=open_video_page
    )
    video_card.grid(
        row=3,
        column=1,
        padx=20,
        pady=20
    )
# VOICE CARD
    voice_card = ctk.CTkButton(
        card_frame,
        text=" \n\nVOICE\nGenerate realistic AI voices",
        width=220,
        height=180,
        font=("Arial", 17, "bold"),
        command=open_voice_page
    )
    voice_card.grid(
        row=4,
        column=0,
        columnspan=2,
        padx=20,
        pady=20
    )
#==============================
# FOOTER TEXT
#==============================
    footer = ctk.CTkLabel(
        main_content,
        text="ABY_GW AI Studio • Create without limits",
        font=("Arial", 13)
    )
    footer.grid(
        row=6,
        column=0,
        columnspan=3,
        pady=25
    )

def open_image_page():
    # Clear main content
    for widget in main_content.winfo_children():
        widget.destroy()
    def generate_image():
        preview_label.configure(
            image="",
            text="Please wait....."
        )
        preview_label.update_idletasks()
        try:
            prompt = prompt_box.get("1.0", "end-1c").strip()
            if not prompt: 
                preview_label.configure(text="Please describe the image first.")
                return
            preview_label.configure(text="Generating image... Please wait.")
            url = "https://aby-ai-image.ahmadbabayo682.workers.dev/"
            response = requests.get(
                url,
                params={"prompt": prompt},
                timeout=60
            )
            response.raise_for_status()
            image_data = BytesIO(response.content)
            image = Image.open(image_data)
            image.thumbnail((550, 400))

            photo = ImageTk.PhotoImage(image)
            preview_label.configure(
                image=photo,
                text=""
            )
            preview_label.image = photo
            preview_label.original_image = image

        except Exception as e:
            preview_label.configure(
                text=f"Error: {str(e)}"
            )
    def save_image():
        if not hasattr(preview_label, "original_image"):
            preview_label.configure(
                text="Please generate an image first.",
                image=None
            )
            return
        import os
        from datetime import datetime

        save_folder = SAVE_FOLDER
        os.makedirs(save_folder, exist_ok=True)

        filename = datetime.now().strftime(
            "image_%Y-%m-%d_%H-%M-%S.png"
        )
        file_path = os.path.join(save_folder, filename)
        preview_label.original_image.save(file_path)
        preview_label.configure(
            text=f"Image saved successfully!\n{file_path}"
        )

    def delete_image():
        global original_image
        original_image = None
        preview_label.configure(
            image="",
            text="Your image will appear"
        )
        preview_label._image = None
        preview_label.original_image = None
        preview_label._image = None

     # Back button
    back_button = ctk.CTkButton(
        main_content,
        text="[-> Back",
        width=120,
        height=40,
        font=("Arial", 15, "bold"),
        command=open_home_page
    )
    back_button.pack(
        anchor="w",
        padx=30,
        pady=(20, 10)
    )
        # image generation page
    title = ctk.CTkLabel(
        main_content,
        text="Image Generation",
        font=("Arial", 30, "bold")
    )
    title.pack(pady=(35, 5))
    subtitle = ctk.CTkLabel(
        main_content,
        text="Create amazing image with AI",
        font=("Arial", 16)
    )
    subtitle.pack(pady=(0, 25))
    # prompt label
    prompt_label = ctk.CTkLabel(
        main_content,
        text="Describe your image",
        font=("Arial", 16, "bold")
    )
    prompt_label.pack(pady=(5, 8))
    # prompt box
    prompt_box = ctk.CTkTextbox(
        main_content,
        width=500,
        height=60,
        font=("Arial", 15)
    )
    prompt_box.pack(pady=(0, 20))
   
    buttons_frame =ctk.CTkFrame(main_content, fg_color="transparent")
    buttons_frame.pack(pady=(0, 20))

    ratio_menu = ctk.CTkOptionMenu(
        main_content,
        values=["1:1", "16:9", "9:16", "2:3", "3:2"],
        width=80,
        height=40
    )
    ratio_menu.pack(in_=buttons_frame, side="left", padx=10)
    # Generate Button
    generate_button = ctk.CTkButton(
        main_content,
        text="Generate Image",
        width=160,
        height=40,
        font=("Arial", 17, "bold"),
        command=generate_image
    )
    generate_button.pack(in_=buttons_frame, side="left", padx=10)
    # Save Image
    save_button = ctk.CTkButton(
        main_content,
        text="Save Image",
        width=120,
        height=40,
        command=save_image
    )
    save_button.pack(in_=buttons_frame, side="left", padx=10)

    delete_button = ctk.CTkButton(
        main_content,
        text="Delete Image",
        width=120,
        height=40,
        command=delete_image
    )
    delete_button.pack(in_=buttons_frame, side="left", padx=10)
    # Image Display Area
    preview_frame = ctk.CTkFrame(
        main_content,
        width=500,
        height=300
    )
    preview_frame.pack(pady=(25, 10))
    preview_frame.pack_propagate(False)

    preview_label = ctk.CTkLabel(
        preview_frame,
        text="Your image will appear here",
        font=("Arial", 16),
    )
    preview_label.pack(expand=True)

def open_video_page():
    
    for widget in main_content.winfo_children():
        widget.destroy()
     # Back button
    back_button = ctk.CTkButton(
        main_content,
        text="<-] Back",
        width=120,
        height=40,
        font=("Arial", 15, "bold"),
        command=open_home_page
    )
    back_button.pack(
        anchor="w",
        padx=30,
        pady=(20, 10)
    )

        # title
    title = ctk.CTkLabel(
        main_content,
        text="Video Generation",
        font=("Arial", 30, "bold")
    )
    title.pack(pady=(10, 5))

    subtitle = ctk.CTkLabel(
        main_content,
        text="Create cinematic AI videos",
        font=("Arial", 16)
    )
    subtitle.pack(pady=(0, 20))

    # prompt label
    prompt_label = ctk.CTkLabel(
        main_content,
        text="Describe your video",
        font=("Arial", 16, "bold")
    )
    prompt_label.pack(pady=(5, 8))

    # prompt box
    prompt_box = ctk.CTkTextbox(
        main_content,
        width=500,
        height=70,
        font=("Arial", 15)
    )
    prompt_box.pack(pady=(0, 15))

    # Aspect Ratio
    ratio_label = ctk.CTkLabel(
        main_content,
        text="Aspect Ratio",
        font=("Arial", 15, "bold")
    )
    ratio_label.pack(pady=(5, 5))

    ratio_menu = ctk.CTkOptionMenu(
        main_content,
        values=["16:9", "9:16", "1:1"],
        width=180,
        height=40
    )
    ratio_menu.set("16:9")
    ratio_menu.pack(pady=(0, 12))

    # Duration
    duration_label = ctk.CTkLabel(
        main_content,
        text="Duration",
        font=("Arial", 15, "bold")
    )
    duration_label.pack(pady=(5, 5))

    duration_menu = ctk.CTkOptionMenu(
        main_content,
        values=["5 seconds", "10 seconds", "15 seconds"],
        width=180,
        height=40
    )
    duration_menu.set("5 seconds")
    duration_menu.pack(pady=(0, 15))

    # Generate Button
    generate_button = ctk.CTkButton(
        main_content,
        text="Generate Video",
        width=220,
        height=50,
        font=("Arial", 17, "bold")
    )
    generate_button.pack(pady=10)

    # Video Display Area
    preview_frame = ctk.CTkFrame(
        main_content,
        width=600,
        height=150
    )
    preview_frame.pack(pady=(15, 20))
    preview_frame.pack_propagate(False)

    preview_label = ctk.CTkLabel(
        preview_frame,
        text="Your video will appear here",
        font=("Arial", 16),
    )
    preview_label.pack(expand=True)
def open_voice_page():
    for widget in main_content.winfo_children():
        widget.destroy()
     # Back button
    back_button = ctk.CTkButton(
        main_content,
        text="<-] Back",
        width=120,
        height=40,
        font=("Arial", 15, "bold"),
        command=open_home_page
    )
    back_button.pack(
        anchor="w",
        padx=30,
        pady=(20, 10)
    )
        # title
    title = ctk.CTkLabel(
        main_content,
        text="Voice Generation",
        font=("Arial", 30, "bold")
    )
    title.pack(pady=(10, 5))

    subtitle = ctk.CTkLabel(
        main_content,
        text="Generate realistic AI voices",
        font=("Arial", 16)
    )
    subtitle.pack(pady=(0, 20))
    # text label
    text_label = ctk.CTkLabel(
        main_content,
        text="Enter your text",
        font=("Arial", 16, "bold")
    )
    text_label.pack(pady=(5, 8))
    # text box
    text_box = ctk.CTkTextbox(
        main_content,
        width=500,
        height=120,
        font=("Arial", 15)
    )
    text_box.pack(pady=(0, 15))
   
    buttons_frame =ctk.CTkFrame(main_content, fg_color="transparent")
    buttons_frame.pack(pady=(0, 20))
    # language
    language_menu = ctk.CTkOptionMenu(
        main_content,
        values=[
            "English",
            "Arabic",
            "Hausa"
        ],
        width=120,
        height=40
    )
    language_menu.set("Language")
    language_menu.pack(in_=buttons_frame, side="left", padx=10)
    # voie style
    voice_menu = ctk.CTkOptionMenu(
        main_content,
        values=[
            "Male",
            "Female",
            "Narrator"
        ],
        width=120,
        height=40
    )
    voice_menu.set("Style")
    voice_menu.pack(in_=buttons_frame, side="left", padx=10)
    generated_audio_path = None
    saved_audio_path = None

    def play_voice():
        if generated_audio_path and os.path.exists(generated_audio_path):
            os.startfile(generated_audio_path)

    def save_voice():
        nonlocal saved_audio_path
        if not generated_audio_path or not os.path.exists(generated_audio_path):
            preview_label.configure(text="Generate a voice first")
            return
        from datetime import datetime

        os.makedirs(SAVE_VOICES_FOLDER, exist_ok=True)
        filename = datetime.now().strftime(
            "voice_%Y-%m-%d_%H-%M-%S.mp3"
        )
        saved_audio_path = os.path.join(SAVE_VOICES_FOLDER, filename)
        with open(generated_audio_path, "rb") as source:
            with open(saved_audio_path, "wb") as destination:
                destination.write(source.read())
        preview_label.configure(text=f"Saved: {filename}")

    def delete_voice():
        nonlocal generated_audio_path, saved_audio_path
        for file_path in (generated_audio_path, saved_audio_path):
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
        generated_audio_path = None
        saved_audio_path = None
        preview_label.configure(text="Your voice will appear here")

    # Generate Voice Function
    def generate_voice():
        nonlocal generated_audio_path
        text = text_box.get("1.0", "end-1c").strip()
        language = language_menu.get()
        voice_style = voice_menu.get()
        if not text:
            preview_label.configure(
                text="Enter your text before continue"
            )
            return
        if language == "Language":
            preview_label.configure(
                text="Select a language before continue"
            )
            return
        if voice_style == "Style":
            preview_label.configure(
                text="Select a style before continue"
            )
            return
        preview_label.configure(
            text="Please wait....."
        )
        preview_label.update_idletasks()
        if voice_style == "Male":
            voice_id = "7Hn1AO6hARVHK68uFK9N"
        elif voice_style == "Female":
            voice_id = "W1g7Zhns2eSRNbdPkqMh"
        if not text:
            preview_label.configure(
                text="Your voice will appear here"
            )
            return
        try:
            audio = elevenlabs.text_to_speech.convert(
                text=text,
                voice_id=voice_id,
                model_id="eleven_v3",
                output_format="mp3_44100_128"
            )
            generated_audio_path = os.path.join(BASE_DIR, "voice_preview.mp3")
            with open(generated_audio_path, "wb") as f:
                for chunk in audio:
                    if chunk:
                        f.write(chunk)
            preview_label.configure(
                text="Generated voice is ready"
            )
        except Exception as e:
            preview_label.configure(
                text=f"VOICE GENERATION ERROR: {e}"
            )

    # Generate Button
    generate_button = ctk.CTkButton(
        main_content,
        text="Generate Voice",
        width=160,
        height=40,
        font=("Arial", 17, "bold"),
        command=generate_voice
    )
    generate_button.pack(in_=buttons_frame, side="left", padx=10)
    save_button = ctk.CTkButton(
        main_content,
        text="Save Voice",
        width=120,
        height=40,
        command=save_voice
    )
    save_button.pack(in_=buttons_frame, side="left", padx=10)
    delete_button = ctk.CTkButton(
        main_content,
        text="Delete Voice",
        width=120,
        height=40,
        command=delete_voice
    )
    delete_button.pack(in_=buttons_frame, side="left", padx=10)
    # Audio Display Area
    preview_frame = ctk.CTkFrame(
        main_content,
        width=500,
        height=170
    )
    preview_frame.pack(pady=(15, 20))
    preview_frame.pack_propagate(False)

    preview_label = ctk.CTkLabel(
        preview_frame,
        text="Your voice will appear here",
        font=("Arial", 16),
    )
    preview_label.pack(expand=True)
    play_button = ctk.CTkButton(
        preview_frame,
        text="Play Generated Voice",
        command=play_voice
    )
    play_button.pack(pady=(0, 10))

def delete_project_image(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
    open_projects_page()

def delete_project_voice(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
    open_projects_page()

def open_projects_page():
    # Clear main content
    for widget in main_content.winfo_children():
        widget.destroy()
     # Back button
    back_button = ctk.CTkButton(
        main_content,
        text="<-] Back",
        width=120,
        height=40,
        font=("Arial", 15, "bold"),
        command=open_home_page
    )
    back_button.pack(
        anchor="w",
        padx=30,
        pady=(20, 10)
    )
        # title
    title = ctk.CTkLabel(
        main_content,
        text="My Projects",
        font=("Arial", 30, "bold")
    )
    title.pack(pady=(10, 5))
    subtitle = ctk.CTkLabel(
        main_content,
        text="Recent AI creations",
        font=("Arial", 16)
    )
    subtitle.pack(pady=(0, 30))
    # projects area
    projects_frame = ctk.CTkScrollableFrame(
        main_content,
        width=700,
        height=350
    )
    projects_frame.pack(
        pady=10,
        padx=30
    )
    # load saved image
    save_folder = SAVE_FOLDER
    image_files = []
    
    if os.path.exists(save_folder):
        image_files = [
            file for file in os.listdir(save_folder)
            if file.lower().endswith((".png", ".jpg", "jpeg"))
        ]
    voice_files = []
    if os.path.exists(SAVE_VOICES_FOLDER):
        voice_files = [
            file for file in os.listdir(SAVE_VOICES_FOLDER)
            if file.lower().endswith(".mp3")
        ]
    if image_files or voice_files:
        row_frame = None
        for index, file in enumerate(image_files):
            if index % 3 == 0:
                row_frame = ctk.CTkFrame(
                    projects_frame,
                    fg_color="transparent"
                )
                row_frame.pack(
                    fill="x",
                    pady=5
                )
            image_path = os.path.join(
                save_folder,
                file
            )
            image = Image.open(image_path)
            project_image = ctk.CTkImage(
                light_image=image,
                dark_image=image,
                size=(200, 140)
            )
            card_frame = ctk.CTkFrame(
                row_frame,
                fg_color="transparent"
            )
            card_frame.pack(
                side="left",
                padx=10,
                pady=10
            )
            image_label = ctk.CTkLabel(
                card_frame,
                text="",
                image=project_image
            )
            image_label.pack()
            image_label.image = project_image
            image_label.bind(
                "<Button-1>",
                lambda event, path=image_path: os.startfile(path)
            )

            delele_button = ctk.CTkButton(
                card_frame,
                text="🗑 Delete",
                width=100,
                command=lambda
                path=image_path: delete_project_image(path)
            )
            delele_button.pack(pady=(5, 10))
        for file in voice_files:
            voice_path = os.path.join(SAVE_VOICES_FOLDER, file)
            voice_frame = ctk.CTkFrame(projects_frame)
            voice_frame.pack(fill="x", padx=10, pady=5)
            voice_label = ctk.CTkLabel(
                voice_frame,
                text=file,
                font=("Arial", 15)
            )
            voice_label.pack(side="left", padx=10, pady=10)
            voice_label.bind(
                "<Button-1>",
                lambda event, path=voice_path: os.startfile(path)
            )
            voice_delete_button = ctk.CTkButton(
                voice_frame,
                text="🗑 Delete",
                width=100,
                command=lambda
                path=voice_path: delete_project_voice(path)
            )
            voice_delete_button.pack(side="right", padx=10, pady=5)
    else:
        empty_label = ctk.CTkLabel(
            projects_frame,
            text="No projects yet!\n\nYour AI creation will appear here"
        )
        empty_label.pack(expand=True)

def open_settings_page():
    # Clear main content
    for widget in main_content.winfo_children():
        widget.destroy()
     # Back button
    back_button = ctk.CTkButton(
        main_content,
        text="<-] Back",
        width=120,
        height=40,
        font=("Arial", 15, "bold"),
        command=open_home_page
    )
    back_button.pack(
        anchor="w",
        padx=30,
        pady=(20, 10)
    )

        # title
    title = ctk.CTkLabel(
        main_content,
        text="Settings",
        font=("Arial", 30, "bold")
    )
    title.pack(pady=(10, 5))

    subtitle = ctk.CTkLabel(
        main_content,
        text="Customize your ABY_GW AI Studio experience",
        font=("Arial", 16)
    )
    subtitle.pack(pady=(0, 30))

    # settings area
    settings_frame = ctk.CTkFrame(
        main_content,
        width=700,
        height=350
    )
    settings_frame.pack(
        pady=10,
        padx=30
    )
    settings_frame.pack_propagate(False)

    # Appearance Section
    appearance_label = ctk.CTkLabel(
        settings_frame,
        text="Appearance",
        font=("Arial", 20, "bold")
    )
    appearance_label.pack(
        pady=(40, 10)
    )
    appearance_menu = ctk.CTkOptionMenu(
        settings_frame,
        values=[
            "Dark",
            "Light",
            "System"
        ],
        width=220,
        height=40
    )
    appearance_menu.set("Dark")
    appearance_menu.pack(pady=(0, 25))

    # Future Settings message
    info_label = ctk.CTkLabel(
        settings_frame,
        text="More settings will be available soon in sha Allah",
        font=("Arial", 15)
    )
    info_label.pack(pady=20)

#==============================
#SIDEBAR
#==============================
sidebar = ctk.CTkFrame(
app,
width=200,
corner_radius=0
)
sidebar.pack(
    side="left",
    fill="y"
)
#Logo/Appname
logo_label = ctk.CTkLabel(
    sidebar,
    text="✦ ABY_GW\nAI Studio",
    font=("Arial",24,"bold"),
    justify="left"
)
logo_label.pack(
    pady=(35, 50),
    padx=25,
    anchor="w"
)
#==============================
#SIDEBAR BUTTONS
#==============================
home_button = ctk.CTkButton(
    sidebar,
    text=" Home",
    height=45,
    anchor="w",
    command=open_home_page
)
home_button.pack(
    fill="x",
    padx=20,
    pady=8
)
image_button = ctk.CTkButton(
    sidebar,
    text=" Image Generation",
    height=45,
    anchor="w",
    command=open_image_page
)

image_button.pack(
    fill="x",
    padx=20,
    pady=8
)
video_button = ctk.CTkButton(
    sidebar,
    text=" Video Generation",
    height=45,
    anchor="w",
    command=open_video_page
)
video_button.pack(
    fill="x",
    padx=20,
    pady=8
)
voice_button = ctk.CTkButton(
    sidebar,
    text="Ω Voice Generation",
    height=45,
    anchor="w",
    command=open_voice_page
)
voice_button.pack(
    fill="x",
    padx=20,
    pady=8
)
projects_button = ctk.CTkButton(
    sidebar,
    text=" My Projects",
    height=45,
    anchor="w",
    command=open_projects_page
)
projects_button.pack(
    fill="x",
    padx=20,
    pady=8
)
#==============================
#SETTING BUTTON
#==============================
settings_button = ctk.CTkButton(
    sidebar,
    text="⚙ Settings",
    height=45,
    anchor="w",
    command=open_settings_page
)
settings_button.pack(
    side="bottom",
    fill="x",
    padx=20,
    pady=30
)

open_home_page()
app.mainloop()

"""
 # voice description
    voice_description_box = ctk.CTkTextbox(
        main_content,
        width=500,
        height=100,
        font=("Arial", 15),
    )
    voice_description_box.pack(pady=(0, 15))
    voice_description_box.insert(
        "1.0",
        "Describe your voice..."
    )
    voice_description_box.bind(
        "<FocusIn>",
        lambda event: (
            voice_description_box.delete("1.0", "end")
            if voice_description_box.get("1.0", "end-1c") == "Describe your voice..."
            else None
        )
    )
"""