"""
P1 - Pydantic Models for request/response validation
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum
import uuid


class ClaimStatusEnum(str, Enum):
    UNINSURED = "uninsured"
    PROTECTED = "protected"
    CLAIM_SUBMITTED = "claim_submitted"
    PROCESSING = "processing"
    APPROVED = "approved"
    REJECTED = "rejected"


# ─── Request Models ───────────────────────────────────

class ClaimCreateRequest(BaseModel):
    """POST /claims - Create a new claim"""
    user_name: str = Field(..., min_length=1, max_length=100, example="John Doe")
    email: Optional[str] = Field(None, example="john@example.com")
    phone: Optional[str] = Field(None, example="+1234567890")
    description: str = Field(..., min_length=1, max_length=1000, example="Car accident on Highway 101")
    document_base64: Optional[str] = Field(None, description="Base64 encoded document/receipt image")
    amount_claimed: Optional[float] = Field(None, ge=0, example=1500.00)


class ClaimUpdateRequest(BaseModel):
    """PATCH /claims/{claim_id} - Update claim status"""
    status: ClaimStatusEnum
    ocr_extracted_total: Optional[float] = None
    reviewer_notes: Optional[str] = None
    approved_amount: Optional[float] = None


# ─── Response Models ──────────────────────────────────

class ClaimResponse(BaseModel):
    """Standard claim response"""
    claim_id: str
    user_name: str
    email: Optional[str]
    phone: Optional[str]
    description: str
    status: ClaimStatusEnum
    amount_claimed: Optional[float]
    ocr_extracted_total: Optional[float]
    approved_amount: Optional[float]
    reviewer_notes: Optional[str]
    created_at: str
    updated_at: str

    class Config:
        json_schema_extra = {
            "example": {
                "claim_id": "CLM-abc12345",
                "user_name": "John Doe",
                "status": "processing",
                "amount_claimed": 1500.00,
                "ocr_extracted_total": 1487.50,
                "created_at": "2024-01-15T10:30:00Z"
            }
        }


class ClaimListResponse(BaseModel):
    """List of claims response"""
    total: int
    claims: list[ClaimResponse]


# ─── WebSocket Models ─────────────────────────────────

class WSMessage(BaseModel):
    """WebSocket message format"""
    event: str  # "status_update", "new_claim", "heartbeat"
    data: dict
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# ─── Database Document ────────────────────────────────

def create_claim_document(request: ClaimCreateRequest) -> dict:
    """Create a MongoDB document from request"""
    now = datetime.utcnow().isoformat() + "Z"
    return {
        "claim_id": f"CLM-{uuid.uuid4().hex[:8]}",
        "user_name": request.user_name,
        "email": request.email,
        "phone": request.phone,
        "description": request.description,
        "document_base64": request.document_base64,
        "status": ClaimStatusEnum.UNINSURED.value,
        "amount_claimed": request.amount_claimed,
        "ocr_extracted_total": None,
        "approved_amount": None,
        "reviewer_notes": None,
        "created_at": now,
        "updated_at": now,
    }