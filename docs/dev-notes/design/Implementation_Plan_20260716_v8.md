# Implementation Plan - Enhancing Layout, Navigation Flow & Storyline Summarization (v8)

We are upgrading the presentation and narrative flow of our web and streamlit applications to create an extremely premium, engaging, and story-driven experience. Specifically, we will implement:
1. **Storyline Summary**: Generate a warm, evocative 1-line Korean summary of the entire storyline using Gemini 3.5 Flash based on the overall photos/themes, and display it beautifully right underneath the album cover.
2. **Interactive Music Playback on Cover Flip**: Automatically trigger the music soundtrack to play as soon as the user transitions past the cover slide (Slide 0) onto any of the memory photo slides.
3. **Side-by-Side Slide Layout**: Restructure the slideshow so that every memory slide displays the **photo on the left** and its **emotional interpretation/analysis on the right**, allowing a synchronized, shared storytelling journey.

---

## User Review Required

> [!IMPORTANT]
> - **Unified Structured Prompt Schema Upgrade**: We are expanding our Pydantic JSON schema (`PromptSynthesis`) to include `storyline_summary: str`. This guarantees structured generation of the 1-line Korean summary in a single LLM API query.
> - **Transition Triggered Audio**: The music will automatically begin playing when the user advances/flips the cover (either manually via buttons, or automatically via autoplay timer).
> - **Premium Split View**: The bare photo slider is transformed into a sleek split-layout card. The photo is showcased on the left, and its rich, warm AI analysis scrolls on the right, synchronized in real-time as the slider moves.

---

## Proposed Changes

All modifications will be confined strictly to the workspace `c:\Users\USER\Desktop\Google`.

### 📂 1. Design & Checklist Documentation

#### [NEW] [Checklist_20260716_v4.md](file:///c:/Users/USER/Desktop/Google/design/Checklist_20260716_v4.md)
* Standardized Checklist version 4, covering the split layout, auto-playback, and 1-line storyline summary.

#### [NEW] [Implementation_Plan_20260716_v8.md](file:///c:/Users/USER/Desktop/Google/design/Implementation_Plan_20260716_v8.md)
* Workspace copy of this design plan.

---

### 🐍 2. Streamlit Sandbox Application

#### [NEW] [MemorySoundtrack_20260716_v7.py](file:///c:/Users/USER/Desktop/Google/MemorySoundtrack_20260716_v7.py)
* **Pydantic Schema Refactoring**:
  ```python
  class PromptSynthesis(BaseModel):
      music_prompt: str
      image_prompt: str
      storyline_summary: str  # Added for 1-line summary
  ```
* **Gemini Synthesis Instructions**: Add requirements to generate a beautiful, literary Korean 1-line summary of the entire narrative arc (under 100 characters).
* **UI Layout Update**:
  - Show the 1-line story summary card right underneath the generated cover art.
  - Structure the memory slide gallery to display each photo alongside its corresponding interpretation in a clean, professional grid.

#### [NEW] [Run_MemorySoundtrack_20260716_v7.bat](file:///c:/Users/USER/Desktop/Google/Run_MemorySoundtrack_20260716_v7.bat)
* Double-clickable Windows batch file to launch the updated `v7` Streamlit application.

---

### 🌐 3. Full-Stack Web Application (SPA)

#### [NEW] [MemorySoundtrack_Web_20260716_v3.py](file:///c:/Users/USER/Desktop/Google/MemorySoundtrack_Web_20260716_v3.py)
* **Backend Refactoring**:
  - Update `PromptSynthesis` schema to include the `storyline_summary` field.
  - Prompt Gemini to synthesize a literary Korean 1-line storyline summary based on the overall memory analyses.
  - Return `storyline_summary` in the JSON response of `/api/create-album`.

#### [NEW] [Run_MemorySoundtrack_Web_20260716_v3.bat](file:///c:/Users/USER/Desktop/Google/Run_MemorySoundtrack_Web_20260716_v3.bat)
* Double-clickable Windows batch file to launch the updated web app on binding `0.0.0.0`.

#### [MODIFY] [index.html](file:///c:/Users/USER/Desktop/Google/index.html)
* **Premium Slider Styles**:
  - Redefine `.slide-image` to a flex row `.slide-item` container.
  - Add `.slide-media-container` (left column, 50% width) for displaying the image, and `.slide-info-container` (right column, 50% width, blur styling) for the rich, scrollable interpretation/analysis text.
  - Style `.cover-story-summary` as a glowing, floating, glassmorphic caption card positioned directly below the cover image on Slide 0.
  - Add standard media queries to stack elements vertically on smaller/mobile viewports for responsive perfection.
* **Slider Rendering Logic**:
  - Re-engineer slide generation in `initializePremiumPlayer()` to dynamically compile the split `.slide-item` markup, mapping each photo slide with its corresponding analyzed storytelling text.
* **Auto-Playback Trigger**:
  - Inside `updateSlideshowView()`, detect if `activeSlideIndex > 0` (meaning user has turned/flipped the cover). If the music audio is currently paused, trigger `audio.play()` automatically and synchronize the visual playback state (spin vinyl, start visualizer, update play button).

---

## Verification Plan

### Automated Verification
* Compile checking Python files for syntax errors:
  ```powershell
  python -m py_compile MemorySoundtrack_20260716_v7.py MemorySoundtrack_Web_20260716_v3.py
  ```

### Manual Verification
1. **Storyline Summary Validation**:
   - Run `/api/create-album` via the Web UI.
   - Verify that the first slide (Slide 0) displays the generated Imagen 4 album cover, with the beautiful 1-line Korean storyline summary floating directly underneath it.
2. **Side-by-Side Presentation**:
   - Advance the slideshow to the subsequent slides.
   - Verify that the memory photo is beautifully displayed on the left, and its detailed Korean interpretation is cleanly laid out on the right.
3. **Cover Flip Audio Trigger**:
   - Click the "▶" Next Slide arrow while viewing the cover slide (Slide 0) with audio paused.
   - Verify that as the slideshow transitions to Slide 1, the music begins playing automatically, and the vinyl record begins rotating with visualizers active.
