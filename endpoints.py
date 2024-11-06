# File: endpoints.py

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict
from datetime import datetime
from sqlalchemy.orm import Session
import asyncio

from database import SessionLocal, TranslationFile, TranslationJob, JobStatus
from auth import verify_api_key, get_db
from api_key_manager import generate_api_key, list_api_keys, deactivate_api_key
from translation_service import (
    translate_text, 
    translate_text_to_multiple_languages,
    get_language_regions, 
    get_supported_languages
)
from file_service import FileManager

router = APIRouter()
file_manager = FileManager()

# Pydantic Models
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

class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    filename: str
    total_languages: int
    processed_languages: int
    current_processing_language: Optional[str]
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime
    files: List[Dict[str, str]]

# Language Routes
@router.get("/languages")
async def list_languages(
    auth_result: dict = Depends(verify_api_key)
):
    """Get list of supported languages organized by region"""
    return get_language_regions()

@router.get("/languages/flat")
async def list_languages_flat(
    auth_result: dict = Depends(verify_api_key)
):
    """Get flat list of supported languages"""
    return get_supported_languages()

# Text Translation Routes
@router.post("/translate/text")
async def translate_text_endpoint(
    translation: TextTranslation,
    auth_result: dict = Depends(verify_api_key)
):
    """
    Translate text to specified language
    Example: {"text": "Hello", "target_language": "hindi", "source_language": "en"}
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

@router.post("/translate/multi")
async def translate_text_multiple_languages(
    translation: MultiLanguageTranslation,
    auth_result: dict = Depends(verify_api_key)
):
    """Translate text to multiple languages simultaneously"""
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

# File Translation Routes
@router.post("/translate/file", response_model=Dict[str, str])
async def translate_file(
    file: UploadFile = File(...),
    target_language: str = Form(...),
    source_language: str = Form(default='auto'),
    auth_result: dict = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """Upload and translate a file to a single language"""
    if not file.filename.endswith('.txt'):
        raise HTTPException(status_code=400, detail="Only .txt files are supported")

    try:
        # Create translation job
        job_id = await file_manager.create_translation_job(
            db, file.filename, [target_language]
        )

        # Save uploaded file
        temp_path = await file_manager.save_uploaded_file(file)
        
        # Read file content
        with open(temp_path, "r", encoding="utf-8") as f:
            text = f.read()

        # Translate text
        translated_text = await translate_text(text, target_language, source_language)
        translations = {target_language: translated_text}

        # Process job in background
        asyncio.create_task(file_manager.process_translation_job(
            db, job_id, temp_path, translations, file.filename
        ))

        return {"job_id": job_id, "message": "Translation job started"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/translate/file/multi", response_model=Dict[str, str])
async def translate_file_multiple_languages(
    file: UploadFile = File(...),
    target_languages: List[str] = Form(...),
    source_language: str = Form(default='auto'),
    auth_result: dict = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """Upload a file and translate to multiple languages"""
    if not file.filename.endswith('.txt'):
        raise HTTPException(status_code=400, detail="Only .txt files are supported")

    try:
        # Validate number of target languages
        if len(target_languages) > 5:
            raise HTTPException(status_code=400, detail="Maximum 5 target languages allowed")

        # Create translation job
        job_id = await file_manager.create_translation_job(
            db, file.filename, target_languages
        )

        # Save uploaded file
        temp_path = await file_manager.save_uploaded_file(file)

        # Read file content
        with open(temp_path, "r", encoding="utf-8") as f:
            text = f.read()

        # Translate to all target languages
        translations = await translate_text_to_multiple_languages(
            text,
            target_languages,
            source_language
        )

        # Process job in background
        asyncio.create_task(file_manager.process_translation_job(
            db, job_id, temp_path, translations, file.filename
        ))

        return {"job_id": job_id, "message": "Translation job started"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/translation/status/{job_id}", response_model=JobStatusResponse)
async def get_translation_status(
    job_id: str,
    auth_result: dict = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """Get the status of a translation job"""
    job = db.query(TranslationJob).filter(TranslationJob.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Get all files associated with this job
    files = db.query(TranslationFile).filter(TranslationFile.job_id == job_id).all()
    files_info = [
        {
            "language": file.language,
            "status": file.status,
            "download_url": file.download_url if file.status == JobStatus.COMPLETED.value else None
        }
        for file in files
    ]

    return {
        "job_id": job.job_id,
        "status": job.status,
        "filename": job.original_filename,
        "total_languages": job.total_languages,
        "processed_languages": job.processed_languages,
        "current_processing_language": job.current_processing_language,
        "error_message": job.error_message,
        "created_at": job.created_at,
        "updated_at": job.updated_at,
        "files": files_info
    }

# Admin Routes
@router.post("/admin/generate-key", response_model=APIKeyResponse)
async def create_api_key(
    key_info: APIKeyCreate,
    auth_result: dict = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """Generate a new API key (Admin only)"""
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

@router.get("/admin/list-keys", response_model=List[APIKeyResponse])
async def get_api_keys(
    auth_result: dict = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """List all API keys (Admin only)"""
    if not auth_result.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    keys = list_api_keys(db)
    return keys

@router.post("/admin/deactivate-key")
async def delete_api_key(
    api_key: str,
    auth_result: dict = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """Deactivate an API key (Admin only)"""
    if not auth_result.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    if deactivate_api_key(db, api_key):
        return {"message": "API key deactivated successfully"}
    raise HTTPException(status_code=404, detail="API key not found")