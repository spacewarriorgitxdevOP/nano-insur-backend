"""
P1 - Configuration Constants
All environment variables and app constants live here.
P1 gives BASE_URL to P2 before T+0.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ─── Server ───────────────────────────────────────────
APP_NAME = "Nano-Insur"
VERSION = "1.0.0"
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# ─── MongoDB Atlas ────────────────────────────────────
# Single collection, no TTL as specified
MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb+srv://Soham:Soham24%40rane@cluster0.yhao69n.mongodb.net/nano_insurance?retryWrites=true&w=majority&appName=Cluster0"
)
DB_NAME = os.getenv("DB_NAME", "insurance_hackathon")
COLLECTION_NAME = "claims"  # 1 collection only

# ─── CORS ─────────────────────────────────────────────
ALLOWED_ORIGINS = [
    "*",  # Hackathon - allow all origins
]

# ─── WebSocket ────────────────────────────────────────
WS_HEARTBEAT_INTERVAL = 30  # seconds

# ─── OCR Service ──────────────────────────────────────
# P3's OCR function will be imported directly
OCR_CONFIDENCE_THRESHOLD = 0.7

# ─── Claim Status Flow ────────────────────────────────
class ClaimStatus:
    UNINSURED = "uninsured"
    PROTECTED = "protected"
    CLAIM_SUBMITTED = "claim_submitted"
    PROCESSING = "processing"
    APPROVED = "approved"
    REJECTED = "rejected"

VALID_TRANSITIONS = {
    ClaimStatus.UNINSURED: [ClaimStatus.PROTECTED],
    ClaimStatus.PROTECTED: [ClaimStatus.CLAIM_SUBMITTED],
    ClaimStatus.CLAIM_SUBMITTED: [ClaimStatus.PROCESSING],
    ClaimStatus.PROCESSING: [ClaimStatus.APPROVED, ClaimStatus.REJECTED],
}

# ─── BASE_URL (Railway will override) ─────────────────
BASE_URL = os.getenv("RAILWAY_PUBLIC_DOMAIN", f"http://localhost:{PORT}")
if not BASE_URL.startswith("http"):
    BASE_URL = f"https://{BASE_URL}"

print(f"[CONFIG] BASE_URL for P2: {BASE_URL}")