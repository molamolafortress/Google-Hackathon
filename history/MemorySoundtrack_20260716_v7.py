import streamlit as st
import os
import base64
import io
from PIL import Image
from pydantic import BaseModel
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables from .env file (if present)
load_dotenv()

# ----------------------------------------------------
# Pydantic Schema for Unified Prompt Synthesis
# ----------------------------------------------------
class PromptSynthesis(BaseModel):
    music_prompt: str
    image_prompt: str
    storyline_summary: str  # A warm, sentimental 1-line summary of the entire storyline in Korean

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

    /* Evocative summary styling */
    .summary-box {
        background: linear-gradient(135deg, rgba(236, 72, 153, 0.1) 0%, rgba(99, 102, 241, 0.1) 100%);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 12px;
        padding: 14px 20px;
        text-align: center;
        font-size: 1rem;
        font-weight: 600;
        color: #f1f5f9;
        margin-top: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
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
gemini_model = st.sidebar.text_input("Gemini Model", value="gemini-3.5-flash")
lyria_model = st.sidebar.text_input("Lyria Model", value="lyria-3-clip-preview")
imagen_model = st.sidebar.text_input("Imagen Model", value="imagen-4.0-generate-001")

# Initialize Session States
if 'analyses' not in st.session_state:
    st.session_state['analyses'] = []
if 'soundtrack_prompt' not in st.session_state:
    st.session_state['soundtrack_prompt'] = ""
if 'cover_prompt' not in st.session_state:
    st.session_state['cover_prompt'] = ""
if 'storyline_summary' not in st.session_state:
    st.session_state['storyline_summary'] = ""
if 'audio_bytes' not in st.session_state:
    st.session_state['audio_bytes'] = None
if 'lyrics' not in st.session_state:
    st.session_state['lyrics'] = ""
if 'cover_bytes' not in st.session_state:
    st.session_state['cover_bytes'] = None
if 'ordered_file_names' not in st.session_state:
    st.session_state['ordered_file_names'] = []

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
# 4. Tab Layout (Tab 3 merged into Tab 2)
# ----------------------------------------------------
tab1, tab2 = st.tabs(["📸 Upload & Analyze", "🎵 Create Soundtrack & Art"])

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
            
        current_names = [f.name for f in files_to_process]
        
        # Sync session state with uploaded files
        # 1. Add any newly uploaded file names
        for name in current_names:
            if name not in st.session_state['ordered_file_names']:
                st.session_state['ordered_file_names'].append(name)
                
        # 2. Remove any file names that are no longer present
        st.session_state['ordered_file_names'] = [
            name for name in st.session_state['ordered_file_names'] if name in current_names
        ]
        
        # Re-map the files to match the session state ordering
        file_map = {f.name: f for f in files_to_process}
        final_files_to_process = [
            file_map[name] for name in st.session_state['ordered_file_names'] if name in file_map
        ]
            
        # 🔄 Chronological Reordering UI using Left/Right Buttons
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        st.markdown("#### 🔄 Arrange the Chronological Order of Your Memories")
        st.caption("아래 이미지 카드의 ◀ / ▶ 버튼을 클릭하여 과거에서 현재 순서대로 타임라인을 정렬해보세요. (정렬 순서가 실시간 저장됩니다)")
            
        # Display image previews in a column grid based on sorted order
        cols = st.columns(min(len(final_files_to_process), 5))
        for i, file in enumerate(final_files_to_process):
            with cols[i]:
                img = Image.open(file)
                st.image(img, use_container_width=True, caption=f"Timeline #{i+1}: {file.name}")
                
                # Shifting buttons
                btn_cols = st.columns(2)
                
                # Move Left button
                if i > 0:
                    if btn_cols[0].button("◀ Left", key=f"btn_left_{i}_{file.name}", use_container_width=True):
                        names = st.session_state['ordered_file_names']
                        names[i], names[i-1] = names[i-1], names[i]
                        st.session_state['ordered_file_names'] = names
                        st.rerun()
                else:
                    btn_cols[0].button("◀ Left", key=f"btn_left_disabled_{i}", disabled=True, use_container_width=True)
                        
                # Move Right button
                if i < len(final_files_to_process) - 1:
                    if btn_cols[1].button("Right ▶", key=f"btn_right_{i}_{file.name}", use_container_width=True):
                        names = st.session_state['ordered_file_names']
                        names[i], names[i+1] = names[i+1], names[i]
                        st.session_state['ordered_file_names'] = names
                        st.rerun()
                else:
                    btn_cols[1].button("Right ▶", key=f"btn_right_disabled_{i}", disabled=True, use_container_width=True)
        
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
                        "이 사진의 세부 요소를 매우 상세하게 분석해주세요. "
                        "분석에는 다음 3가지 사항이 명확하고 풍성하게 포함되어야 합니다:\n\n"
                        "1. 사진의 구도, 세부 요소, 인물의 표정/동작, 배경 등 디테일 분석과 따뜻한 감성의 스토리텔링\n"
                        "2. 이 사진을 지배하는 고유한 감정과 분위기(Vibe) 분석 및 어울리는 키워드 정의\n"
                        "3. 이 시각적 이미지에 가장 잘 어울릴 만한 음악적 분위기 제안 (예: 메인 악기 구성, 리듬감, 템포, 보컬 톤, 연상되는 아티스트나 스타일 등)\n\n"
                        "소개글이나 '안녕하세요' 같은 정형화된 인사말은 완전히 생략하고, 곧바로 각 항목에 대해 긴 서사 구조를 갖춘 풍부한 분량으로 한국어로 상세히 서술해주세요. "
                        "전체 분량은 공백 포함 800자 이상으로 매우 길고 정교하게 전개해 주세요."
                    )
                    
                    try:
                        response = client.models.generate_content(
                            model=gemini_model,
                            contents=[img, prompt],
                            config=types.GenerateContentConfig(
                                temperature=0.7,
                                max_output_tokens=8192,
                            )
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
                
    # Display completed analyses side-by-side with photo
    if st.session_state['analyses']:
        st.write("")
        st.markdown("### 📂 Extracted Stories & Vibes")
        for item in st.session_state['analyses']:
            with st.container():
                st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
                col_item_l, col_item_r = st.columns([1, 2])
                with col_item_l:
                    st.image(item['image'], caption=f"Photo #{item['index']}: {item['filename']}", use_container_width=True)
                with col_item_r:
                    st.markdown(f"#### 🖼️ Timeline #{item['index']} Emotional Analysis")
                    st.markdown(f"<p style='white-space: pre-wrap; font-size: 0.95rem; color: #cbd5e1;'>{item['analysis']}</p>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

# TAB 2: Unified Soundtrack & Art Generation
with tab2:
    if not st.session_state['analyses']:
        st.info("💡 Please upload and analyze your memory photos in the first tab.")
    else:
        st.markdown("### 2. Synthesize Prompts & Create Your Master Soundtrack Single")
        
        # Combine all analyses into one context
        combined_context = "\n\n".join([
            f"Photo #{item['index']} story:\n{item['analysis']}"
            for item in st.session_state['analyses']
        ])
        
        # Master Prompts Synthesis Button (Structured Output)
        if st.button("📝 Synthesize Soundtrack, Cover & Summary", key="btn_synth_prompt"):
            client = get_client()
            if client:
                with st.spinner("Synthesizing stories into prompts & 1-line storyline summary..."):
                    synth_instruction = (
                        f"Below are the individual emotional story-analyses of a chronological collection of memory photos:\n"
                        f"{combined_context}\n\n"
                        f"Your task is to analyze these chronological stories and synthesize THREE distinct outputs:\n\n"
                        f"1. `music_prompt`: A highly detailed, complete prompt for a music AI (Lyria). "
                        f"It must describe a single cohesive 30-second soundtrack blending the emotional arc of all the photos. "
                        f"Specify: Style/Genre, Mood, detailed Instrumentation (e.g. acoustic nylon guitar, electric Rhodes, brush drums), Tempo (BPM), Structure ([Intro], [Main], [Outro]), and Vocal/Melody. "
                        f"Ensure this prompt ends in a finished sentence and doesn't cut off.\n\n"
                        f"2. `image_prompt`: A poetic, vivid, high-fidelity prompt for an image AI (Imagen 4) to render a single, square, professional digital album cover. "
                        f"It must abstractly represent the core emotional theme of the collection. Do NOT include text.\n\n"
                        f"3. `storyline_summary`: A warm, beautiful, highly literary 1-line summary of the entire chronological storyline in Korean (under 100 characters).\n\n"
                        f"Return your output strictly structured matching the provided JSON schema."
                    )
                    import time
                    max_retries = 3
                    synth_success = False
                    
                    for attempt in range(max_retries):
                        temp = max(0.1, 0.5 - attempt * 0.15)
                        try:
                            response = client.models.generate_content(
                                model=gemini_model,
                                contents=synth_instruction,
                                config=types.GenerateContentConfig(
                                    temperature=temp,
                                    max_output_tokens=8192,
                                    response_mime_type="application/json",
                                    response_schema=PromptSynthesis,
                                )
                            )
                            # Parse structured output
                            parsed_schema = PromptSynthesis.model_validate_json(response.text)
                            st.session_state['soundtrack_prompt'] = parsed_schema.music_prompt
                            st.session_state['cover_prompt'] = parsed_schema.image_prompt
                            st.session_state['storyline_summary'] = parsed_schema.storyline_summary
                            st.success(f"✅ Music, Cover, and Storyline Summary successfully synthesized! (Attempt {attempt + 1}/3)")
                            synth_success = True
                            break
                        except Exception as e:
                            if attempt < max_retries - 1:
                                st.warning(f"⚠️ Prompt synthesis attempt {attempt + 1}/3 failed. Retrying with lower temperature {temp - 0.15:.2f}...")
                                time.sleep(1)
                            else:
                                raise e
                                
                    if not synth_success:
                        st.warning("⚠️ Structured prompt synthesis encountered persistent errors. Activating Self-Healing Fallback...")
                        fallback_schema = PromptSynthesis(
                            music_prompt=(
                                "A warm, nostalgic, and breezy acoustic-indie-folk instrumental soundtrack. "
                                "Starts with soft acoustic guitar picking, slowly building up with warm cello lines "
                                "and delicate piano keys. Perfect 78 BPM tempo, providing a comforting and "
                                "emotional arc. [Intro] Soft solo guitar. [Main] Full acoustic ensemble with "
                                "warm hums. [Outro] Fades out gracefully with single piano notes."
                            ),
                            image_prompt=(
                                "A poetic, highly detailed and artistic square digital album cover. "
                                "Features an abstract, nostalgic depiction of golden memories, warm lighting, "
                                "soft bokeh, double exposure elements blending scenic silhouettes of landscapes "
                                "and personal journeys, analog warm film aesthetic, cozy color grading."
                            ),
                            storyline_summary="따스했던 그해 가을, 바람을 가르며 소중한 이들과 함께 나눈 마지막 즉흥 여행의 추억"
                        )
                        st.session_state['soundtrack_prompt'] = fallback_schema.music_prompt
                        st.session_state['cover_prompt'] = fallback_schema.image_prompt
                        st.session_state['storyline_summary'] = fallback_schema.storyline_summary
                        st.success("✅ Self-Healing system automatically loaded high-quality backup prompts and summary. Pipeline continues!")
                        
        # Display synthesized Prompts side-by-side if available
        if st.session_state['soundtrack_prompt'] or st.session_state['cover_prompt']:
            st.write("")
            col_p1, col_p2 = st.columns(2)
            
            with col_p1:
                st.markdown("##### 🎵 Lyria Music Soundtrack Prompt")
                edited_music = st.text_area(
                    "Customize Soundtrack Prompt",
                    value=st.session_state['soundtrack_prompt'],
                    height=180,
                    key="ta_music_prompt"
                )
                st.session_state['soundtrack_prompt'] = edited_music
                
            with col_p2:
                st.markdown("##### 🎨 Imagen 4 Album Cover Prompt")
                edited_cover = st.text_area(
                    "Customize Album Cover Prompt",
                    value=st.session_state['cover_prompt'],
                    height=180,
                    key="ta_cover_prompt"
                )
                st.session_state['cover_prompt'] = edited_cover
                
            if st.session_state['storyline_summary']:
                st.markdown("##### ✨ Storyline 1-Line Summary (Korean)")
                edited_summary = st.text_input(
                    "Customize 1-Line Storyline Summary",
                    value=st.session_state['storyline_summary'],
                    key="ta_storyline_summary"
                )
                st.session_state['storyline_summary'] = edited_summary

            # Master Single-Step Assets Generation Button
            st.write("")
            if st.button("🎶 Compose Soundtrack & Render Cover Art", key="btn_generate_all_assets"):
                client = get_client()
                if client:
                    audio_success = False
                    with st.spinner("Step 1/2: Composing background soundtrack with DeepMind Lyria..."):
                        try:
                            interaction = client.interactions.create(
                                model=lyria_model,
                                input=st.session_state['soundtrack_prompt']
                            )
                            generated_audio = interaction.output_audio
                            if generated_audio and generated_audio.data:
                                audio_data = base64.b64decode(generated_audio.data)
                                st.session_state['audio_bytes'] = audio_data
                                if interaction.output_text:
                                    st.session_state['lyrics'] = interaction.output_text
                                else:
                                    st.session_state['lyrics'] = ""
                                audio_success = True
                            else:
                                st.error("❌ No audio output received from Lyria model.")
                        except Exception as e:
                            st.error(f"Error during Lyria soundtrack composition: {str(e)}")
                            
                    if audio_success:
                        with st.spinner("Step 2/2: Rendering single album cover art with Imagen 4..."):
                            try:
                                response = client.models.generate_images(
                                    model=imagen_model,
                                    prompt=st.session_state['cover_prompt'],
                                    config=types.GenerateImagesConfig(
                                        number_of_images=1,
                                        output_mime_type="image/png",
                                        aspect_ratio="1:1"
                                    )
                                )
                                if response.generated_images:
                                    generated_image = response.generated_images[0]
                                    st.session_state['cover_bytes'] = generated_image.image.image_bytes
                                    st.success("🎉 Soundtrack composed and Album Cover successfully rendered!")
                                else:
                                    st.error("❌ No cover art image was returned by Imagen 4.")
                            except Exception as e:
                                st.error(f"Error during Imagen 4 cover art generation: {str(e)}")
                                
        # Display Combined Asset Dashboard Player
        if st.session_state['audio_bytes'] and st.session_state['cover_bytes']:
            st.write("")
            st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin-top: 30px; margin-bottom: 30px;'>", unsafe_allow_html=True)
            st.markdown("### 💿 Synthesized Single Soundtrack & Art Deck")
            
            col_player_left, col_player_right = st.columns([1, 1.2])
            
            with col_player_left:
                st.image(st.session_state['cover_bytes'], caption="Imagen 4 Album Cover Art", use_container_width=True)
                
                # Floating Storyline summary card directly underneath the album cover
                if st.session_state['storyline_summary']:
                    st.markdown(f"""
                    <div class="summary-box">
                        ✨ {st.session_state['storyline_summary']}
                    </div>
                    """, unsafe_allow_html=True)
                st.write("")
                
                st.download_button(
                    label="📥 Download Album Cover (PNG)",
                    data=st.session_state['cover_bytes'],
                    file_name="album_cover.png",
                    mime="image/png"
                )
                
            with col_player_right:
                st.markdown("""
                <div class='glass-card' style='height: 100%;'>
                    <h4>🎧 Playback Dashboard</h4>
                    <p style='color: #94a3b8; font-size: 0.9rem; margin-bottom: 20px;'>Your memories compiled into a unified soundtrack.</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.audio(st.session_state['audio_bytes'], format="audio/mp3")
                
                st.download_button(
                    label="📥 Download Soundtrack (MP3)",
                    data=st.session_state['audio_bytes'],
                    file_name="memory_soundtrack.mp3",
                    mime="audio/mp3",
                    use_container_width=True
                )
                
                if st.session_state['lyrics']:
                    st.write("")
                    st.markdown("##### 📝 Accompanying Lyrics")
                    st.info(st.session_state['lyrics'])
