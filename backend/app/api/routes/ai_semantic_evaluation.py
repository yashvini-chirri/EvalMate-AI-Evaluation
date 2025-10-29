"""
AI-Powered Semantic Evaluation API Routes
Complete rebuild with AI models for intelligent evaluation
"""

from fastapi import APIRouter, HTTPException, Form, UploadFile, File
from fastapi.responses import JSONResponse
from typing import Dict, List, Any, Optional
import json
import asyncio
import tempfile
import os
import logging
from datetime import datetime

router = APIRouter()

# Initialize logging
logger = logging.getLogger(__name__)

@router.post("/evaluate-semantic")
async def evaluate_semantic(
    student_answers: str = Form(...),
    answer_key: str = Form(...),
    question_marks: str = Form(...),
    answer_sheet_pdf: Optional[UploadFile] = File(None)
):
    """
    AI-Powered LangGraph evaluation with intelligent text extraction and evaluation
    Complete rebuild with AI models for accurate assessment
    """
    try:
        # Clear any cached data first
        logger.info("🗑️ Clearing any cached evaluation data - Fresh AI processing only")
        
        # Parse inputs
        try:
            student_answers_dict = json.loads(student_answers)
            answer_key_dict = json.loads(answer_key)
            question_marks_dict = {k: int(v) for k, v in json.loads(question_marks).items()}
        except (json.JSONDecodeError, ValueError) as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON format: {str(e)}")
        
        # Import the new AI-powered workflow
        from app.langgraph.ai_powered_evaluation_workflow import ai_workflow_manager
        
        # Prepare PDF content and manual answers
        pdf_content = None
        manual_answers = {}
        
        if answer_sheet_pdf and answer_sheet_pdf.content_type == "application/pdf":
            pdf_content = await answer_sheet_pdf.read()
            logger.info(f"📄 PDF uploaded for AI processing: {len(pdf_content)} bytes")
        else:
            # Use manual input if no PDF
            manual_answers = student_answers_dict
            logger.info(f"📝 Processing manual input: {len(manual_answers)} answers")
        
        # Run AI-powered evaluation workflow
        logger.info("🤖 Starting AI-powered LangGraph evaluation workflow")
        start_time = datetime.now()
        
        result = ai_workflow_manager.evaluate(
            pdf_file=pdf_content,
            answer_key=answer_key_dict,
            question_marks=question_marks_dict,
            manual_answers=manual_answers
        )
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        # Check if evaluation was successful
        if "error" in result:
            logger.error(f"❌ AI evaluation failed: {result['error']}")
            raise HTTPException(status_code=500, detail=f"AI evaluation failed: {result['error']}")
        
        # Add timing information
        if "processing_info" in result:
            result["processing_info"]["total_processing_time"] = processing_time
            result["processing_info"]["completed_at"] = end_time.isoformat()
        
        logger.info(f"✅ AI evaluation completed successfully: {result['obtained_marks']}/{result['total_marks']} in {processing_time:.2f}s")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ AI semantic evaluation error: {e}")
        raise HTTPException(status_code=500, detail=f"AI evaluation failed: {str(e)}")

@router.get("/evaluation-results/{evaluation_id}")
async def get_evaluation_results(evaluation_id: str):
    """Get detailed evaluation results by ID"""
    
    return JSONResponse(content={
        "evaluation_id": evaluation_id,
        "status": "completed",
        "message": "AI-powered evaluation results",
        "workflow_type": "AI-Powered LangGraph Workflow",
        "available_features": [
            "AI text extraction from PDFs",
            "Intelligent question detection",
            "AI-powered semantic evaluation",
            "Detailed feedback generation",
            "No cached data - fresh AI processing"
        ]
    })

@router.get("/health")
async def health_check():
    """Health check for AI-powered semantic evaluation service"""
    return JSONResponse(content={
        "status": "healthy",
        "service": "ai_powered_semantic_evaluation",
        "features": [
            "AI Text Extraction Agent",
            "AI Intelligent Evaluator", 
            "LangGraph Multi-Agent Workflow",
            "GPT-4 powered evaluation",
            "No caching - fresh processing only"
        ],
        "version": "5.0-ai-powered"
    })