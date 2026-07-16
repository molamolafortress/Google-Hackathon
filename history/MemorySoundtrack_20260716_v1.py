import streamlit as st
import os
import base64
import io
from PIL import Image
from google import genai
from google.genai import types

# ----------------------------------------------------
# 1. Page Configuration & Theme Initialization
# ----------------------------------------------------
st.set_page_config(
    page_title="Memory Soundtrack Generator",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium styling with glassmorphism and animations
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap" rel="stylesheet">

<style>
    /* Main body background & font family */
    .stApp {
        background: linear-gradient(135deg, #09090e 0%, #111122 50%, #0c0c16 100%);
        font-family: 'Outfit', sans-serif;
        color: #e2e8f0;
    }
    
    /* Title and gradients */
    .title-gradient {
        background: linear-gradient(45deg, #ff3366, #ff6633, #a855f7, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: -0.05em;
    }
    
    .subtitle {
        text-align: center;
        color: #94a3b8;
        font-size: 1.2rem;
        margin-bottom: 3rem;
        font-weight: 300;
    }
    
    /* Glassmorphism Card styling */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px 0 rgba(0, 0, 0, 0.3);
        transition: transform 0.3s ease, border-color 0.3s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-5px);
        border-color: rgba(255, 255, 255, 0.15);
    }
    
    /* Header/Section Text */
    h1, h2, h3 {
        font-family: 'Outfit', sans-serif;
        font-weight: 600;
        color: #ffffff;
    }
    
    /* Custom Streamlit component adjustments */
    div.stButton > button {
        background: linear-gradient(135deg, #ff3366 0%, #ec4899 50%, #8b5cf6 100%);
        color: white;
        border: none;
        border-radius: 30px;
        padding: 12px 36px;
        font-weight: 600;
        font-size: 1rem;
        letter-spacing: 0.05em;
        box-shadow: 0 4px 15px rgba(236, 72, 153, 0.4);
        transition: all 0.3s ease;
        width: 100%;
        margin-top: 10px;
    }
    
    div.stButton > button:hover {
        transform: scale(1.03);
        box-shadow: 0 6px 20px rgba(236, 72, 153, 0.6);
        background: linear-gradient(135deg, #ff4d7d 0%, #f43f5e 50%, #9c27b0 100%);
        color: white;
    }
    
    .status-text {
        font-weight: 500;
        color: #38bdf8;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 2. Sidebar Configuration (API Authentication)
# ----------------------------------------------------
st.sidebar.title("🛠️ Config & Models")

api_type = st.sidebar.selectbox(
    "API Type",
    ["Gemini Developer API", "Vertex AI"],
    index=0
)

# API Type specific inputs
api_key = None
project_id = None
location = "us-central1"

if api_type == "Gemini Developer API":
    default_key = os.environ.get("GEMINI_API_KEY", "")
    api_key = st.sidebar.text_input(
        "Gemini API Key",
        value=default_key,
        type="password",
        help="Provide your Gemini API Key. Fallback is the GEMINI_API_KEY environment variable."
    )
else:
    default_proj = os.environ.get("ANTIGRAVITY_PROJECT_ID", "")
    project_id = st.sidebar.text_input(
        "GCP Project ID",
        value=default_proj,
        help="Google Cloud Project ID. Fallback is the ANTIGRAVITY_PROJECT_ID environment variable."
    )
    location = st.sidebar.text_input("GCP Location", value=location)

# Model Selections
st.sidebar.markdown("### 🤖 Models")
gemini_model = st.sidebar.text_input("Gemini Model", value="gemini-2.5-flash")
lyria_model = st.sidebar.text_input("Lyria Model", value="lyria-3-clip-preview")
imagen_model = st.sidebar.text_input("Imagen Model", value="imagen-3.0-generate-002")

# Initialize Session States
if 'analyses' not in st.session_state:
    st.session_state['analyses'] = []
if 'soundtrack_prompt' not in st.session_state:
    st.session_state['soundtrack_prompt'] = ""
if 'audio_bytes' not in st.session_state:
    st.session_state['audio_bytes'] = None
if 'lyrics' not in st.session_state:
    st.session_state['lyrics'] = ""
if 'cover_bytes' not in st.session_state:
    st.session_state['cover_bytes'] = None

# Helper to initialize client
def get_client():
    try:
        if api_type == "Gemini Developer API":
            target_key = api_key if api_key else os.environ.get("GEMINI_API_KEY")
            if not target_key:
                st.error("❌ Gemini API Key is missing. Please set it in the sidebar.")
                return None
            return genai.Client(api_key=target_key)
        else:
            target_proj = project_id if project_id else os.environ.get("ANTIGRAVITY_PROJECT_ID")
            if not target_proj:
                st.error("❌ Google Cloud Project ID is missing. Please specify it in the sidebar.")
                return None
            return genai.Client(vertexai=True, project=target_proj, location=location)
    except Exception as e:
        st.error(f"❌ Failed to initialize client: {str(e)}")
        return None

# ----------------------------------------------------
# 3. Main Interface Header
# ----------------------------------------------------
st.markdown("<div class='title-gradient'>Memory Soundtrack Generator</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Upload 5 of your cherished photos to interpret their story and compose a unique soundtrack via Lyria</div>", unsafe_allow_html=True)

# ----------------------------------------------------
# 4. Tab Layout
# ----------------------------------------------------
tab1, tab2, tab3 = st.tabs(["📸 Upload & Analyze", "🎵 Generate Music", "🎨 Album Cover"])

# TAB 1: Upload and Multimodal Analysis
with tab1:
    st.markdown("### 1. Upload up to 5 Memory Photos")
    
    uploaded_files = st.file_uploader(
        "Choose image files",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        key="memory_uploader"
    )
    
    if uploaded_files:
        # Enforce max 5 files
        files_to_process = uploaded_files[:5]
        if len(uploaded_files) > 5:
            st.warning("⚠️ Only the first 5 images will be processed.")
            
        # 🔄 Chronological Reordering UI
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        st.markdown("#### 🔄 Arrange the Chronological Order of Your Memories")
        ordered_names = st.multiselect(
            "Select files in chronological order (First chosen is Photo #1, second is Photo #2, etc.):",
            options=[f.name for f in files_to_process],
            default=[f.name for f in files_to_process],
            help="이름을 선택하는 순서대로 타임라인이 정렬됩니다. 과거부터 현재 순서로 구성해 보세요!"
        )
        
        # Map back to file objects based on the selected order
        file_map = {f.name: f for f in files_to_process}
        ordered_files = [file_map[name] for name in ordered_names if name in file_map]
        
        # If not all files are selected, automatically append the remaining ones
        missing_files = [f for f in files_to_process if f.name not in ordered_names]
        final_files_to_process = ordered_files + missing_files
            
        # Display image previews in a column grid based on sorted order
        cols = st.columns(min(len(final_files_to_process), 5))
        for i, file in enumerate(final_files_to_process):
            with cols[i]:
                img = Image.open(file)
                st.image(img, use_container_width=True, caption=f"Timeline #{i+1}: {file.name}")
        
        # Analyze Button
        st.write("")
        if st.button("🧠 Analyze Memories", key="btn_analyze"):
            client = get_client()
            if client:
                progress_text = "Analyzing your memory photos with Gemini..."
                progress_bar = st.progress(0, text=progress_text)
                
                temp_analyses = []
                
                for idx, file in enumerate(final_files_to_process):
                    progress_bar.progress((idx + 1) / len(final_files_to_process), text=f"Processing Photo #{idx+1}...")
                    
                    # Convert to PIL for the API
                    img = Image.open(file)
                    
                    # Multimodal prompt for Gemini
                    prompt = (
                        "당신은 따뜻한 감성을 가진 전문 스토리텔러이자 음악 평론가입니다. "
                        "이 사진의 세부 요소를 분석하여 담겨 있는 이야기, 지배적인 감정 및 분위기(Vibe), "
                        "그리고 이 사진에 어울릴 만한 음악적 분위기(예: 어쿠스틱 기타의 쓸쓸함, 잔잔한 피아노 선율, 활기찬 팝 비트 등)를 "
                        "상세하게 서술해주세요. 한국어로 작성해 주세요."
                    )
                    
                    try:
                        response = client.models.generate_content(
                            model=gemini_model,
                            contents=[img, prompt]
                        )
                        temp_analyses.append({
                            "index": idx + 1,
                            "filename": file.name,
                            "image": img,
                            "analysis": response.text
                        })
                    except Exception as e:
                        st.error(f"Error analyzing image #{idx+1}: {str(e)}")
                        
                progress_bar.empty()
                st.session_state['analyses'] = temp_analyses
                st.success("✅ Memory analysis complete!")
                
    # Display completed analyses
    if st.session_state['analyses']:
        st.write("")
        st.markdown("### 📂 Extracted Stories & Vibes")
        for item in st.session_state['analyses']:
            with st.container():
                st.markdown(f"""
                <div class='glass-card'>
                    <h4>🖼️ Photo #{item['index']}: {item['filename']}</h4>
                    <p style='white-space: pre-wrap; font-size: 0.95rem; color: #cbd5e1;'>{item['analysis']}</p>
                </div>
                """, unsafe_allow_html=True)

# TAB 2: Soundtrack Generation
with tab2:
    if not st.session_state['analyses']:
        st.info("💡 Please upload and analyze your memory photos in the first tab.")
    else:
        st.markdown("### 2. Generate Your Cohesive Soundtrack")
        
        # Combine all analyses into one context
        combined_context = "\n\n".join([
            f"Photo #{item['index']} story:\n{item['analysis']}"
            for item in st.session_state['analyses']
        ])
        
        # Button to generate music prompt
        if st.button("📝 Synthesize Music Prompt", key="btn_synth_prompt"):
            client = get_client()
            if client:
                with st.spinner("Synthesizing stories into music prompts..."):
                    synth_prompt = (
                        f"Below are the stories and musical directions for a collection of memory photos:\n"
                        f"{combined_context}\n\n"
                        f"Based on these stories, please synthesize a highly detailed prompt for a music generation model (Lyria). "
                        f"The prompt must describe a single cohesive 30-second soundtrack that blends the emotional elements of all these memories. "
                        f"Describe the style, genre, instrumentation, tempo, mood, and vocal features (if any). "
                        f"Write this prompt in clear English, optimized for music AI. "
                        f"Output ONLY the optimized music generation prompt."
                    )
                    try:
                        response = client.models.generate_content(
                            model=gemini_model,
                            contents=synth_prompt
                        )
                        st.session_state['soundtrack_prompt'] = response.text
                        st.success("✅ Music prompt synthesized!")
                    except Exception as e:
                        st.error(f"Error synthesizing music prompt: {str(e)}")
                        
        # Display/Edit Music Prompt
        if st.session_state['soundtrack_prompt']:
            edited_prompt = st.text_area(
                "Customize the Lyria Music Prompt",
                value=st.session_state['soundtrack_prompt'],
                height=150
            )
            st.session_state['soundtrack_prompt'] = edited_prompt
            
            # Generate Audio Button
            st.write("")
            if st.button("🎵 Generate Soundtrack via Lyria", key="btn_generate_music"):
                client = get_client()
                if client:
                    with st.spinner("Composing soundtrack with DeepMind Lyria (please wait)..."):
                        try:
                            # Use interactions API for lyria
                            interaction = client.interactions.create(
                                model=lyria_model,
                                input=st.session_state['soundtrack_prompt']
                            )
                            
                            # Extract audio
                            generated_audio = interaction.output_audio
                            if generated_audio and generated_audio.data:
                                # Decode base64
                                audio_data = base64.b64decode(generated_audio.data)
                                st.session_state['audio_bytes'] = audio_data
                                if interaction.output_text:
                                    st.session_state['lyrics'] = interaction.output_text
                                st.success("✅ Music composition completed!")
                            else:
                                st.error("❌ No audio output received from Lyria model.")
                        except Exception as e:
                            st.error(f"Error during Lyria music generation: {str(e)}")
                            
        # Display Audio Player
        if st.session_state['audio_bytes']:
            st.write("")
            st.markdown("""
            <div class='glass-card'>
                <h3>🎧 Your Memory Soundtrack</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Audio player and download
            st.audio(st.session_state['audio_bytes'], format="audio/mp3")
            st.download_button(
                label="📥 Download Soundtrack (MP3)",
                data=st.session_state['audio_bytes'],
                file_name="memory_soundtrack.mp3",
                mime="audio/mp3"
            )
            
            if st.session_state['lyrics']:
                st.markdown("#### 📝 Accompanying Lyrics")
                st.write(st.session_state['lyrics'])

# TAB 3: Album Cover (Imagen 3)
with tab3:
    if not st.session_state['audio_bytes']:
        st.info("💡 Please generate your soundtrack in the second tab before creating an album cover.")
    else:
        st.markdown("### 3. Generate Album Cover")
        
        # Design a cover prompt
        suggested_cover_prompt = (
            f"A beautiful artistic, poetic album cover representing these memory themes: "
            f"{st.session_state['soundtrack_prompt'][:200]}... "
            f"Vibrant aesthetics, cinematic lighting, digital art, high quality, no text."
        )
        
        cover_prompt_input = st.text_area(
            "Customize Album Cover Prompt",
            value=suggested_cover_prompt,
            height=100
        )
        
        if st.button("🎨 Create Album Cover via Imagen 3", key="btn_generate_cover"):
            client = get_client()
            if client:
                with st.spinner("Generating album cover with Imagen 3..."):
                    try:
                        response = client.models.generate_images(
                            model=imagen_model,
                            prompt=cover_prompt_input,
                            config=types.GenerateImagesConfig(
                                number_of_images=1,
                                output_mime_type="image/png",
                                aspect_ratio="1:1"
                            )
                        )
                        if response.generated_images:
                            generated_image = response.generated_images[0]
                            st.session_state['cover_bytes'] = generated_image.image.image_bytes
                            st.success("✅ Album cover generated!")
                        else:
                            st.error("❌ No image was returned.")
                    except Exception as e:
                        st.error(f"Error during Imagen 3 generation: {str(e)}")
                        
        if st.session_state['cover_bytes']:
            st.write("")
            col_cover, col_details = st.columns([1, 1])
            with col_cover:
                st.image(st.session_state['cover_bytes'], caption="Album Cover", use_container_width=True)
                st.download_button(
                    label="📥 Download Cover (PNG)",
                    data=st.session_state['cover_bytes'],
                    file_name="album_cover.png",
                    mime="image/png"
                )
            with col_details:
                st.markdown("""
                <div class='glass-card' style='height: 100%;'>
                    <h3>💿 Memory Soundtrack Single</h3>
                    <p style='color: #94a3b8; font-style: italic;'>Featuring your memory photographs</p>
                    <hr style='border-color: rgba(255,255,255,0.1);'>
                    <h5>🎧 Audio Playback</h5>
                </div>
                """, unsafe_allow_html=True)
                st.audio(st.session_state['audio_bytes'], format="audio/mp3")
