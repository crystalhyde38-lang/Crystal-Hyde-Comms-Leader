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
    Create a professional infographic matching the web page design
    """
    # Image dimensions (portrait)
    width = 1024
    height = 1536
    
    # Colors matching the web design
    bg_dark = (10, 14, 39)  # #0a0e27
    bg_card = (26, 31, 58)  # #1a1f3a
    visa_blue = (20, 52, 203)  # #1434CB
    gold = (255, 215, 0)  # #FFD700
    white = (255, 255, 255)
    light_text = (200, 200, 200)
    
    # Create background
    img = Image.new('RGB', (width, height), bg_dark)
    draw = ImageDraw.Draw(img)
    
    # Load fonts
    try:
        logo_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 64)
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 42)
        heading_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
        body_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
        small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    except:
        logo_font = heading_font = title_font = body_font = small_font = ImageFont.load_default()
    
    padding = 50
    y_pos = padding
    
    # VISA logo with glow effect
    draw.text((width // 2, y_pos), "VISA", font=logo_font, fill=gold, anchor="mm", stroke_width=2, stroke_fill=visa_blue)
    y_pos += 90
    
    # Main title
    draw.text((width // 2, y_pos), "WOMEN'S WORLD CUP 2023", font=title_font, fill=white, anchor="mm")
    y_pos += 50
    draw.text((width // 2, y_pos), "SMALL BUSINESS GRANT PROGRAM", font=title_font, fill=white, anchor="mm")
    y_pos += 80
    
    # Separator
    draw.rectangle([(100, y_pos), (width - 100, y_pos + 2)], fill=visa_blue)
    y_pos += 50
    
    # KEY FACTS heading
    draw.text((width // 2, y_pos), "KEY FACTS", font=heading_font, fill=gold, anchor="mm")
    y_pos += 50
    
    # Three fact cards in modern style
    facts = [
        ("$500,000 USD", "Total Global Funding", "💰"),
        ("64 Matches", "Grant Opportunities", "⚽"),
        ("Historic First", "Award Linked to Grant", "🏆")
    ]
    
    card_width = 280
    card_height = 140
    card_spacing = 30
    total_width = (card_width * 3) + (card_spacing * 2)
    start_x = (width - total_width) // 2
    
    for i, (main_text, sub_text, emoji) in enumerate(facts):
        x = start_x + i * (card_width + card_spacing)
        
        # Card background with border
        draw.rectangle(
            [(x, y_pos), (x + card_width, y_pos + card_height)],
            fill=bg_card,
            outline=visa_blue,
            width=3
        )
        
        # Emoji at top
        draw.text((x + card_width // 2, y_pos + 25), emoji, font=heading_font, fill=gold, anchor="mm")
        
        # Main text
        draw.text((x + card_width // 2, y_pos + 70), main_text, 
                 font=heading_font, fill=gold, anchor="mm")
        
        # Sub text
        draw.text((x + card_width // 2, y_pos + 105), sub_text, 
                 font=small_font, fill=light_text, anchor="mm")
    
    y_pos += card_height + 60
    
    # Separator
    draw.rectangle([(100, y_pos), (width - 100, y_pos + 2)], fill=visa_blue)
    y_pos += 40
    
    # HOW IT WORKED section
    draw.text((width // 2, y_pos), "⚙️ HOW IT WORKED", font=heading_font, fill=gold, anchor="mm")
    y_pos += 50
    
    # Content card
    card_x = 70
    card_width = width - 140
    card_y = y_pos
    card_height = 180
    
    draw.rectangle(
        [(card_x, card_y), (card_x + card_width, card_y + card_height)],
        fill=bg_card,
        outline=visa_blue,
        width=3
    )
    
    how_text = [
        "▸ Female small business owners received grants",
        "   after each of the 64 matches",
        "",
        "▸ Grant amounts ranged from $5,000 USD",
        "   (group-stage) to $50,000 USD (Final)",
        "",
        "▸ Grant awarded based on Player of the Match",
        "   winner's country"
    ]
    
    text_y = card_y + 25
    for line in how_text:
        if line:
            draw.text((card_x + 30, text_y), line, font=body_font, fill=white, anchor="lm")
        text_y += 24
    
    y_pos = card_y + card_height + 60
    
    # Separator
    draw.rectangle([(100, y_pos), (width - 100, y_pos + 2)], fill=visa_blue)
    y_pos += 40
    
    # CANADA PARTNERSHIP section
    draw.text((width // 2, y_pos), "🇨🇦 CANADA PARTNERSHIP", font=heading_font, fill=gold, anchor="mm")
    y_pos += 50
    
    # Partnership card
    card_y = y_pos
    card_height = 200
    
    # Add special highlight for Canada section
    draw.rectangle(
        [(card_x, card_y), (card_x + card_width, card_y + card_height)],
        fill=bg_card,
        outline=gold,
        width=3
    )
    
    canada_text = [
        "Canadian Council of Aboriginal Business",
        "(CCAB) Partnership",
        "",
        "▸ Supporting Indigenous women entrepreneurs",
        "",
        "▸ Aligned with She's Next Program mission",
        "",
        "▸ When a Canadian player won Player of the Match,",
        "   funds were granted to the CCAB"
    ]
    
    text_y = card_y + 25
    for line in canada_text:
        if line:
            draw.text((card_x + 30, text_y), line, font=body_font, fill=white, anchor="lm")
        text_y += 22
    
    y_pos = card_y + card_height + 50
    
    # Footer separator
    draw.rectangle([(100, y_pos), (width - 100, y_pos + 2)], fill=visa_blue)
    y_pos += 30
    
    # Footer text
    draw.text((width // 2, y_pos), "FIFA Women's World Cup Australia & New Zealand 2023™", 
             font=small_font, fill=light_text, anchor="mm")
    
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
