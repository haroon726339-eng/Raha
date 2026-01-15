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
    come_logo = "https://customer-assets.emergentagent.com/job_cricketapp-5/artifacts/jnjiun6g_IMG_20260115_174805_313.png"
    
    # High quality flag URLs (4K)
    team1_logo = campaign['team1_logo']
    team2_logo = campaign['team2_logo']
    
    # Use high-res flags if using flagcdn
    if 'flagcdn.com/w80' in team1_logo:
        team1_logo = team1_logo.replace('/w80/', '/w320/')
    if 'flagcdn.com/w80' in team2_logo:
        team2_logo = team2_logo.replace('/w80/', '/w320/')
    
    # Celebration confetti GIF
    confetti_gif = "https://i.gifer.com/origin/07/077ed95a694ee43eb0ce4e42c2aea47a_w200.gif"
    celebration_gif = "https://i.gifer.com/7plX.gif"
    
    # Dream11 exact style email template with animations
    html = f'''
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="x-apple-disable-message-reformatting">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <title>You Champion! You're a winner in {campaign['team1_name']} vs {campaign['team2_name']}</title>
</head>
<body style="margin: 0; padding: 0; background-color: #0d0d1a; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%;">
    <!-- Preheader Text -->
    <div style="display: none; max-height: 0px; overflow: hidden;">
        Congratulations {campaign['winner_name']}! You've won ₹{campaign['winning_amount']} in {campaign['team1_name']} vs {campaign['team2_name']} match!
    </div>
    
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color: #0d0d1a;">
        <tr>
            <td align="center" style="padding: 0;">
                <table role="presentation" width="600" cellspacing="0" cellpadding="0" border="0" style="max-width: 600px; width: 100%; background-color: #12122a;">
                    
                    <!-- Red Header Banner with COME Logo - FIXED -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%); padding: 0;">
                            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                                <tr>
                                    <td style="padding: 18px 25px;" valign="middle">
                                        <img src="{come_logo}" alt="COME" width="140" height="50" style="display: block; width: 140px; height: 50px; object-fit: contain;">
                                    </td>
                                    <td align="right" style="padding: 18px 25px;" valign="middle">
                                        <span style="color: #ffffff; font-size: 14px; font-weight: 600;">20 Crore+ users</span>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Main Content Area with Celebration Background -->
                    <tr>
                        <td style="background: linear-gradient(180deg, #1a1a3e 0%, #0f0f2d 100%); position: relative;">
                            <!-- Celebration Animation Background -->
                            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="position: relative;">
                                <tr>
                                    <td style="padding: 0; position: relative;">
                                        <!-- Confetti overlay left -->
                                        <img src="{confetti_gif}" alt="" width="100" style="position: absolute; left: 0; top: 0; opacity: 0.6; pointer-events: none;">
                                        <!-- Confetti overlay right -->
                                        <img src="{confetti_gif}" alt="" width="100" style="position: absolute; right: 0; top: 0; opacity: 0.6; pointer-events: none; transform: scaleX(-1);">
                                    </td>
                                </tr>
                            </table>
                            
                            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="position: relative; z-index: 1;">
                                <tr>
                                    <td style="padding: 35px 25px 20px 25px;">
                                        
                                        <!-- Congratulations Header with Sparkle -->
                                        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                                            <tr>
                                                <td align="center">
                                                    <h1 style="color: #22c55e; font-size: 32px; font-weight: 700; margin: 0 0 25px 0; letter-spacing: 0.5px; text-shadow: 0 0 20px rgba(34, 197, 94, 0.5);">
                                                        Congratulations {campaign['winner_name']},
                                                    </h1>
                                                </td>
                                            </tr>
                                        </table>
                                        
                                        <!-- Trophy Section with COME Logo - FIXED SIZE -->
                                        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                                            <tr>
                                                <td align="center" style="padding: 10px 0 25px 0;">
                                                    <table role="presentation" cellspacing="0" cellpadding="0" border="0">
                                                        <tr>
                                                            <td align="center" valign="middle" style="padding-right: 20px;">
                                                                <img src="https://em-content.zobj.net/source/apple/391/trophy_1f3c6.png" alt="" width="55" height="55" style="display: block; width: 55px; height: 55px;">
                                                            </td>
                                                            <td align="center" valign="middle">
                                                                <!-- COME Logo Circle - PROPERLY FIXED -->
                                                                <table role="presentation" cellspacing="0" cellpadding="0" border="0">
                                                                    <tr>
                                                                        <td style="background: linear-gradient(135deg, #ff0080, #ff8c00, #00ff88, #00bfff); padding: 5px; border-radius: 50%;">
                                                                            <table role="presentation" cellspacing="0" cellpadding="0" border="0">
                                                                                <tr>
                                                                                    <td style="background-color: #12122a; border-radius: 50%; width: 90px; height: 90px; text-align: center; vertical-align: middle;">
                                                                                        <img src="{come_logo}" alt="COME" width="75" height="75" style="display: inline-block; width: 75px; height: 75px; object-fit: contain; border-radius: 50%;">
                                                                                    </td>
                                                                                </tr>
                                                                            </table>
                                                                        </td>
                                                                    </tr>
                                                                </table>
                                                            </td>
                                                            <td align="center" valign="middle" style="padding-left: 20px;">
                                                                <img src="https://em-content.zobj.net/source/apple/391/trophy_1f3c6.png" alt="" width="55" height="55" style="display: block; width: 55px; height: 55px;">
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
                                                    <p style="color: #9ca3af; font-size: 16px; margin: 0;">
                                                        You've won in {campaign['contests_won']} contest(s).
                                                    </p>
                                                </td>
                                            </tr>
                                        </table>
                                        
                                        <!-- Big Winning Amount with Glow Effect -->
                                        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                                            <tr>
                                                <td align="center" style="padding: 15px 0 5px 0;">
                                                    <h2 style="color: #ffffff; font-size: 58px; font-weight: 800; margin: 0; letter-spacing: -1px; text-shadow: 0 0 30px rgba(255,255,255,0.3);">
                                                        ₹{campaign['winning_amount']}
                                                    </h2>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td align="center" style="padding: 5px 0 30px 0;">
                                                    <p style="color: #9ca3af; font-size: 14px; margin: 0;">
                                                        ₹{campaign['winning_amount']} (total winnings after deductions)
                                                    </p>
                                                </td>
                                            </tr>
                                        </table>
                                        
                                        <!-- Match Info with HIGH QUALITY Team Logos -->
                                        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                                            <tr>
                                                <td align="center" style="padding: 15px 0 25px 0;">
                                                    <table role="presentation" cellspacing="0" cellpadding="0" border="0">
                                                        <tr>
                                                            <td align="center" valign="middle" style="padding: 0 15px;">
                                                                <!-- Team 1 Logo - HIGH QUALITY 4K -->
                                                                <table role="presentation" cellspacing="0" cellpadding="0" border="0">
                                                                    <tr>
                                                                        <td style="background-color: #1e1e3f; border-radius: 50%; padding: 4px; border: 3px solid #3b3b5c;">
                                                                            <img src="{team1_logo}" alt="{campaign['team1_name']}" width="65" height="65" style="display: block; width: 65px; height: 65px; border-radius: 50%; object-fit: cover;">
                                                                        </td>
                                                                    </tr>
                                                                </table>
                                                            </td>
                                                            <td align="center" valign="middle" style="padding: 0 20px;">
                                                                <p style="color: #ffffff; font-size: 20px; font-weight: 700; margin: 0 0 5px 0;">
                                                                    {campaign['team1_name']} vs {campaign['team2_name']}
                                                                </p>
                                                                <p style="color: #9ca3af; font-size: 14px; margin: 0;">
                                                                    {campaign['match_date']}
                                                                </p>
                                                            </td>
                                                            <td align="center" valign="middle" style="padding: 0 15px;">
                                                                <!-- Team 2 Logo - HIGH QUALITY 4K -->
                                                                <table role="presentation" cellspacing="0" cellpadding="0" border="0">
                                                                    <tr>
                                                                        <td style="background-color: #1e1e3f; border-radius: 50%; padding: 4px; border: 3px solid #3b3b5c;">
                                                                            <img src="{team2_logo}" alt="{campaign['team2_name']}" width="65" height="65" style="display: block; width: 65px; height: 65px; border-radius: 50%; object-fit: cover;">
                                                                        </td>
                                                                    </tr>
                                                                </table>
                                                            </td>
                                                        </tr>
                                                    </table>
                                                </td>
                                            </tr>
                                        </table>
                                        
                                        <!-- Winning Breakup Table -->
                                        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin-top: 10px;">
                                            <tr>
                                                <td>
                                                    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color: #0a0a1f; border-radius: 12px; overflow: hidden; border: 1px solid #1e1e3f;">
                                                        <!-- Header -->
                                                        <tr>
                                                            <td colspan="3" style="padding: 16px 20px; border-bottom: 1px solid #1e1e3f; background-color: #0f0f25;">
                                                                <p style="color: #ffffff; font-size: 18px; font-weight: 700; margin: 0; text-align: center;">
                                                                    Winning Breakup
                                                                </p>
                                                            </td>
                                                        </tr>
                                                        <!-- Row 1: Prize Pool, Spots, Entry -->
                                                        <tr>
                                                            <td style="padding: 16px 20px; border-bottom: 1px solid #1e1e3f; width: 33%;">
                                                                <p style="color: #6b7280; font-size: 11px; margin: 0 0 5px 0; text-transform: uppercase; letter-spacing: 0.5px;">Prize Pool</p>
                                                                <p style="color: #ffffff; font-size: 17px; font-weight: 700; margin: 0;">₹{campaign['prize_pool']}</p>
                                                            </td>
                                                            <td style="padding: 16px 20px; border-bottom: 1px solid #1e1e3f; text-align: center; width: 34%;">
                                                                <p style="color: #6b7280; font-size: 11px; margin: 0 0 5px 0; text-transform: uppercase; letter-spacing: 0.5px;">Spots</p>
                                                                <p style="color: #ffffff; font-size: 17px; font-weight: 700; margin: 0;">{campaign['spots']}</p>
                                                            </td>
                                                            <td style="padding: 16px 20px; border-bottom: 1px solid #1e1e3f; text-align: right; width: 33%;">
                                                                <p style="color: #6b7280; font-size: 11px; margin: 0 0 5px 0; text-transform: uppercase; letter-spacing: 0.5px;">Entry</p>
                                                                <p style="color: #ffffff; font-size: 17px; font-weight: 700; margin: 0;">₹{campaign['entry_fee']}</p>
                                                            </td>
                                                        </tr>
                                                        <!-- Row 2: Winnings from Team -->
                                                        <tr>
                                                            <td colspan="2" style="padding: 16px 20px; border-bottom: 1px solid #1e1e3f;">
                                                                <p style="color: #9ca3af; font-size: 14px; margin: 0;">Winnings from Team 1</p>
                                                                <p style="color: #6b7280; font-size: 12px; margin: 4px 0 0 0;">(Rank #{campaign['rank']})</p>
                                                            </td>
                                                            <td style="padding: 16px 20px; border-bottom: 1px solid #1e1e3f; text-align: right;">
                                                                <p style="color: #22c55e; font-size: 20px; font-weight: 700; margin: 0;">₹{campaign['winning_amount']}</p>
                                                            </td>
                                                        </tr>
                                                        <!-- Row 3: Total Winnings -->
                                                        <tr>
                                                            <td colspan="2" style="padding: 18px 20px; background-color: #0f0f25;">
                                                                <p style="color: #ffffff; font-size: 17px; font-weight: 700; margin: 0;">Total Winnings</p>
                                                            </td>
                                                            <td style="padding: 18px 20px; text-align: right; background-color: #0f0f25;">
                                                                <p style="color: #22c55e; font-size: 24px; font-weight: 800; margin: 0;">₹{campaign['winning_amount']}</p>
                                                            </td>
                                                        </tr>
                                                    </table>
                                                </td>
                                            </tr>
                                        </table>
                                        
                                        <!-- PLAY NOW Button -->
                                        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin-top: 35px;">
                                            <tr>
                                                <td align="center">
                                                    <a href="#" target="_blank" style="display: inline-block; background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%); color: #000000; font-size: 18px; font-weight: 800; text-decoration: none; padding: 18px 100px; border-radius: 10px; text-transform: uppercase; letter-spacing: 1.5px; box-shadow: 0 4px 20px rgba(34, 197, 94, 0.4);">
                                                        PLAY NOW
                                                    </a>
                                                </td>
                                            </tr>
                                        </table>
                                        
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #080815; padding: 30px 25px; border-top: 1px solid #1e1e3f;">
                            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                                <tr>
                                    <td align="center">
                                        <img src="{come_logo}" alt="COME" width="100" height="36" style="display: block; width: 100px; height: 36px; object-fit: contain; margin-bottom: 15px;">
                                        <p style="color: #6b7280; font-size: 13px; margin: 0 0 8px 0;">
                                            This email was sent by COME Fantasy Sports.
                                        </p>
                                        <p style="color: #4b5563; font-size: 12px; margin: 0;">
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
        # ============ NATIONAL TEAMS - HIGH QUALITY FLAGS ============
        {"name": "India", "short_name": "IND", "logo_url": "https://flagcdn.com/w320/in.png", "category": "team"},
        {"name": "Australia", "short_name": "AUS", "logo_url": "https://flagcdn.com/w320/au.png", "category": "team"},
        {"name": "Pakistan", "short_name": "PAK", "logo_url": "https://flagcdn.com/w320/pk.png", "category": "team"},
        {"name": "England", "short_name": "ENG", "logo_url": "https://flagcdn.com/w320/gb-eng.png", "category": "team"},
        {"name": "South Africa", "short_name": "SA", "logo_url": "https://flagcdn.com/w320/za.png", "category": "team"},
        {"name": "New Zealand", "short_name": "NZ", "logo_url": "https://flagcdn.com/w320/nz.png", "category": "team"},
        {"name": "Sri Lanka", "short_name": "SL", "logo_url": "https://flagcdn.com/w320/lk.png", "category": "team"},
        {"name": "Bangladesh", "short_name": "BAN", "logo_url": "https://flagcdn.com/w320/bd.png", "category": "team"},
        {"name": "West Indies", "short_name": "WI", "logo_url": "https://flagcdn.com/w320/jm.png", "category": "team"},
        {"name": "Afghanistan", "short_name": "AFG", "logo_url": "https://flagcdn.com/w320/af.png", "category": "team"},
        
        # ============ IPL MEN'S TEAMS (10 Teams) ============
        {"name": "Chennai Super Kings", "short_name": "CSK", "logo_url": "https://bcciplayerimages.s3.ap-south-1.amazonaws.com/ipl/CSK/logos/Roundbig/CSKroundbig.png", "category": "ipl"},
        {"name": "Mumbai Indians", "short_name": "MI", "logo_url": "https://bcciplayerimages.s3.ap-south-1.amazonaws.com/ipl/MI/Logos/Roundbig/MIroundbig.png", "category": "ipl"},
        {"name": "Royal Challengers Bengaluru", "short_name": "RCB", "logo_url": "https://bcciplayerimages.s3.ap-south-1.amazonaws.com/ipl/RCB/Logos/Roundbig/RCBroundbig.png", "category": "ipl"},
        {"name": "Kolkata Knight Riders", "short_name": "KKR", "logo_url": "https://bcciplayerimages.s3.ap-south-1.amazonaws.com/ipl/KKR/Logos/Roundbig/KKRroundbig.png", "category": "ipl"},
        {"name": "Delhi Capitals", "short_name": "DC", "logo_url": "https://bcciplayerimages.s3.ap-south-1.amazonaws.com/ipl/DC/Logos/Roundbig/DCroundbig.png", "category": "ipl"},
        {"name": "Punjab Kings", "short_name": "PBKS", "logo_url": "https://bcciplayerimages.s3.ap-south-1.amazonaws.com/ipl/PBKS/Logos/Roundbig/PBKSroundbig.png", "category": "ipl"},
        {"name": "Rajasthan Royals", "short_name": "RR", "logo_url": "https://bcciplayerimages.s3.ap-south-1.amazonaws.com/ipl/RR/Logos/Roundbig/RRroundbig.png", "category": "ipl"},
        {"name": "Sunrisers Hyderabad", "short_name": "SRH", "logo_url": "https://bcciplayerimages.s3.ap-south-1.amazonaws.com/ipl/SRH/Logos/Roundbig/SRHroundbig.png", "category": "ipl"},
        {"name": "Gujarat Titans", "short_name": "GT", "logo_url": "https://bcciplayerimages.s3.ap-south-1.amazonaws.com/ipl/GT/Logos/Roundbig/GTroundbig.png", "category": "ipl"},
        {"name": "Lucknow Super Giants", "short_name": "LSG", "logo_url": "https://bcciplayerimages.s3.ap-south-1.amazonaws.com/ipl/LSG/Logos/Roundbig/LSGroundbig.png", "category": "ipl"},
        
        # ============ WPL WOMEN'S TEAMS (5 Teams) ============
        {"name": "Mumbai Indians Women", "short_name": "MI-W", "logo_url": "https://bcciplayerimages.s3.ap-south-1.amazonaws.com/ipl/MI/Logos/Roundbig/MIroundbig.png", "category": "wpl"},
        {"name": "Delhi Capitals Women", "short_name": "DC-W", "logo_url": "https://bcciplayerimages.s3.ap-south-1.amazonaws.com/ipl/DC/Logos/Roundbig/DCroundbig.png", "category": "wpl"},
        {"name": "Royal Challengers Bengaluru Women", "short_name": "RCB-W", "logo_url": "https://bcciplayerimages.s3.ap-south-1.amazonaws.com/ipl/RCB/Logos/Roundbig/RCBroundbig.png", "category": "wpl"},
        {"name": "Gujarat Giants", "short_name": "GG", "logo_url": "https://www.wplt20.com/static-assets/images/teams/gg-logo.png", "category": "wpl"},
        {"name": "UP Warriorz", "short_name": "UPW", "logo_url": "https://www.wplt20.com/static-assets/images/teams/upw-logo.png", "category": "wpl"},
        
        # ============ BIG BASH LEAGUE TEAMS (8 Teams) ============
        {"name": "Sydney Sixers", "short_name": "SIX", "logo_url": "https://www.bigbash.com.au/-/media/Logos/Teams/BBL/Sixers-Logo.ashx", "category": "bbl"},
        {"name": "Sydney Thunder", "short_name": "THU", "logo_url": "https://www.bigbash.com.au/-/media/Logos/Teams/BBL/Thunder-Logo.ashx", "category": "bbl"},
        {"name": "Melbourne Stars", "short_name": "STA", "logo_url": "https://www.bigbash.com.au/-/media/Logos/Teams/BBL/Stars-Logo.ashx", "category": "bbl"},
        {"name": "Melbourne Renegades", "short_name": "REN", "logo_url": "https://www.bigbash.com.au/-/media/Logos/Teams/BBL/Renegades-Logo.ashx", "category": "bbl"},
        {"name": "Brisbane Heat", "short_name": "HEA", "logo_url": "https://www.bigbash.com.au/-/media/Logos/Teams/BBL/Heat-Logo.ashx", "category": "bbl"},
        {"name": "Adelaide Strikers", "short_name": "STR", "logo_url": "https://www.bigbash.com.au/-/media/Logos/Teams/BBL/Strikers-Logo.ashx", "category": "bbl"},
        {"name": "Perth Scorchers", "short_name": "SCO", "logo_url": "https://www.bigbash.com.au/-/media/Logos/Teams/BBL/Scorchers-Logo.ashx", "category": "bbl"},
        {"name": "Hobart Hurricanes", "short_name": "HUR", "logo_url": "https://www.bigbash.com.au/-/media/Logos/Teams/BBL/Hurricanes-Logo.ashx", "category": "bbl"},
        
        # ============ TOURNAMENTS ============
        {"name": "TATA IPL", "short_name": "IPL", "logo_url": "https://upload.wikimedia.org/wikipedia/en/thumb/8/84/Indian_Premier_League_Official_Logo.svg/800px-Indian_Premier_League_Official_Logo.svg.png", "category": "tournament"},
        {"name": "WPL Women's Premier League", "short_name": "WPL", "logo_url": "https://www.wplt20.com/static-assets/images/wpl-logo.png", "category": "tournament"},
        {"name": "Big Bash League", "short_name": "BBL", "logo_url": "https://www.bigbash.com.au/-/media/Logos/Leagues/BBL-Logo.ashx", "category": "tournament"},
        {"name": "WBBL Women's Big Bash", "short_name": "WBBL", "logo_url": "https://www.bigbash.com.au/-/media/Logos/Leagues/WBBL-Logo.ashx", "category": "tournament"},
        {"name": "ICC World Cup", "short_name": "WC", "logo_url": "https://resources.pulse.icc-cricket.com/ICC/photo/2023/01/12/e4e69cf0-0187-4fc4-8df5-cb47ba3f5d0e/CWC23.png", "category": "tournament"},
        {"name": "Asia Cup", "short_name": "AC", "logo_url": "https://resources.pulse.icc-cricket.com/ICC/photo/2022/08/17/f8762c1b-e82e-4cc8-a47c-aae98c2e0e15/Asia-Cup.png", "category": "tournament"},
        {"name": "T20 World Cup", "short_name": "T20WC", "logo_url": "https://resources.pulse.icc-cricket.com/ICC/photo/2024/01/09/ca46a2d2-04c2-4e06-8cf7-b4f56e40d9e9/T20WC24.png", "category": "tournament"},
        {"name": "Champions Trophy", "short_name": "CT", "logo_url": "https://resources.pulse.icc-cricket.com/ICC/photo/2024/06/04/44c2a6c4-2c5c-4b9f-9bd6-08fd0e2cfbd1/CT25.png", "category": "tournament"},
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
