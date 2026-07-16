# Memory Soundtrack Generator - Standardized Project Checklist (v1)

This checklist tracks the implementation, integration, and verification states for our project designs. Use it to check off completed features and verify system integrity after each design change.

---

## 📋 Section 1: Streamlit Dual-Mode Application (v4) Checklist

### 1.1 Infrastructure & Environment
- [x] Python 3.11+ virtual environment configured.
- [x] Required dependencies installed (`streamlit`, `google-genai`, `pillow`, `python-dotenv`).
- [x] `.env` file successfully loads variables using `load_dotenv()`.
- [x] Streamlit page config sets layout to `wide` and injects premium CSS.

### 1.2 Model Verification
- [x] **Gemini 3.5 Flash** (`gemini-3.5-flash`) used as the default model for image analysis and story synthesis.
- [x] **DeepMind Lyria 3** (`lyria-3-clip-preview`) used via client interactions API.
- [x] **Imagen 4** (`imagen-4.0-generate-001`) used as default for high-fidelity cover art.

### 1.3 Interface & Playback Experience
- [x] Dual-mode selection toggle in the sidebar (`Customer View` vs `Developer View`).
- [x] State preservation: switching between modes does not wipe out generated audio/images.
- [x] Base64 converters encode images, cover art, and audio files into correct Data URLs.
- [x] Custom HTML/JS component displays a rotating vinyl, neon pink pulsing visualizer, and custom control panel.
- [x] Chronological slideshow automatically cross-fades photos every 5 seconds.
- [x] Slideshow autoplay pauses when audio pauses and resumes when audio plays.
- [x] Left/Right manual slide navigation arrows work correctly without breaking audio.

---

## 📋 Section 2: Web Application Migration (FastAPI + HTML SPA) Checklist

This section tracks the upcoming full-stack web application implementation.

### 2.1 Backend Server (FastAPI) Setup
- [ ] Install FastAPI and Uvicorn packages (`pip install fastapi uvicorn`).
- [ ] Initialize FastAPI application instance in `MemorySoundtrack_Web_20260716_v1.py`.
- [ ] Configure automatic CORS settings to allow local frontend access if needed.
- [ ] Mount a static files directory or serve `index.html` on the root route (`/`).
- [ ] Create API Endpoint `POST /api/create-album` to receive image uploads.

### 2.2 Orchestration API Logic
- [ ] Parse incoming multipart form data containing uploaded image files.
- [ ] Preserve chronological sequence mapping provided by the frontend.
- [ ] Run sequential orchestration pipeline in backend:
  - [ ] Multimodal analyses of 1-5 images via Gemini 3.5 Flash.
  - [ ] Story synthesis via Gemini 3.5 Flash.
  - [ ] Soundtrack generation via Lyria 3.
  - [ ] Cover art rendering via Imagen 4.
- [ ] Return JSON response with Base64 encoded audio, cover art, analyses, and lyrics.

### 2.3 Frontend Single-Page App (SPA) UI
- [ ] Build a premium landing page `index.html` styled with high-fidelity glassmorphism.
- [ ] Add drag-and-drop file uploader (supporting 1-5 files).
- [ ] Implement interactive chronological timeline sorting UI using raw JS.
- [ ] Design custom HTML/JS/CSS slideshow player:
  - [ ] Ambient background blurring matching the active photo.
  - [ ] Spinning vinyl record with the generated album cover art.
  - [ ] Pulsing visualizer bars synchronized to playback state.
  - [ ] Autoplay timer synchronized to audio play/pause events.
  - [ ] Manual arrows and autoplay Toggle.
  - [ ] Custom glowing control buttons, volume slider, progress tracking.

### 2.4 Operations & Syncing
- [ ] Create `Run_MemorySoundtrack_Web_20260716_v1.bat` batch script to start server and launch the browser automatically.
- [ ] Perform a full syntax check on the new python app.
- [ ] Push all new Web Application files and checklists to the remote GitHub repository.
- [ ] Update the central daily log with implementation and verification results.
