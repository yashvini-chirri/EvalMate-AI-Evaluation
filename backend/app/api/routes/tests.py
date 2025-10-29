from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.db.models import Test, Examiner
from app.core.security import get_current_user
from app.schemas.test import TestCreate, TestResponse, TestUpdate
from app.services.question_detection_service import question_detection_service
import aiofiles
import os
import json
from datetime import datetime

router = APIRouter()

@router.post("/", response_model=TestResponse)
async def create_test(
    name: str = Form(...),
    subject: str = Form(...),
    standard: str = Form(...),
    section: str = Form(...),
    question_paper: Optional[UploadFile] = File(None),
    answer_key: Optional[UploadFile] = File(None),
    reference_book: Optional[UploadFile] = File(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new test with file uploads and automatic question detection"""
    
    # Verify user is an examiner
    if current_user["user_type"] != "examiner":
        raise HTTPException(status_code=403, detail="Only examiners can create tests")
    
    # Create upload directory if it doesn't exist
    upload_dir = "uploads/tests"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Save uploaded files
    file_paths = {}
    question_analysis = None
    
    async def save_file(file: UploadFile, file_type: str) -> str:
        if file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{file_type}_{timestamp}_{file.filename}"
            file_path = os.path.join(upload_dir, filename)
            
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            return file_path
        return None
    
    file_paths["question_paper_path"] = await save_file(question_paper, "question_paper")
    file_paths["answer_key_path"] = await save_file(answer_key, "answer_key")
    file_paths["reference_book_path"] = await save_file(reference_book, "reference_book")
    
    # Analyze question paper to detect questions and structure
    if question_paper:
        try:
            # Read the PDF content for analysis
            question_paper_content = await question_paper.read()
            # Reset file pointer for saving
            await question_paper.seek(0)
            
            # Analyze question paper
            question_analysis = question_detection_service.analyze_question_paper(question_paper_content)
            
            print(f"✅ Question analysis completed: {question_analysis.get('total_questions_detected', 0)} questions detected")
            
        except Exception as e:
            print(f"⚠️ Question analysis failed: {e}")
            question_analysis = {
                "total_questions_detected": 0,
                "error": str(e),
                "analysis_method": "failed"
            }
    
    # Create test record with question analysis
    test = Test(
        name=name,
        subject=subject,
        standard=standard,
        section=section,
        examiner_id=current_user["user_id"],
        question_paper_path=file_paths["question_paper_path"],
        answer_key_path=file_paths["answer_key_path"],
        reference_book_path=file_paths["reference_book_path"],
        # Store question analysis as JSON in metadata field
        metadata=json.dumps(question_analysis) if question_analysis else None
    )
    
    db.add(test)
    db.commit()
    db.refresh(test)
    
    # Add question analysis info to response
    test_dict = test.__dict__.copy()
    if question_analysis:
        test_dict["question_analysis"] = question_analysis
        test_dict["detected_questions"] = question_analysis.get("total_questions_detected", 0)
        test_dict["confidence_score"] = question_analysis.get("confidence_score", 0.0)
    
    return test

@router.get("/", response_model=List[TestResponse])
async def get_tests(
    standard: Optional[str] = None,
    subject: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get tests based on user type and filters"""
    
    query = db.query(Test).filter(Test.is_active == True)
    
    if current_user["user_type"] == "examiner":
        # Examiners see only their tests
        query = query.filter(Test.examiner_id == current_user["user_id"])
    elif current_user["user_type"] == "student":
        # Students see tests for their standard
        student = current_user["user"]
        query = query.filter(Test.standard == student.standard)
        if hasattr(student, 'section'):
            query = query.filter(Test.section == student.section)
    
    if standard:
        query = query.filter(Test.standard == standard)
    if subject:
        query = query.filter(Test.subject == subject)
    
    return query.all()

@router.get("/{test_id}", response_model=TestResponse)
async def get_test(
    test_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific test details"""
    
    test = db.query(Test).filter(Test.id == test_id, Test.is_active == True).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    # Check permissions
    if current_user["user_type"] == "examiner" and test.examiner_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    elif current_user["user_type"] == "student":
        student = current_user["user"]
        if test.standard != student.standard or test.section != student.section:
            raise HTTPException(status_code=403, detail="Test not available for your class")
    
    return test

@router.put("/{test_id}", response_model=TestResponse)
async def update_test(
    test_id: int,
    test_update: TestUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update test details"""
    
    if current_user["user_type"] != "examiner":
        raise HTTPException(status_code=403, detail="Only examiners can update tests")
    
    test = db.query(Test).filter(
        Test.id == test_id, 
        Test.examiner_id == current_user["user_id"],
        Test.is_active == True
    ).first()
    
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    # Update fields
    for field, value in test_update.dict(exclude_unset=True).items():
        setattr(test, field, value)
    
    db.commit()
    db.refresh(test)
    
    return test

@router.delete("/{test_id}")
async def delete_test(
    test_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Soft delete a test"""
    
    if current_user["user_type"] != "examiner":
        raise HTTPException(status_code=403, detail="Only examiners can delete tests")
    
    test = db.query(Test).filter(
        Test.id == test_id, 
        Test.examiner_id == current_user["user_id"],
        Test.is_active == True
    ).first()
    
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    test.is_active = False
    db.commit()
    
    return {"message": "Test deleted successfully"}

@router.get("/{test_id}/students")
async def get_test_students(
    test_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get students eligible for a specific test"""
    
    if current_user["user_type"] != "examiner":
        raise HTTPException(status_code=403, detail="Only examiners can view student lists")
    
    test = db.query(Test).filter(
        Test.id == test_id, 
        Test.examiner_id == current_user["user_id"],
        Test.is_active == True
    ).first()
    
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    from app.db.models import Student
    
    students = db.query(Student).filter(
        Student.standard == test.standard,
        Student.section == test.section,
        Student.is_active == True
    ).order_by(Student.roll_number).all()
    
    return students