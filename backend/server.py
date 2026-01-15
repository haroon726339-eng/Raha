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
    
    # Dream11 exact style email template
    html = f'''
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="x-apple-disable-message-reformatting">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <title>You Champion! You're a winner in {campaign['team1_name']} vs {campaign['team2_name']}</title>
    <!--[if mso]>
    <style type="text/css">
    body, table, td {{font-family: Arial, Helvetica, sans-serif !important;}}
    </style>
    <![endif]-->
</head>
<body style="margin: 0; padding: 0; background-color: #1a1a2e; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%;">
    <!-- Preheader Text -->
    <div style="display: none; max-height: 0px; overflow: hidden;">
        🏆 Congratulations {campaign['winner_name']}! You've won ₹{campaign['winning_amount']} in {campaign['team1_name']} vs {campaign['team2_name']} match!
    </div>
    
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color: #1a1a2e;">
        <tr>
            <td align="center" style="padding: 0;">
                <table role="presentation" width="600" cellspacing="0" cellpadding="0" border="0" style="max-width: 600px; width: 100%; background-color: #16213e;">
                    
                    <!-- Red Header Banner with COME Logo -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #e94560 0%, #c62a47 100%); padding: 0;">
                            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                                <tr>
                                    <td style="padding: 15px 20px;">
                                        <table role="presentation" cellspacing="0" cellpadding="0" border="0">
                                            <tr>
                                                <td>
                                                    <img src="{come_logo}" alt="COME" width="120" height="45" style="display: block; max-width: 120px; height: auto;">
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                    <td align="right" style="padding: 15px 20px;">
                                        <span style="color: #ffffff; font-size: 13px; font-weight: 500;">20 Crore+ users</span>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Main Content Area -->
                    <tr>
                        <td style="background-color: #1a1a2e; padding: 30px 20px;">
                            
                            <!-- Congratulations Header -->
                            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                                <tr>
                                    <td align="center">
                                        <h1 style="color: #4ade80; font-size: 26px; font-weight: 700; margin: 0 0 20px 0; letter-spacing: 0.5px;">
                                            Congratulations {campaign['winner_name']},
                                        </h1>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Trophy Section with Logo -->
                            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                                <tr>
                                    <td align="center" style="padding: 10px 0 20px 0;">
                                        <table role="presentation" cellspacing="0" cellpadding="0" border="0">
                                            <tr>
                                                <td style="padding-right: 15px;">
                                                    <img src="https://em-content.zobj.net/source/apple/391/trophy_1f3c6.png" alt="🏆" width="50" height="50" style="display: block;">
                                                </td>
                                                <td>
                                                    <div style="width: 90px; height: 90px; border-radius: 50%; background: linear-gradient(135deg, #e94560, #ff6b6b, #4ade80); padding: 4px;">
                                                        <div style="width: 82px; height: 82px; border-radius: 50%; background-color: #1a1a2e; display: flex; align-items: center; justify-content: center; overflow: hidden;">
                                                            <img src="{come_logo}" alt="COME" width="70" height="70" style="display: block; object-fit: contain;">
                                                        </div>
                                                    </div>
                                                </td>
                                                <td style="padding-left: 15px;">
                                                    <img src="https://em-content.zobj.net/source/apple/391/trophy_1f3c6.png" alt="🏆" width="50" height="50" style="display: block;">
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Contest Win Message -->
                            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                                <tr>
                                    <td align="center" style="padding: 10px 0;">
                                        <p style="color: #9ca3af; font-size: 15px; margin: 0;">
                                            You've won in {campaign['contests_won']} contest(s).
                                        </p>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Big Winning Amount -->
                            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                                <tr>
                                    <td align="center" style="padding: 15px 0 5px 0;">
                                        <h2 style="color: #ffffff; font-size: 52px; font-weight: 800; margin: 0; letter-spacing: -1px;">
                                            ₹{campaign['winning_amount']}
                                        </h2>
                                    </td>
                                </tr>
                                <tr>
                                    <td align="center" style="padding: 5px 0 25px 0;">
                                        <p style="color: #9ca3af; font-size: 13px; margin: 0;">
                                            ₹{campaign['winning_amount']} (total winnings after deductions)
                                        </p>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Match Info with Team Logos -->
                            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                                <tr>
                                    <td align="center" style="padding: 15px 0;">
                                        <table role="presentation" cellspacing="0" cellpadding="0" border="0">
                                            <tr>
                                                <td align="center" style="padding: 0 12px;">
                                                    <div style="width: 55px; height: 55px; border-radius: 50%; background-color: #374151; overflow: hidden; border: 2px solid #4b5563;">
                                                        <img src="{campaign['team1_logo']}" alt="{campaign['team1_name']}" width="55" height="55" style="display: block; object-fit: cover;">
                                                    </div>
                                                </td>
                                                <td align="center" style="padding: 0 15px;">
                                                    <p style="color: #ffffff; font-size: 17px; font-weight: 600; margin: 0 0 4px 0;">
                                                        {campaign['team1_name']} vs {campaign['team2_name']}
                                                    </p>
                                                    <p style="color: #9ca3af; font-size: 13px; margin: 0;">
                                                        {campaign['match_date']}
                                                    </p>
                                                </td>
                                                <td align="center" style="padding: 0 12px;">
                                                    <div style="width: 55px; height: 55px; border-radius: 50%; background-color: #374151; overflow: hidden; border: 2px solid #4b5563;">
                                                        <img src="{campaign['team2_logo']}" alt="{campaign['team2_name']}" width="55" height="55" style="display: block; object-fit: cover;">
                                                    </div>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Winning Breakup Table -->
                            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin-top: 25px;">
                                <tr>
                                    <td>
                                        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color: #0f172a; border-radius: 10px; overflow: hidden;">
                                            <!-- Header -->
                                            <tr>
                                                <td colspan="3" style="padding: 14px 16px; border-bottom: 1px solid #1e293b;">
                                                    <p style="color: #ffffff; font-size: 16px; font-weight: 700; margin: 0; text-align: center;">
                                                        Winning Breakup
                                                    </p>
                                                </td>
                                            </tr>
                                            <!-- Row 1: Prize Pool, Spots, Entry -->
                                            <tr>
                                                <td style="padding: 14px 16px; border-bottom: 1px solid #1e293b; width: 33%;">
                                                    <p style="color: #9ca3af; font-size: 11px; margin: 0 0 4px 0; text-transform: uppercase;">Prize Pool</p>
                                                    <p style="color: #ffffff; font-size: 15px; font-weight: 600; margin: 0;">₹{campaign['prize_pool']}</p>
                                                </td>
                                                <td style="padding: 14px 16px; border-bottom: 1px solid #1e293b; text-align: center; width: 34%;">
                                                    <p style="color: #9ca3af; font-size: 11px; margin: 0 0 4px 0; text-transform: uppercase;">Spots</p>
                                                    <p style="color: #ffffff; font-size: 15px; font-weight: 600; margin: 0;">{campaign['spots']}</p>
                                                </td>
                                                <td style="padding: 14px 16px; border-bottom: 1px solid #1e293b; text-align: right; width: 33%;">
                                                    <p style="color: #9ca3af; font-size: 11px; margin: 0 0 4px 0; text-transform: uppercase;">Entry</p>
                                                    <p style="color: #ffffff; font-size: 15px; font-weight: 600; margin: 0;">₹{campaign['entry_fee']}</p>
                                                </td>
                                            </tr>
                                            <!-- Row 2: Winnings from Team -->
                                            <tr>
                                                <td colspan="2" style="padding: 14px 16px; border-bottom: 1px solid #1e293b;">
                                                    <p style="color: #9ca3af; font-size: 12px; margin: 0;">Winnings from Team 1</p>
                                                    <p style="color: #6b7280; font-size: 11px; margin: 3px 0 0 0;">(Rank #{campaign['rank']})</p>
                                                </td>
                                                <td style="padding: 14px 16px; border-bottom: 1px solid #1e293b; text-align: right;">
                                                    <p style="color: #4ade80; font-size: 17px; font-weight: 700; margin: 0;">₹{campaign['winning_amount']}</p>
                                                </td>
                                            </tr>
                                            <!-- Row 3: Total Winnings -->
                                            <tr>
                                                <td colspan="2" style="padding: 16px;">
                                                    <p style="color: #ffffff; font-size: 15px; font-weight: 700; margin: 0;">Total Winnings</p>
                                                </td>
                                                <td style="padding: 16px; text-align: right;">
                                                    <p style="color: #4ade80; font-size: 20px; font-weight: 800; margin: 0;">₹{campaign['winning_amount']}</p>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- PLAY NOW Button -->
                            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin-top: 30px;">
                                <tr>
                                    <td align="center">
                                        <a href="#" target="_blank" style="display: inline-block; background-color: #22c55e; color: #000000; font-size: 16px; font-weight: 800; text-decoration: none; padding: 16px 80px; border-radius: 8px; text-transform: uppercase; letter-spacing: 1px;">
                                            PLAY NOW
                                        </a>
                                    </td>
                                </tr>
                            </table>
                            
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #0f172a; padding: 25px 20px; border-top: 1px solid #1e293b;">
                            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                                <tr>
                                    <td align="center">
                                        <img src="{come_logo}" alt="COME" width="80" height="30" style="display: block; margin-bottom: 15px;">
                                        <p style="color: #6b7280; font-size: 12px; margin: 0 0 8px 0;">
                                            This email was sent by COME Fantasy Sports.
                                        </p>
                                        <p style="color: #6b7280; font-size: 11px; margin: 0;">
                                            © 2025 COME. All rights reserved.
                                        </p>
                                    </td>
                                </tr>
                            </table>
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
        # National Teams
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
        # Tournaments - Using placeholder colors for reliable loading
        {"name": "IPL Men's", "short_name": "IPL-M", "logo_url": "https://placehold.co/80x80/1e40af/ffffff?text=IPL", "category": "tournament"},
        {"name": "IPL Women's", "short_name": "IPL-W", "logo_url": "https://placehold.co/80x80/be185d/ffffff?text=WIPL", "category": "tournament"},
        {"name": "Big Bash Men's", "short_name": "BBL-M", "logo_url": "https://placehold.co/80x80/15803d/ffffff?text=BBL", "category": "tournament"},
        {"name": "Big Bash Women's", "short_name": "BBL-W", "logo_url": "https://placehold.co/80x80/7c3aed/ffffff?text=WBBL", "category": "tournament"},
        {"name": "World Cup", "short_name": "WC", "logo_url": "https://placehold.co/80x80/0369a1/ffffff?text=WC", "category": "tournament"},
        {"name": "Asia Cup", "short_name": "AC", "logo_url": "https://placehold.co/80x80/c2410c/ffffff?text=AC", "category": "tournament"},
        {"name": "T20 World Cup", "short_name": "T20WC", "logo_url": "https://placehold.co/80x80/4338ca/ffffff?text=T20", "category": "tournament"},
        {"name": "Champions Trophy", "short_name": "CT", "logo_url": "https://placehold.co/80x80/b45309/ffffff?text=CT", "category": "tournament"},
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
