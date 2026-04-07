"""
Nano-Insur - Configuration Constants
All environment variables and app constants live here.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ─── Server ───────────────────────────────────────────
APP_NAME = "Nano-Insur"
VERSION = "1.0.0"
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8001))  # ✅ Fixed to 8001
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# ─── MongoDB Atlas ────────────────────────────────────
MONGO_URI = os.getenv(
    "MONGO_URI",
    os.getenv("MONGO_URL", "mongodb://localhost:27017/nano_insurance")
)
DB_NAME = os.getenv("DB_NAME", "nano_insurance")
COLLECTION_NAME = "claims"

# ─── CORS ─────────────────────────────────────────────
ALLOWED_ORIGINS = [
    "*",  # Allow all origins for development
]

# ─── WebSocket ────────────────────────────────────────
WS_HEARTBEAT_INTERVAL = 30  # seconds

# ─── OCR Service ──────────────────────────────────────
OCR_CONFIDENCE_THRESHOLD = 0.7
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

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

# ─── Coverage Timer (24 hours) ────────────────────────
COVERAGE_DURATION_HOURS = 24

# ─── BASE_URL ─────────────────────────────────────────
BASE_URL = os.getenv("BASE_URL", f"http://localhost:{PORT}")
if not BASE_URL.startswith("http"):
    BASE_URL = f"https://{BASE_URL}"

print(f"[CONFIG] Nano-Insur API: {BASE_URL}")
print(f"[CONFIG] Port: {PORT}")
print(f"[CONFIG] MongoDB: {DB_NAME}")
