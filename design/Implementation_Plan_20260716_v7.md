# Implementation Plan - Unifying Music & Image Prompt Synthesis (v7)

We are restructuring the application's core workflow to unify the synthesis of music and album cover prompts, and combine their generation into a single cohesive action. This eliminates the need for separate tabs and manual stages, creating a vastly superior, integrated user experience.

---

## User Review Required

> [!IMPORTANT]
> - **Unified Generation Tab**: Tab 3 ("Album Cover") is removed. Tab 2 is renamed to **"🎵 Create Soundtrack & Art"**. Inside this tab, synthesizing prompts will now output **both** a dedicated Music Prompt (Lyria) and a dedicated Cover Art Prompt (Imagen 4) in a single LLM query.
> - **Unified Execution**: Generating assets is now combined. Clicking the generation button will run both Lyria soundtrack generation and Imagen 4 rendering sequentially in a single step, displaying the spinning vinyl with the custom cover and the audio player together.
> - **Structured Prompt Output**: We are using the GenAI SDK's structured output capability (`response_mime_type="application/json"` with a Pydantic schema) to guarantee that both prompts are synthesized reliably without truncation.

---

## Proposed Changes

We will work strictly inside the workspace folder `c:\Users\USER\Desktop\Google`.

### 📂 1. Design & Checklist Components

#### [NEW] [Checklist_20260716_v3.md](file:///c:/Users/USER/Desktop/Google/design/Checklist_20260716_v3.md)
* Standardized Checklist version 3 including updated steps for Unified Prompt Synthesis and Unified Asset Generation.

#### [NEW] [Implementation_Plan_20260716_v7.md](file:///c:/Users/USER/Desktop/Google/design/Implementation_Plan_20260716_v7.md)
* Workspaced copy of this design plan for repository persistence.

---

### 🐍 2. Streamlit Sandboxed Application

#### [NEW] [MemorySoundtrack_20260716_v6.py](file:///c:/Users/USER/Desktop/Google/MemorySoundtrack_20260716_v6.py)
* **Image Interpretation**: Keep the original detailed multimodal Korean story analysis. Add explicit instructions to prevent generic greeting truncation.
* **Unified Prompt Synthesis**:
  * Define a Pydantic model:
    ```python
    from pydantic import BaseModel
    class PromptSynthesis(BaseModel):
        music_prompt: str
        image_prompt: str
    ```
  * Update `btn_synth_prompt` logic to call Gemini 3.5 Flash using `response_mime_type="application/json"` and `response_schema=PromptSynthesis`.
  * Store both `soundtrack_prompt` and `cover_prompt` in `st.session_state`.
* **Unified UI**:
  * Merge Tab 2 and Tab 3 into a single Tab: **"🎵 Create Soundtrack & Art"**.
  * Display two editable text areas side-by-side (or sequentially) for the synthesized **Music Prompt** and **Album Cover Prompt**.
  * Implement a single master button: **"🎶 Compose Soundtrack & Render Cover Art"**.
  * When clicked, run Lyria (audio) and Imagen 4 (cover) sequentially under separate progress spinner descriptions.
  * Render the resulting music player and spinning album cover side-by-side in the same card once complete.

#### [NEW] [Run_MemorySoundtrack_20260716_v6.bat](file:///c:/Users/USER/Desktop/Google/Run_MemorySoundtrack_20260716_v6.bat)
* Double-clickable Windows batch file to launch the updated `v6` Streamlit application.

---

### 🌐 3. Full-Stack Web Application

#### [NEW] [MemorySoundtrack_Web_20260716_v2.py](file:///c:/Users/USER/Desktop/Google/MemorySoundtrack_Web_20260716_v2.py)
* **Backend Refactoring**:
  * Apply the Pydantic structured output model to the `/api/create-album` endpoint during prompt synthesis.
  * Generate the Imagen 4 cover art using the *dedicated, synthesized* `image_prompt` instead of slicing the `soundtrack_prompt[:200]`.
  * Return `cover_prompt` in the final JSON response along with other assets.

#### [NEW] [Run_MemorySoundtrack_Web_20260716_v2.bat](file:///c:/Users/USER/Desktop/Google/Run_MemorySoundtrack_Web_20260716_v2.bat)
* Double-clickable Windows batch file to launch the updated web application.

---

## Verification Plan

### Automated Verification
* Run Python compilation checks on both updated files:
  ```powershell
  python -m py_compile MemorySoundtrack_20260716_v6.py MemorySoundtrack_Web_20260716_v2.py
  ```

### Manual Verification
1. **Unified Prompts**:
   - Upload images and trigger "Analyze Memories".
   - Go to Tab 2 and click "Synthesize Soundtrack & Cover Prompts".
   - Verify that **both** a highly detailed Music Prompt and a dedicated, poetic Album Cover Prompt are successfully generated in the text areas without truncation.
2. **Unified Generation**:
   - Click "Compose Soundtrack & Render Cover Art".
   - Verify that the process runs end-to-end, and displays the audio player alongside the spinning album cover art in the same tab.
