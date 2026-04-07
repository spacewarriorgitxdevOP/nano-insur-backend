"""
P1 - Business Logic Layer
Handles claim CRUD operations and status transitions.
"""

import sys
import os
from datetime import datetime
from typing import Optional
from database import Database
from models import (
    ClaimCreateRequest,
    ClaimUpdateRequest,
    ClaimResponse,
    create_claim_document,
)
from config import ClaimStatus, VALID_TRANSITIONS
import logging

logger = logging.getLogger(__name__)

# ─── Import P3's OCR function ─────────────────────────
# P3's ocr.py sits in ../ai/ocr.py - we add it to path
AI_PATH = os.path.join(os.path.dirname(__file__), '..', 'ai')
sys.path.insert(0, AI_PATH)

try:
    from ocr import extract_total
    OCR_AVAILABLE = True
    print("✅ OCR module loaded from P3")
except ImportError:
    OCR_AVAILABLE = False
    print("⚠️  OCR module not available - using fallback")
    def extract_total(image_base64: str) -> Optional[float]:
        """Fallback if P3's OCR isn't ready yet"""
        return None


class ClaimService:
    """Service layer for all claim operations"""

    # ─── CREATE ────────────────────────────────────────

    @staticmethod
    async def create_claim(request: ClaimCreateRequest) -> dict:
        """
        Route 1: POST /claims
        Creates a new claim, optionally runs OCR on document.
        """
        collection = Database.get_collection()
        
        # Build document
        doc = create_claim_document(request)
        
        # If document image provided, run P3's OCR
        if request.document_base64 and OCR_AVAILABLE:
            try:
                extracted = extract_total(request.document_base64)
                if extracted is not None:
                    doc["ocr_extracted_total"] = extracted
                    logger.info(f"OCR extracted total: ${extracted}")
            except Exception as e:
                logger.warning(f"OCR failed, continuing without: {e}")
        
        # Insert into MongoDB
        await collection.insert_one(doc)
        
        # Remove MongoDB _id for response
        doc.pop("_id", None)
        doc.pop("document_base64", None)  # Don't return base64 in response
        
        logger.info(f"✅ Claim created: {doc['claim_id']}")
        return doc

    # ─── READ (GET ALL) ───────────────────────────────

    @staticmethod
    async def get_all_claims(
        status: Optional[str] = None,
        limit: int = 50,
        skip: int = 0
    ) -> dict:
        """
        Route 2: GET /claims
        Returns all claims with optional status filter.
        """
        collection = Database.get_collection()
        
        # Build filter
        query = {}
        if status:
            query["status"] = status
        
        # Get total count
        total = await collection.count_documents(query)
        
        # Fetch claims
        cursor = collection.find(
            query,
            {"_id": 0, "document_base64": 0}  # Exclude heavy fields
        ).sort("created_at", -1).skip(skip).limit(limit)
        
        claims = await cursor.to_list(length=limit)
        
        return {
            "total": total,
            "claims": claims
        }

    # ─── READ (GET ONE) ───────────────────────────────

    @staticmethod
    async def get_claim(claim_id: str) -> Optional[dict]:
        """Get a single claim by ID"""
        collection = Database.get_collection()
        doc = await collection.find_one(
            {"claim_id": claim_id},
            {"_id": 0, "document_base64": 0}
        )
        return doc

    # ─── UPDATE STATUS ─────────────────────────────────

    @staticmethod
    async def update_claim(claim_id: str, request: ClaimUpdateRequest) -> Optional[dict]:
        """
        Route 3: PATCH /claims/{claim_id}
        Updates claim status with validation.
        """
        collection = Database.get_collection()
        
        # Fetch current claim
        current = await collection.find_one({"claim_id": claim_id})
        if not current:
            return None
        
        # Validate status transition
        current_status = current["status"]
        new_status = request.status.value
        
        allowed = VALID_TRANSITIONS.get(current_status, [])
        if new_status not in allowed and new_status != current_status:
            raise ValueError(
                f"Invalid transition: {current_status} → {new_status}. "
                f"Allowed: {allowed}"
            )
        
        # Build update
        now = datetime.utcnow().isoformat() + "Z"
        update_fields = {
            "status": new_status,
            "updated_at": now,
        }
        
        if request.ocr_extracted_total is not None:
            update_fields["ocr_extracted_total"] = request.ocr_extracted_total
        if request.reviewer_notes is not None:
            update_fields["reviewer_notes"] = request.reviewer_notes
        if request.approved_amount is not None:
            update_fields["approved_amount"] = request.approved_amount
        
        # Update in database
        result = await collection.find_one_and_update(
            {"claim_id": claim_id},
            {"$set": update_fields},
            return_document=True
        )
        
        if result:
            result.pop("_id", None)
            result.pop("document_base64", None)
            logger.info(f"✅ Claim {claim_id}: {current_status} → {new_status}")
        
        return result

    # ─── DELETE (optional utility) ─────────────────────

    @staticmethod
    async def delete_claim(claim_id: str) -> bool:
        """Delete a claim (for testing/demo reset)"""
        collection = Database.get_collection()
        result = await collection.delete_one({"claim_id": claim_id})
        return result.deleted_count > 0

    # ─── PROCESS WITH OCR ──────────────────────────────

    @staticmethod
    async def process_claim_ocr(claim_id: str, image_base64: str) -> Optional[dict]:
        """
        Run OCR on a document and update the claim.
        Called when user uploads a receipt/document.
        """
        collection = Database.get_collection()
        
        # Run P3's OCR
        extracted_total = None
        if OCR_AVAILABLE:
            try:
                extracted_total = extract_total(image_base64)
            except Exception as e:
                logger.warning(f"OCR processing failed: {e}")
        
        # Update claim
        now = datetime.utcnow().isoformat() + "Z"
        update = {
            "ocr_extracted_total": extracted_total,
            "status": ClaimStatus.PROCESSING,
            "updated_at": now,
        }
        
        result = await collection.find_one_and_update(
            {"claim_id": claim_id},
            {"$set": update},
            return_document=True
        )
        
        if result:
            result.pop("_id", None)
            result.pop("document_base64", None)
        
        return result