const views = {
  home: {
    eyebrow: "ABY_GW AI STUDIO",
    title: "Create without limits.",
    message: "A focused workspace for turning your ideas into images, videos, and voices.",
    home: true,
  },
  image: {
    eyebrow: "CREATION TOOL",
    title: "Image Generation",
    message: "Create an image from a description using the ABY_GW image engine.",
    imageTool: true,
  },
  video: {
    eyebrow: "CREATION TOOL",
    title: "Video Generation",
    message: "Create cinematic AI videos from text, images, or audio.",
    videoTool: true,
  },
  voice: {
    eyebrow: "CREATION TOOL",
    title: "Voice Generation",
    message: "Create and shape natural-sounding voices from this workspace.",
  },
  "video-cutter": {
    eyebrow: "VIDEO SERVICES",
    title: "Video Cutter",
    message: "Extract a precise section from a video file.",
    serviceType: "video-cutter",
  },
  "video-merger": {
    eyebrow: "VIDEO SERVICES",
    title: "Video Merger",
    message: "Join multiple video files in their selected order.",
    serviceType: "video-merger",
  },
  "video-editing": {
    eyebrow: "VIDEO SERVICES",
    title: "Video Editing",
    message: "Add one background audio track to an existing video.",
    videoEditing: true,
  },
  "audio-cutter": {
    eyebrow: "AUDIO SERVICES",
    title: "Audio Cutter",
    message: "Extract a precise section from an audio file.",
    serviceType: "audio-cutter",
  },
  "audio-merger": {
    eyebrow: "AUDIO SERVICES",
    title: "Audio Merger",
    message: "Join multiple audio files in their selected order.",
    serviceType: "audio-merger",
  },
  projects: {
    eyebrow: "YOUR WORKSPACE",
    title: "My Projects",
    message: "Your saved creative projects will appear here.",
  },
  settings: {
    eyebrow: "PREFERENCES",
    title: "Settings",
    message: "Studio preferences and account controls will live here.",
  },
};

const featureCards = [
  { icon: "✦", title: "Image Generation", text: "Bring visual ideas to life." },
  { icon: "▶", title: "Video Generation", text: "Build cinematic moments." },
  { icon: "◉", title: "Voice Generation", text: "Give your ideas a voice." },
];

const SETTINGS_KEY = "aby-gw-ai-studio-settings";
const DEFAULT_SETTINGS = {
  theme: "dark",
  accent: "#83c9dc",
  scale: "100%",
  language: "English",
};
const translations = {
  English: {
    workspace: "AI Workspace", home: "Home", imageGeneration: "Image Generation",
    videoGeneration: "Video Generation", voiceGeneration: "Voice Generation", videoEditing: "Video Editing",
    videoServices: "Video Services", videoCutter: "Video Cutter", videoMerger: "Video Merger",
    audioServices: "Audio Services", audioCutter: "Audio Cutter", audioMerger: "Audio Merger",
    projects: "Projects", myProjects: "My Projects", settings: "Settings",
    studioOnline: "Studio online", creativeWorkspace: "CREATIVE WORKSPACE", webVersion: "Web version",
    appearance: "Appearance", theme: "Theme", accentColor: "Accent Color", interface: "Interface",
    uiScale: "UI Scale", language: "Language", about: "About", application: "Application",
    version: "Version", saveSettings: "Settings saved", dark: "Dark", light: "Light",
  },
  Arabic: {
    workspace: "مساحة عمل الذكاء الاصطناعي", home: "الرئيسية", imageGeneration: "إنشاء الصور",
    videoGeneration: "إنشاء الفيديو", voiceGeneration: "إنشاء الصوت", videoEditing: "تحرير الفيديو", videoServices: "خدمات الفيديو",
    videoCutter: "قص الفيديو", videoMerger: "دمج الفيديو", audioServices: "خدمات الصوت",
    audioCutter: "قص الصوت", audioMerger: "دمج الصوت", projects: "المشاريع",
    myProjects: "مشاريعي", settings: "الإعدادات", studioOnline: "الاستوديو متصل",
    creativeWorkspace: "مساحة العمل الإبداعية", webVersion: "إصدار الويب", appearance: "المظهر",
    theme: "السمة", accentColor: "لون التمييز", interface: "الواجهة", uiScale: "مقياس الواجهة",
    language: "اللغة", about: "حول التطبيق", application: "التطبيق", version: "الإصدار",
    saveSettings: "تم حفظ الإعدادات", dark: "داكن", light: "فاتح",
  },
};

function loadSettings() {
  try {
    return { ...DEFAULT_SETTINGS, ...JSON.parse(localStorage.getItem(SETTINGS_KEY) || "{}") };
  } catch (error) {
    return { ...DEFAULT_SETTINGS };
  }
}

let appSettings = loadSettings();

function applySettings() {
  const root = document.documentElement;
  root.dataset.theme = appSettings.theme;
  root.dataset.language = appSettings.language;
  root.dir = appSettings.language === "Arabic" ? "rtl" : "ltr";
  root.lang = appSettings.language === "Arabic" ? "ar" : "en";
  root.style.setProperty("--accent", appSettings.accent);
  root.style.setProperty("--accent-soft", `${appSettings.accent}1f`);
  root.style.setProperty("--ui-scale", appSettings.scale.replace("%", "") / 100);
  document.querySelectorAll("[data-i18n]").forEach((element) => {
    const value = translations[appSettings.language][element.dataset.i18n];
    if (value) element.textContent = value;
  });
}

function saveSettings() {
  localStorage.setItem(SETTINGS_KEY, JSON.stringify(appSettings));
  applySettings();
}

const PROJECT_DATABASE = "aby-gw-ai-studio";
const PROJECT_STORE = "image-projects";
let projectImageUrls = [];
let projectVideoUrls = [];
let projectAudioUrls = [];

function openProjectDatabase() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(PROJECT_DATABASE, 1);
    request.onupgradeneeded = () => {
      request.result.createObjectStore(PROJECT_STORE, {
        keyPath: "id",
        autoIncrement: true,
      });
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

async function saveImageProject(project) {
  const database = await openProjectDatabase();
  return new Promise((resolve, reject) => {
    const transaction = database.transaction(PROJECT_STORE, "readwrite");
    transaction.objectStore(PROJECT_STORE).add(project);
    transaction.oncomplete = () => {
      database.close();
      resolve();
    };
    transaction.onerror = () => {
      database.close();
      reject(transaction.error);
    };
  });
}

async function getImageProjects() {
  const database = await openProjectDatabase();
  return new Promise((resolve, reject) => {
    const request = database.transaction(PROJECT_STORE, "readonly")
      .objectStore(PROJECT_STORE)
      .getAll();
    request.onsuccess = () => {
      database.close();
      resolve(request.result.sort((first, second) => second.createdAt - first.createdAt));
    };
    request.onerror = () => {
      database.close();
      reject(request.error);
    };
  });
}

async function deleteImageProject(projectId) {
  const database = await openProjectDatabase();
  return new Promise((resolve, reject) => {
    const transaction = database.transaction(PROJECT_STORE, "readwrite");
    transaction.objectStore(PROJECT_STORE).delete(projectId);
    transaction.oncomplete = () => {
      database.close();
      resolve();
    };
    transaction.onerror = () => {
      database.close();
      reject(transaction.error);
    };
  });
}

function escapeHtml(value) {
  return value.replace(/[&<>'"]/g, (character) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    "'": "&#39;",
    '"': "&quot;",
  }[character]));
}

function renderView(viewName) {
  const view = views[viewName] || views.home;
  const appView = document.querySelector("#app-view");

  if (view.imageTool) {
    appView.innerHTML = `
      <div class="tool-header">
        <p class="eyebrow">${view.eyebrow}</p>
        <h1>${view.title}</h1>
        <p class="tool-message">${view.message}</p>
      </div>
      <div class="image-tool-layout">
        <form id="image-form" class="image-controls">
          <label for="image-prompt">Describe your image</label>
          <textarea id="image-prompt" name="prompt" rows="4" maxlength="2000" placeholder="A cinematic mountain landscape at sunrise..." required></textarea>
          <div class="control-row">
            <div class="ratio-control">
              <label for="image-ratio">Aspect ratio</label>
              <select id="image-ratio" name="ratio">
                <option value="1:1">1:1</option>
                <option value="16:9">16:9</option>
                <option value="9:16">9:16</option>
                <option value="2:3">2:3</option>
                <option value="3:2">3:2</option>
              </select>
            </div>
            <button class="primary-button" type="submit" id="generate-image">Generate</button>
          </div>
          <p id="image-status" class="form-status" role="status"></p>
        </form>
        <section class="image-preview-panel" aria-label="Generated image preview">
          <div id="image-preview" class="image-preview">
            <span>Your image will appear here</span>
          </div>
          <div class="preview-actions">
            <button class="secondary-button" type="button" id="save-image" disabled>Save</button>
            <button class="secondary-button danger-button" type="button" id="delete-image" disabled>Delete</button>
          </div>
        </section>
      </div>
    `;
    bindImageTool();
  } else if (view.videoTool) {
    appView.innerHTML = `
      <div class="tool-header">
        <p class="eyebrow">${view.eyebrow}</p>
        <h1>${view.title}</h1>
        <p class="tool-message">${view.message}</p>
      </div>
      <div class="image-tool-layout video-tool-layout">
        <form id="video-form" class="image-controls">
          <label for="video-prompt">Describe your video</label>
          <textarea id="video-prompt" name="prompt" rows="4" maxlength="2000" placeholder="A cinematic ocean sunset with gentle waves..." required></textarea>
          <div class="video-select-row">
            <div class="ratio-control">
              <label for="video-ratio">Aspect ratio</label>
              <select id="video-ratio" name="ratio">
                <option value="16:9">16:9</option>
                <option value="9:16">9:16</option>
                <option value="1:1">1:1</option>
              </select>
            </div>
            <div class="duration-control">
              <label for="video-duration">Duration</label>
              <select id="video-duration" name="duration">
                <option value="1">1 sec</option><option value="2">2 sec</option><option value="3">3 sec</option>
                <option value="4">4 sec</option><option value="5">5 sec</option><option value="10">10 sec</option><option value="15">15 sec</option>
              </select>
            </div>
          </div>
          <label for="video-image">Optional image</label>
          <input id="video-image" type="file" accept="image/png,image/jpeg,image/webp">
          <label for="video-audio">Optional audio</label>
          <input id="video-audio" type="file" accept="audio/mpeg,audio/wav,audio/mp4,audio/aac">
          <button class="primary-button" type="submit" id="generate-video">Generate Video</button>
          <p id="video-status" class="form-status" role="status"></p>
        </form>
        <section class="image-preview-panel" aria-label="Generated video preview">
          <div id="video-preview" class="image-preview video-preview">
            <span>Your video will appear here</span>
          </div>
          <div class="preview-actions">
            <button class="secondary-button" type="button" id="save-video" disabled>Save</button>
            <button class="secondary-button danger-button" type="button" id="delete-video" disabled>Delete</button>
          </div>
        </section>
      </div>
    `;
    bindVideoTool();
  } else if (viewName === "voice") {
    appView.innerHTML = `
      <div class="tool-header">
        <p class="eyebrow">${view.eyebrow}</p>
        <h1>${view.title}</h1>
        <p class="tool-message">${view.message}</p>
      </div>
      <div class="image-tool-layout voice-tool-layout">
        <form id="voice-form" class="image-controls">
          <label for="voice-text">Enter your text</label>
          <textarea id="voice-text" name="text" rows="6" maxlength="5000" placeholder="Write the words you want to hear..." required></textarea>
          <div class="video-select-row">
            <div class="ratio-control">
              <label for="voice-language">Language</label>
              <select id="voice-language" name="language" required>
                <option value="">Select language</option>
                <option value="English">English</option>
                <option value="Arabic">Arabic</option>
                <option value="Hausa">Hausa</option>
              </select>
            </div>
            <div class="voice-style-control">
              <label for="voice-style">Voice style</label>
              <select id="voice-style" name="voice_style" required>
                <option value="">Select style</option>
                <option value="Male">Male</option>
                <option value="Female">Female</option>
                <option value="Narrator">Narrator</option>
              </select>
            </div>
          </div>
          <button class="primary-button" type="submit" id="generate-voice">Generate Voice</button>
          <p id="voice-status" class="form-status" role="status"></p>
        </form>
        <section class="image-preview-panel" aria-label="Generated voice preview">
          <div id="voice-preview" class="image-preview voice-preview">
            <span>Your voice will appear here</span>
          </div>
          <div class="preview-actions">
            <button class="secondary-button" type="button" id="save-voice" disabled>Save and Download</button>
            <button class="secondary-button danger-button" type="button" id="delete-voice" disabled>Delete</button>
          </div>
        </section>
      </div>
    `;
    bindVoiceTool();
  } else if (view.videoEditing) {
    appView.innerHTML = `
      <div class="tool-header">
        <p class="eyebrow">${view.eyebrow}</p>
        <h1>${view.title}</h1>
        <p class="tool-message">${view.message}</p>
      </div>
      <div class="image-tool-layout video-editing-layout">
        <form id="video-editing-form" class="image-controls">
          <label for="editing-video">Video</label>
          <input id="editing-video" type="file" accept="video/*" required>
          <p id="editing-video-name" class="file-name">No video selected.</p>
          <label for="editing-audio">Additional Audio</label>
          <input id="editing-audio" type="file" accept="audio/*" required>
          <p id="editing-audio-name" class="file-name">No audio selected.</p>
          <label for="editing-volume">Audio Volume <output id="editing-volume-value">28%</output></label>
          <input id="editing-volume" type="range" min="0" max="100" value="28" step="1">
          <div class="service-time-row">
            <div><label for="editing-start">Start time (seconds)</label><input id="editing-start" type="number" min="0" step="0.01" value="0" required></div>
            <div><label for="editing-end">End time (optional)</label><input id="editing-end" type="number" min="0.01" step="0.01" placeholder="Until video ends"></div>
          </div>
          <button class="primary-button" type="submit" id="generate-edited-video">Generate Edited Video</button>
          <p id="video-editing-status" class="form-status" role="status"></p>
        </form>
        <section class="image-preview-panel" aria-label="Edited video preview">
          <div id="video-editing-preview" class="image-preview service-preview">
            <span>Your edited video will appear here</span>
          </div>
          <div class="preview-actions">
            <button class="secondary-button" type="button" id="save-edited-video" disabled>Save and Download</button>
            <button class="secondary-button danger-button" type="button" id="delete-edited-video" disabled>Delete</button>
          </div>
        </section>
      </div>
    `;
    bindVideoEditing();
  } else if (view.serviceType) {
    appView.innerHTML = `
      <div class="tool-header">
        <p class="eyebrow">${view.eyebrow}</p>
        <h1>${view.title}</h1>
        <p class="tool-message">${view.message}</p>
      </div>
      <div class="image-tool-layout service-tool-layout">
        <form id="service-form" class="image-controls">
          <label for="service-files">${view.serviceType.includes("merger") ? "Select media files in order" : "Select a media file"}</label>
          <input id="service-files" type="file" ${view.serviceType.includes("video") ? 'accept="video/*"' : 'accept="audio/*"'} ${view.serviceType.includes("merger") ? "multiple" : ""} required>
          ${view.serviceType.includes("cutter") ? `
            <div class="service-time-row">
              <div><label for="service-start">Start time (seconds)</label><input id="service-start" type="number" min="0" step="0.01" value="0" required></div>
              <div><label for="service-end">End time (seconds)</label><input id="service-end" type="number" min="0.01" step="0.01" required></div>
            </div>
          ` : ""}
          <button class="primary-button" type="submit" id="process-service">${view.title}</button>
          <p id="service-status" class="form-status" role="status"></p>
        </form>
        <section class="image-preview-panel" aria-label="Processed media preview">
          <div id="service-preview" class="image-preview service-preview">
            <span>Your processed media will appear here</span>
          </div>
          <div class="preview-actions">
            <button class="secondary-button" type="button" id="save-service" disabled>Save and Download</button>
            <button class="secondary-button danger-button" type="button" id="delete-service" disabled>Delete</button>
          </div>
        </section>
      </div>
    `;
    bindMediaService(view.serviceType, view.title);
  } else if (viewName === "settings") {
    const text = translations[appSettings.language];
    appView.innerHTML = `
      <div class="simple-page settings-header">
        <p class="eyebrow">${text.settings}</p>
        <h1>${text.settings}</h1>
        <p>${appSettings.language === "Arabic" ? "خصص تجربة ABY_GW AI Studio." : "Customize your ABY_GW AI Studio experience."}</p>
      </div>
      <div class="settings-grid">
        <section class="settings-section">
          <h2>${text.appearance}</h2>
          <label for="setting-theme">${text.theme}</label>
          <select id="setting-theme">
            <option value="dark" ${appSettings.theme === "dark" ? "selected" : ""}>${text.dark}</option>
            <option value="light" ${appSettings.theme === "light" ? "selected" : ""}>${text.light}</option>
          </select>
          <label for="setting-accent">${text.accentColor}</label>
          <input id="setting-accent" class="accent-picker" type="color" value="${appSettings.accent}" aria-label="${text.accentColor}">
        </section>
        <section class="settings-section">
          <h2>${text.interface}</h2>
          <label for="setting-scale">${text.uiScale}</label>
          <select id="setting-scale">
            ${["80%", "90%", "100%", "110%", "120%"].map((scale) => `<option value="${scale}" ${appSettings.scale === scale ? "selected" : ""}>${scale}</option>`).join("")}
          </select>
          <label for="setting-language">${text.language}</label>
          <select id="setting-language">
            <option value="English" ${appSettings.language === "English" ? "selected" : ""}>English</option>
            <option value="Arabic" ${appSettings.language === "Arabic" ? "selected" : ""}>العربية</option>
          </select>
        </section>
        <section class="settings-section about-section">
          <h2>${text.about}</h2>
          <p><strong>${text.application}:</strong> ABY_GW AI Studio</p>
          <p><strong>${text.version}:</strong> 1.0.0</p>
        </section>
      </div>
      <p id="settings-status" class="form-status settings-status" role="status"></p>
    `;
    bindSettings();
  } else if (viewName === "projects") {
    appView.innerHTML = `
      <div class="simple-page projects-header">
        <p class="eyebrow">${view.eyebrow}</p>
        <h1>${view.title}</h1>
        <p>${view.message}</p>
      </div>
      <div id="projects-grid" class="projects-grid" aria-live="polite">
        <p class="projects-status">Loading saved projects...</p>
      </div>
    `;
    loadProjects();
  } else if (view.home) {
    appView.innerHTML = `
      <div class="home-header">
        <p class="eyebrow">${view.eyebrow}</p>
        <h1>${view.title}</h1>
        <p class="welcome-message">${view.message}</p>
      </div>
      <div class="feature-grid">
        ${featureCards.map((card) => `
          <article class="feature-card">
            <div class="feature-icon" aria-hidden="true">${card.icon}</div>
            <h2>${card.title}</h2>
            <p>${card.text}</p>
          </article>
        `).join("")}
      </div>
    `;
  } else {
    appView.innerHTML = `
      <div class="simple-page">
        <p class="eyebrow">${view.eyebrow}</p>
        <h1>${view.title}</h1>
        <p>${view.message}</p>
      </div>
    `;
  }

  appView.classList.remove("app-view");
  void appView.offsetWidth;
  appView.classList.add("app-view");
}

function bindVideoEditing() {
  const form = document.querySelector("#video-editing-form");
  const videoInput = document.querySelector("#editing-video");
  const audioInput = document.querySelector("#editing-audio");
  const videoName = document.querySelector("#editing-video-name");
  const audioName = document.querySelector("#editing-audio-name");
  const volumeInput = document.querySelector("#editing-volume");
  const volumeValue = document.querySelector("#editing-volume-value");
  const startInput = document.querySelector("#editing-start");
  const endInput = document.querySelector("#editing-end");
  const generateButton = document.querySelector("#generate-edited-video");
  const saveButton = document.querySelector("#save-edited-video");
  const deleteButton = document.querySelector("#delete-edited-video");
  const status = document.querySelector("#video-editing-status");
  const preview = document.querySelector("#video-editing-preview");
  let videoUrl = null;
  let editedVideoUrl = null;

  videoInput.addEventListener("change", () => {
    const file = videoInput.files[0];
    videoName.textContent = file ? file.name : "No video selected.";
    if (videoUrl) URL.revokeObjectURL(videoUrl);
    videoUrl = file ? URL.createObjectURL(file) : null;
    if (videoUrl) preview.innerHTML = `<video src="${videoUrl}" controls></video>`;
  });
  audioInput.addEventListener("change", () => {
    audioName.textContent = audioInput.files[0]?.name || "No audio selected.";
  });
  volumeInput.addEventListener("input", () => {
    volumeValue.textContent = `${volumeInput.value}%`;
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const video = videoInput.files[0];
    const audio = audioInput.files[0];
    const start = Number(startInput.value);
    const end = endInput.value.trim() ? Number(endInput.value) : null;
    if (!video || !audio) {
      status.textContent = "Select both a video and an audio file first.";
      return;
    }
    if (!Number.isFinite(start) || start < 0 || (end !== null && (!Number.isFinite(end) || end <= start))) {
      status.textContent = "Enter a valid time range.";
      return;
    }

    const formData = new FormData();
    formData.append("video", video);
    formData.append("audio", audio);
    formData.append("volume", String(Number(volumeInput.value) / 100));
    formData.append("start_time", String(start));
    if (end !== null) formData.append("end_time", String(end));
    generateButton.disabled = true;
    saveButton.disabled = true;
    deleteButton.disabled = true;
    status.textContent = "Generating edited video... Please wait.";
    preview.innerHTML = '<span class="loading-state">Mixing the audio tracks...</span>';
    try {
      const response = await fetch("/api/services/video/edit", { method: "POST", body: formData });
      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || "Video editing failed.");
      }
      const blob = await response.blob();
      if (editedVideoUrl) URL.revokeObjectURL(editedVideoUrl);
      editedVideoUrl = URL.createObjectURL(blob);
      preview.innerHTML = `<video src="${editedVideoUrl}" controls autoplay></video>`;
      saveButton.disabled = false;
      deleteButton.disabled = false;
      status.textContent = "Edited video generated successfully.";
    } catch (error) {
      preview.innerHTML = videoUrl ? `<video src="${videoUrl}" controls></video>` : "<span>Your edited video will appear here</span>";
      status.textContent = error.message;
    } finally {
      generateButton.disabled = false;
    }
  });

  saveButton.addEventListener("click", async () => {
    if (!editedVideoUrl) return;
    saveButton.disabled = true;
    try {
      const response = await fetch(editedVideoUrl);
      await saveImageProject({
        type: "video",
        service: "edited",
        prompt: `Video Editing: ${videoInput.files[0].name} + ${audioInput.files[0].name}`,
        blob: await response.blob(),
        createdAt: Date.now(),
      });
      const downloadLink = document.createElement("a");
      downloadLink.href = editedVideoUrl;
      downloadLink.download = `aby-gw-edited-video-${new Date().toISOString().slice(0, 10)}.mp4`;
      downloadLink.click();
      status.textContent = "Edited video saved and added to My Projects.";
    } catch (error) {
      status.textContent = "The edited video could not be saved locally.";
    } finally {
      saveButton.disabled = false;
    }
  });

  deleteButton.addEventListener("click", () => {
    if (editedVideoUrl) URL.revokeObjectURL(editedVideoUrl);
    editedVideoUrl = null;
    preview.innerHTML = videoUrl ? `<video src="${videoUrl}" controls></video>` : "<span>Your edited video will appear here</span>";
    saveButton.disabled = true;
    deleteButton.disabled = true;
    status.textContent = "Edited video cleared.";
  });
}

function bindSettings() {
  const themeInput = document.querySelector("#setting-theme");
  const accentInput = document.querySelector("#setting-accent");
  const scaleInput = document.querySelector("#setting-scale");
  const languageInput = document.querySelector("#setting-language");
  const status = document.querySelector("#settings-status");

  const update = (changes) => {
    appSettings = { ...appSettings, ...changes };
    saveSettings();
    status.textContent = translations[appSettings.language].saveSettings;
    renderView("settings");
    setActiveNavigation("settings");
  };

  themeInput.addEventListener("change", () => update({ theme: themeInput.value }));
  accentInput.addEventListener("input", () => update({ accent: accentInput.value }));
  scaleInput.addEventListener("change", () => update({ scale: scaleInput.value }));
  languageInput.addEventListener("change", () => update({ language: languageInput.value }));
}

async function loadProjects() {
  const projectsGrid = document.querySelector("#projects-grid");
  if (!projectsGrid) {
    return;
  }

  try {
    const projects = await getImageProjects();
    if (!projects.length) {
      projectsGrid.innerHTML = '<p class="projects-status">Saved images, videos, and voices will appear here.</p>';
      return;
    }

    projectImageUrls.forEach((url) => URL.revokeObjectURL(url));
    projectVideoUrls.forEach((url) => URL.revokeObjectURL(url));
    projectAudioUrls.forEach((url) => URL.revokeObjectURL(url));
    projectImageUrls = projects.map((project) => project.type ? null : URL.createObjectURL(project.blob));
    projectVideoUrls = projects.map((project) => project.type === "video" ? URL.createObjectURL(project.blob) : null);
    projectAudioUrls = projects.map((project) => ["voice", "audio"].includes(project.type) ? URL.createObjectURL(project.blob) : null);
    projectsGrid.innerHTML = projects.map((project, index) => `
      <article class="project-card">
        ${project.type === "video"
          ? `<video src="${projectVideoUrls[index]}" controls preload="metadata" aria-label="Saved video project"></video>`
          : ["voice", "audio"].includes(project.type)
            ? `<div class="project-audio"><span aria-hidden="true">Audio</span><audio src="${projectAudioUrls[index]}" controls preload="metadata" aria-label="Saved voice project"></audio></div>`
            : `<img src="${projectImageUrls[index]}" alt="Saved image project">`}
        <div class="project-card-details">
          <h2>${project.type === "video" ? (project.service ? `Video ${project.service} project` : "Video project") : ["voice", "audio"].includes(project.type) ? (project.service ? `Audio ${project.service} project` : "Voice project") : "Image project"}</h2>
          <p>${escapeHtml(project.prompt)}</p>
          <time datetime="${new Date(project.createdAt).toISOString()}">${new Date(project.createdAt).toLocaleString()}</time>
          <div class="project-card-actions">
            <button class="secondary-button project-open" type="button" data-project-id="${project.id}" data-media-url="${project.type === "video" ? projectVideoUrls[index] : ["voice", "audio"].includes(project.type) ? projectAudioUrls[index] : projectImageUrls[index]}">Open</button>
            <button class="secondary-button danger-button project-delete" type="button" data-project-id="${project.id}">Delete</button>
          </div>
        </div>
      </article>
    `).join("");
    bindProjectActions();
  } catch (error) {
    projectsGrid.innerHTML = '<p class="projects-status">Saved projects could not be loaded.</p>';
  }
}

function bindMediaService(serviceType, title) {
  const form = document.querySelector("#service-form");
  const filesInput = document.querySelector("#service-files");
  const startInput = document.querySelector("#service-start");
  const endInput = document.querySelector("#service-end");
  const processButton = document.querySelector("#process-service");
  const saveButton = document.querySelector("#save-service");
  const deleteButton = document.querySelector("#delete-service");
  const status = document.querySelector("#service-status");
  const preview = document.querySelector("#service-preview");
  const isVideo = serviceType.startsWith("video");
  const isMerger = serviceType.endsWith("merger");
  let mediaUrl = null;

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const files = Array.from(filesInput.files);
    if ((!isMerger && files.length !== 1) || (isMerger && files.length < 2)) {
      status.textContent = isMerger ? "Select at least 2 files in the order to merge." : "Select one media file first.";
      return;
    }
    if (!isMerger && Number(endInput.value) <= Number(startInput.value)) {
      status.textContent = "End time must be greater than start time.";
      return;
    }

    const formData = new FormData();
    const fieldName = isVideo && isMerger ? "videos" : isVideo ? "video" : "audio";
    files.forEach((file) => formData.append(fieldName, file));
    if (!isMerger) {
      formData.append("start_time", startInput.value);
      formData.append("end_time", endInput.value);
    }
    processButton.disabled = true;
    saveButton.disabled = true;
    deleteButton.disabled = true;
    status.textContent = `${title} processing... Please wait.`;
    preview.innerHTML = '<span class="loading-state">Processing your media...</span>';

    try {
      const response = await fetch(`/api/services/${isVideo ? "video" : "audio"}/${isMerger ? "merge" : "cut"}`, {
        method: "POST",
        body: formData,
      });
      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || `${title} failed.`);
      }
      const mediaBlob = await response.blob();
      if (mediaUrl) URL.revokeObjectURL(mediaUrl);
      mediaUrl = URL.createObjectURL(mediaBlob);
      preview.innerHTML = isVideo
        ? `<video src="${mediaUrl}" controls autoplay></video>`
        : `<audio src="${mediaUrl}" controls autoplay></audio>`;
      saveButton.disabled = false;
      deleteButton.disabled = false;
      status.textContent = `${title} completed successfully.`;
    } catch (error) {
      preview.innerHTML = "<span>Your processed media will appear here</span>";
      status.textContent = error.message;
    } finally {
      processButton.disabled = false;
    }
  });

  saveButton.addEventListener("click", async () => {
    if (!mediaUrl) return;
    saveButton.disabled = true;
    status.textContent = `Saving ${title.toLowerCase()}...`;
    try {
      const mediaResponse = await fetch(mediaUrl);
      await saveImageProject({
        type: isVideo ? "video" : "audio",
        service: title.replace("Video ", "").replace("Audio ", "").toLowerCase(),
        prompt: `${title}: ${Array.from(filesInput.files).map((file) => file.name).join(", ")}`,
        blob: await mediaResponse.blob(),
        createdAt: Date.now(),
      });
      const downloadLink = document.createElement("a");
      downloadLink.href = mediaUrl;
      downloadLink.download = `aby-gw-${serviceType}-${new Date().toISOString().slice(0, 10)}.${isVideo ? "mp4" : "mp3"}`;
      downloadLink.click();
      status.textContent = `${title} saved successfully and added to My Projects.`;
    } catch (error) {
      status.textContent = `The ${title.toLowerCase()} could not be saved locally.`;
    } finally {
      saveButton.disabled = false;
    }
  });

  deleteButton.addEventListener("click", () => {
    if (mediaUrl) URL.revokeObjectURL(mediaUrl);
    mediaUrl = null;
    preview.innerHTML = "<span>Your processed media will appear here</span>";
    saveButton.disabled = true;
    deleteButton.disabled = true;
    status.textContent = "Processed media cleared.";
  });
}

function bindVoiceTool() {
  const form = document.querySelector("#voice-form");
  const textInput = document.querySelector("#voice-text");
  const languageInput = document.querySelector("#voice-language");
  const styleInput = document.querySelector("#voice-style");
  const generateButton = document.querySelector("#generate-voice");
  const saveButton = document.querySelector("#save-voice");
  const deleteButton = document.querySelector("#delete-voice");
  const status = document.querySelector("#voice-status");
  const preview = document.querySelector("#voice-preview");
  let audioUrl = null;

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const text = textInput.value.trim();
    if (!text || !languageInput.value || !styleInput.value) {
      status.textContent = "Enter text and select a language and voice style.";
      return;
    }

    generateButton.disabled = true;
    saveButton.disabled = true;
    deleteButton.disabled = true;
    status.textContent = "Generating voice... Please wait.";
    preview.innerHTML = '<span class="loading-state">Creating your voice...</span>';
    try {
      const response = await fetch("/api/voices/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, language: languageInput.value, voice_style: styleInput.value }),
      });
      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || "Voice generation failed.");
      }
      const audioBlob = await response.blob();
      if (audioUrl) URL.revokeObjectURL(audioUrl);
      audioUrl = URL.createObjectURL(audioBlob);
      preview.innerHTML = `<audio src="${audioUrl}" controls autoplay aria-label="Generated voice"></audio>`;
      saveButton.disabled = false;
      deleteButton.disabled = false;
      status.textContent = "Voice generated successfully.";
    } catch (error) {
      preview.innerHTML = "<span>Your voice will appear here</span>";
      status.textContent = error.message;
    } finally {
      generateButton.disabled = false;
    }
  });

  saveButton.addEventListener("click", async () => {
    if (!audioUrl) return;
    saveButton.disabled = true;
    status.textContent = "Saving voice...";
    try {
      const audioResponse = await fetch(audioUrl);
      await saveImageProject({
        type: "voice",
        prompt: textInput.value.trim(),
        language: languageInput.value,
        voiceStyle: styleInput.value,
        blob: await audioResponse.blob(),
        createdAt: Date.now(),
      });
      const downloadLink = document.createElement("a");
      downloadLink.href = audioUrl;
      downloadLink.download = `aby-gw-voice-${new Date().toISOString().slice(0, 10)}.mp3`;
      downloadLink.click();
      status.textContent = "Voice saved successfully and added to My Projects.";
    } catch (error) {
      status.textContent = "The voice could not be saved locally.";
    } finally {
      saveButton.disabled = false;
    }
  });

  deleteButton.addEventListener("click", () => {
    if (audioUrl) URL.revokeObjectURL(audioUrl);
    audioUrl = null;
    preview.innerHTML = "<span>Your voice will appear here</span>";
    saveButton.disabled = true;
    deleteButton.disabled = true;
    status.textContent = "Voice cleared.";
  });
}

function bindVideoTool() {
  const form = document.querySelector("#video-form");
  const promptInput = document.querySelector("#video-prompt");
  const ratioInput = document.querySelector("#video-ratio");
  const durationInput = document.querySelector("#video-duration");
  const imageInput = document.querySelector("#video-image");
  const audioInput = document.querySelector("#video-audio");
  const generateButton = document.querySelector("#generate-video");
  const saveButton = document.querySelector("#save-video");
  const deleteButton = document.querySelector("#delete-video");
  const status = document.querySelector("#video-status");
  const preview = document.querySelector("#video-preview");
  let videoUrl = null;

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const prompt = promptInput.value.trim();
    if (!prompt) {
      status.textContent = "Please describe the video first.";
      return;
    }
    const formData = new FormData();
    formData.append("prompt", prompt);
    formData.append("ratio", ratioInput.value);
    formData.append("duration", durationInput.value);
    if (imageInput.files[0]) formData.append("image", imageInput.files[0]);
    if (audioInput.files[0]) formData.append("audio", audioInput.files[0]);
    generateButton.disabled = true;
    saveButton.disabled = true;
    deleteButton.disabled = true;
    status.textContent = "Generating video... Please wait.";
    preview.innerHTML = '<span class="loading-state">Creating your video...</span>';
    try {
      const response = await fetch("/api/videos/generate", { method: "POST", body: formData });
      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || "Video generation failed.");
      }
      const videoBlob = await response.blob();
      if (videoUrl) URL.revokeObjectURL(videoUrl);
      videoUrl = URL.createObjectURL(videoBlob);
      preview.innerHTML = `<video src="${videoUrl}" controls autoplay muted></video>`;
      saveButton.disabled = false;
      deleteButton.disabled = false;
      status.textContent = "Video generated successfully.";
    } catch (error) {
      preview.innerHTML = "<span>Your video will appear here</span>";
      status.textContent = error.message;
    } finally {
      generateButton.disabled = false;
    }
  });

  saveButton.addEventListener("click", async () => {
    if (!videoUrl) return;
    saveButton.disabled = true;
    status.textContent = "Saving video...";
    try {
      const videoResponse = await fetch(videoUrl);
      await saveImageProject({ type: "video", prompt: promptInput.value.trim(), ratio: ratioInput.value, duration: Number(durationInput.value), blob: await videoResponse.blob(), createdAt: Date.now() });
      const downloadLink = document.createElement("a");
      downloadLink.href = videoUrl;
      downloadLink.download = `aby-gw-video-${new Date().toISOString().slice(0, 10)}.mp4`;
      downloadLink.click();
      status.textContent = "Video saved successfully and added to My Projects.";
    } catch (error) {
      status.textContent = "The video could not be saved locally.";
    } finally {
      saveButton.disabled = false;
    }
  });

  deleteButton.addEventListener("click", () => {
    if (videoUrl) URL.revokeObjectURL(videoUrl);
    videoUrl = null;
    preview.innerHTML = "<span>Your video will appear here</span>";
    saveButton.disabled = true;
    deleteButton.disabled = true;
    status.textContent = "Video cleared.";
  });
}

function bindProjectActions() {
  document.querySelectorAll(".project-open").forEach((button) => {
    button.addEventListener("click", () => {
      window.open(button.dataset.mediaUrl, "_blank", "noopener,noreferrer");
    });
  });

  document.querySelectorAll(".project-delete").forEach((button) => {
    button.addEventListener("click", async () => {
      button.disabled = true;
      try {
        await deleteImageProject(Number(button.dataset.projectId));
        await loadProjects();
      } catch (error) {
        button.disabled = false;
      }
    });
  });
}

function bindImageTool() {
  const form = document.querySelector("#image-form");
  const promptInput = document.querySelector("#image-prompt");
  const generateButton = document.querySelector("#generate-image");
  const status = document.querySelector("#image-status");
  const preview = document.querySelector("#image-preview");
  const saveButton = document.querySelector("#save-image");
  const deleteButton = document.querySelector("#delete-image");
  const imageRatio = document.querySelector("#image-ratio");
  let imageUrl = null;

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const prompt = promptInput.value.trim();
    if (!prompt) {
      status.textContent = "Please describe the image first.";
      return;
    }

    generateButton.disabled = true;
    saveButton.disabled = true;
    deleteButton.disabled = true;
    status.textContent = "Generating image... Please wait.";
    preview.innerHTML = '<span class="loading-state">Creating your image...</span>';

    try {
      const response = await fetch("/api/images/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt }),
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || "Image generation failed.");
      }

      const imageBlob = await response.blob();
      if (imageUrl) {
        URL.revokeObjectURL(imageUrl);
      }
      imageUrl = URL.createObjectURL(imageBlob);
      preview.innerHTML = `<img src="${imageUrl}" alt="Generated image">`;
      saveButton.disabled = false;
      deleteButton.disabled = false;
      status.textContent = "Image generated successfully.";
    } catch (error) {
      preview.innerHTML = "<span>Your image will appear here</span>";
      status.textContent = error.message;
    } finally {
      generateButton.disabled = false;
    }
  });

  saveButton.addEventListener("click", async () => {
    if (!imageUrl) {
      return;
    }
    saveButton.disabled = true;
    status.textContent = "Saving image...";
    try {
      const imageResponse = await fetch(imageUrl);
      const imageBlob = await imageResponse.blob();
      await saveImageProject({
        prompt: promptInput.value.trim(),
        ratio: imageRatio.value,
        blob: imageBlob,
        createdAt: Date.now(),
      });

      const downloadLink = document.createElement("a");
      downloadLink.href = imageUrl;
      downloadLink.download = `aby-gw-image-${new Date().toISOString().slice(0, 10)}.png`;
      downloadLink.click();
      status.textContent = "Image saved successfully and added to My Projects.";
    } catch (error) {
      status.textContent = "The image could not be saved locally.";
    } finally {
      saveButton.disabled = false;
    }
  });

  deleteButton.addEventListener("click", () => {
    if (imageUrl) {
      URL.revokeObjectURL(imageUrl);
    }
    imageUrl = null;
    preview.innerHTML = "<span>Your image will appear here</span>";
    saveButton.disabled = true;
    deleteButton.disabled = true;
    status.textContent = "Image cleared.";
  });
}

function setActiveNavigation(viewName) {
  document.querySelectorAll(".nav-item").forEach((item) => {
    const isActive = item.dataset.view === viewName;
    item.classList.toggle("active", isActive);
    if (isActive) {
      item.setAttribute("aria-current", "page");
    } else {
      item.removeAttribute("aria-current");
    }
  });
}

function setNavigationDrawer(isOpen) {
  document.body.classList.toggle("navigation-open", isOpen);
  document.querySelector(".menu-toggle").setAttribute("aria-expanded", String(isOpen));
}

document.addEventListener("DOMContentLoaded", () => {
  applySettings();
  document.querySelectorAll("[data-navigation-close]").forEach((element) => {
    element.addEventListener("click", () => setNavigationDrawer(false));
  });

  document.querySelector(".menu-toggle").addEventListener("click", () => {
    setNavigationDrawer(!document.body.classList.contains("navigation-open"));
  });

  document.querySelectorAll("[data-nav-group]").forEach((group) => {
    const toggle = group.querySelector(".nav-group-toggle");
    toggle.addEventListener("click", () => {
      const isExpanded = group.classList.toggle("is-collapsed") === false;
      toggle.setAttribute("aria-expanded", String(isExpanded));
    });
  });

  document.querySelectorAll(".nav-item").forEach((item) => {
    item.addEventListener("click", () => {
      const viewName = item.dataset.view;
      setActiveNavigation(viewName);
      renderView(viewName);
      setNavigationDrawer(false);
    });
  });

  renderView("home");
});
