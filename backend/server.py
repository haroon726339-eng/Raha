from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import resend
import asyncio
import jwt

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Resend setup
resend.api_key = os.environ.get('RESEND_API_KEY', '')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'onboarding@resend.dev')
JWT_SECRET = os.environ.get('JWT_SECRET', 'come-app-secret-2025')

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")
security = HTTPBearer()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ========== Models ==========
class UserLogin(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    token: str
    username: str

class TeamLogo(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    short_name: str
    logo_url: str
    category: str  # 'team', 'tournament'
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class TeamLogoCreate(BaseModel):
    name: str
    short_name: str
    logo_url: str
    category: str

class EmailCampaign(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    winner_name: str
    winner_email: EmailStr
    winning_amount: str
    contests_won: int = 1
    team1_name: str
    team1_logo: str
    team2_name: str
    team2_logo: str
    match_date: str
    prize_pool: str
    spots: str
    entry_fee: str
    rank: int = 1
    tournament_name: Optional[str] = None
    tournament_logo: Optional[str] = None
    status: str = "draft"  # draft, sent, failed
    sent_at: Optional[str] = None
    email_id: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class EmailCampaignCreate(BaseModel):
    winner_name: str
    winner_email: EmailStr
    winning_amount: str
    contests_won: int = 1
    team1_name: str
    team1_logo: str
    team2_name: str
    team2_logo: str
    match_date: str
    prize_pool: str
    spots: str
    entry_fee: str
    rank: int = 1
    tournament_name: Optional[str] = None
    tournament_logo: Optional[str] = None

class SendEmailRequest(BaseModel):
    campaign_id: str

# ========== Auth Helpers ==========
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Hardcoded users for simplicity (like reference site)
USERS = {
    "aryan": "726339",
    "admin": "admin123"
}

# ========== Email Template Generator ==========
def generate_email_html(campaign: dict) -> str:
    come_logo = "https://customer-assets.emergentagent.com/job_cricketapp-5/artifacts/1fb8tcpa_IMG_20260115_162945_452.png"
    
    html = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Congratulations {campaign['winner_name']}!</title>
</head>
<body style="margin: 0; padding: 0; background-color: #111111; font-family: Arial, sans-serif;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color: #111111;">
        <tr>
            <td align="center" style="padding: 20px 0;">
                <table role="presentation" width="600" cellspacing="0" cellpadding="0" border="0" style="max-width: 600px; width: 100%; background-color: #1a1a1a; border-radius: 12px; overflow: hidden;">
                    
                    <!-- Header with COME Logo -->
                    <tr>
                        <td style="background: linear-gradient(90deg, #FF0080, #00FF88); padding: 3px;">
                            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color: #1a1a1a;">
                                <tr>
                                    <td align="center" style="padding: 20px;">
                                        <img src="{come_logo}" alt="COME" width="150" style="max-width: 150px; height: auto;">
                                        <p style="color: #A1A1AA; margin: 10px 0 0; font-size: 14px;">20 Crore+ Users</p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Congratulations Section -->
                    <tr>
                        <td align="center" style="padding: 30px 20px;">
                            <h1 style="color: #00FF88; font-size: 28px; margin: 0 0 10px; font-weight: 700;">
                                Congratulations {campaign['winner_name']},
                            </h1>
                            
                            <!-- Trophy Icon -->
                            <div style="margin: 20px 0;">
                                <table role="presentation" cellspacing="0" cellpadding="0" border="0" style="margin: 0 auto;">
                                    <tr>
                                        <td style="font-size: 40px;">🏆</td>
                                        <td style="padding: 0 15px;">
                                            <div style="width: 80px; height: 80px; border-radius: 50%; background: linear-gradient(135deg, #FF0080, #FF8C00, #00FF88); display: flex; align-items: center; justify-content: center;">
                                                <img src="{come_logo}" alt="COME" width="60" style="border-radius: 50%;">
                                            </div>
                                        </td>
                                        <td style="font-size: 40px;">🏆</td>
                                    </tr>
                                </table>
                            </div>
                            
                            <p style="color: #A1A1AA; font-size: 16px; margin: 20px 0 10px;">
                                You've won in {campaign['contests_won']} contest(s).
                            </p>
                            
                            <!-- Winning Amount -->
                            <h2 style="color: #FFFFFF; font-size: 48px; margin: 0; font-weight: 700;">
                                ₹{campaign['winning_amount']}
                            </h2>
                            <p style="color: #A1A1AA; font-size: 14px; margin: 5px 0 0;">
                                ₹{campaign['winning_amount']} (total winnings after deductions)
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Match Info -->
                    <tr>
                        <td align="center" style="padding: 20px;">
                            <table role="presentation" cellspacing="0" cellpadding="0" border="0" style="margin: 0 auto;">
                                <tr>
                                    <td align="center" style="padding: 0 15px;">
                                        <img src="{campaign['team1_logo']}" alt="{campaign['team1_name']}" width="50" height="50" style="border-radius: 50%; border: 2px solid #333; object-fit: cover;">
                                    </td>
                                    <td style="padding: 0 15px;">
                                        <p style="color: #FFFFFF; font-size: 18px; margin: 0; font-weight: 600;">
                                            {campaign['team1_name']} vs {campaign['team2_name']}
                                        </p>
                                        <p style="color: #A1A1AA; font-size: 14px; margin: 5px 0 0;">
                                            {campaign['match_date']}
                                        </p>
                                    </td>
                                    <td align="center" style="padding: 0 15px;">
                                        <img src="{campaign['team2_logo']}" alt="{campaign['team2_name']}" width="50" height="50" style="border-radius: 50%; border: 2px solid #333; object-fit: cover;">
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Winning Breakup -->
                    <tr>
                        <td style="padding: 20px;">
                            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color: #252525; border-radius: 8px; overflow: hidden;">
                                <tr>
                                    <td colspan="3" style="padding: 15px; border-bottom: 1px solid #333;">
                                        <p style="color: #FFFFFF; font-size: 18px; margin: 0; font-weight: 700; text-align: center;">
                                            Winning Breakup
                                        </p>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 12px 15px; border-bottom: 1px solid #333;">
                                        <p style="color: #A1A1AA; font-size: 12px; margin: 0;">Prize Pool</p>
                                        <p style="color: #FFFFFF; font-size: 16px; margin: 5px 0 0; font-weight: 600;">₹{campaign['prize_pool']}</p>
                                    </td>
                                    <td style="padding: 12px 15px; border-bottom: 1px solid #333; text-align: center;">
                                        <p style="color: #A1A1AA; font-size: 12px; margin: 0;">Spots</p>
                                        <p style="color: #FFFFFF; font-size: 16px; margin: 5px 0 0; font-weight: 600;">{campaign['spots']}</p>
                                    </td>
                                    <td style="padding: 12px 15px; border-bottom: 1px solid #333; text-align: right;">
                                        <p style="color: #A1A1AA; font-size: 12px; margin: 0;">Entry</p>
                                        <p style="color: #FFFFFF; font-size: 16px; margin: 5px 0 0; font-weight: 600;">₹{campaign['entry_fee']}</p>
                                    </td>
                                </tr>
                                <tr>
                                    <td colspan="2" style="padding: 12px 15px; border-bottom: 1px solid #333;">
                                        <p style="color: #A1A1AA; font-size: 12px; margin: 0;">Winnings from Team 1</p>
                                        <p style="color: #A1A1AA; font-size: 12px; margin: 2px 0 0;">(Rank #{campaign['rank']})</p>
                                    </td>
                                    <td style="padding: 12px 15px; border-bottom: 1px solid #333; text-align: right;">
                                        <p style="color: #00FF88; font-size: 18px; margin: 0; font-weight: 700;">₹{campaign['winning_amount']}</p>
                                    </td>
                                </tr>
                                <tr>
                                    <td colspan="2" style="padding: 15px;">
                                        <p style="color: #FFFFFF; font-size: 16px; margin: 0; font-weight: 700;">Total Winnings</p>
                                    </td>
                                    <td style="padding: 15px; text-align: right;">
                                        <p style="color: #00FF88; font-size: 20px; margin: 0; font-weight: 700;">₹{campaign['winning_amount']}</p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- CTA Button -->
                    <tr>
                        <td align="center" style="padding: 20px;">
                            <a href="#" style="display: inline-block; background-color: #00FF88; color: #000000; font-size: 18px; font-weight: 700; text-decoration: none; padding: 15px 60px; border-radius: 8px; text-transform: uppercase;">
                                PLAY NOW
                            </a>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="padding: 20px; border-top: 1px solid #333;">
                            <p style="color: #A1A1AA; font-size: 12px; margin: 0; text-align: center;">
                                This email was sent by COME App.<br>
                                © 2025 COME. All rights reserved.
                            </p>
                        </td>
                    </tr>
                    
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
'''
    return html

# ========== Auth Routes ==========
@api_router.post("/auth/login", response_model=TokenResponse)
async def login(data: UserLogin):
    if data.username in USERS and USERS[data.username] == data.password:
        token = jwt.encode(
            {"username": data.username, "exp": datetime.now(timezone.utc).timestamp() + 86400},
            JWT_SECRET,
            algorithm="HS256"
        )
        return TokenResponse(token=token, username=data.username)
    raise HTTPException(status_code=401, detail="Invalid credentials")

@api_router.get("/auth/me")
async def get_me(payload: dict = Depends(verify_token)):
    return {"username": payload.get("username")}

# ========== Logo Management Routes ==========
@api_router.post("/logos", response_model=TeamLogo)
async def create_logo(data: TeamLogoCreate, payload: dict = Depends(verify_token)):
    logo = TeamLogo(**data.model_dump())
    await db.logos.insert_one(logo.model_dump())
    return logo

@api_router.get("/logos", response_model=List[TeamLogo])
async def get_logos(category: Optional[str] = None, payload: dict = Depends(verify_token)):
    query = {} if not category else {"category": category}
    logos = await db.logos.find(query, {"_id": 0}).to_list(100)
    return logos

@api_router.delete("/logos/{logo_id}")
async def delete_logo(logo_id: str, payload: dict = Depends(verify_token)):
    result = await db.logos.delete_one({"id": logo_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Logo not found")
    return {"message": "Logo deleted"}

# ========== Campaign Routes ==========
@api_router.post("/campaigns", response_model=EmailCampaign)
async def create_campaign(data: EmailCampaignCreate, payload: dict = Depends(verify_token)):
    campaign = EmailCampaign(**data.model_dump())
    await db.campaigns.insert_one(campaign.model_dump())
    return campaign

@api_router.get("/campaigns", response_model=List[EmailCampaign])
async def get_campaigns(payload: dict = Depends(verify_token)):
    campaigns = await db.campaigns.find({}, {"_id": 0}).sort("created_at", -1).to_list(100)
    return campaigns

@api_router.get("/campaigns/{campaign_id}", response_model=EmailCampaign)
async def get_campaign(campaign_id: str, payload: dict = Depends(verify_token)):
    campaign = await db.campaigns.find_one({"id": campaign_id}, {"_id": 0})
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign

@api_router.delete("/campaigns/{campaign_id}")
async def delete_campaign(campaign_id: str, payload: dict = Depends(verify_token)):
    result = await db.campaigns.delete_one({"id": campaign_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return {"message": "Campaign deleted"}

# ========== Email Sending ==========
@api_router.post("/campaigns/{campaign_id}/send")
async def send_campaign_email(campaign_id: str, payload: dict = Depends(verify_token)):
    campaign = await db.campaigns.find_one({"id": campaign_id}, {"_id": 0})
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    html_content = generate_email_html(campaign)
    
    params = {
        "from": SENDER_EMAIL,
        "to": [campaign['winner_email']],
        "subject": f"🏆 You Champion! You're a winner in {campaign['team1_name']} vs {campaign['team2_name']}",
        "html": html_content
    }
    
    try:
        email = await asyncio.to_thread(resend.Emails.send, params)
        
        # Update campaign status
        await db.campaigns.update_one(
            {"id": campaign_id},
            {"$set": {
                "status": "sent",
                "sent_at": datetime.now(timezone.utc).isoformat(),
                "email_id": email.get("id")
            }}
        )
        
        return {
            "status": "success",
            "message": f"Email sent to {campaign['winner_email']}",
            "email_id": email.get("id")
        }
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        await db.campaigns.update_one(
            {"id": campaign_id},
            {"$set": {"status": "failed"}}
        )
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

@api_router.post("/campaigns/{campaign_id}/preview")
async def preview_campaign_email(campaign_id: str, payload: dict = Depends(verify_token)):
    campaign = await db.campaigns.find_one({"id": campaign_id}, {"_id": 0})
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    html_content = generate_email_html(campaign)
    return {"html": html_content}

# ========== Stats ==========
@api_router.get("/stats")
async def get_stats(payload: dict = Depends(verify_token)):
    total_campaigns = await db.campaigns.count_documents({})
    sent_campaigns = await db.campaigns.count_documents({"status": "sent"})
    draft_campaigns = await db.campaigns.count_documents({"status": "draft"})
    failed_campaigns = await db.campaigns.count_documents({"status": "failed"})
    total_logos = await db.logos.count_documents({})
    
    return {
        "total_campaigns": total_campaigns,
        "sent_campaigns": sent_campaigns,
        "draft_campaigns": draft_campaigns,
        "failed_campaigns": failed_campaigns,
        "total_logos": total_logos
    }

# ========== Default Logos Seed ==========
@api_router.post("/seed-logos")
async def seed_default_logos(payload: dict = Depends(verify_token)):
    default_logos = [
        {"name": "India", "short_name": "IND", "logo_url": "https://flagcdn.com/w80/in.png", "category": "team"},
        {"name": "Australia", "short_name": "AUS", "logo_url": "https://flagcdn.com/w80/au.png", "category": "team"},
        {"name": "Pakistan", "short_name": "PAK", "logo_url": "https://flagcdn.com/w80/pk.png", "category": "team"},
        {"name": "England", "short_name": "ENG", "logo_url": "https://flagcdn.com/w80/gb-eng.png", "category": "team"},
        {"name": "South Africa", "short_name": "SA", "logo_url": "https://flagcdn.com/w80/za.png", "category": "team"},
        {"name": "New Zealand", "short_name": "NZ", "logo_url": "https://flagcdn.com/w80/nz.png", "category": "team"},
        {"name": "Sri Lanka", "short_name": "SL", "logo_url": "https://flagcdn.com/w80/lk.png", "category": "team"},
        {"name": "Bangladesh", "short_name": "BAN", "logo_url": "https://flagcdn.com/w80/bd.png", "category": "team"},
        {"name": "West Indies", "short_name": "WI", "logo_url": "https://flagcdn.com/w80/jm.png", "category": "team"},
        {"name": "Afghanistan", "short_name": "AFG", "logo_url": "https://flagcdn.com/w80/af.png", "category": "team"},
        {"name": "IPL", "short_name": "IPL", "logo_url": "https://images.unsplash.com/photo-1531415074968-036ba1b575da?w=100&h=100&fit=crop", "category": "tournament"},
        {"name": "World Cup", "short_name": "WC", "logo_url": "https://images.unsplash.com/photo-1540747913346-19e32dc3e97e?w=100&h=100&fit=crop", "category": "tournament"},
        {"name": "Asia Cup", "short_name": "AC", "logo_url": "https://images.unsplash.com/photo-1624526267942-ab0ff8a3e972?w=100&h=100&fit=crop", "category": "tournament"},
    ]
    
    inserted = 0
    for logo_data in default_logos:
        existing = await db.logos.find_one({"name": logo_data["name"]})
        if not existing:
            logo = TeamLogo(**logo_data)
            await db.logos.insert_one(logo.model_dump())
            inserted += 1
    
    return {"message": f"Seeded {inserted} logos"}

# ========== Root ==========
@api_router.get("/")
async def root():
    return {"message": "COME Email Campaign API"}

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
