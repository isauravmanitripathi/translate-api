import secrets
from sqlalchemy.orm import Session
from database import APIKey

def generate_api_key(db: Session, description: str, created_by: str) -> str:
    api_key = secrets.token_urlsafe(32)
    db_api_key = APIKey(
        key=api_key,
        description=description,
        created_by=created_by
    )
    db.add(db_api_key)
    db.commit()
    db.refresh(db_api_key)
    return api_key

def list_api_keys(db: Session):
    return db.query(APIKey).all()

def deactivate_api_key(db: Session, api_key: str):
    db_key = db.query(APIKey).filter(APIKey.key == api_key).first()
    if db_key:
        db_key.is_active = 0
        db.commit()
        return True
    return False