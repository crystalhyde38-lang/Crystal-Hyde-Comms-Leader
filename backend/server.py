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
    visa_blue_dark = (10, 31, 111)
    gold = (255, 215, 0)  # #FFD700
    white = (255, 255, 255)
    light_blue = (70, 100, 220)
    
    # Create solid background
    img = Image.new('RGB', (width, height), visa_blue)
    draw = ImageDraw.Draw(img)
    
    # Load fonts with better sizes
    try:
        logo_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 70)
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
        heading_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
        body_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
    except:
        logo_font = heading_font = title_font = body_font = small_font = ImageFont.load_default()
    
    # Add padding
    padding = 60
    y_pos = padding
    
    # VISA logo with background box
    logo_box_height = 100
    draw.rectangle([(0, 0), (width, logo_box_height)], fill=visa_blue_dark)
    draw.text((width // 2, logo_box_height // 2), "VISA", font=logo_font, fill=gold, anchor="mm")
    y_pos = logo_box_height + 50
    
    # Main title - cleaner, larger
    title_lines = [
        "WOMEN'S WORLD CUP 2023",
        "SMALL BUSINESS GRANT PROGRAM"
    ]
    for line in title_lines:
        draw.text((width // 2, y_pos), line, font=title_font, fill=white, anchor="mm")
        y_pos += 58
    
    y_pos += 30
    
    # Separator line
    line_margin = 80
    draw.rectangle([(line_margin, y_pos), (width - line_margin, y_pos + 3)], fill=gold)
    y_pos += 50
    
    # KEY FACTS - single row, larger boxes
    draw.text((width // 2, y_pos), "KEY FACTS", font=heading_font, fill=gold, anchor="mm")
    y_pos += 50
    
    # Three key stats in clean boxes
    facts = [
        ("$500K", "Total Funding"),
        ("64", "Matches"),
        ("First Ever", "Linked Grant")
    ]
    
    box_width = 260
    box_height = 110
    box_spacing = 40
    total_width = (box_width * 3) + (box_spacing * 2)
    start_x = (width - total_width) // 2
    
    for i, (main_text, sub_text) in enumerate(facts):
        x = start_x + i * (box_width + box_spacing)
        
        # Box with shadow effect
        shadow_offset = 4
        draw.rectangle(
            [(x + shadow_offset, y_pos + shadow_offset), 
             (x + box_width + shadow_offset, y_pos + box_height + shadow_offset)],
            fill=(10, 20, 80)
        )
        
        # Main box
        draw.rectangle(
            [(x, y_pos), (x + box_width, y_pos + box_height)],
            fill=light_blue,
            outline=gold,
            width=4
        )
        
        # Text
        draw.text((x + box_width // 2, y_pos + 35), main_text, 
                 font=heading_font, fill=gold, anchor="mm")
        draw.text((x + box_width // 2, y_pos + 75), sub_text, 
                 font=body_font, fill=white, anchor="mm")
    
    y_pos += box_height + 60
    
    # HOW IT WORKED section
    draw.rectangle([(line_margin, y_pos), (width - line_margin, y_pos + 3)], fill=gold)
    y_pos += 40
    draw.text((width // 2, y_pos), "HOW IT WORKED", font=heading_font, fill=gold, anchor="mm")
    y_pos += 50
    
    # Content box
    content_padding = 100
    how_text = [
        "Female small business owners received grants",
        "after each of 64 matches",
        "",
        "$5,000 (group stage) → $50,000 (final)",
        "",
        "Grant awarded based on Player of the",
        "Match winner's country"
    ]
    
    for line in how_text:
        if line:
            draw.text((content_padding, y_pos), line, font=body_font, fill=white, anchor="lm")
        y_pos += 34
    
    y_pos += 30
    
    # CANADA PARTNERSHIP section
    draw.rectangle([(line_margin, y_pos), (width - line_margin, y_pos + 3)], fill=gold)
    y_pos += 40
    draw.text((width // 2, y_pos), "🇨🇦 CANADA PARTNERSHIP", font=heading_font, fill=gold, anchor="mm")
    y_pos += 50
    
    # Partnership box with shadow
    box_y_start = y_pos
    box_height = 200
    shadow_offset = 4
    
    draw.rectangle(
        [(line_margin + shadow_offset, box_y_start + shadow_offset), 
         (width - line_margin + shadow_offset, box_y_start + box_height + shadow_offset)],
        fill=(10, 20, 80)
    )
    
    draw.rectangle(
        [(line_margin, box_y_start), (width - line_margin, box_y_start + box_height)],
        fill=light_blue,
        outline=gold,
        width=4
    )
    
    canada_text = [
        "Canadian Council of Aboriginal Business",
        "(CCAB) Partnership",
        "",
        "Supporting Indigenous women entrepreneurs",
        "through the She's Next Program"
    ]
    
    text_y = box_y_start + 40
    for line in canada_text:
        if line:
            draw.text((width // 2, text_y), line, font=body_font, fill=white, anchor="mm")
        text_y += 32
    
    y_pos = box_y_start + box_height + 50
    
    # Footer
    draw.rectangle([(line_margin, y_pos), (width - line_margin, y_pos + 3)], fill=gold)
    y_pos += 30
    draw.text((width // 2, y_pos), "FIFA Women's World Cup Australia & New Zealand 2023™", 
             font=small_font, fill=white, anchor="mm")
    
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
        logger.info("Starting infographic generation using Pillow...")
        
        # Create the infographic
        img = create_infographic()
        
        # Convert to base64
        buffered = BytesIO()
        img.save(buffered, format="PNG", quality=95)
        img_bytes = buffered.getvalue()
        image_base64 = base64.b64encode(img_bytes).decode('utf-8')
        image_data_uri = f"data:image/png;base64,{image_base64}"
        
        logger.info("Infographic generated successfully")
        
        # Save to database
        infographic_obj = InfographicGeneration(
            image_base64=image_data_uri,
            prompt="Generated using Pillow - Visa Women's World Cup 2023 Grant Program"
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
