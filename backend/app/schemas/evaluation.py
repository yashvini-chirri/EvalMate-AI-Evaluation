from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EvaluationCreate(BaseModel):
    test_id: int
    student_id: int
    answer_sheet_path: str

class EvaluationResponse(BaseModel):
    id: int
    test_id: int
    student_id: int
    answer_sheet_path: str
    total_marks: Optional[float] = None
    obtained_marks: Optional[float] = None
    percentage: Optional[float] = None
    grade: Optional[str] = None
    feedback: Optional[str] = None
    status: str
    created_at: datetime
    evaluated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True