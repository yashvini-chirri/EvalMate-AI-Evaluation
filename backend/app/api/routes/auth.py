from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Student, Examiner
from app.core.security import verify_password, create_access_token, get_password_hash, get_current_user
from app.schemas.auth import Token, UserLogin, UserResponse
from datetime import timedelta
from app.core.config import settings

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/login/student", response_model=Token)
async def login_student(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.username == form_data.username).first()
    if not student or not verify_password(form_data.password, student.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": student.username, "user_type": "student", "user_id": student.id}, 
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "user_type": "student"}

@router.post("/login/examiner", response_model=Token)
async def login_examiner(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    examiner = db.query(Examiner).filter(Examiner.username == form_data.username).first()
    if not examiner or not verify_password(form_data.password, examiner.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": examiner.username, "user_type": "examiner", "user_id": examiner.id}, 
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "user_type": "examiner"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    user = current_user["user"]
    return {
        "id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "user_type": current_user["user_type"]
    }