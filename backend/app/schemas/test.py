from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TestCreate(BaseModel):
    name: str
    subject: str
    standard: str
    section: str

class TestUpdate(BaseModel):
    name: Optional[str] = None
    subject: Optional[str] = None
    standard: Optional[str] = None
    section: Optional[str] = None

class TestResponse(BaseModel):
    id: int
    name: str
    subject: str
    standard: str
    section: str
    examiner_id: int
    question_paper_path: Optional[str] = None
    answer_key_path: Optional[str] = None
    reference_book_path: Optional[str] = None
    created_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True