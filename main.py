from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
import uvicorn
from enum import Enum
from sqlalchemy.orm import Session  # Add this import

from database import SessionLocal
from auth import verify_api_key, get_db
from api_key_manager import generate_api_key, list_api_keys, deactivate_api_key
from translation_service import translate_text, get_language_regions, get_supported_languages

app = FastAPI(title="Regional Language Translation API")

class TextTranslation(BaseModel):
    text: str
    target_language: str
    source_language: Optional[str] = Field(default='auto', description="Leave as 'auto' for automatic detection")

class APIKeyCreate(BaseModel):
    description: str
    created_by: str

class APIKeyResponse(BaseModel):
    key: str
    description: str
    created_at: datetime
    created_by: str
    is_active: bool

@app.get("/languages")
async def list_languages(
    auth_result: dict = Depends(verify_api_key)
):
    """Get list of supported languages organized by region"""
    return get_language_regions()

@app.get("/languages/flat")
async def list_languages_flat(
    auth_result: dict = Depends(verify_api_key)
):
    """Get flat list of supported languages"""
    return get_supported_languages()

@app.post("/translate/text")
async def translate_text_endpoint(
    translation: TextTranslation,
    auth_result: dict = Depends(verify_api_key)
):
    """
    Translate text to specified language
    Example: {"text": "Hello", "target_language": "hindi", "source_language": "english_us"}
    """
    try:
        translated_text = translate_text(
            translation.text,
            translation.target_language,
            translation.source_language
        )
        return {
            "translated_text": translated_text,
            "source_language": translation.source_language,
            "target_language": translation.target_language
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Translation failed: {str(e)}"
        )

@app.post("/admin/generate-key", response_model=APIKeyResponse)
async def create_api_key(
    key_info: APIKeyCreate,
    auth_result: dict = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    if not auth_result.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    api_key = generate_api_key(db, key_info.description, key_info.created_by)
    return {
        "key": api_key,
        "description": key_info.description,
        "created_at": datetime.utcnow(),
        "created_by": key_info.created_by,
        "is_active": True
    }

@app.get("/admin/list-keys", response_model=List[APIKeyResponse])
async def get_api_keys(
    auth_result: dict = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    if not auth_result.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    keys = list_api_keys(db)
    return keys

@app.post("/admin/deactivate-key")
async def delete_api_key(
    api_key: str,
    auth_result: dict = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    if not auth_result.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    if deactivate_api_key(db, api_key):
        return {"message": "API key deactivated successfully"}
    raise HTTPException(status_code=404, detail="API key not found")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)