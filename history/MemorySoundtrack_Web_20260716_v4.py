import streamlit as st
import os
import base64
import io
import re
import time
import logging
from PIL import Image
from pydantic import BaseModel
from google import genai
from google.genai import types
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MemorySoundtrackWeb_v4")

# Load environment variables from .env file
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
    page_title="Memory Soundtrack - Ultimate Concurrency Edition",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom premium styling with glassmorphism and animations
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;800&display=swap" rel="stylesheet">

<style>
    /* Main body background & font family */
    .stApp {
        background: linear-gradient(135deg, #07070a 0%, #0d0d1b 50%, #05050a 100%);
        font-family: 'Outfit', sans-serif;
        color: #e2e8f0;
    }
    
    /* Title and gradients */
    .title-gradient {
        background: linear-gradient(45deg, #ff2a5f, #ff7e40, #a855f7, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.8rem;
        font-weight: 800;
        text-align: center;
        margin-top: 1rem;
        margin-bottom: 0.2rem;
        letter-spacing: -0.06em;
        text-shadow: 0px 10px 40px rgba(255, 42, 95, 0.15);
    }
    
    .subtitle {
        text-align: center;
        color: #94a3b8;
        font-size: 1.25rem;
        margin-bottom: 2.5rem;
        font-weight: 300;
    }
    
    /* Glassmorphism Card styling */
    .glass-card {
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 24px;
        padding: 28px;
        margin-bottom: 24px;
        box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.4);
        transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.4s ease, box-shadow 0.4s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-4px);
        border-color: rgba(255, 255, 255, 0.12);
        box-shadow: 0 16px 50px 0 rgba(236, 72, 153, 0.1);
    }
    
    /* Header/Section Text */
    h1, h2, h3 {
        font-family: 'Outfit', sans-serif;
        font-weight: 600;
        color: #ffffff;
        letter-spacing: -0.02em;
    }
    
    /* Custom Streamlit component adjustments */
    div.stButton > button {
        background: linear-gradient(135deg, #ff2a5f 0%, #ec4899 50%, #8b5cf6 100%);
        color: white;
        border: none;
        border-radius: 30px;
        padding: 14px 40px;
        font-weight: 600;
        font-size: 1.05rem;
        letter-spacing: 0.05em;
        box-shadow: 0 6px 20px rgba(236, 72, 153, 0.35);
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        width: 100%;
        margin-top: 12px;
    }
    
    div.stButton > button:hover {
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 8px 25px rgba(236, 72, 153, 0.55);
        background: linear-gradient(135deg, #ff4070 0%, #f43f5e 50%, #9c27b0 100%);
        color: white;
    }
    
    .status-text {
        font-weight: 500;
        color: #38bdf8;
    }

    /* Evocative summary styling */
    .summary-box {
        background: linear-gradient(135deg, rgba(236, 72, 153, 0.08) 0%, rgba(99, 102, 241, 0.08) 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 18px 24px;
        text-align: center;
        font-size: 1.15rem;
        font-weight: 500;
        font-style: italic;
        color: #f8fafc;
        margin-top: 16px;
        margin-bottom: 16px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.25);
    }
    
    /* Spinning Vinyl animation for album player */
    .vinyl-container {
        display: flex;
        justify-content: center;
        align-items: center;
        position: relative;
        margin-bottom: 20px;
    }
    
    .vinyl-record {
        width: 260px;
        height: 260px;
        border-radius: 50%;
        background: radial-gradient(circle, #0c0c0c 30%, #1f1f1f 40%, #111 41%, #1e1e1e 50%, #0f0f0f 51%, #2c2c2c 60%, #121212 61%, #050505 70%);
        border: 4px solid #333;
        box-shadow: 0 10px 30px rgba(0,0,0,0.6);
        animation: spin 6s linear infinite;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    
    .vinyl-cover {
        width: 110px;
        height: 110px;
        border-radius: 50%;
        overflow: hidden;
        border: 3px solid #000;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 2. Sidebar Configuration (Clean Consumer UX with Collapsed Developer Settings)
# ----------------------------------------------------
st.sidebar.markdown("""
<div style='text-align: center; padding: 10px 0;'>
    <h3 style='margin:0; color:#ff2a5f;'>🌌 Memory Soundtrack</h3>
    <p style='color:#94a3b8; font-size:0.85rem; margin-top:5px;'>Ultimate Concurrency Edition v4</p>
</div>
<hr style='border-color: rgba(255,255,255,0.06); margin-top: 10px; margin-bottom: 20px;'>
""", unsafe_allow_html=True)

st.sidebar.markdown("""
#### 📖 How to Use
1. **📸 Upload Photos**: Upload up to 5 memorable photos.
2. **🔄 Rearrange**: Drag or click the ◀ / ▶ buttons under each card to align them chronologically.
3. **🎶 Generate**: Click **나의 추억 앨범 생성하기** to run the complete automated orchestration in one go.
""")

st.sidebar.markdown("<br>", unsafe_allow_html=True)

# Advanced developer settings collapsed by default for clean consumer UX
with st.sidebar.expander("⚙️ Advanced Developer Settings", expanded=False):
    st.info("These configurations are pre-loaded from environment defaults. Only modify if you have custom development endpoints.")
    
    api_type = st.selectbox(
        "API Service Type",
        ["Gemini Developer API", "Vertex AI"],
        index=0
    )
    
    # API Type specific inputs with fallback to env variables
    api_key = None
    project_id = None
    location = "us-central1"
    
    if api_type == "Gemini Developer API":
        default_key = os.environ.get("GEMINI_API_KEY", "")
        api_key = st.text_input(
            "Gemini API Key",
            value=default_key,
            type="password",
            help="Your Google AI Studio key. Falls back to GEMINI_API_KEY."
        )
    else:
        default_proj = os.environ.get("ANTIGRAVITY_PROJECT_ID", "")
        project_id = st.text_input(
            "GCP Project ID",
            value=default_proj,
            help="Your Google Cloud Project ID. Falls back to ANTIGRAVITY_PROJECT_ID."
        )
        location = st.text_input("GCP Location", value=location)
        
    st.markdown("##### 🤖 Models")
    gemini_model = st.text_input("Gemini Storyteller", value="gemini-3.5-flash")
    lyria_model = st.text_input("Lyria Audio Composer", value="lyria-3-clip-preview")
    imagen_model = st.text_input("Imagen Art Studio", value="imagen-4.0-generate-001")

# Clean, safe defaults if settings are collapsed/omitted
if 'api_type' not in locals():
    api_type = "Gemini Developer API"
    api_key = os.environ.get("GEMINI_API_KEY", "")
    project_id = os.environ.get("ANTIGRAVITY_PROJECT_ID", "")
    location = "us-central1"
    gemini_model = "gemini-3.5-flash"
    lyria_model = "lyria-3-clip-preview"
    imagen_model = "imagen-4.0-generate-001"

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
if 'album_generated' not in st.session_state:
    st.session_state['album_generated'] = False

# Helper to initialize Google GenAI Client
def get_client():
    try:
        if api_type == "Gemini Developer API":
            target_key = api_key if api_key else os.environ.get("GEMINI_API_KEY")
            if not target_key:
                st.error("❌ Gemini API Key is missing. Please set GEMINI_API_KEY in the environment or sidebar.")
                return None
            return genai.Client(api_key=target_key)
        else:
            target_proj = project_id if project_id else os.environ.get("ANTIGRAVITY_PROJECT_ID")
            if not target_proj:
                st.error("❌ Google Cloud Project ID is missing. Please set ANTIGRAVITY_PROJECT_ID in the environment or sidebar.")
                return None
            return genai.Client(vertexai=True, project=target_proj, location=location)
    except Exception as e:
        st.error(f"❌ Failed to initialize client: {str(e)}")
        return None

# ----------------------------------------------------
# 3. Prompt Sanitization & Self-Healing Utilities
# ----------------------------------------------------
def sanitize_music_prompt_regex(prompt: str) -> str:
    """
    Strips copyrighted words, specific artist/band names, and platform tags that violate Lyria's policy.
    """
    triggers = [
        r"\bcoldplay\b", r"\bbts\b", r"\biu\b", r"\bed sheeran\b", r"\blofi girl\b", 
        r"\blo-fi girl\b", r"\byoutube\b", r"\bspotify\b", r"\bghibli\b", r"\bdisney\b", 
        r"\bhans zimmer\b", r"\bshinkai\b", r"\bmakoto\b", r"\bnetflix\b", r"\bcoachella\b",
        r"\bsuno\b", r"\budio\b", r"\baimusic\b", r"\bgoogle\b"
    ]
    sanitized = prompt
    for trigger in triggers:
        sanitized = re.sub(trigger, "", sanitized, flags=re.IGNORECASE)
    
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    return sanitized

def rewrite_prompt_via_gemini(client, bad_prompt: str, error_msg: str) -> str:
    """
    Leverages Gemini 3.5 Flash to automatically rebuild blocked prompts to be completely policy-safe.
    """
    instruction = (
        f"The following music prompt was BLOCKED by the safety/content policy of the music generation model.\n"
        f"Error reported: {error_msg}\n"
        f"Blocked prompt: {bad_prompt}\n\n"
        f"Please rewrite this prompt to be 100% compliant with safety guidelines. "
        f"Remove all specific artist names, band names, brand names, platform names, and copyrighted terms. "
        f"Do not mention anyone or any company. Describe only the instruments, acoustic textures, generic genre (e.g. warm indie folk), mood, tempo, and song structure ([Intro], [Main], [Outro]) in rich detail. "
        f"Return ONLY the rewritten, safe English prompt without any prefix, conversational text, markdown formatting, or quotes."
    )
    try:
        response = client.models.generate_content(
            model=gemini_model,
            contents=instruction,
            config=types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=1000
            )
        )
        rewritten = response.text.strip()
        rewritten = rewritten.replace('```', '').replace('`', '').strip()
        return rewritten
    except Exception as e:
        logger.error(f"Failed to rewrite prompt via Gemini: {str(e)}")
        return sanitize_music_prompt_regex(bad_prompt)

# ----------------------------------------------------
# 4. Multi-Agent Concurrent Single Image Analyzer (3-Line Constraint)
# ----------------------------------------------------
def analyze_single_image(client, idx, file, gemini_model):
    """
    Asynchronously analyzes a single memory image in parallel using Gemini.
    Restricts the narrative to EXACTLY 3 lines of emotional essay, in Korean.
    """
    try:
        img = Image.open(file)
        prompt = (
            "당신은 따뜻하고 섬세한 감성을 가진 전문 스토리텔러이자 음악 감독입니다. "
            "이 사진의 미장센, 빛의 느낌, 구도, 그리고 분위기를 분석하고 서정적인 스토리로 풀어주세요.\n\n"
            "🚨 작성 제약 조건 (가장 중요):\n"
            "1. 이 사진에서 느껴지는 감정과 분위기를 담아 딱 3줄의 아름다운 한글 감성 에세이(또는 3개의 정갈한 한글 문장)로만 짧고 서정적이게 작성해 주세요. (반드시 정확히 3줄로 끝내야 합니다.)\n"
            "2. 이 시각적 연출과 완벽하게 조화될 만한 보편적인 음악적 무드 묘사(예: 어쿠스틱 nylon 기타 선율, 서정적인 피아노 톤)를 3줄의 내용 중 한 구절에 자연스럽게 녹여내어 작성해 주세요.\n\n"
            "⚠️ 극도로 중요한 주의사항: 분석 본문과 제안에 '콜드플레이', '지브리', 'BTS', '아이유', '신카이 마코토' 등 어떠한 특정 아티스트명, 밴드명, 작곡가명, 애니메이션, 혹은 플랫폼 상표명(Suno, Udio, 유튜브, 스포티파이 등)도 언급하는 것을 완전히 금지합니다. 오직 보편적인 음악 묘사 단어만을 사용해야 합니다.\n\n"
            "인사말이나 부연 설명 없이, 곧바로 정교하고 섬세한 한국어 텍스트로 딱 3줄로만 작성해주세요."
        )
        response = client.models.generate_content(
            model=gemini_model,
            contents=[img, prompt],
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=1500,
            )
        )
        # Enforce clean 3 lines structure just in case of any trailing spaces
        text_lines = [line.strip() for line in response.text.split('\n') if line.strip()]
        three_lines = "\n".join(text_lines[:3])
        
        return {
            "index": idx + 1,
            "filename": file.name,
            "image": img,
            "analysis": three_lines
        }
    except Exception as e:
        logger.error(f"Error in parallel analysis of image #{idx+1}: {str(e)}")
        return {
            "index": idx + 1,
            "filename": file.name,
            "image": Image.open(file),
            "analysis": f"사진을 분석하는 도중 예상치 못한 오류가 발생했습니다.\n서정적인 피아노와 어쿠스틱 선율이 흘러나옵니다.\n소중한 순간의 따스한 감성만이 공기 중에 감돕니다."
        }

# ----------------------------------------------------
# 5. Main Interface Header
# ----------------------------------------------------
st.markdown("<div class='title-gradient'>Memory Soundtrack Generator</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Weave your precious chronological memories into a single, safety-guarded master soundtrack single in just one click</div>", unsafe_allow_html=True)

# ----------------------------------------------------
# 6. Step 1: Upload & Timeline Configuration
# ----------------------------------------------------
st.markdown("### 📸 1. Chronological Image Slide-Deck")

uploaded_files = st.file_uploader(
    "Choose memory photos to compose into your timeline (Max 5)",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True,
    key="memory_uploader"
)

final_files_to_process = []

if uploaded_files:
    files_to_process = uploaded_files[:5]
    if len(uploaded_files) > 5:
        st.warning("⚠️ High volume detected. Only the first 5 images will be analyzed.")
        
    current_names = [f.name for f in files_to_process]
    
    # Sync session state with uploaded files
    for name in current_names:
        if name not in st.session_state['ordered_file_names']:
            st.session_state['ordered_file_names'].append(name)
            
    st.session_state['ordered_file_names'] = [
        name for name in st.session_state['ordered_file_names'] if name in current_names
    ]
    
    # Re-map the files to match the session state ordering
    file_map = {f.name: f for f in files_to_process}
    final_files_to_process = [
        file_map[name] for name in st.session_state['ordered_file_names'] if name in file_map
    ]
        
    # 🔄 Chronological Reordering UI using Left/Right Buttons
    st.write("")
    st.markdown("#### 🔄 Organize Chronological Sequence")
    st.caption("Use the buttons below each memory card to arrange them from oldest (left) to newest (right).")
        
    cols = st.columns(min(len(final_files_to_process), 5))
    for i, file in enumerate(final_files_to_process):
        with cols[i]:
            img = Image.open(file)
            st.image(img, use_container_width=True, caption=f"Slide #{i+1}: {file.name}")
            
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

# ----------------------------------------------------
# 7. Step 2: One-Click Master Execution (Concurrent Multi-Agent)
# ----------------------------------------------------
if uploaded_files and final_files_to_process:
    st.markdown("<hr style='border-color: rgba(255,255,255,0.08); margin-top: 35px; margin-bottom: 35px;'>", unsafe_allow_html=True)
    st.markdown("### 💿 2. Create Soundtrack & Cover Art")
    st.write("Clicking the button below will analyze your memories, synthesize safe prompts, compose your original soundtrack, and generate a customized album cover in one consecutive flow.")
    
    if st.button("🎶 나의 추억 앨범 생성하기 (One-Click Generation)", key="btn_one_click_generate"):
        client = get_client()
        if client:
            # Stage 1: Parallel Multi-Agent Image Story Analysis
            st_stage1_progress = st.empty()
            st_stage1_progress.info("⚡ [Stage 1/4] 멀티 에이전트(Multi-Agent)를 기동하여 모든 이미지 분석을 초고속 동시 병렬 진행하는 중입니다...")
            
            analyses_results = []
            try:
                # Execute Gemini requests in parallel threads
                with ThreadPoolExecutor(max_workers=len(final_files_to_process)) as executor:
                    futures = [
                        executor.submit(analyze_single_image, client, idx, file, gemini_model)
                        for idx, file in enumerate(final_files_to_process)
                    ]
                    analyses_results = [future.result() for future in futures]
                
                # Ensure they are sorted in correct chronological index
                analyses_results.sort(key=lambda x: x['index'])
                st.session_state['analyses'] = analyses_results
            except Exception as e:
                st.error(f"❌ Error during concurrent Multi-Agent analysis: {str(e)}")
                
            st_stage1_progress.empty()
            
            # Stage 2: Prompt Synthesis & Storyline Summarization
            st_stage2_status = st.empty()
            with st_stage2_status.container():
                st.info("[Stage 2/4] Synthesizing stories into safe production prompts...")
                combined_context = "\n\n".join([
                    f"Photo #{item['index']} story:\n{item['analysis']}"
                    for item in st.session_state['analyses']
                ])
                
                synth_instruction = (
                    f"Below are the individual emotional story-analyses of a chronological collection of memory photos:\n"
                    f"{combined_context}\n\n"
                    f"Your task is to analyze these chronological stories and synthesize THREE distinct outputs:\n\n"
                    f"1. `music_prompt`: A highly detailed, complete prompt for a music AI (Lyria). "
                    f"It must describe a single cohesive 30-second soundtrack blending the emotional arc of all the photos. "
                    f"Specify: Style/Genre, Mood, detailed Instrumentation (e.g. acoustic nylon guitar, electric Rhodes, brush drums), Tempo (BPM), Structure ([Intro], [Main], [Outro]), and Vocal/Melody.\n"
                    f"🚨 CRITICAL CONSTRAINT: Do NOT include any specific artist names, band names, brand names, composers, platform names, or copyrighted song titles (e.g. Coldplay, BTS, Hans Zimmer, Lofi Girl, YouTube, Spotify etc.) in the music_prompt. Describe only the style, genre, instrumentation, mood, and tempo using descriptive terms.\n"
                    f"Ensure this prompt ends in a finished sentence and doesn't cut off.\n\n"
                    f"2. `image_prompt`: A poetic, vivid, high-fidelity prompt for an image AI (Imagen 4) to render a single, square, professional digital album cover. "
                    f"It must abstractly represent the core emotional theme of the collection. Do NOT include text.\n\n"
                    f"3. `storyline_summary`: A warm, beautiful, highly literary 1-line summary of the entire chronological storyline in Korean (under 100 characters).\n\n"
                    f"Return your output strictly structured matching the provided JSON schema."
                )
                
                max_retries = 3
                synth_success = False
                for attempt in range(max_retries):
                    temp = max(0.1, 0.4 - attempt * 0.12)
                    try:
                        response = client.models.generate_content(
                            model=gemini_model,
                            contents=synth_instruction,
                            config=types.GenerateContentConfig(
                                temperature=temp,
                                max_output_tokens=10000,
                                response_mime_type="application/json",
                                response_schema=PromptSynthesis,
                            )
                        )
                        parsed_schema = PromptSynthesis.model_validate_json(response.text)
                        st.session_state['soundtrack_prompt'] = parsed_schema.music_prompt
                        st.session_state['cover_prompt'] = parsed_schema.image_prompt
                        st.session_state['storyline_summary'] = parsed_schema.storyline_summary
                        synth_success = True
                        break
                    except Exception as e:
                        logger.warning(f"Synthesis attempt {attempt+1} failed: {str(e)}")
                        time.sleep(1)
                        
                if not synth_success:
                    st.session_state['soundtrack_prompt'] = (
                        "A warm, nostalgic, and breezy acoustic-indie-folk instrumental soundtrack. "
                        "Starts with soft acoustic guitar picking, slowly building up with warm cello lines "
                        "and delicate piano keys. Perfect 78 BPM tempo, providing a comforting and "
                        "emotional arc. [Intro] Soft solo guitar. [Main] Full acoustic ensemble with "
                        "warm hums. [Outro] Fades out gracefully with single piano notes."
                    )
                    st.session_state['cover_prompt'] = (
                        "A poetic, highly detailed and artistic square digital album cover. "
                        "Features an abstract, nostalgic depiction of golden memories, warm lighting, "
                        "soft bokeh, double exposure elements blending scenic silhouettes of landscapes "
                        "and personal journeys, analog warm film aesthetic, cozy color grading."
                    )
                    st.session_state['storyline_summary'] = "따스했던 그해 가을, 바람을 가르며 소중한 이들과 함께 나눈 마지막 즉흥 여행의 추억"
                    
            st_stage2_status.empty()
            
            # Stage 3: Lyria Soundtrack Composition with Multi-Stage Self-Healing
            st_stage3_status = st.empty()
            audio_success = False
            with st_stage3_status.container():
                st.info("[Stage 3/4] Composing single soundtrack with DeepMind Lyria...")
                current_prompt = st.session_state['soundtrack_prompt']
                
                for attempt in range(3):
                    try:
                        if attempt == 1:
                            st.warning("⚠️ Safety filter triggered. Re-sanitizing and safe-rewriting prompt via Gemini...")
                            regex_clean = sanitize_music_prompt_regex(current_prompt)
                            rewritten_prompt = rewrite_prompt_via_gemini(client, regex_clean, "content_blocked")
                            current_prompt = rewritten_prompt
                            st.info(f"🔄 Retrying with policy-safe prompt: {current_prompt}")
                        elif attempt == 2:
                            st.warning("⚠️ Double safety block. Injecting pre-cleared sentimental acoustic fallback...")
                            current_prompt = (
                                "A warm, nostalgic, and breezy acoustic-indie-folk instrumental soundtrack. "
                                "Starts with soft acoustic guitar picking, slowly building up with warm cello lines "
                                "and delicate piano keys. Perfect 78 BPM tempo, providing a comforting and "
                                "emotional arc. [Intro] Soft solo guitar. [Main] Full acoustic ensemble with "
                                "warm hums. [Outro] Fades out gracefully with single piano notes."
                            )
                        
                        interaction = client.interactions.create(
                            model=lyria_model,
                            input=current_prompt
                        )
                        generated_audio = interaction.output_audio
                        
                        if generated_audio and generated_audio.data:
                            audio_data = base64.b64decode(generated_audio.data)
                            st.session_state['audio_bytes'] = audio_data
                            st.session_state['soundtrack_prompt'] = current_prompt
                            
                            if interaction.output_text:
                                st.session_state['lyrics'] = interaction.output_text
                            else:
                                st.session_state['lyrics'] = ""
                                
                            audio_success = True
                            break
                        else:
                            raise Exception("Empty payload received.")
                    except Exception as e:
                        err_str = str(e)
                        logger.error(f"Lyria generation failed on attempt {attempt+1}: {err_str}")
                        continue
                        
            st_stage3_status.empty()
            
            # Stage 4: Imagen 4 Cover Art Generation
            if audio_success:
                st_stage4_status = st.empty()
                with st_stage4_status.container():
                    st.info("[Stage 4/4] Rendering beautiful single album cover art with Imagen 4...")
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
                            st.session_state['album_generated'] = True
                            st.success("🎉 Single album successfully generated!")
                        else:
                            st.error("❌ No image was returned by Imagen 4.")
                    except Exception as e:
                        st.error(f"Error during Imagen 4 generation: {str(e)}")
                        
                st_stage4_status.empty()
                st.rerun()

# ----------------------------------------------------
# 8. Step 3: Complete Album Playback & Slide Deck
# ----------------------------------------------------
if st.session_state['album_generated'] and st.session_state['audio_bytes'] and st.session_state['cover_bytes']:
    st.markdown("<hr style='border-color: rgba(255,255,255,0.08); margin-top: 40px; margin-bottom: 40px;'>", unsafe_allow_html=True)
    st.markdown("### 💿 완성된 나의 추억 싱글 앨범 (Playback Dashboard)")
    
    col_player_left, col_player_right = st.columns([1.1, 1.3])
    
    with col_player_left:
        # Premium spinning record player preview
        cover_b64 = base64.b64encode(st.session_state['cover_bytes']).decode('utf-8')
        cover_src = f"data:image/png;base64,{cover_b64}"
        
        st.markdown(f"""
        <div class="vinyl-container">
            <div class="vinyl-record">
                <div class="vinyl-cover" style="background-image: url('{cover_src}'); background-size: cover; background-position: center;">
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Floating Storyline summary card directly underneath the spinning cover
        if st.session_state['storyline_summary']:
            st.markdown(f"""
            <div class="summary-box">
                ✨ {st.session_state['storyline_summary']}
            </div>
            """, unsafe_allow_html=True)
        st.write("")
        
        st.download_button(
            label="📥 Download Album Cover Art (PNG)",
            data=st.session_state['cover_bytes'],
            file_name="album_cover.png",
            mime="image/png"
        )
        
    with col_player_right:
        st.markdown("""
        <div class='glass-card'>
            <h4 style='margin-top:0; color:#ff2a5f;'>🎧 High-Fidelity Audio Deck</h4>
            <p style='color: #94a3b8; font-size: 0.95rem; margin-bottom: 25px;'>Your sequential timeline memories mixed into a safe, gorgeous soundtrack.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.audio(st.session_state['audio_bytes'], format="audio/mp3")
        st.write("")
        
        st.download_button(
            label="📥 Download Soundtrack Master Single (MP3)",
            data=st.session_state['audio_bytes'],
            file_name="memory_soundtrack.mp3",
            mime="audio/mp3",
            use_container_width=True
        )
        
        if st.session_state['lyrics']:
            st.write("")
            st.markdown("##### 📝 Accompanying Soundtrack Script / Hums")
            st.info(st.session_state['lyrics'])
            
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("##### 🛠️ Verified Safe Prompts Used")
        with st.expander("View Sanitized Execution Prompt", expanded=False):
            st.caption("This prompt was passed through the self-healing filter and accepted by Lyria's policy engines:")
            st.code(st.session_state['soundtrack_prompt'], language="text")

    # Display original timeline emotional analyses side-by-side (With clean 3-line presentation)
    if st.session_state['analyses']:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 📂 Extracted Stories & Vibes (3-Line Summary)")
        for item in st.session_state['analyses']:
            with st.container():
                st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
                col_item_l, col_item_r = st.columns([1, 1.8])
                with col_item_l:
                    st.image(item['image'], caption=f"Timeline Slide #{item['index']}: {item['filename']}", use_container_width=True)
                with col_item_r:
                    st.markdown(f"#### 🖼️ Timeline Slide #{item['index']} Emotional Analysis")
                    st.markdown(f"<p style='white-space: pre-wrap; font-size: 1.05rem; color: #f1f5f9; line-height:1.8; font-style: italic; border-left: 3px solid #ff2a5f; padding-left: 15px;'>{item['analysis']}</p>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

    # Collapsible Advanced Customization Section (Advanced Prompt Editor)
    st.markdown("<br><hr style='border-color: rgba(255,255,255,0.06);'>", unsafe_allow_html=True)
    with st.expander("⚙️ 프롬프트 수정 및 재작곡 (Advanced Prompt Editor)", expanded=False):
        st.info("You can fine-tune the synthesized prompts and summary manually and re-generate the album singe.")
        
        col_ed1, col_ed2 = st.columns(2)
        with col_ed1:
            custom_music = st.text_area("Soundtrack Prompt", value=st.session_state['soundtrack_prompt'], height=180)
        with col_ed2:
            custom_cover = st.text_area("Album Cover Prompt", value=st.session_state['cover_prompt'], height=180)
            
        custom_summary = st.text_input("1-Line Storyline Summary (Korean)", value=st.session_state['storyline_summary'])
        
        st.write("")
        if st.button("🔄 수정된 프롬프트로 재작곡하기 (Re-compose Single)", key="btn_recompose"):
            client = get_client()
            if client:
                st.session_state['soundtrack_prompt'] = custom_music
                st.session_state['cover_prompt'] = custom_cover
                st.session_state['storyline_summary'] = custom_summary
                
                audio_success = False
                with st.spinner("Re-composing soundtrack with Lyria (incorporating safety self-healing)..."):
                    current_prompt = st.session_state['soundtrack_prompt']
                    for attempt in range(3):
                        try:
                            if attempt == 1:
                                regex_clean = sanitize_music_prompt_regex(current_prompt)
                                rewritten_prompt = rewrite_prompt_via_gemini(client, regex_clean, "content_blocked")
                                current_prompt = rewritten_prompt
                            elif attempt == 2:
                                current_prompt = (
                                    "A warm, nostalgic, and breezy acoustic-indie-folk instrumental soundtrack. "
                                    "Starts with soft acoustic guitar picking, slowly building up with warm cello lines "
                                    "and delicate piano keys. Perfect 78 BPM tempo, providing a comforting and "
                                    "emotional arc. [Intro] Soft solo guitar. [Main] Full acoustic ensemble with "
                                    "warm hums. [Outro] Fades out gracefully with single piano notes."
                                )
                            
                            interaction = client.interactions.create(
                                model=lyria_model,
                                input=current_prompt
                            )
                            generated_audio = interaction.output_audio
                            
                            if generated_audio and generated_audio.data:
                                audio_bytes = base64.b64decode(generated_audio.data)
                                st.session_state['audio_bytes'] = audio_bytes
                                st.session_state['soundtrack_prompt'] = current_prompt
                                if interaction.output_text:
                                    st.session_state['lyrics'] = interaction.output_text
                                else:
                                    st.session_state['lyrics'] = ""
                                audio_success = True
                                break
                        except Exception as e:
                            logger.error(f"Re-composition attempt {attempt+1} failed: {str(e)}")
                            continue
                            
                if audio_success:
                    with st.spinner("Re-rendering album cover with Imagen 4..."):
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
                                st.success("🎉 Single album successfully regenerated!")
                                st.rerun()
                            else:
                                st.error("❌ No image was returned by Imagen 4.")
                        except Exception as e:
                            st.error(f"Error during Imagen 4 re-rendering: {str(e)}")
