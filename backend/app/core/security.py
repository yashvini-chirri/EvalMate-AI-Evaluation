from datetime import datetime, timedelta
from typing import Optional
import hashlib
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.database import get_db
from app.db.models import Student, Examiner

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    # Simple hash for development - use bcrypt in production
    return hashlib.md5(plain_password.encode()).hexdigest() == hashed_password

def get_password_hash(password):
    # Simple hash for development - use bcrypt in production
    return hashlib.md5(password.encode()).hexdigest()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    # Simple token for development - use JWT in production
    import json
    import base64
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire.timestamp()})
    token = base64.b64encode(json.dumps(to_encode).encode()).decode()
    return token

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        import json
        import base64
        payload = json.loads(base64.b64decode(token).decode())
        username: str = payload.get("sub")
        user_type: str = payload.get("user_type")
        user_id: int = payload.get("user_id")
        if username is None:
            raise credentials_exception
        
        # Check token expiration
        exp = payload.get("exp")
        if exp and datetime.utcnow().timestamp() > exp:
            raise credentials_exception
            
    except Exception:
        raise credentials_exception
    
    if user_type == "student":
        user = db.query(Student).filter(Student.username == username).first()
    elif user_type == "examiner":
        user = db.query(Examiner).filter(Examiner.username == username).first()
    else:
        raise credentials_exception
    
    if user is None:
        raise credentials_exception
    
    return {"user": user, "user_type": user_type, "user_id": user_id}