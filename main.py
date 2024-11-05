from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
import uvicorn
from deep_translator import GoogleTranslator

from database import SessionLocal
from auth import verify_api_key, get_db
from api_key_manager import generate_api_key, list_api_keys, deactivate_api_key

app = FastAPI(title="Translation API with Auth")
translator = GoogleTranslator(source='en', target='hi')

class TextTranslation(BaseModel):
    text: str

class APIKeyCreate(BaseModel):
    description: str
    created_by: str

class APIKeyResponse(BaseModel):
    key: str
    description: str
    created_at: datetime
    created_by: str
    is_active: bool

@app.post("/admin/generate-key", response_model=APIKeyResponse)
async def create_api_key(
    key_info: APIKeyCreate,
    auth_result: dict = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    if not auth_result.get("is_admin"):
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
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
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    keys = list_api_keys(db)
    return keys

@app.post("/admin/deactivate-key")
async def delete_api_key(
    api_key: str,
    auth_result: dict = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    if not auth_result.get("is_admin"):
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    if deactivate_api_key(db, api_key):
        return {"message": "API key deactivated successfully"}
    raise HTTPException(
        status_code=404,
        detail="API key not found"
    )

@app.post("/translate/text")
async def translate_text(
    translation: TextTranslation,
    auth_result: dict = Depends(verify_api_key)
):
    try:
        translated_text = translator.translate(translation.text)
        return {"translated_text": translated_text}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Translation failed: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)