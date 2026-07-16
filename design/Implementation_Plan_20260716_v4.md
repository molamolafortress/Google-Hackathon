# Memory Soundtrack Generator - Dual-Mode Design (v4)

We are updating the design of the **Memory Soundtrack Generator** to support two distinct modes of operation:
1. **Developer View (Dev Side)**: The current interactive, step-by-step tabbed interface allowing full control, custom prompt edits, and detailed analysis inspection.
2. **Customer View (Customer Side)**: A simplified, highly aesthetic, automated experience where the customer uploads photos, clicks a single button, and receives an auto-playing musical memory album slideshow.

---

## Technical Design & Concept

### 1. Dual-Mode Interface Toggle
We will introduce an elegant sidebar selector to toggle between the two modes:
- **Default Mode**: `Customer View (Premium Playback)`
- **Advanced Mode**: `Developer View (Detailed Progress)`

This structure ensures that judges or customers see the simplified, high-impact demonstration first, while developers can easily switch to inspect the underlying multimodal pipeline.

### 2. Customer View: Automated Pipeline
In Customer View, the complex multi-step process will be orchestrated behind a single button click: `✨ Create Memory Album ✨`.
When clicked, the application will automatically execute the following steps sequentially inside a single unified progress indicator:
1. **Multimodal Analysis**: Call `gemini-3.5-flash` to extract narratives and vibes for all uploaded images.
2. **Music Prompt Synthesis**: Call `gemini-3.5-flash` to merge narratives into a cohesive English prompt.
3. **Soundtrack Composition**: Call `lyria-3-clip-preview` via the `interactions` API to generate the 30-second soundtrack.
4. **Album Cover Generation**: Call `imagen-3.0-generate-002` to render a high-quality square album cover.

All generated assets (audio bytes, cover bytes, image analyses) are saved in the Streamlit `st.session_state`, ensuring they can be shared and viewed across both views.

### 3. Customer View: Premium Interactive Slideshow Player
To deliver a premium, seamless presentation, we will implement a custom client-side **HTML/JS Slideshow Player** embedded in Streamlit.
- **Why HTML/JS?** Running the slideshow client-side avoids the latency and audio interruption associated with Streamlit server-side re-runs. It enables smooth GPU-accelerated CSS cross-fade transitions and absolute playback stability.
- **Assets Integration**: The uploaded memory images and the generated album cover will be converted to Base64 strings along with the generated soundtrack audio, and passed directly into the HTML component.
- **Player Interface Features**:
  - **Cover Art Start**: Displays the generated Imagen 3 Album Cover as the song starts.
  - **Auto-Scrolling Slideshow**: As the song plays, the slideshow automatically transitions through the uploaded memory photos in chronological order (every 5-6 seconds).
  - **Manual Navigation**: Users can click Left/Right arrows to navigate through the photos at their own pace.
  - **Visualizer & Spinning Vinyl**: Elegant CSS animations including a spinning record and a pulsing visualizer bar to make the interface feel alive.
  - **Glassmorphic Control Dashboard**: Smooth play/pause controls, progress bar, track name, and lyrics display.

---

## User Review Required

> [!IMPORTANT]
> **Key Design Choices**:
> - We will set the **Customer View** as the default landing mode so that anyone loading the page gets the "Wow" factor immediately.
> - The slideshow will automatically loop through the uploaded photos while the soundtrack is playing.
> - We will include a toggle inside the slideshow to enable/disable autoplay so customers can manually explore the photos if they prefer.

---

## Proposed Changes

We will work strictly inside the workspace folder `c:\Users\USER\Desktop\Google`.

### Streamlit Application & Scripts

#### [MODIFY] [MemorySoundtrack_20260716_v4.py](file:///c:/Users/USER/Desktop/Google/MemorySoundtrack_20260716_v4.py)
We will create a new version of our main script:
- Add a view mode toggle in the sidebar.
- Implement the automated pipeline for the **Customer View**.
- Add helper functions to convert uploaded images and the generated cover/audio to Base64 data URLs.
- Build a premium custom HTML/JS/CSS string for the slideshow player and render it using `st.components.v1.html`.
- Preserve the detailed tabbed interface under the **Developer View** so both workflows coexist perfectly.

#### [NEW] [Run_MemorySoundtrack_20260716_v4.bat](file:///c:/Users/USER/Desktop/Google/Run_MemorySoundtrack_20260716_v4.bat)
- Create an executable batch file to run the new v4 version directly.

#### [NEW] [design/Implementation_Plan_20260716_v4.md](file:///c:/Users/USER/Desktop/Google/design/Implementation_Plan_20260716_v4.md)
- Save this implementation plan inside the workspace `design` directory for version tracking.

---

## Verification Plan

### Automated & Manual Verification
1. **Compilation Test**:
   - Run `python -m py_compile MemorySoundtrack_20260716_v4.py` to ensure zero syntax or package errors.
2. **Dual-Mode Verification**:
   - Run the application via Streamlit:
     ```powershell
     streamlit run MemorySoundtrack_20260716_v4.py
     ```
   - Verify that switching modes in the sidebar updates the UI instantly without losing state.
3. **Automated Pipeline Test (Customer View)**:
   - Upload 3 sample images, click "Create Memory Album", and verify that all steps execute automatically and sequentially.
4. **Interactive Slideshow Player Test**:
   - Verify the audio plays smoothly, the album cover displays, and the uploaded memory photos cycle automatically with smooth cross-fades.
   - Verify manual navigation works and does not interrupt audio playback.
