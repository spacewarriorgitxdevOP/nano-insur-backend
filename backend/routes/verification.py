"""Verification endpoints for doctor ID and hospital GSTIN"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from utils.validators import validate_doctor_id, validate_gstin

router = APIRouter(prefix="/verify", tags=["Verification"])

class DoctorVerifyRequest(BaseModel):
    doctor_id: str
    doctor_name: str
    state_code: str = None

class GSTINVerifyRequest(BaseModel):
    gstin: str
    hospital_name: str

@router.post("/doctor")
async def verify_doctor(request: DoctorVerifyRequest):
    """Verify Indian Medical Council doctor ID"""
    result = validate_doctor_id(request.doctor_id, request.state_code)
    
    if not result["valid"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {
        "verified": True,
        "doctor_name": request.doctor_name,
        "doctor_id": result["formatted_id"],
        "state": result["state"],
        "registration_year": result["year"],
        "message": "Doctor ID format valid"
    }

@router.post("/gstin")
async def verify_gstin(request: GSTINVerifyRequest):
    """Verify hospital GSTIN"""
    result = validate_gstin(request.gstin)
    
    if not result["valid"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {
        "verified": True,
        "hospital_name": request.hospital_name,
        "gstin": result["gstin"],
        "state_code": result["state_code"],
        "pan": result["pan"],
        "message": "GSTIN format valid"
    }
