import os
import base64
import io
import logging
from typing import List
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MemorySoundtrackWeb")

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Memory Soundtrack Generator API",
    description="Backend service for generating music soundtracks and album covers from memory photos.",
    version="1.0.0"
)

# Enable CORS for local cross-origin testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------
# 1. API Client Helper Functions
# ----------------------------------------------------
def get_client(api_type: str = "Gemini Developer API", api_key_override: str = None, project_id_override: str = None, location_override: str = "us-central1"):
    try:
        if api_type == "Gemini Developer API":
            target_key = api_key_override if api_key_override else os.environ.get("GEMINI_API_KEY")
            if not target_key:
                raise HTTPException(status_code=400, detail="Gemini Developer API Key is missing. Please set GEMINI_API_KEY in environment or pass key override.")
            return genai.Client(api_key=target_key)
        else:
            target_proj = project_id_override if project_id_override else os.environ.get("ANTIGRAVITY_PROJECT_ID")
            if not target_proj:
                raise HTTPException(status_code=400, detail="Google Cloud Project ID is missing. Please set ANTIGRAVITY_PROJECT_ID in environment or pass project ID override.")
            return genai.Client(vertexai=True, project=target_proj, location=location_override)
    except Exception as e:
        logger.error(f"Failed to initialize Google GenAI Client: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to initialize Google GenAI Client: {str(e)}")

# ----------------------------------------------------
# 2. Endpoints
# ----------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serves the main single-page application frontend."""
    frontend_path = os.path.join(os.getcwd(), "index.html")
    if not os.path.exists(frontend_path):
        raise HTTPException(status_code=404, detail="index.html not found in the workspace directory.")
    return FileResponse(frontend_path)

@app.post("/api/create-album")
async def create_album(
    images: List[UploadFile] = File(...),
    api_type: str = Form("Gemini Developer API"),
    api_key: str = Form(None),
    project_id: str = Form(None),
    location: str = Form("us-central1"),
    gemini_model: str = Form("gemini-3.5-flash"),
    lyria_model: str = Form("lyria-3-clip-preview"),
    imagen_model: str = Form("imagen-4.0-generate-001")
):
    """
    Receives chronological memory photos and orchestrates:
    1. Chronological Image Story Analysis (Gemini 3.5 Flash)
    2. Music Prompt Synthesis (Gemini 3.5 Flash)
    3. Soundtrack Generation (DeepMind Lyria 3)
    4. Album Cover Art Generation (Imagen 4)
    Returns complete asset payload in Base64 JSON format.
    """
    if not images or len(images) == 0:
        raise HTTPException(status_code=400, detail="No memory photos were uploaded.")
    
    if len(images) > 5:
        logger.warning("More than 5 images uploaded. Limiting processing to the first 5 images.")
        images = images[:5]
        
    logger.info(f"Received {len(images)} images for processing via model {gemini_model}.")
    
    # Initialize the client
    client = get_client(
        api_type=api_type,
        api_key_override=api_key if api_key else None,
        project_id_override=project_id if project_id else None,
        location_override=location
    )
    
    # Step 1: Sequential Chronological Multimodal Analysis
    logger.info("Step 1: Running Multimodal Image Story Analysis via Gemini...")
    analyses_results = []
    
    # We will also convert each uploaded image to base64 so we can return them to the frontend
    # to serve as slides inside the customized client player.
    original_images_base64 = []
    
    for idx, file in enumerate(images):
        logger.info(f"Analyzing Image #{idx+1}: {file.filename}")
        try:
            # Read image bytes
            file_bytes = await file.read()
            
            # Base64 encode the uploaded photo for frontend slider display
            mime_type = file.content_type if file.content_type else "image/png"
            img_b64 = f"data:{mime_type};base64,{base64.b64encode(file_bytes).decode('utf-8')}"
            original_images_base64.append(img_b64)
            
            # Load into Pillow image
            pil_img = Image.open(io.BytesIO(file_bytes))
            
            # Formulate the story prompt
            prompt = (
                "당신은 따뜻한 감성을 가진 전문 스토리텔러이자 음악 평론가입니다. "
                "이 사진의 세부 요소를 분석하여 담겨 있는 이야기, 지배적인 감정 및 분위기(Vibe), "
                "그리고 이 사진에 어울릴 만한 음악적 분위기(예: 어쿠스틱 기타의 쓸쓸함, 잔잔한 피아노 선율, 활기찬 팝 비트 등)를 "
                "상세하게 서술해주세요. 한국어로 작성해 주세요."
            )
            
            response = client.models.generate_content(
                model=gemini_model,
                contents=[pil_img, prompt]
            )
            
            analyses_results.append({
                "index": idx + 1,
                "filename": file.filename,
                "analysis": response.text
            })
            
        except Exception as e:
            logger.error(f"Error analyzing image #{idx+1}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error analyzing image #{idx+1} ({file.filename}): {str(e)}")
            
    # Step 2: Story Synthesis & Music Prompt Creation
    logger.info("Step 2: Synthesizing music prompts via Gemini...")
    combined_context = "\n\n".join([
        f"Photo #{item['index']} story:\n{item['analysis']}"
        for item in analyses_results
    ])
    
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
        soundtrack_prompt = response.text.strip()
        logger.info(f"Music Prompt Synthesized: {soundtrack_prompt[:100]}...")
    except Exception as e:
        logger.error(f"Error synthesizing music prompt: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error synthesizing music prompt: {str(e)}")
        
    # Step 3: Soundtrack Generation (DeepMind Lyria 3)
    logger.info("Step 3: Composing soundtrack via DeepMind Lyria...")
    audio_base64_data = ""
    lyrics_text = ""
    
    try:
        interaction = client.interactions.create(
            model=lyria_model,
            input=soundtrack_prompt
        )
        
        generated_audio = interaction.output_audio
        if generated_audio and generated_audio.data:
            # We already have base64 data string in generated_audio.data from Lyria API
            # Just wrap it in Data URL structure or keep standard base64
            audio_base64_data = f"data:audio/mp3;base64,{generated_audio.data}"
            if interaction.output_text:
                lyrics_text = interaction.output_text
            logger.info("Lyria soundtrack composed successfully.")
        else:
            raise HTTPException(status_code=502, detail="No audio output received from Lyria composer service.")
    except Exception as e:
        logger.error(f"Error during Lyria music generation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error during Lyria music generation: {str(e)}")
        
    # Step 4: Album Cover Art (Imagen 4)
    logger.info("Step 4: Rendering album cover via Imagen 4...")
    cover_base64_data = ""
    
    cover_prompt = (
        f"A beautiful artistic, poetic album cover representing these memory themes: "
        f"{soundtrack_prompt[:200]}... "
        f"Vibrant aesthetics, cinematic lighting, digital art, high quality, no text."
    )
    
    try:
        response = client.models.generate_images(
            model=imagen_model,
            prompt=cover_prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                output_mime_type="image/png",
                aspect_ratio="1:1"
            )
        )
        
        if response.generated_images:
            image_bytes = response.generated_images[0].image.image_bytes
            cover_base64_data = f"data:image/png;base64,{base64.b64encode(image_bytes).decode('utf-8')}"
            logger.info("Imagen 4 album cover rendered successfully.")
        else:
            raise HTTPException(status_code=502, detail="No image returned from Imagen 4 rendering service.")
    except Exception as e:
        logger.error(f"Error during Imagen 4 generation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error during Imagen 4 generation: {str(e)}")
        
    # Assemble final JSON packet
    return {
        "success": True,
        "analyses": analyses_results,
        "soundtrack_prompt": soundtrack_prompt,
        "audio_base64": audio_base64_data,
        "lyrics": lyrics_text,
        "cover_base64": cover_base64_data,
        "slides": original_images_base64
    }
