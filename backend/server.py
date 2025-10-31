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
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

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

def create_infographic():
    """
    Create a professional infographic using Pillow with crystal-clear text
    """
    # Image dimensions (portrait)
    width = 1024
    height = 1536
    
    # Colors
    visa_blue = (20, 52, 203)  # #1434CB
    visa_blue_dark = (10, 31, 111)  # Darker shade
    gold = (255, 215, 0)  # #FFD700
    white = (255, 255, 255)
    light_blue = (100, 130, 230)
    
    # Create image with gradient background
    img = Image.new('RGB', (width, height), visa_blue)
    draw = ImageDraw.Draw(img)
    
    # Create gradient background
    for y in range(height):
        shade = int(255 * (1 - y / height * 0.3))
        color = (
            int(visa_blue[0] * shade / 255),
            int(visa_blue[1] * shade / 255),
            int(visa_blue[2] * shade / 255)
        )
        draw.rectangle([(0, y), (width, y + 1)], fill=color)
    
    # Try to load fonts, fallback to default if not available
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 52)
        heading_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
        subheading_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
        body_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 26)
        small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
    except:
        # Fallback to default font
        title_font = ImageFont.load_default()
        heading_font = ImageFont.load_default()
        subheading_font = ImageFont.load_default()
        body_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    y_pos = 60
    
    # Draw VISA logo text
    draw.text((width // 2, y_pos), "VISA", font=heading_font, fill=gold, anchor="mm")
    y_pos += 80
    
    # Draw main title
    title_lines = [
        "WOMEN'S WORLD CUP 2023",
        "SMALL BUSINESS",
        "GRANT PROGRAM"
    ]
    for line in title_lines:
        draw.text((width // 2, y_pos), line, font=title_font, fill=white, anchor="mm")
        y_pos += 60
    
    y_pos += 20
    
    # Draw decorative line
    draw.rectangle([(100, y_pos), (width - 100, y_pos + 4)], fill=gold)
    y_pos += 40
    
    # KEY FACTS section
    draw.text((width // 2, y_pos), "KEY FACTS", font=heading_font, fill=gold, anchor="mm")
    y_pos += 60
    
    # Key facts in boxes
    facts = [
        ("💰 $500,000 USD", "Total Global Funding"),
        ("⚽ 64 Matches", "Grant Opportunities"),
        ("🏆 Historic First", "Award Linked to Grant")
    ]
    
    box_width = 280
    box_height = 100
    spacing = 30
    start_x = (width - (box_width * 3 + spacing * 2)) // 2
    
    for i, (main_text, sub_text) in enumerate(facts):
        x = start_x + i * (box_width + spacing)
        # Draw box background
        draw.rectangle(
            [(x, y_pos), (x + box_width, y_pos + box_height)],
            fill=light_blue,
            outline=gold,
            width=3
        )
        # Draw text
        draw.text((x + box_width // 2, y_pos + 30), main_text, font=body_font, fill=white, anchor="mm")
        draw.text((x + box_width // 2, y_pos + 70), sub_text, font=small_font, fill=white, anchor="mm")
    
    y_pos += box_height + 50
    
    # HOW IT WORKED section
    draw.rectangle([(80, y_pos), (width - 80, y_pos + 4)], fill=gold)
    y_pos += 30
    draw.text((width // 2, y_pos), "HOW IT WORKED", font=heading_font, fill=gold, anchor="mm")
    y_pos += 60
    
    how_it_worked = [
        "• Female small business owners received grants",
        "• $5,000 (group stage) to $50,000 (final)",
        "• One grant per match based on Player of",
        "  the Match winner's country"
    ]
    
    for line in how_it_worked:
        draw.text((120, y_pos), line, font=body_font, fill=white, anchor="lm")
        y_pos += 40
    
    y_pos += 20
    
    # CANADA PARTNERSHIP section
    draw.rectangle([(80, y_pos), (width - 80, y_pos + 4)], fill=gold)
    y_pos += 30
    draw.text((width // 2, y_pos), "🇨🇦 CANADA PARTNERSHIP", font=heading_font, fill=gold, anchor="mm")
    y_pos += 60
    
    # Canada partnership box
    draw.rectangle(
        [(80, y_pos), (width - 80, y_pos + 180)],
        fill=light_blue,
        outline=gold,
        width=3
    )
    
    canada_text = [
        "Canadian Council of Aboriginal",
        "Business (CCAB) Partnership",
        "",
        "Supporting Indigenous women",
        "entrepreneurs through the",
        "She's Next Program"
    ]
    
    text_y = y_pos + 30
    for line in canada_text:
        if line:
            draw.text((width // 2, text_y), line, font=body_font, fill=white, anchor="mm")
        text_y += 30
    
    y_pos += 220
    
    # Bottom decoration
    draw.rectangle([(100, y_pos), (width - 100, y_pos + 4)], fill=gold)
    y_pos += 30
    
    # Footer text
    draw.text((width // 2, y_pos), "FIFA Women's World Cup", font=small_font, fill=white, anchor="mm")
    y_pos += 30
    draw.text((width // 2, y_pos), "Australia & New Zealand 2023", font=small_font, fill=white, anchor="mm")
    
    return img

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
Create a clean, professional corporate infographic poster with CLEAR, READABLE TEXT in English.

CRITICAL: All text must be in ENGLISH, large, bold, and easy to read. No blurry or garbled text.

Title at top (large, bold, white text):
"VISA WOMEN'S WORLD CUP 2023
SMALL BUSINESS GRANT PROGRAM"

Layout sections from top to bottom with large, readable text:

SECTION 1 - KEY FACTS (with icons):
💰 Total Funding: $500,000 USD
⚽ Matches: 64 Grant Opportunities  
🏆 Innovation: First Player of Match Award Linked to Grant

SECTION 2 - HOW IT WORKED:
• Female small business owners received grants
• $5,000 (group stage) to $50,000 (final)
• One grant per match based on Player of the Match winner's country

SECTION 3 - CANADA PARTNERSHIP:
🇨🇦 Partnership with CCAB (Canadian Council of Aboriginal Business)
• Supporting Indigenous women entrepreneurs
• Aligned with She's Next Program mission

Design Style:
• Visa blue (#1434CB) background
• Gold/yellow (#FFD700) accents and text highlights
• White text for maximum readability
• Simple, clean layout with plenty of white space
• Large, bold, sans-serif typography
• Simple icons (trophy, soccer ball, money bag, maple leaf)
• Professional corporate style
• Portrait orientation (1024x1536)

IMPORTANT: Focus on text clarity and readability. Large fonts, high contrast, simple design.
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
