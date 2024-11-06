# File: file_service.py

import os
import uuid
import asyncio
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from database import TranslationJob, TranslationFile, JobStatus
from fastapi import HTTPException
import logging
import b2sdk.v2 as b2
from dotenv import load_dotenv
from translation_service import (
    translate_text, 
    translate_text_to_multiple_languages,
    get_supported_languages,
    get_standard_language_code
)

load_dotenv()

SUPPORTED_LANGUAGES = get_supported_languages()

class B2StorageManager:
    def __init__(self):
        try:
            self.info = b2.InMemoryAccountInfo()
            self.b2_api = b2.B2Api(self.info)
            self.application_key_id = os.getenv('B2_APPLICATION_KEY_ID')
            self.application_key = os.getenv('B2_APPLICATION_KEY')
            self.bucket_name = os.getenv('B2_BUCKET_NAME')
            
            if not all([self.application_key_id, self.application_key, self.bucket_name]):
                raise ValueError("B2 credentials not properly configured")
                
            self.b2_api.authorize_account("production", self.application_key_id, self.application_key)
            self.bucket = self.b2_api.get_bucket_by_name(self.bucket_name)
            self.b2_available = True
            
        except Exception as e:
            logging.warning(f"B2 initialization failed: {str(e)}")
            self.b2_available = False

    async def upload_file(self, local_path: str, language: str) -> Dict[str, str]:
        """Upload file to B2 and return file info"""
        if not self.b2_available:
            raise ValueError("B2 storage is not available")
            
        file_uuid = str(uuid.uuid4())
        base_name = os.path.basename(local_path)
        name_without_ext, ext = os.path.splitext(base_name)
        
        # Create new filename with language and UUID
        new_filename = f"{name_without_ext}_{language}_{file_uuid}{ext}"
        date_folder = datetime.now().strftime('%Y-%m-%d')
        b2_key = f"{date_folder}/{new_filename}"
        
        uploaded_file = self.bucket.upload_local_file(
            local_file=local_path,
            file_name=b2_key
        )
        
        download_url = f"https://s3.us-east-005.backblazeb2.com/{self.bucket_name}/{b2_key}"
        
        return {
            "file_id": uploaded_file.id_,
            "download_url": download_url,
            "filename": new_filename,
            "uuid": file_uuid
        }

class FileManager:
    def __init__(self):
        self.upload_dir = "./upload"
        self.storage_manager = B2StorageManager()
        os.makedirs(self.upload_dir, exist_ok=True)

    def validate_languages(self, languages: List[str]):
        """Validate that all languages are supported"""
        for lang in languages:
            if get_standard_language_code(lang) not in SUPPORTED_LANGUAGES.values():
                raise HTTPException(
                    status_code=400,
                    detail=f"Language '{lang}' is not supported. Supported languages: {list(SUPPORTED_LANGUAGES.keys())}"
                )

    async def save_uploaded_file(self, file) -> str:
        """Save uploaded file to temporary directory"""
        temp_path = os.path.join(self.upload_dir, file.filename)
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        return temp_path

    def cleanup_temp_file(self, filepath: str):
        """Remove temporary file"""
        if os.path.exists(filepath):
            os.remove(filepath)

    async def create_translation_job(
        self,
        db: Session,
        filename: str,
        target_languages: List[str]
    ) -> str:
        """Create a new translation job and return job_id"""
        # Validate languages before creating job
        self.validate_languages(target_languages)
        
        job_id = str(uuid.uuid4())
        job = TranslationJob(
            job_id=job_id,
            original_filename=filename,
            status=JobStatus.QUEUED.value,
            total_languages=len(target_languages),
            processed_languages=0
        )
        db.add(job)
        db.commit()
        return job_id

    async def update_job_status(
        self,
        db: Session,
        job_id: str,
        status: str,
        current_language: Optional[str] = None,
        error_message: Optional[str] = None
    ):
        """Update job status"""
        job = db.query(TranslationJob).filter(TranslationJob.job_id == job_id).first()
        if job:
            job.status = status
            job.current_processing_language = current_language
            if error_message:
                job.error_message = error_message
            job.updated_at = datetime.utcnow()
            db.commit()

    async def process_translation_job(
        self,
        db: Session,
        job_id: str,
        temp_path: str,
        translations: Dict[str, str],
        filename: str
    ):
        """Process translation job with status updates"""
        try:
            # Update job to processing
            await self.update_job_status(db, job_id, JobStatus.PROCESSING.value)

            # Upload original file first
            await self.update_job_status(
                db, job_id, JobStatus.PROCESSING.value,
                current_language="original"
            )
            
            original_file_info = await self.storage_manager.upload_file(temp_path, "original")
            
            db_file = TranslationFile(
                job_id=job_id,
                original_filename=filename,
                b2_file_id=original_file_info["file_id"],
                download_url=original_file_info["download_url"],
                language="original",
                status=JobStatus.COMPLETED.value
            )
            db.add(db_file)
            db.commit()

            # Process each translation
            for lang, translated_text in translations.items():
                try:
                    await self.update_job_status(
                        db, job_id, JobStatus.PROCESSING.value,
                        current_language=lang
                    )

                    # Save translated text to temporary file
                    temp_translated_path = os.path.join(
                        self.upload_dir,
                        f"temp_translated_{lang}.txt"
                    )
                    
                    with open(temp_translated_path, "w", encoding="utf-8") as f:
                        f.write(translated_text)

                    # Upload translated file
                    file_info = await self.storage_manager.upload_file(temp_translated_path, lang)

                    # Save to database
                    db_file = TranslationFile(
                        job_id=job_id,
                        original_filename=filename,
                        b2_file_id=file_info["file_id"],
                        download_url=file_info["download_url"],
                        language=lang,
                        status=JobStatus.COMPLETED.value
                    )
                    db.add(db_file)

                    # Update processed languages count
                    job = db.query(TranslationJob).filter(TranslationJob.job_id == job_id).first()
                    job.processed_languages += 1
                    db.commit()

                    # Cleanup temporary translated file
                    self.cleanup_temp_file(temp_translated_path)

                except Exception as e:
                    logging.error(f"Error processing language {lang}: {str(e)}")
                    # Create failed file record
                    db_file = TranslationFile(
                        job_id=job_id,
                        original_filename=filename,
                        language=lang,
                        status=JobStatus.FAILED.value,
                        error_message=str(e)
                    )
                    db.add(db_file)
                    db.commit()

            # Mark job as completed
            await self.update_job_status(db, job_id, JobStatus.COMPLETED.value)

            # Cleanup original temporary file
            self.cleanup_temp_file(temp_path)

        except Exception as e:
            await self.update_job_status(
                db, job_id, JobStatus.FAILED.value,
                error_message=str(e)
            )
            raise e