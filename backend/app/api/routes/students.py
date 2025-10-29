from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.db.models import Student
from app.core.security import get_current_user
from app.schemas.auth import UserResponse

router = APIRouter()

@router.get("/")
async def get_students(
    standard: Optional[str] = Query(None, description="Filter by standard (e.g., '10th', '11th', '12th')"),
    section: Optional[str] = Query(None, description="Filter by section (e.g., 'A', 'B')"),
    db: Session = Depends(get_db)
):
    """Get list of students with optional filtering by standard and section"""
    query = db.query(Student)
    
    if standard:
        query = query.filter(Student.standard == standard)
    if section:
        query = query.filter(Student.section == section)
    
    students = query.all()
    
    return [
        {
            "id": student.id,
            "username": student.username,
            "name": f"{student.first_name} {student.last_name}",
            "first_name": student.first_name,
            "last_name": student.last_name,
            "email": student.email,
            "standard": student.standard,
            "section": student.section,
            "roll_number": student.roll_number
        } for student in students
    ]

@router.get("/me", response_model=UserResponse)
async def get_current_student(current_user: dict = Depends(get_current_user)):
    """Get current student details"""
    if current_user["user_type"] != "student":
        raise HTTPException(status_code=403, detail="Student access only")
    
    student = current_user["user"]
    return {
        "id": student.id,
        "username": student.username,
        "first_name": student.first_name,
        "last_name": student.last_name,
        "email": student.email,
        "user_type": "student"
    }

@router.get("/dashboard")
async def get_student_dashboard(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get student dashboard data"""
    if current_user["user_type"] != "student":
        raise HTTPException(status_code=403, detail="Student access only")
    
    student = current_user["user"]
    
    # Get student's tests and evaluations
    from app.db.models import Test, Evaluation
    
    # Available tests for the student
    available_tests = db.query(Test).filter(
        Test.standard == student.standard,
        Test.section == student.section,
        Test.is_active == True
    ).all()
    
    # Student's evaluations
    evaluations = db.query(Evaluation).filter(
        Evaluation.student_id == student.id
    ).all()
    
    # Calculate statistics
    total_tests = len(available_tests)
    completed_tests = len([e for e in evaluations if e.status == "completed"])
    pending_tests = len([e for e in evaluations if e.status in ["pending", "processing"]])
    
    # Average performance
    completed_evaluations = [e for e in evaluations if e.status == "completed" and e.percentage is not None]
    average_percentage = sum(e.percentage for e in completed_evaluations) / len(completed_evaluations) if completed_evaluations else 0
    
    return {
        "student_info": {
            "name": f"{student.first_name} {student.last_name}",
            "standard": student.standard,
            "section": student.section,
            "roll_number": student.roll_number
        },
        "statistics": {
            "total_tests": total_tests,
            "completed_tests": completed_tests,
            "pending_tests": pending_tests,
            "average_percentage": round(average_percentage, 2)
        },
        "recent_evaluations": [
            {
                "id": e.id,
                "test_name": next((t.name for t in available_tests if t.id == e.test_id), "Unknown"),
                "subject": next((t.subject for t in available_tests if t.id == e.test_id), "Unknown"),
                "percentage": e.percentage,
                "grade": e.grade,
                "status": e.status,
                "evaluated_at": e.evaluated_at
            } for e in evaluations[-5:]  # Last 5 evaluations
        ]
    }

@router.get("/performance")
async def get_performance_analytics(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed performance analytics for student"""
    if current_user["user_type"] != "student":
        raise HTTPException(status_code=403, detail="Student access only")
    
    student = current_user["user"]
    
    from app.db.models import Evaluation, Test
    
    # Get all completed evaluations
    evaluations = db.query(Evaluation).filter(
        Evaluation.student_id == student.id,
        Evaluation.status == "completed"
    ).all()
    
    # Subject-wise performance
    subject_performance = {}
    for evaluation in evaluations:
        test = db.query(Test).filter(Test.id == evaluation.test_id).first()
        if test:
            subject = test.subject
            if subject not in subject_performance:
                subject_performance[subject] = []
            subject_performance[subject].append(evaluation.percentage or 0)
    
    # Calculate averages
    subject_averages = {
        subject: sum(scores) / len(scores) if scores else 0
        for subject, scores in subject_performance.items()
    }
    
    # Grade distribution
    grade_distribution = {}
    for evaluation in evaluations:
        grade = evaluation.grade or "N/A"
        grade_distribution[grade] = grade_distribution.get(grade, 0) + 1
    
    return {
        "subject_performance": subject_averages,
        "grade_distribution": grade_distribution,
        "improvement_trend": [e.percentage for e in evaluations[-10:]],  # Last 10 scores
        "total_evaluations": len(evaluations)
    }