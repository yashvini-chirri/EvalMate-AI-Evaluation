from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.db.models import Examiner, Test, Evaluation
from app.core.security import get_current_user
from app.schemas.auth import UserResponse

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def get_current_examiner(current_user: dict = Depends(get_current_user)):
    """Get current examiner details"""
    if current_user["user_type"] != "examiner":
        raise HTTPException(status_code=403, detail="Examiner access only")
    
    examiner = current_user["user"]
    return {
        "id": examiner.id,
        "username": examiner.username,
        "first_name": examiner.first_name,
        "last_name": examiner.last_name,
        "email": examiner.email,
        "user_type": "examiner"
    }

@router.get("/dashboard")
async def get_examiner_dashboard(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get examiner dashboard data"""
    if current_user["user_type"] != "examiner":
        raise HTTPException(status_code=403, detail="Examiner access only")
    
    examiner = current_user["user"]
    
    # Get examiner's tests
    tests = db.query(Test).filter(
        Test.examiner_id == examiner.id,
        Test.is_active == True
    ).all()
    
    # Get evaluations for examiner's tests
    test_ids = [test.id for test in tests]
    evaluations = db.query(Evaluation).filter(
        Evaluation.test_id.in_(test_ids)
    ).all() if test_ids else []
    
    # Calculate statistics
    total_tests = len(tests)
    total_evaluations = len(evaluations)
    completed_evaluations = len([e for e in evaluations if e.status == "completed"])
    pending_evaluations = len([e for e in evaluations if e.status in ["pending", "processing"]])
    
    # Subject-wise test distribution
    subject_distribution = {}
    for test in tests:
        subject = test.subject
        subject_distribution[subject] = subject_distribution.get(subject, 0) + 1
    
    # Recent activity
    recent_tests = sorted(tests, key=lambda x: x.created_at, reverse=True)[:5]
    recent_evaluations = sorted(
        [e for e in evaluations if e.status == "completed"], 
        key=lambda x: x.evaluated_at or x.created_at, 
        reverse=True
    )[:5]
    
    return {
        "examiner_info": {
            "name": f"{examiner.first_name} {examiner.last_name}",
            "subject": examiner.subject
        },
        "statistics": {
            "total_tests": total_tests,
            "total_evaluations": total_evaluations,
            "completed_evaluations": completed_evaluations,
            "pending_evaluations": pending_evaluations
        },
        "subject_distribution": subject_distribution,
        "recent_tests": [
            {
                "id": test.id,
                "name": test.name,
                "standard": test.standard,
                "section": test.section,
                "created_at": test.created_at
            } for test in recent_tests
        ],
        "recent_evaluations": [
            {
                "id": evaluation.id,
                "test_name": next((t.name for t in tests if t.id == evaluation.test_id), "Unknown"),
                "student_id": evaluation.student_id,
                "percentage": evaluation.percentage,
                "grade": evaluation.grade,
                "evaluated_at": evaluation.evaluated_at
            } for evaluation in recent_evaluations
        ]
    }

@router.get("/analytics")
async def get_examiner_analytics(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed analytics for examiner"""
    if current_user["user_type"] != "examiner":
        raise HTTPException(status_code=403, detail="Examiner access only")
    
    examiner = current_user["user"]
    
    # Get examiner's tests and evaluations
    tests = db.query(Test).filter(
        Test.examiner_id == examiner.id,
        Test.is_active == True
    ).all()
    
    test_ids = [test.id for test in tests]
    evaluations = db.query(Evaluation).filter(
        Evaluation.test_id.in_(test_ids),
        Evaluation.status == "completed"
    ).all() if test_ids else []
    
    # Performance analytics
    test_performance = {}
    for test in tests:
        test_evaluations = [e for e in evaluations if e.test_id == test.id]
        if test_evaluations:
            avg_percentage = sum(e.percentage or 0 for e in test_evaluations) / len(test_evaluations)
            test_performance[test.name] = {
                "average_percentage": round(avg_percentage, 2),
                "total_students": len(test_evaluations),
                "test_id": test.id
            }
    
    # Grade distribution across all tests
    grade_distribution = {}
    for evaluation in evaluations:
        grade = evaluation.grade or "N/A"
        grade_distribution[grade] = grade_distribution.get(grade, 0) + 1
    
    # Standard-wise performance
    standard_performance = {}
    for test in tests:
        standard = test.standard
        test_evaluations = [e for e in evaluations if e.test_id == test.id]
        if test_evaluations:
            avg_percentage = sum(e.percentage or 0 for e in test_evaluations) / len(test_evaluations)
            if standard not in standard_performance:
                standard_performance[standard] = []
            standard_performance[standard].append(avg_percentage)
    
    # Calculate standard averages
    standard_averages = {
        standard: sum(scores) / len(scores) if scores else 0
        for standard, scores in standard_performance.items()
    }
    
    return {
        "test_performance": test_performance,
        "grade_distribution": grade_distribution,
        "standard_performance": standard_averages,
        "total_evaluations_completed": len(evaluations),
        "evaluation_completion_rate": (len(evaluations) / len(test_ids)) * 100 if test_ids else 0
    }