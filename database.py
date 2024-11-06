from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import enum

SQLALCHEMY_DATABASE_URL = "sqlite:///./translation_api.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class JobStatus(enum.Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    UPLOADING = "uploading"
    COMPLETED = "completed"
    FAILED = "failed"

class APIKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String)
    is_active = Column(Integer, default=1)

class TranslationJob(Base):
    __tablename__ = "translation_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, unique=True, index=True)
    original_filename = Column(String)
    status = Column(String)  # overall job status
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    total_languages = Column(Integer)
    processed_languages = Column(Integer, default=0)
    current_processing_language = Column(String, nullable=True)
    error_message = Column(String, nullable=True)

class TranslationFile(Base):
    __tablename__ = "translation_files"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, ForeignKey('translation_jobs.job_id'))
    original_filename = Column(String)
    b2_file_id = Column(String)
    download_url = Column(String)
    language = Column(String)
    status = Column(String)  # individual file status
    created_at = Column(DateTime, default=datetime.utcnow)
    
Base.metadata.create_all(bind=engine)