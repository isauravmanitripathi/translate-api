from fastapi import HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy.orm import Session
from datetime import datetime
import os
from dotenv import load_dotenv
from database import SessionLocal, APIKey

load_dotenv()

ADMIN_ACCESS_KEY = os.getenv("ADMIN_ACCESS_KEY")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def verify_api_key(api_key: str = Security(api_key_header), db: Session = Depends(get_db)):
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="API Key missing"
        )
    
    # Check if it's the admin key
    if api_key == ADMIN_ACCESS_KEY:
        return {"is_admin": True}
        
    # Check if it's a valid API key
    db_key = db.query(APIKey).filter(APIKey.key == api_key, APIKey.is_active == 1).first()
    if not db_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid or inactive API key"
        )
    return {"is_admin": False}
