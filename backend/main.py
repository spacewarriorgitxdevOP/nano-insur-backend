"""
P1 - FastAPI Main Application
3 REST routes + 1 WebSocket endpoint
Deploy target: Railway

Run locally:  uvicorn main:app --reload --port 8000
Deploy:       git push (Railway auto-deploys)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from config import APP_NAME, VERSION, HOST, PORT, ALLOWED_ORIGINS, BASE_URL
from database import Database
from routes.claims import router as claims_router
from routes.websocket import router as ws_router

# ─── Logging ──────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


# ─── Lifespan (startup/shutdown) ──────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    print("=" * 50)
    print(f"🚀 Starting {APP_NAME} v{VERSION}")
    print(f"📡 BASE_URL: {BASE_URL}")
    print("=" * 50)
    
    await Database.connect()
    
    yield
    
    # Shutdown
    await Database.disconnect()
    print("👋 Server shut down gracefully")


# ─── FastAPI App ──────────────────────────────────────

app = FastAPI(
    title=APP_NAME,
    version=VERSION,
    description="Insurance Claim Processing API with real-time WebSocket updates",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ─── CORS Middleware ──────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Register Routes ─────────────────────────────────
# Route 1: POST   /claims
# Route 2: GET    /claims
# Route 3: PATCH  /claims/{claim_id}
app.include_router(claims_router, prefix="/api/v1")

# WebSocket: ws://BASE_URL/ws
app.include_router(ws_router)


# ─── Health Check ─────────────────────────────────────

@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    return {
        "app": APP_NAME,
        "version": VERSION,
        "status": "healthy",
        "base_url": BASE_URL,
        "endpoints": {
            "REST": {
                "create_claim": "POST /api/v1/claims",
                "list_claims": "GET /api/v1/claims",
                "update_claim": "PATCH /api/v1/claims/{claim_id}",
            },
            "WebSocket": "ws://BASE_URL/ws",
            "docs": "/docs",
        }
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check"""
    try:
        # Test DB connection
        collection = Database.get_collection()
        count = await collection.count_documents({})
        db_status = "connected"
    except Exception:
        count = 0
        db_status = "disconnected"
    
    return {
        "status": "healthy",
        "database": db_status,
        "total_claims": count,
    }


# ─── Run Server ──────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=True,
        log_level="info",
        ws_max_size=16 * 1024 * 1024,  # 16MB for base64 images
    )