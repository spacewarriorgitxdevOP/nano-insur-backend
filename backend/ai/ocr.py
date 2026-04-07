"""
Nano-Insur OCR Module
Extracts total amount from medical bills/receipts using Tesseract OCR.
Supports Indian currency format (₹).
"""

import re
import base64
import io
from typing import Optional
from PIL import Image
import pytesseract
import logging

logger = logging.getLogger(__name__)


def extract_total(image_base64: str) -> Optional[float]:
    """
    Extract total amount from medical bill image.
    
    Args:
        image_base64: Base64 encoded image string
        
    Returns:
        Extracted total amount as float, or None if extraction fails
    """
    try:
        # Decode base64 image
        if ',' in image_base64:
            # Remove data:image/... prefix if present
            image_base64 = image_base64.split(',')[1]
        
        image_data = base64.b64decode(image_base64)
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Extract text using Tesseract
        text = pytesseract.image_to_string(image)
        logger.info(f"OCR extracted text: {text[:200]}...")  # Log first 200 chars
        
        # Extract amounts from text
        amounts = extract_amounts_from_text(text)
        
        if amounts:
            # Return the largest amount (likely the total)
            total = max(amounts)
            logger.info(f"✅ OCR extracted total: ₹{total}")
            return total
        else:
            logger.warning("⚠️ No amounts found in OCR text")
            return None
            
    except Exception as e:
        logger.error(f"❌ OCR extraction failed: {e}")
        return None


def extract_amounts_from_text(text: str) -> list[float]:
    """
    Extract all monetary amounts from text.
    Supports Indian formats: ₹1,23,456.78 or Rs. 1,23,456 or 123456.78
    
    Args:
        text: OCR extracted text
        
    Returns:
        List of amounts found
    """
    amounts = []
    
    # Patterns to match Indian currency amounts
    patterns = [
        r'₹\s*([\d,]+\.?\d*)',  # ₹1,23,456.78
        r'Rs\.?\s*([\d,]+\.?\d*)',  # Rs. 1,23,456
        r'INR\s*([\d,]+\.?\d*)',  # INR 123456
        r'Total[:\s]+₹?\s*([\d,]+\.?\d*)',  # Total: 123456
        r'Amount[:\s]+₹?\s*([\d,]+\.?\d*)',  # Amount: 123456
        r'(?<![\d])([\d,]+\.\d{2})(?![\d])',  # Generic decimal amounts like 123456.78
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            try:
                # Remove commas and convert to float
                amount_str = match.replace(',', '')
                amount = float(amount_str)
                
                # Filter out unrealistic amounts (too small or too large)
                if 10 <= amount <= 10000000:  # Between ₹10 and ₹1 crore
                    amounts.append(amount)
            except ValueError:
                continue
    
    return amounts


def extract_total_with_confidence(image_base64: str) -> dict:
    """
    Extract total with confidence score.
    
    Returns:
        {"total": float, "confidence": float, "all_amounts": list}
    """
    try:
        # Decode image
        if ',' in image_base64:
            image_base64 = image_base64.split(',')[1]
        
        image_data = base64.b64decode(image_base64)
        image = Image.open(io.BytesIO(image_data))
        
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Extract with detailed data
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
        
        # Build text with confidence
        text_parts = []
        confidences = []
        
        for i, word in enumerate(data['text']):
            if word.strip():
                text_parts.append(word)
                confidences.append(int(data['conf'][i]))
        
        full_text = ' '.join(text_parts)
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        # Extract amounts
        amounts = extract_amounts_from_text(full_text)
        
        return {
            "total": max(amounts) if amounts else None,
            "confidence": avg_confidence / 100.0,  # Normalize to 0-1
            "all_amounts": amounts,
            "text_preview": full_text[:200]
        }
        
    except Exception as e:
        logger.error(f"OCR with confidence failed: {e}")
        return {
            "total": None,
            "confidence": 0.0,
            "all_amounts": [],
            "text_preview": ""
        }
