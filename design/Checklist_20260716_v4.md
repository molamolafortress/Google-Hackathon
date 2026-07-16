# Memory Soundtrack Generator - Standardized Project Checklist (v4)

This checklist tracks the implementation, integration, and verification states for our project designs. Use it to check off completed features and verify system integrity after each design change.

---

## 📋 Section 1: Streamlit Dual-Mode Application (v6) Checklist

### 1.1 Infrastructure & Environment
- [x] Python 3.11+ virtual environment configured.
- [x] Required dependencies installed (`streamlit`, `google-genai`, `pillow`, `python-dotenv`, `pydantic`).
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

### 1.4 Stateful Chronological Ordering & Image Syncing
- [x] Initialize `st.session_state['ordered_file_names']` safely.
- [x] Synchronize newly uploaded images from `st.file_uploader` to state (append new, remove deleted).
- [x] Replace broken `st.multiselect` ordering with tactile, physical Left (◀) and Right (▶) shift buttons.
- [x] Add explicit boundary checks:
  - Disable or hide "◀ Left" for the first image.
  - Disable or hide "Right ▶" for the last image.
- [x] Trigger an explicit `st.rerun()` upon swapping positions to guarantee UI reflects the state change immediately.
- [x] Verify that E2E pipeline (`Analyze Memories`) analyzes photos strictly in the adjusted stateful order.

### 1.5 Unified Synthesis & Combined Asset Generation
- [x] Implement a Pydantic structured output model `class PromptSynthesis(BaseModel)` containing:
  - `music_prompt: str` (highly detailed, complete, structured English prompt for Lyria)
  - `image_prompt: str` (poetic, high-fidelity prompt for Imagen 4 album cover)
- [x] Synthesize both prompts in a single Gemini 3.5 Flash API call utilizing `response_mime_type="application/json"` and `response_schema`.
- [x] Merge Tab 2 and Tab 3 into a single Tab: **"🎵 Create Soundtrack & Art"**.
- [x] Display the synthesized Music Prompt and Album Cover Prompt as editable text areas in a clean side-by-side or stacked grid.
- [x] Introduce a master button: **"🎶 Compose Soundtrack & Render Cover Art"** to trigger both Lyria and Imagen 4 generations sequentially.
- [x] Render the resulting audio player and spinning vinyl side-by-side in a single premium layout upon completion.

---

## 📋 Section 2: Web Application Migration (FastAPI + HTML SPA) Checklist

### 2.1 Backend Server (FastAPI) Setup & Local Access Exposing
- [x] FastAPI and Uvicorn packages installed.
- [x] Initialize FastAPI application instance in `MemorySoundtrack_Web_20260716_v2.py`.
- [x] Configure automatic CORS settings to allow local frontend access if needed.
- [x] Serve `index.html` on the root route (`/`).
- [x] Expose uvicorn host binding to `0.0.0.0` in batch scripts to enable local Wi-Fi LAN access for external devices.
- [x] Integrate socket UDP lookup to print the local network IP and connection URL on server startup.
- [x] Create API Endpoint `POST /api/create-album` to receive image uploads.

### 2.2 Orchestration API Logic & Unified Synthesis
- [x] Parse incoming multipart form data containing uploaded image files in frontend-prescribed chronological order.
- [x] Keep original multimodal Korean detailed story analysis.
- [x] Upgrade prompt synthesis using the Pydantic structured output model to generate **both** the `music_prompt` and `image_prompt` in a single query.
- [x] Execute soundtrack generation via Lyria and cover art generation via Imagen 4 using the *dedicated synthesized* `image_prompt`.
- [x] Return both synthesized prompts, the base64-encoded audio, cover art, and image story descriptions in a unified JSON packet.

### 2.3 Frontend Single-Page App (SPA) UI
- [x] Build a premium landing page `index.html` styled with high-fidelity glassmorphism.
- [x] Add drag-and-drop file uploader (supporting 1-5 files).
- [x] Implement interactive chronological timeline sorting UI using raw JS.
- [x] Update frontend to display the dedicated `cover_prompt` and support unified client slideshow/audio playing.
- [x] Design custom HTML/JS/CSS slideshow player:
  - [x] Ambient background blurring matching the active photo.
  - [x] Spinning vinyl record with the generated album cover art.
  - [x] Pulsing visualizer bars synchronized to playback state.
  - [x] Autoplay timer synchronized to audio play/pause events.
  - [x] Manual arrows and autoplay Toggle.
  - [x] Custom glowing control buttons, volume slider, progress tracking.

### 2.4 Operations & Syncing
- [x] Create `Run_MemorySoundtrack_Web_20260716_v2.bat` batch script to start uvicorn on `0.0.0.0` and open the local browser.
- [x] Perform a full syntax check on the new Python app.
- [x] Push all new Web Application files and checklists to the remote GitHub repository.
- [x] Update the central daily log with implementation and verification results.

---

## 📋 [NEW] Section 3: Self-Healing Structured Prompt Synthesis (v7 Plan)

This section outlines the action plan and verification checklists for implementing robust, fault-tolerant unified prompt synthesis.

### 3.1 Action Plan & Technical Design
- [x] **Raise Token Limit Ceiling**: Increase `max_output_tokens` in Gemini generation configurations to `10000` to prevent truncation during long memory syntheses.
- [x] **Enforce Prompt Formatting Guidelines**: Inject clear instructions into system prompts to strictly forbid unescaped control characters or unescaped double quotes that could breach JSON structure.
- [x] **Implement Auto-Retry with Temperature Decay**: 
  - Wrap Pydantic validation and JSON loading inside a robust `try-except` retry block (up to 3 attempts).
  - Gradually lower `temperature` on each retry attempt (`0.5 -> 0.3 -> 0.1`) to force the model to produce more deterministic and syntactically clean responses.
- [x] **Configure Self-Healing Fallback**:
  - Implement a default high-quality backup prompt set to load automatically if all 3 retry attempts fail.
  - Ensure that the pipeline never halts or crashes due to structured parsing exceptions.

### 3.2 Implementation Execution Checkpoints
- [x] Apply the self-healing retry and fallback logic to the Streamlit sandboxed app: `MemorySoundtrack_20260716_v6.py`.
- [x] Apply the self-healing retry and fallback logic to the FastAPI backend: `MemorySoundtrack_Web_20260716_v2.py`.

### 3.3 Verification & Deployment Checklist
- [x] Run syntax check on modified files using `python -m py_compile`.
- [x] Manually test or simulate a truncated response parse error and verify that the fallback triggers correctly.
- [x] Stage, commit, and push changes to the remote GitHub repository.
- [x] Update the centralized daily log at `C:\Users\USER\Desktop\Deal\Workspace_antigravity\Floria\log\daily_log.md`.
