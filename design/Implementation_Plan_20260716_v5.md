# Web Application Migration & Standardized Checklist Design (v5)

We are updating our design to transition the **Customer Mode** from a Streamlit-based sandbox into a production-grade, highly aesthetic **Web Application**. Additionally, we are introducing a **Standardized Checklist System** that will act as a permanent trace to verify and sign off on all design changes.

---

## 1. Technical Web Architecture (Customer Mode)

To deliver a premium, fast, and production-grade web experience, we propose a split architecture:

```mermaid
graph LR
    subgraph Browser Frontend (SPA)
        A["HTML5 / CSS3 / ES6 Javascript"]
    end
    subgraph Python Backend (REST API)
        B["FastAPI / Uvicorn Server"]
        C["google-genai Client"]
    end
    subgraph Google GenAI Cloud
        D["Gemini 3.5 Flash"]
        E["DeepMind Lyria 3"]
        F["Imagen 4"]
    end
    A -- "POST /api/create-album" --> B
    B -- "Analyze & Synthesize" --> C
    C -- "Orchestrate" --> D
    C -- "Compose Soundtrack" --> E
    C -- "Render Art" --> F
    B -- "JSON Response (Base64 Assets)" --> A
```

### A. Frontend (Single Page Application - SPA)
* **Tech Stack**: Vanilla HTML5, modern CSS3 (sleek dark mode, custom glowing visualizer, rotating vinyl disk, glassmorphic layout), and modern ES6 Javascript.
* **Benefits**: Ultra-smooth rendering, pure client-side audio execution, absolute layout stability, and a fully polished consumer landing page.
* **State Management**: Zero-server lag when navigating photos. The frontend will communicate asynchronously via `fetch` to trigger the backend creation pipeline.

### B. Backend (Python REST API - FastAPI)
* **Tech Stack**: `FastAPI` + `Uvicorn` server.
* **Why FastAPI?** 
  - Perfect compatibility with our preconfigured Python virtual environments, Google Cloud settings, and `google-genai` SDK.
  - Automatically generates interactive OpenAPI documentation (`/docs`).
  - High performance, lightweight, and modern.
* **API Endpoint**:
  - `POST /api/create-album`: Receives multi-part file uploads (1-5 images), runs the 4-step orchestration pipeline sequentially, and returns a JSON package containing Base64-encoded audio, album cover, and image story descriptions.

---

## 2. Standardized Checklist System

Whenever our design gets updated, we will create/update a dedicated **Checklist** following the `Name_YYYYMMDD_vX` version order.
We will create a central file: **`design/Checklist_20260716_v1.md`** containing:
* **Infrastructure & Setup Checks** (Python environment, Streamlit, FastAPI, Uvicorn, API keys).
* **AI Orchestration Checks** (Gemini 3.5 Flash chronological logic, Lyria 3 Soundtrack, Imagen 4 Cover Art).
* **Customer UI Checks** (HTML/JS player, CSS transitions, cross-fade slide timing, manual arrows, autoplay state).
* **System Operations Checks** (Windows batch runners, remote GitHub syncing, log files updates).

This checklist will be manually or automatically checked off during verification of each step!

---

## Proposed Changes

We will work strictly inside the workspace folder `c:\Users\USER\Desktop\Google`.

### New & Modified Files

#### [NEW] [MemorySoundtrack_Web_20260716_v1.py](file:///c:/Users/USER/Desktop/Google/MemorySoundtrack_Web_20260716_v1.py)
* The FastAPI backend application.
* Serves the frontend static files (HTML/CSS/JS) and exposes `/api/create-album`.

#### [NEW] [index.html](file:///c:/Users/USER/Desktop/Google/index.html)
* The gorgeous frontend landing page for customers, containing the image uploader, sorting timeline, and the premium interactive player.

#### [NEW] [Run_MemorySoundtrack_Web_20260716_v1.bat](file:///c:/Users/USER/Desktop/Google/Run_MemorySoundtrack_Web_20260716_v1.bat)
* Double-clickable Windows batch file to start the FastAPI server and open the web browser to `http://localhost:8000`.

#### [NEW] [design/Checklist_20260716_v1.md](file:///c:/Users/USER/Desktop/Google/design/Checklist_20260716_v1.md)
* Standardized, comprehensive checklist file to track the implementation state.

#### [NEW] [design/Implementation_Plan_20260716_v5.md](file:///c:/Users/USER/Desktop/Google/design/Implementation_Plan_20260716_v5.md)
* This implementation plan saved in our workspace design folder.

---

## Verification Plan

### Automated & Manual Verification
1. **Packages Check**:
   - Install `fastapi` and `uvicorn` using `pip install fastapi uvicorn`.
2. **Server Check**:
   - Start the FastAPI server locally:
     ```powershell
     uvicorn MemorySoundtrack_Web_20260716_v1:app --reload
     ```
   - Verify server is listening on `http://127.0.0.1:8000`.
3. **End-to-End Test**:
   - Load `http://127.0.0.1:8000` in the browser.
   - Upload images, click "Create Memory Album", and verify that the HTML player is loaded with correct audio, spinning vinyl, and cross-fading slideshow.
