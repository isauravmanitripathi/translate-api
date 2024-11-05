# File: main.py
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict
from datetime import datetime
from sqlalchemy.orm import Session
import uvicorn

from database import SessionLocal
from auth import verify_api_key, get_db
from api_key_manager import generate_api_key, list_api_keys, deactivate_api_key
from translation_service import (
    translate_text, 
    translate_text_to_multiple_languages,
    get_language_regions, 
    get_supported_languages
)

app = FastAPI(title="Regional Language Translation API")

class TextTranslation(BaseModel):
    text: str
    target_language: str
    source_language: Optional[str] = Field(default='auto', description="Leave as 'auto' for automatic detection")

class MultiLanguageTranslation(BaseModel):
    text: str
    target_languages: List[str]
    source_language: Optional[str] = Field(default='auto', description="Leave as 'auto' for automatic detection")

    @validator('target_languages')
    def validate_target_languages(cls, v):
        if not v:
            raise ValueError("At least one target language must be specified")
        if len(v) > 5:
            raise ValueError("Maximum 5 target languages are allowed")
        return v

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
        translated_text = await translate_text(
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

@app.post("/translate/multi")
async def translate_text_multiple_languages(
    translation: MultiLanguageTranslation,
    auth_result: dict = Depends(verify_api_key)
):
    """
    Translate text to multiple languages simultaneously (maximum 5 languages)
    Example: {
        "text": "Hello, how are you?",
        "target_languages": ["hindi", "spanish", "french"],
        "source_language": "english_us"
    }
    """
    try:
        translations = await translate_text_to_multiple_languages(
            translation.text,
            translation.target_languages,
            translation.source_language
        )
        return {
            "translations": translations,
            "source_language": translation.source_language,
            "original_text": translation.text
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