"""
Tesseract OCR + Parser Evaluation API Routes
Alternative to GPT-4 using open-source tools
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional, Dict, Any
import json
import logging

from app.services.tesseract_evaluation_service import tesseract_evaluation_service

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/evaluate-tesseract")
async def evaluate_with_tesseract(
    answer_key: str = Form(...),
    question_marks: str = Form(...),
    question_texts: Optional[str] = Form(None),
    student_answers: Optional[str] = Form(None),
    answer_sheet: Optional[UploadFile] = File(None)
):
    """
    Evaluate answers using Tesseract OCR and custom parser
    
    This endpoint provides a free, open-source alternative to GPT-4
    using Tesseract for OCR and intelligent custom parsing for evaluation.
    """
    try:
        # Parse JSON inputs
        try:
            answer_key_dict = json.loads(answer_key)
            question_marks_dict = json.loads(question_marks)
            question_texts_dict = json.loads(question_texts) if question_texts else None
            student_answers_dict = json.loads(student_answers) if student_answers else None
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON format: {str(e)}")
        
        # Validate inputs
        if not answer_key_dict or not question_marks_dict:
            raise HTTPException(status_code=400, detail="Answer key and question marks are required")
        
        # Read PDF file if provided
        pdf_content = None
        if answer_sheet:
            if answer_sheet.content_type != "application/pdf":
                raise HTTPException(status_code=400, detail="Only PDF files are supported")
            
            pdf_content = await answer_sheet.read()
            logger.info(f"Processing PDF file: {answer_sheet.filename} ({len(pdf_content)} bytes)")
        
        # Run Tesseract evaluation
        result = tesseract_evaluation_service.evaluate(
            pdf_file=pdf_content,
            answer_key=answer_key_dict,
            question_marks=question_marks_dict,
            question_texts=question_texts_dict,
            manual_answers=student_answers_dict
        )
        
        if "error" in result:
            logger.error(f"Tesseract evaluation failed: {result['error']}")
            raise HTTPException(status_code=500, detail=result["error"])
        
        logger.info(f"Tesseract evaluation completed: {result['evaluation_id']}")
        return {
            "success": True,
            "message": "Evaluation completed successfully using Tesseract OCR and custom parser",
            "evaluation_type": "tesseract_ocr_custom_parser",
            "cost": "Free - No API costs",
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Tesseract evaluation endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")

@router.post("/demo-tesseract")
async def demo_tesseract_evaluation():
    """
    Demo endpoint for Tesseract OCR + Custom Parser evaluation
    Shows the capabilities without requiring file upload
    """
    try:
        # Demo data
        demo_answer_key = {
            "1": "Photosynthesis is the process by which plants make food using sunlight, water, and carbon dioxide.",
            "2": "The main parts of a plant are roots, stem, leaves, and flowers.",
            "3": "Water cycle includes evaporation, condensation, precipitation, and collection."
        }
        
        demo_question_marks = {
            "1": 5,
            "2": 3,
            "3": 4
        }
        
        demo_question_texts = {
            "1": "Explain the process of photosynthesis in plants.",
            "2": "List the main parts of a plant.",
            "3": "Describe the water cycle."
        }
        
        demo_student_answers = {
            "1": "Plants make food using sunlight and water. They use chlorophyll to capture light energy and convert it to glucose.",
            "2": "Plants have roots that absorb water, stems for support, leaves for photosynthesis, and flowers for reproduction.",
            "3": "Water evaporates from oceans, forms clouds through condensation, falls as rain, and flows back to water bodies."
        }
        
        # Run evaluation
        result = tesseract_evaluation_service.evaluate(
            pdf_file=None,
            answer_key=demo_answer_key,
            question_marks=demo_question_marks,
            question_texts=demo_question_texts,
            manual_answers=demo_student_answers
        )
        
        return {
            "success": True,
            "message": "Demo evaluation completed using Tesseract OCR and custom parser",
            "evaluation_type": "tesseract_ocr_custom_parser_demo",
            "cost": "Free - No API costs",
            "features": [
                "Tesseract OCR for text extraction",
                "Custom intelligent parser",
                "Multi-criteria evaluation",
                "Detailed feedback generation",
                "No API costs or dependencies"
            ],
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Demo Tesseract evaluation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Demo evaluation failed: {str(e)}")

@router.get("/tesseract-info")
async def get_tesseract_info():
    """
    Get information about Tesseract OCR evaluation system
    """
    return {
        "system_name": "Tesseract OCR + Custom Parser Evaluation",
        "description": "Free, open-source evaluation system using Tesseract OCR and intelligent text analysis",
        "features": {
            "ocr_engine": "Tesseract OCR with image preprocessing",
            "text_extraction": "PyMuPDF + Tesseract for digital and scanned PDFs",
            "answer_parsing": "Custom intelligent parser with multiple pattern matching",
            "evaluation_method": "Multi-criteria text analysis with similarity scoring",
            "feedback_generation": "Automated detailed feedback with strengths and improvements",
            "cost": "Completely free - no API costs"
        },
        "evaluation_criteria": {
            "text_similarity": "30% - Overall text similarity to model answer",
            "keyword_matching": "25% - Relevant terminology usage",
            "concept_analysis": "25% - Understanding of key concepts",
            "completeness": "20% - Answer completeness and detail"
        },
        "advantages": [
            "No API costs or dependencies",
            "Works offline",
            "Customizable evaluation logic",
            "Fast processing",
            "Privacy-friendly (no data sent to external APIs)",
            "Reliable OCR with Tesseract",
            "Intelligent text analysis"
        ],
        "requirements": [
            "Tesseract OCR installed on system",
            "Python packages: pytesseract, PyMuPDF, nltk",
            "NLTK data: punkt, stopwords"
        ],
        "supported_formats": ["PDF (digital and scanned)", "Manual text input"],
        "api_version": "6.0-tesseract-parser"
    }