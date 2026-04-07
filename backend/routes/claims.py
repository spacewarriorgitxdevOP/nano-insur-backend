"""
P1 - REST API Routes (3 routes as specified)
Route 1: POST   /claims          - Create claim
Route 2: GET    /claims          - List claims  
Route 3: PATCH  /claims/{id}     - Update claim status
"""

from fastapi import APIRouter, HTTPException, Query, File, UploadFile
from typing import Optional
import base64
from models import (
    ClaimCreateRequest,
    ClaimUpdateRequest,
    ClaimResponse,
    ClaimListResponse,
)
from services.claim_service import ClaimService
from routes.websocket import manager  # WebSocket manager for broadcasting

router = APIRouter(prefix="/claims", tags=["Claims"])


# ─── Route 1: POST /claims ────────────────────────────

@router.post("", response_model=ClaimResponse, status_code=201)
async def create_claim(request: ClaimCreateRequest):
    """
    Create a new insurance claim.
    Optionally processes document with OCR (P3's module).
    Broadcasts new claim event via WebSocket.
    """
    try:
        claim = await ClaimService.create_claim(request)
        
        # Broadcast to all connected WebSocket clients (P2's mobile app)
        await manager.broadcast({
            "event": "new_claim",
            "data": claim
        })
        
        return claim
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Route 2: GET /claims ─────────────────────────────

@router.get("", response_model=ClaimListResponse)
async def list_claims(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100),
    skip: int = Query(0, ge=0),
):
    """
    List all claims with optional status filter.
    Supports pagination.
    """
    try:
        result = await ClaimService.get_all_claims(
            status=status,
            limit=limit,
            skip=skip
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Route 2b: GET /claims/{claim_id} ─────────────────

@router.get("/{claim_id}", response_model=ClaimResponse)
async def get_claim(claim_id: str):
    """Get a specific claim by ID."""
    claim = await ClaimService.get_claim(claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail=f"Claim {claim_id} not found")
    return claim


# ─── Route 3: PATCH /claims/{claim_id} ────────────────

@router.patch("/{claim_id}", response_model=ClaimResponse)
async def update_claim(claim_id: str, request: ClaimUpdateRequest):
    """
    Update claim status.
    Validates status transitions.
    Broadcasts status change via WebSocket.
    """
    try:
        claim = await ClaimService.update_claim(claim_id, request)
        if not claim:
            raise HTTPException(status_code=404, detail=f"Claim {claim_id} not found")
        
        # Broadcast status update to all connected clients
        await manager.broadcast({
            "event": "status_update",
            "data": {
                "claim_id": claim_id,
                "new_status": request.status.value,
                "claim": claim
            }
        })
        
        return claim
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Bonus: OCR Processing endpoint ───────────────────

@router.post("/{claim_id}/ocr")
async def process_ocr(claim_id: str, body: dict):
    """
    Upload a document image for OCR processing.
    Uses P3's extract_total() function.
    """
    image_base64 = body.get("image_base64")
    if not image_base64:
        raise HTTPException(status_code=400, detail="image_base64 required")
    
    result = await ClaimService.process_claim_ocr(claim_id, image_base64)
    if not result:
        raise HTTPException(status_code=404, detail=f"Claim {claim_id} not found")
    
    # Broadcast OCR result
    await manager.broadcast({
        "event": "ocr_complete",
        "data": {
            "claim_id": claim_id,
            "ocr_extracted_total": result.get("ocr_extracted_total"),
            "claim": result
        }
    })
    
    return result


# ─── Utility: Delete claim (demo reset) ───────────────

@router.delete("/{claim_id}", status_code=204)
async def delete_claim(claim_id: str):
    """Delete a claim (for demo/testing reset)."""
    deleted = await ClaimService.delete_claim(claim_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Claim {claim_id} not found")
    return None


# ─── NEW: Upload hospital bill ────────────────────────

@router.post("/{claim_id}/upload-bill")
async def upload_hospital_bill(claim_id: str, file: UploadFile = File(...)):
    """
    Upload hospital bill document (PDF/JPG/PNG).
    Automatically triggers OCR processing.
    """
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/jpg", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file type. Allowed: JPG, PNG, PDF"
        )
    
    # Read and encode file
    contents = await file.read()
    file_base64 = base64.b64encode(contents).decode('utf-8')
    
    # Process with OCR
    result = await ClaimService.process_claim_ocr(claim_id, file_base64)
    if not result:
        raise HTTPException(status_code=404, detail=f"Claim {claim_id} not found")
    
    # Broadcast OCR result
    await manager.broadcast({
        "event": "bill_uploaded",
        "data": {
            "claim_id": claim_id,
            "filename": file.filename,
            "ocr_extracted_total": result.get("ocr_extracted_total"),
            "claim": result
        }
    })
    
    return {
        "message": "Hospital bill uploaded successfully",
        "filename": file.filename,
        "ocr_extracted_total": result.get("ocr_extracted_total"),
        "claim": result
    }