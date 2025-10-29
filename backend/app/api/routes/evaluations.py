from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.db.models import Evaluation, Test, Student, AnswerSheetUpload
from app.core.security import get_current_user
# from app.langgraph.evaluation_workflow import EvaluationWorkflow
from app.schemas.evaluation import EvaluationResponse, EvaluationCreate
import aiofiles
import os
from datetime import datetime
import asyncio

router = APIRouter()
# Simple mock evaluation for demo purposes
class MockEvaluationWorkflow:
    async def run_evaluation(self, evaluation_data):
        # Mock evaluation results
        return {
            "status": "completed",
            "total_marks": 100,
            "obtained_marks": 75,
            "percentage": 75.0,
            "grade": "B",
            "feedback": "Good performance! Keep practicing to improve further.",
            "evaluation_details": '{"detailed_analysis": {"1": {"marks_obtained": 8, "feedback": "Good answer"}}}',
            "ocr_text": "Sample extracted text from answer sheet",
            "errors": []
        }

evaluation_workflow = MockEvaluationWorkflow()

@router.post("/upload-answer-sheet")
async def upload_answer_sheet(
    test_id: int = Form(...),
    student_id: int = Form(...),
    answer_sheet: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload answer sheet for evaluation"""
    
    # Verify permissions
    if current_user["user_type"] == "student" and current_user["user_id"] != student_id:
        raise HTTPException(status_code=403, detail="Can only upload your own answer sheet")
    
    # Verify test exists and is accessible
    test = db.query(Test).filter(Test.id == test_id, Test.is_active == True).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    # Verify student exists
    student = db.query(Student).filter(Student.id == student_id, Student.is_active == True).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Check if student is eligible for this test
    if test.standard != student.standard or test.section != student.section:
        raise HTTPException(status_code=403, detail="Student not eligible for this test")
    
    # Create upload directory
    upload_dir = f"uploads/answer_sheets/test_{test_id}"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Save answer sheet
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"student_{student_id}_{timestamp}_{answer_sheet.filename}"
    file_path = os.path.join(upload_dir, filename)
    
    async with aiofiles.open(file_path, 'wb') as f:
        content = await answer_sheet.read()
        await f.write(content)
    
    # Create upload record
    upload_record = AnswerSheetUpload(
        test_id=test_id,
        student_id=student_id,
        file_path=file_path,
        file_name=answer_sheet.filename,
        file_size=len(content)
    )
    db.add(upload_record)
    db.commit()
    
    # Check if evaluation already exists
    existing_evaluation = db.query(Evaluation).filter(
        Evaluation.test_id == test_id,
        Evaluation.student_id == student_id
    ).first()
    
    if existing_evaluation:
        # Update existing evaluation
        existing_evaluation.answer_sheet_path = file_path
        existing_evaluation.status = "pending"
        db.commit()
        evaluation_id = existing_evaluation.id
    else:
        # Create new evaluation record
        evaluation = Evaluation(
            test_id=test_id,
            student_id=student_id,
            answer_sheet_path=file_path,
            status="pending"
        )
        db.add(evaluation)
        db.commit()
        db.refresh(evaluation)
        evaluation_id = evaluation.id
    
    # Start evaluation process asynchronously
    asyncio.create_task(process_evaluation(evaluation_id, db))
    
    return {"message": "Answer sheet uploaded successfully", "evaluation_id": evaluation_id}

async def process_evaluation(evaluation_id: int, db: Session):
    """Process evaluation asynchronously"""
    try:
        evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
        if not evaluation:
            return
        
        evaluation.status = "processing"
        db.commit()
        
        # Get test details
        test = db.query(Test).filter(Test.id == evaluation.test_id).first()
        
        # Prepare evaluation data
        evaluation_data = {
            "answer_sheet_path": evaluation.answer_sheet_path,
            "question_paper_path": test.question_paper_path,
            "answer_key_path": test.answer_key_path,
            "reference_book_path": test.reference_book_path,
            "test_id": evaluation.test_id,
            "student_id": evaluation.student_id
        }
        
        # Run evaluation workflow
        results = await evaluation_workflow.run_evaluation(evaluation_data)
        
        # Update evaluation with results
        evaluation.total_marks = results.get("total_marks", 0)
        evaluation.obtained_marks = results.get("obtained_marks", 0)
        evaluation.percentage = results.get("percentage", 0)
        evaluation.grade = results.get("grade", "")
        evaluation.feedback = results.get("feedback", "")
        evaluation.evaluation_details = results.get("evaluation_details", "{}")
        evaluation.ocr_text = results.get("ocr_text", "")
        evaluation.status = results.get("status", "completed")
        evaluation.evaluated_at = datetime.utcnow()
        
        db.commit()
        
    except Exception as e:
        evaluation.status = "failed"
        evaluation.feedback = f"Evaluation failed: {str(e)}"
        db.commit()

@router.get("/test/{test_id}", response_model=List[EvaluationResponse])
async def get_test_evaluations(
    test_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all evaluations for a test (examiner view)"""
    
    if current_user["user_type"] != "examiner":
        raise HTTPException(status_code=403, detail="Only examiners can view all evaluations")
    
    # Verify test belongs to examiner
    test = db.query(Test).filter(
        Test.id == test_id,
        Test.examiner_id == current_user["user_id"],
        Test.is_active == True
    ).first()
    
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    evaluations = db.query(Evaluation).filter(Evaluation.test_id == test_id).all()
    return evaluations

@router.get("/student/{student_id}", response_model=List[EvaluationResponse])
async def get_student_evaluations(
    student_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all evaluations for a student"""
    
    # Students can only view their own evaluations
    if current_user["user_type"] == "student" and current_user["user_id"] != student_id:
        raise HTTPException(status_code=403, detail="Can only view your own evaluations")
    
    evaluations = db.query(Evaluation).filter(Evaluation.student_id == student_id).all()
    return evaluations

@router.get("/{evaluation_id}", response_model=EvaluationResponse)
async def get_evaluation(
    evaluation_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific evaluation details"""
    
    evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    
    # Check permissions
    if current_user["user_type"] == "student" and evaluation.student_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    elif current_user["user_type"] == "examiner":
        test = db.query(Test).filter(Test.id == evaluation.test_id).first()
        if test.examiner_id != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Access denied")
    
    return evaluation

@router.get("/{evaluation_id}/detailed")
async def get_detailed_evaluation(
    evaluation_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed evaluation with question-wise analysis"""
    
    evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    
    # Check permissions (same as above)
    if current_user["user_type"] == "student" and evaluation.student_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    elif current_user["user_type"] == "examiner":
        test = db.query(Test).filter(Test.id == evaluation.test_id).first()
        if test.examiner_id != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Access denied")
    
    import json
    
    # Parse evaluation details
    evaluation_details = {}
    if evaluation.evaluation_details:
        try:
            evaluation_details = json.loads(evaluation.evaluation_details)
        except:
            evaluation_details = {}
    
    return {
        "evaluation": evaluation,
        "detailed_analysis": evaluation_details.get("detailed_analysis", {}),
        "question_scores": evaluation_details.get("question_scores", {}),
        "total_marks": evaluation.total_marks,
        "obtained_marks": evaluation.obtained_marks,
        "percentage": evaluation.percentage,
        "grade": evaluation.grade,
        "feedback": evaluation.feedback
    }