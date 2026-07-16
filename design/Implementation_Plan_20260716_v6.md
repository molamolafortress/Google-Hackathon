# Memory Soundtrack Generator - Design & Checklist Review (v6)

We have reviewed the core architecture, the standardized checklist, and the actual implementation of both the **Streamlit Sandbox (v4)** and the **Web Application (FastAPI + HTML SPA)**. 

During our deep-dive analysis, we identified a critical state-management flaw in how Streamlit handles image upload ordering, causing the chronological sorting to fail or reset during user interaction.

---

## 1. Root Cause Analysis (RCA) - Image Sorting Failure

In `MemorySoundtrack_20260716_v4.py`, the image uploading and sorting is handled as follows:

```python
st.file_uploader("Choose image files", ..., key="memory_uploader")
...
ordered_names = st.multiselect(
    "Select files in chronological order...",
    options=[f.name for f in files_to_process],
    default=[f.name for f in files_to_process]
)
```

### Why it Fails:
1. **The Rerun & Reset Loop**: Streamlit executes the entire script from top to bottom on every user interaction. When the user uploads images, `files_to_process` contains the images in their default uploaded order.
2. **`default` Override**: Because the `default` parameter of `st.multiselect` is bound statically to `[f.name for f in files_to_process]`, any attempt by the user to unselect or change the selection instantly triggers a rerun. Upon rerun, the `default` list is re-evaluated back to the original upload order, overwriting the user's custom ordering.
3. **Poor UX**: `st.multiselect` does not support drag-and-drop or logical reordering. Users must delete items and re-add them in a precise order, which is highly error-prone and frustrating.

---

## 2. Proposed Architectural Solution

We will completely refactor the chronological sorting system to use **`st.session_state` synchronization** and introduce a premium, visual **"◀ Left / Right ▶" Move Button Interface**.

### A. State Synchronization Strategy
We will store the current chronological name order in `st.session_state['ordered_file_names']`.
- **On Upload**: If new files are uploaded, append them to the end of the session state list.
- **On Deletion**: If files are removed from the uploader, remove them from the session state list.
- **On Shift**: Clicking the "◀ Left" or "Right ▶" buttons under any photo card swaps its position with its neighbor inside `st.session_state['ordered_file_names']` and calls `st.rerun()`.

This ensures **absolute state persistence** and a highly aesthetic, interactive tactile sorting experience.

### B. Standardizing the Checklist
We are updating the Checklist to **v2** to formally include verification steps for:
- State-persisted chronological order syncing.
- Left/Right manual button movement and automatic slider alignment.

---

## Proposed Changes

We will work strictly inside the workspace folder `c:\Users\USER\Desktop\Google`.

### New & Modified Files

#### [NEW] [MemorySoundtrack_20260716_v5.py](file:///c:/Users/USER/Desktop/Google/MemorySoundtrack_20260716_v5.py)
* Refactored Streamlit application.
* Removes the broken `st.multiselect` sorting and replaces it with a beautiful, fully functional **Left/Right shifting layout** powered by `st.session_state`.

#### [NEW] [Run_MemorySoundtrack_20260716_v5.bat](file:///c:/Users/USER/Desktop/Google/Run_MemorySoundtrack_20260716_v5.bat)
* Updated Windows double-clickable batch runner targeting the new `v5` script.

#### [NEW] [design/Checklist_20260716_v2.md](file:///c:/Users/USER/Desktop/Google/design/Checklist_20260716_v2.md)
* Standardized Checklist version 2 with granular checkmarks for the new stateful order adjustment system.

---

## Verification Plan

### Manual Verification
1. **Upload Phase**:
   - Upload 3 different images (e.g., `A.png`, `B.png`, `C.png`).
   - Verify they are displayed in the initial order `[A, B, C]`.
2. **Order Shifting Phase**:
   - Click "Right ▶" on `A.png`. Verify the order immediately changes to `[B, A, C]` visually.
   - Click "◀ Left" on `C.png`. Verify the order becomes `[B, C, A]`.
   - Verify that adding a new image `D.png` appends it correctly to the end `[B, C, A, D]` without breaking the existing sorted order.
3. **E2E Orchestration Phase**:
   - Trigger "Analyze Memories" and verify that Gemini 3.5 Flash analyzes the photos in the newly sorted chronological order.
