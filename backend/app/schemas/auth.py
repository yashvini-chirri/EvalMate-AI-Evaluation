from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str
    user_type: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    first_name: str
    last_name: str
    email: Optional[str] = None
    user_type: str
    
    class Config:
        from_attributes = True

class StudentCreate(BaseModel):
    username: str
    password: str
    first_name: str
    last_name: str
    email: Optional[str] = None
    standard: str
    section: str
    roll_number: int

class ExaminerCreate(BaseModel):
    username: str
    password: str
    first_name: str
    last_name: str
    email: Optional[str] = None
    subject: str