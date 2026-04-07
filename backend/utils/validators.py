"""Validation utilities for Indian medical documents"""
import re

def validate_doctor_id(doctor_id: str, state_code: str = None) -> dict:
    """Validate Indian Medical Council doctor ID (STATE-NUMBER-YEAR)"""
    pattern = r'^([A-Z]{2})-([0-9]{5,7})-([0-9]{4})$'
    match = re.match(pattern, doctor_id.upper())
    
    if not match:
        return {"valid": False, "error": "Invalid format. Expected: STATE-NUMBER-YEAR (e.g., MH-12345-2023)"}
    
    state, number, year = match.groups()
    current_year = 2026
    
    if int(year) > current_year:
        return {"valid": False, "error": "Registration year cannot be in future"}
    
    if state_code and state != state_code:
        return {"valid": False, "error": f"State mismatch. Expected {state_code}, got {state}"}
    
    return {
        "valid": True,
        "state": state,
        "registration_number": number,
        "year": year,
        "formatted_id": doctor_id.upper()
    }

def validate_gstin(gstin: str) -> dict:
    """Validate Indian GSTIN (15 characters)"""
    gstin = gstin.upper().strip()
    
    if len(gstin) != 15:
        return {"valid": False, "error": "GSTIN must be 15 characters"}
    
    pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
    if not re.match(pattern, gstin):
        return {"valid": False, "error": "Invalid GSTIN format"}
    
    state_code = gstin[:2]
    pan = gstin[2:12]
    entity_number = gstin[12]
    z_constant = gstin[13]
    checksum = gstin[14]
    
    if z_constant != 'Z':
        return {"valid": False, "error": "13th character must be Z"}
    
    return {
        "valid": True,
        "gstin": gstin,
        "state_code": state_code,
        "pan": pan,
        "entity_number": entity_number,
        "checksum": checksum
    }
