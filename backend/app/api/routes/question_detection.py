"""
Question Detection API Routes
Specifically for testing and debugging question paper recognition
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import Optional
import json
import logging

from app.services.question_detection_service import question_detection_service

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/analyze-question-paper")
async def analyze_question_paper(
    question_paper: UploadFile = File(...)
):
    """
    Analyze a question paper PDF to detect questions accurately
    
    This endpoint focuses specifically on correctly identifying and counting questions
    from question papers to solve the incorrect question counting issue.
    """
    try:
        # Validate file type
        if question_paper.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Read PDF content
        pdf_content = await question_paper.read()
        logger.info(f"Analyzing question paper: {question_paper.filename} ({len(pdf_content)} bytes)")
        
        # Analyze the question paper
        analysis_result = question_detection_service.analyze_question_paper(pdf_content)
        
        if "error" in analysis_result:
            logger.error(f"Question paper analysis failed: {analysis_result['error']}")
            raise HTTPException(status_code=500, detail=analysis_result["error"])
        
        # Format response for easy understanding
        response = {
            "success": True,
            "filename": question_paper.filename,
            "analysis": {
                "total_questions_detected": analysis_result["total_questions_detected"],
                "confidence_score": analysis_result["confidence_score"],
                "detection_method": analysis_result["analysis_method"],
                "question_structure": analysis_result["question_structure"]
            },
            "detected_questions": [
                {
                    "question_number": q["number"],
                    "preview_text": q["text"],
                    "detection_pattern": q["pattern"],
                    "character_length": len(q["full_text"])
                }
                for q in analysis_result["detected_questions"]
            ],
            "recommendations": _generate_recommendations(analysis_result),
            "debug_info": {
                "full_text_length": len(analysis_result["full_text"]),
                "marks_detection": analysis_result["question_structure"].get("marks_pattern", {}),
                "numbering_sequence": analysis_result["question_structure"].get("number_sequence", [])
            }
        }
        
        logger.info(f"Question analysis completed: {analysis_result['total_questions_detected']} questions detected")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Question paper analysis endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/question-detection-patterns")
async def get_question_detection_patterns():
    """
    Get information about supported question detection patterns
    """
    return {
        "supported_patterns": [
            {
                "pattern_name": "numbered_dots",
                "description": "Questions numbered with dots (1. What is...?, 2. Explain...)",
                "examples": ["1. What is photosynthesis?", "2. Explain democracy."]
            },
            {
                "pattern_name": "q_prefix",
                "description": "Questions with Q prefix (Q1, Q2, Q3)",
                "examples": ["Q1. Define physics", "Q2. What is mathematics?"]
            },
            {
                "pattern_name": "brackets",
                "description": "Questions in brackets ((1), (2), (3))",
                "examples": ["(1) Solve for x", "(2) Calculate the area"]
            },
            {
                "pattern_name": "question_word",
                "description": "Questions with 'Question' word (Question 1, Question 2)",
                "examples": ["Question 1: Define science", "Question 2: Explain theory"]
            },
            {
                "pattern_name": "roman_numerals",
                "description": "Questions with Roman numerals (i., ii., iii.)",
                "examples": ["i. What is energy?", "ii. Define force."]
            }
        ],
        "tips_for_better_detection": [
            "Ensure question numbers are clearly visible",
            "Use consistent numbering throughout the paper",
            "Keep adequate spacing between questions",
            "Avoid handwritten question numbers if possible",
            "Use standard numbering patterns (1., 2., 3., etc.)"
        ],
        "common_issues": [
            "Inconsistent numbering patterns",
            "Poor image quality in scanned PDFs",
            "Handwritten question numbers",
            "Questions split across multiple pages",
            "No clear separation between questions"
        ]
    }

def _generate_recommendations(analysis_result: dict) -> list:
    """Generate recommendations based on analysis results"""
    recommendations = []
    
    confidence = analysis_result.get("confidence_score", 0)
    question_count = analysis_result.get("total_questions_detected", 0)
    structure = analysis_result.get("question_structure", {})
    
    if confidence < 0.5:
        recommendations.append("Low confidence detected. Consider improving question paper formatting.")
    
    if question_count == 0:
        recommendations.append("No questions detected. Check if PDF contains text or improve image quality.")
    
    if not structure.get("is_sequential", True):
        recommendations.append("Non-sequential question numbering detected. Verify question order.")
    
    if structure.get("marks_pattern", {}).get("detected", False):
        total_marks = structure["marks_pattern"].get("total_marks", 0)
        recommendations.append(f"Marks pattern detected. Total marks: {total_marks}")
    else:
        recommendations.append("No marks pattern detected. Consider adding mark allocations.")
    
    if confidence > 0.8:
        recommendations.append("High confidence detection. Question paper format is excellent.")
    
    return recommendations