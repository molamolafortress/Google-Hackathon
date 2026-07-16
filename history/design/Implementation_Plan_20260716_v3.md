# Memory Soundtrack Generator Implementation Plan

We are building a demo project where users can upload up to 5 memory photos, have them analyzed by Gemini, and generate a representative soundtrack using Lyria 3 (and optionally an album cover using Imagen 3) in a unified Streamlit application.

## Design Concept

1. **Multimodal Analysis**:
   - The user uploads 1 to 5 images.
   - For each image, Gemini (`gemini-3.5-flash`) generates a descriptive narrative and extracts the emotional tone/vibe (e.g., "nostalgic, warm, bittersweet").

2. **Soundtrack Synthesis**:
   - The app aggregates the narratives and emotional tones from all uploaded images.
   - It prompts Gemini to synthesize a cohesive musical prompt (e.g., genre, tempo, instruments, vocals, lyrics).
   - The generated prompt is sent to `lyria-3-clip-preview` using the Google GenAI `interactions` API to generate a 30-second soundtrack.

3. **Album Cover Generation (Optional/Phase 2)**:
   - Once the soundtrack is ready, the app uses Imagen 3 (`imagen-3.0-generate-002`) to create a beautiful album cover based on the synthesized story and display it.

4. **UI Design (Streamlit)**:
   - Modern, sleek dark mode theme with glassmorphism styles and subtle transitions.
   - Step-by-step layout: Image Upload -> Analysis & Vibe Extraction -> Soundtrack Generation -> Playback & Album Cover.

---

## User Review Required

> [!IMPORTANT]
> **API Key / Authentication Configuration**:
> - We noticed the environment has `ANTIGRAVITY_PROJECT_ID` configured but no `GEMINI_API_KEY`.
> - If utilizing Vertex AI, the client should be initialized with `client = genai.Client(vertexai=True, project=...)`.
> - If utilizing the Gemini Developer API, the user needs to provide a `GEMINI_API_KEY` (either in the environment, `.env` file, or entered directly in the Streamlit sidebar). We will support both options (environment/sidebar) for maximum flexibility.

---

## Proposed Changes

We will work strictly inside the workspace folder `c:\Users\USER\Desktop\Google`.

### Streamlit Application

#### [NEW] [MemorySoundtrack_20260716_v3.py](file:///c:/Users/USER/Desktop/Google/MemorySoundtrack_20260716_v3.py)
A clean, self-contained Streamlit application that implements:
- Sidebar configuration for API Key / Vertex AI settings.
- Multimodal image uploader (supports up to 5 files).
- Interactive step-by-step UI with state management.
- Multi-image analysis using `google-genai` SDK and `gemini-3.5-flash`.
- Music generation using `client.interactions.create` with `lyria-3-clip-preview`.
- Album cover generation using Imagen 3.
- Premium styling with custom HTML/CSS injects.
- Automatic API key loading from `.env` with a fallback UI sidebar editable textbox.

---

## Verification Plan

### Automated/Manual Verification
- Run the Streamlit app locally:
  ```powershell
  streamlit run MemorySoundtrack_20260716_v3.py
  ```
- Test with 5 mock/sample images.
- Verify image analysis output.
- Verify audio generation, playback, and download.
- Verify album cover generation and display.
