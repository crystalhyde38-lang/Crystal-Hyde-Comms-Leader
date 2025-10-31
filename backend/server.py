from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import base64
from emergentintegrations.llm.openai.image_generation import OpenAIImageGeneration

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize OpenAI Image Generation
emergent_llm_key = os.environ.get('EMERGENT_LLM_KEY')
if not emergent_llm_key:
    logger.error("EMERGENT_LLM_KEY not found in environment")
    raise ValueError("EMERGENT_LLM_KEY is required")

# Define Models
class InfographicGeneration(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    image_base64: str
    prompt: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class InfographicGenerationResponse(BaseModel):
    id: str
    image_base64: str
    message: str

# Routes
@api_router.get("/")
async def root():
    return {"message": "Visa Women's World Cup Infographic Generator API"}

@api_router.post("/generate-infographic", response_model=InfographicGenerationResponse)
async def generate_infographic():
    """
    Generate an infographic for Visa's Women's World Cup 2023 Small Business Grant Program
    """
    try:
        logger.info("Starting infographic generation...")
        
        # Detailed prompt with all the information
        prompt = """
Create a professional infographic for Visa's Women's World Cup 2023 Small Business Grant Program with the following information:

Title: "Visa Women's World Cup 2023 Small Business Grant Program"

Key Information:
• Year: 2023 (FIFA Women's World Cup Australia & New Zealand 2023™)
• Program: Visa Player of the Match Grant
• Total Funding: $500,000 USD globally
• Innovation: First time the Visa Player of the Match award was linked to a grant

How it Worked:
• After each of the 64 matches, a female small business owner from the winning player's country received a grant
• Grant amounts ranged from $5,000 USD (group-stage matches) to $50,000 USD (Final)

Canada Partnership:
• Visa partnered with the Canadian Council of Aboriginal Business (CCAB)
• When a Canadian player won Player of the Match, funds were granted to CCAB
• Purpose: Support Indigenous women entrepreneurs

Design Requirements:
• Use Visa blue (#1434CB) as the primary color
• Include gold accents for premium feel
• Professional, modern layout
• Clear visual hierarchy
• Icons or graphics representing: soccer ball, trophy, business/entrepreneurship, global reach
• Canada flag or maple leaf to highlight the Canadian angle
• Clean typography with headers and organized information blocks

Style: Professional corporate infographic, clean and modern, suitable for business presentation
        """
        
        logger.info("Calling OpenAI Image Generation API...")
        
        # Initialize image generator
        image_gen = OpenAIImageGeneration(api_key=emergent_llm_key)
        
        # Generate images
        images = await image_gen.generate_images(
            prompt=prompt,
            model="gpt-image-1",
            number_of_images=1
        )
        
        if not images or len(images) == 0:
            logger.error("No image was generated")
            raise HTTPException(status_code=500, detail="No image was generated")
        
        # Convert image to base64
        image_base64 = base64.b64encode(images[0]).decode('utf-8')
        image_data_uri = f"data:image/png;base64,{image_base64}"
        
        logger.info("Infographic generated successfully")
        
        # Save to database
        infographic_obj = InfographicGeneration(
            image_base64=image_data_uri,
            prompt=prompt
        )
        
        doc = infographic_obj.model_dump()
        doc['timestamp'] = doc['timestamp'].isoformat()
        
        await db.infographics.insert_one(doc)
        logger.info(f"Infographic saved to database with ID: {infographic_obj.id}")
        
        return InfographicGenerationResponse(
            id=infographic_obj.id,
            image_base64=image_data_uri,
            message="Infographic generated successfully"
        )
        
    except Exception as e:
        logger.error(f"Error generating infographic: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating infographic: {str(e)}")

@api_router.get("/infographics", response_model=List[InfographicGeneration])
async def get_infographics():
    """
    Get all generated infographics
    """
    try:
        infographics = await db.infographics.find({}, {"_id": 0}).to_list(100)
        
        # Convert ISO string timestamps back to datetime objects
        for infographic in infographics:
            if isinstance(infographic['timestamp'], str):
                infographic['timestamp'] = datetime.fromisoformat(infographic['timestamp'])
        
        return infographics
    except Exception as e:
        logger.error(f"Error fetching infographics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching infographics: {str(e)}")

@api_router.get("/infographic/{infographic_id}")
async def get_infographic(infographic_id: str):
    """
    Get a specific infographic by ID
    """
    try:
        infographic = await db.infographics.find_one({"id": infographic_id}, {"_id": 0})
        
        if not infographic:
            raise HTTPException(status_code=404, detail="Infographic not found")
        
        if isinstance(infographic['timestamp'], str):
            infographic['timestamp'] = datetime.fromisoformat(infographic['timestamp'])
        
        return infographic
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching infographic: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching infographic: {str(e)}")

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
