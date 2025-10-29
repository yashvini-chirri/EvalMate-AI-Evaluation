"""
Semantic Evaluation API Routes - Clean Implementation
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

from app.langgraph.advanced_evaluation_workflow import LangGraphEvaluationWorkflow
from app.services.evaluation_validator import EvaluationValidator

router = APIRouter()

# Initialize logging
logger = logging.getLogger(__name__)

# Initialize services
langgraph_workflow = LangGraphEvaluationWorkflow()
evaluation_validator = EvaluationValidator()

@router.post("/evaluate-semantic")
async def evaluate_semantic(
    student_answers: str = Form(..., description="JSON string of student answers"),
    answer_key: str = Form(..., description="JSON string of answer key"), 
    question_marks: str = Form(..., description="JSON string of question marks"),
    answer_sheet_pdf: UploadFile = File(None, description="Student answer sheet PDF")
) -> JSONResponse:
    """
    Advanced LangGraph-based PDF evaluation with line-by-line scanning
    
    Multi-agent workflow:
    1. PDFScannerAgent: Scans PDF line by line
    2. QuestionDetectorAgent: Detects questions and answers by question numbers
    3. AnswerValidatorAgent: Validates against answer key
    4. SemanticEvaluatorAgent: Performs semantic evaluation
    5. ResultAggregatorAgent: Aggregates final results
    
    NO CACHED DATA - Fresh processing for every request
    """
    try:
        logger.info(f"🚀 Starting LangGraph evaluation workflow at {datetime.now()}")
        
        # Parse input data
        answer_key_dict = json.loads(answer_key)
        question_marks_dict = {}
        
        # Convert question marks to proper format
        for q_id, marks in json.loads(question_marks).items():
            question_marks_dict[q_id] = int(marks) if isinstance(marks, str) else marks
        
        # PDF processing is REQUIRED for this workflow
        if not answer_sheet_pdf or not answer_sheet_pdf.filename:
            # If no PDF, use manual answers with workflow
            manual_answers = json.loads(student_answers)
            
            # Create a temporary state for manual processing
            manual_results = []
            total_marks = 0
            obtained_marks = 0
            
            for q_id, student_answer in manual_answers.items():
                model_answer = answer_key_dict.get(q_id, "")
                max_marks = question_marks_dict.get(q_id, 0)
                total_marks += max_marks
                
                if not student_answer or student_answer.strip() == "":
                    # Skipped question
                    result = {
                        "question_id": int(q_id),
                        "question_text": f"Question {q_id}",
                        "student_answer": "",
                        "model_answer": model_answer,
                        "marks_allocated": max_marks,
                        "marks_obtained": 0,
                        "semantic_similarity": 0.0,
                        "conceptual_understanding": 0.0,
                        "factual_accuracy": 0.0,
                        "overall_score": 0.0,
                        "feedback": "Question not attempted",
                        "status": "skipped",
                        "strengths": [],
                        "weaknesses": ["Question not answered"]
                    }
                else:
                    # Simple manual evaluation for non-PDF input
                    semantic_score = 0.5  # Basic score for manual input
                    marks_obtained_q = int(semantic_score * max_marks)
                    obtained_marks += marks_obtained_q
                    
                    result = {
                        "question_id": int(q_id),
                        "question_text": f"Question {q_id}",
                        "student_answer": student_answer,
                        "model_answer": model_answer,
                        "marks_allocated": max_marks,
                        "marks_obtained": marks_obtained_q,
                        "semantic_similarity": semantic_score,
                        "conceptual_understanding": semantic_score,
                        "factual_accuracy": semantic_score,
                        "overall_score": semantic_score,
                        "feedback": "Manual input - basic evaluation applied",
                        "status": "evaluated_manual",
                        "strengths": ["Manual input provided"],
                        "weaknesses": ["PDF upload recommended for accurate evaluation"]
                    }
                
                manual_results.append(result)
            
            percentage = (obtained_marks / total_marks * 100) if total_marks > 0 else 0
            grade = "A+" if percentage >= 95 else "A" if percentage >= 85 else "B+" if percentage >= 75 else "B" if percentage >= 65 else "C" if percentage >= 55 else "D" if percentage >= 40 else "F"
            
            return JSONResponse(content={
                "evaluation_id": f"manual_eval_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]}",
                "total_marks": total_marks,
                "obtained_marks": obtained_marks,
                "percentage": round(percentage, 2),
                "grade": grade,
                "overall_feedback": "Manual evaluation completed. Upload PDF for advanced line-by-line analysis.",
                "detailed_results": manual_results,
                "evaluation_summary": {
                    "total_questions": len(manual_results),
                    "answered_questions": len([r for r in manual_results if r["status"].startswith("evaluated")]),
                    "skipped_questions": len([r for r in manual_results if r["status"] == "skipped"]),
                    "pdf_lines_processed": 0,
                    "detection_confidence": {}
                },
                "processing_info": {
                    "workflow_type": "Manual Input Processing",
                    "recommendation": "Upload PDF for advanced LangGraph workflow",
                    "processed_at": datetime.now().isoformat(),
                    "api_version": "4.0-langgraph"
                }
            })
        
        # MAIN WORKFLOW: PDF Processing with LangGraph
        logger.info(f"📁 Processing PDF with LangGraph workflow: {answer_sheet_pdf.filename}")
        
        # Create unique temporary file for this request
        temp_dir = tempfile.mkdtemp(prefix=f"langgraph_{datetime.now().strftime('%Y%m%d_%H%M%S')}_")
        temp_path = os.path.join(temp_dir, f"upload_{datetime.now().strftime('%H%M%S')}_{answer_sheet_pdf.filename}")
        
        try:
            # Save PDF content
            content = await answer_sheet_pdf.read()
            with open(temp_path, "wb") as f:
                f.write(content)
            
            logger.info(f"💾 PDF saved for LangGraph processing: {temp_path}")
            
            # Run LangGraph workflow
            workflow_start = datetime.now()
            workflow_results = await langgraph_workflow.run_workflow(
                pdf_path=temp_path,
                answer_key=answer_key_dict,
                question_marks=question_marks_dict
            )
            workflow_end = datetime.now()
            workflow_duration = (workflow_end - workflow_start).total_seconds()
            
            logger.info(f"🎉 LangGraph workflow completed in {workflow_duration:.2f}s")
            
            if not workflow_results.get("success", False):
                raise HTTPException(
                    status_code=500, 
                    detail=f"LangGraph workflow failed: {workflow_results.get('error', 'Unknown error')}"
                )
            
            # Add processing timing to results
            workflow_results["processing_info"]["processing_time_seconds"] = round(workflow_duration, 2)
            workflow_results["processing_info"]["workflow_completed_at"] = workflow_end.isoformat()
            
            return JSONResponse(content=workflow_results)
            
        finally:
            # Cleanup temporary files
            try:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    logger.info(f"🗑️ Cleaned up: {temp_path}")
                if os.path.exists(temp_dir):
                    os.rmdir(temp_dir)
                    logger.info(f"🗑️ Cleaned up: {temp_dir}")
            except Exception as cleanup_error:
                logger.warning(f"⚠️ Cleanup warning: {cleanup_error}")
        
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON format: {str(e)}")
    except Exception as e:
        logger.error(f"❌ LangGraph evaluation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")
        
        if answer_sheet_pdf and answer_sheet_pdf.filename:
            logger.info(f"📁 Processing uploaded PDF: {answer_sheet_pdf.filename} (Size: {answer_sheet_pdf.size if hasattr(answer_sheet_pdf, 'size') else 'Unknown'})")
            
            # Create unique temporary directory for this request
            temp_dir = tempfile.mkdtemp(prefix=f"evalmate_{datetime.now().strftime('%Y%m%d_%H%M%S')}_")
            temp_path = os.path.join(temp_dir, f"upload_{datetime.now().strftime('%H%M%S')}_{answer_sheet_pdf.filename}")
            
            try:
                # Read and save PDF content
                logger.info(f"💾 Reading PDF content...")
                content = await answer_sheet_pdf.read()
                
                with open(temp_path, "wb") as f:
                    f.write(content)
                
                logger.info(f"💾 PDF saved temporarily: {temp_path} ({len(content)} bytes)")
                
                # Force fresh OCR extraction - no caching
                logger.info(f"🔍 Starting real-time OCR extraction...")
                ocr_start_time = datetime.now()
                
                # Create fresh OCR service instance to avoid any caching
                fresh_ocr_service = get_ocr_service()
                ocr_results = await fresh_ocr_service.extract_content(temp_path)
                
                ocr_end_time = datetime.now()
                ocr_duration = (ocr_end_time - ocr_start_time).total_seconds()
                
                logger.info(f"🔍 OCR extraction completed in {ocr_duration:.2f}s: {ocr_results.get('extraction_method', 'unknown')}")
                
                extracted_answers = ocr_results.get("extracted_text", {})
                ocr_confidence_scores = ocr_results.get("confidence_scores", {})
                
                logger.info(f"📝 Fresh extraction results: {len(extracted_answers)} answers found")
                
                # Clear student_answers_dict and populate with fresh OCR results
                if extracted_answers:
                    logger.info(f"🔄 Replacing manual input with fresh OCR extraction")
                    student_answers_dict.clear()  # Clear any existing data
                    
                    for q_id, ocr_answer in extracted_answers.items():
                        student_answers_dict[q_id] = ocr_answer.strip() if ocr_answer else ""
                        if ocr_answer and ocr_answer.strip():
                            logger.info(f"✅ Question {q_id}: Fresh OCR extracted '{ocr_answer[:50]}...'")
                        else:
                            logger.info(f"⚠️ Question {q_id}: Detected as skipped by fresh OCR")
                
                # Add processing info with timing
                processing_info = {
                    "pdf_processed": True,
                    "ocr_method": ocr_results.get("extraction_method", "unknown"),
                    "questions_detected": ocr_results.get("total_questions_detected", 0),
                    "available_engines": ocr_results.get("available_engines", []),
                    "processing_details": ocr_results.get("processing_info", {}),
                    "processing_time_seconds": ocr_duration,
                    "fresh_extraction": True,
                    "cache_used": False,
                    "extraction_timestamp": ocr_end_time.isoformat()
                }
                
            except Exception as e:
                logger.error(f"❌ Fresh PDF processing failed: {str(e)}")
                processing_info = {
                    "pdf_processed": False,
                    "error": str(e),
                    "fallback_to_manual": True,
                    "fresh_extraction": False,
                    "processing_attempted": True
                }
                
            finally:
                # Cleanup temp files immediately
                try:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                        logger.info(f"🗑️ Cleaned up temp file: {temp_path}")
                    if os.path.exists(temp_dir):
                        os.rmdir(temp_dir)
                        logger.info(f"🗑️ Cleaned up temp directory: {temp_dir}")
                except Exception as cleanup_error:
                    logger.warning(f"⚠️ Cleanup warning: {cleanup_error}")
        else:
            processing_info = {
                "pdf_processed": False,
                "manual_input": True,
                "fresh_extraction": False,
                "cache_used": False
            }
        
        # Validate fresh input data - ensure we have questions to evaluate
        if not all([student_answers_dict, answer_key_dict, question_marks_dict]):
            raise HTTPException(status_code=400, detail="Missing required evaluation data")
        
        logger.info(f"🔄 Starting fresh semantic evaluation for {len(student_answers_dict)} questions")
        
        # Perform fresh semantic evaluation for each question - no caching
        detailed_results = []
        total_marks_obtained = 0
        total_max_marks = 0
        evaluation_start_time = datetime.now()
        detailed_results = []
        total_marks_obtained = 0
        total_max_marks = 0
        
        # Store original data for validation
        original_student_answers = student_answers_dict.copy()
        original_answer_key = answer_key_dict.copy()
        original_question_marks = {}
        for q_id, marks in question_marks_dict.items():
            original_question_marks[q_id] = int(marks) if isinstance(marks, str) else marks
        
        for question_id_str, student_answer in student_answers_dict.items():
            question_id = int(question_id_str)
            
            logger.info(f"🔄 Processing Question {question_id} - Fresh evaluation")
            
            # Get corresponding answer key and marks
            correct_answer = answer_key_dict.get(question_id_str, "")
            max_marks = question_marks_dict.get(question_id_str, 0)
            
            if isinstance(max_marks, str):
                max_marks = int(max_marks)
            
            total_max_marks += max_marks
            
            if not student_answer or student_answer.strip() == "":
                # Skipped question - ensure 0 marks
                logger.info(f"📝 Question {question_id}: Detected as skipped")
                result = {
                    "question_id": question_id,
                    "student_answer": "",
                    "correct_answer": correct_answer,
                    "marks_allocated": max_marks,
                    "marks_obtained": 0,  # CRITICAL: Skipped questions get 0 marks
                    "semantic_similarity": 0.0,
                    "conceptual_understanding": 0.0,
                    "factual_accuracy": 0.0,
                    "overall_score": 0.0,
                    "feedback": "Question not attempted - correctly identified as skipped by advanced OCR analysis",
                    "status": "skipped",
                    "evaluation_method": "advanced_ocr_semantic_analysis",
                    "answer_completeness": 0.0,
                    "sentence_coherence": 0.0,
                    "strengths": [],
                    "error_analysis": ["Question not answered"],
                    "ocr_confidence": ocr_confidence_scores.get(question_id_str, 0.0)
                }
            else:
                # Get OCR confidence for this question
                ocr_confidence = ocr_confidence_scores.get(question_id_str, 1.0)
                logger.info(f"📝 Question {question_id}: Processing answer (OCR confidence: {ocr_confidence:.2f})")
                
                # Perform semantic evaluation with OCR confidence
                evaluation_result = await semantic_evaluator.evaluate_answer_semantically(
                    student_answer=student_answer,
                    model_answer=correct_answer,
                    question_type="academic",
                    max_marks=max_marks,
                    ocr_confidence=ocr_confidence
                )
                
                marks_obtained = evaluation_result.marks_obtained
                total_marks_obtained += marks_obtained
                
                result = {
                    "question_id": question_id,
                    "student_answer": student_answer,
                    "correct_answer": correct_answer,
                    "marks_allocated": max_marks,
                    "marks_obtained": marks_obtained,
                    "semantic_similarity": evaluation_result.semantic_similarity,
                    "conceptual_understanding": evaluation_result.conceptual_understanding,
                    "factual_accuracy": evaluation_result.factual_accuracy,
                    "overall_score": evaluation_result.final_score,
                    "feedback": evaluation_result.detailed_feedback,
                    "status": "evaluated",
                    "evaluation_method": "advanced_ocr_semantic_analysis",
                    "answer_completeness": evaluation_result.answer_completeness,
                    "sentence_coherence": evaluation_result.sentence_coherence,
                    "strengths": evaluation_result.strengths,
                    "error_analysis": evaluation_result.error_analysis,
                    "ocr_confidence": ocr_confidence
                }
            
            detailed_results.append(result)
        
        # CRITICAL: Validate and correct evaluation results
        corrected_results, validation_errors = evaluation_validator.validate_and_correct_evaluation(
            original_student_answers,
            original_answer_key,
            original_question_marks,
            detailed_results
        )
        
        # Recalculate totals from corrected results
        total_marks_obtained = sum(r['marks_obtained'] for r in corrected_results)
        total_max_marks = sum(r['marks_allocated'] for r in corrected_results)
        answered_count = len([r for r in corrected_results if r['status'] == 'evaluated'])
        skipped_count = len([r for r in corrected_results if r['status'] == 'skipped'])
        
        # Calculate overall performance metrics
        evaluation_end_time = datetime.now()
        total_processing_time = (evaluation_end_time - processing_start_time).total_seconds()
        
        percentage = (total_marks_obtained / total_max_marks * 100) if total_max_marks > 0 else 0
        
        grade = "A+" if percentage >= 95 else "A" if percentage >= 85 else "B+" if percentage >= 75 else "B" if percentage >= 65 else "C" if percentage >= 55 else "D" if percentage >= 40 else "F"
        
        # Generate overall feedback
        if percentage >= 90:
            overall_feedback = "Outstanding performance! Excellent semantic understanding of concepts."
        elif percentage >= 80:
            overall_feedback = "Very good performance with strong conceptual grasp."
        elif percentage >= 70:
            overall_feedback = "Good performance with room for improvement in understanding depth."
        elif percentage >= 60:
            overall_feedback = "Satisfactory performance. Focus on strengthening concept clarity."
        else:
            overall_feedback = "Needs significant improvement in conceptual understanding."
        
        logger.info(f"✅ Fresh evaluation completed: {total_marks_obtained}/{total_max_marks} ({percentage:.1f}%) in {total_processing_time:.2f}s")
        
        return JSONResponse(content={
            "evaluation_id": f"fresh_eval_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]}",
            "total_marks": total_max_marks,
            "obtained_marks": total_marks_obtained,
            "percentage": round(percentage, 2),
            "grade": grade,
            "overall_feedback": overall_feedback,
            "detailed_results": corrected_results,  # Use corrected results
            "evaluation_summary": {
                "total_questions": len(corrected_results),
                "answered_questions": answered_count,
                "skipped_questions": skipped_count,
                "average_semantic_similarity": round(
                    sum(r["semantic_similarity"] for r in corrected_results if r["status"] == "evaluated") / 
                    max(answered_count, 1), 3
                ),
                "average_conceptual_understanding": round(
                    sum(r["conceptual_understanding"] for r in corrected_results if r["status"] == "evaluated") / 
                    max(answered_count, 1), 3
                )
            },
            "processing_info": {
                "evaluation_method": "Fresh Real-time OCR + Semantic Analysis",
                "semantic_understanding": "True sentence-level comprehension with OCR confidence",
                "keyword_matching": "Eliminated in favor of meaning analysis",
                "processed_at": datetime.now().isoformat(),
                "processing_time_seconds": round(total_processing_time, 2),
                "api_version": "3.1-realtime",
                "validation_applied": True,
                "validation_errors": validation_errors if validation_errors else None,
                "ocr_processing": processing_info,
                "cache_policy": "no_cache_fresh_processing_only",
                "evaluation_timestamp": evaluation_end_time.isoformat()
            }
        })
        
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")

@router.get("/evaluation-results/{evaluation_id}")
async def get_evaluation_results(evaluation_id: str):
    """Get detailed evaluation results by ID"""
    
    # In a real implementation, this would fetch from database
    # For now, return a sample result
    return JSONResponse(content={
        "evaluation_id": evaluation_id,
        "status": "completed",
        "message": "This endpoint would return stored evaluation results in a production system",
        "available_features": [
            "Detailed question-wise analysis",
            "Performance analytics",
            "Learning recommendations",
            "Progress tracking"
        ]
    })

@router.post("/compare-evaluations")
async def compare_evaluations(
    semantic_answers: str = Form(...),
    keyword_answers: str = Form(...),
    answer_key: str = Form(...),
    question_marks: str = Form(...)
):
    """
    Compare semantic evaluation vs keyword-based evaluation
    
    Demonstrates the difference between true understanding and keyword matching
    """
    try:
        # Parse inputs
        semantic_dict = json.loads(semantic_answers)
        keyword_dict = json.loads(keyword_answers)
        answer_key_dict = json.loads(answer_key)
        marks_dict = json.loads(question_marks)
        
        comparison_results = []
        
        for q_id, semantic_answer in semantic_dict.items():
            keyword_answer = keyword_dict.get(q_id, "")
            correct_answer = answer_key_dict.get(q_id, "")
            max_marks = int(marks_dict.get(q_id, 0))
            
            # Semantic evaluation
            semantic_result = await semantic_evaluator.evaluate_answer_semantically(
                student_answer=semantic_answer,
                model_answer=correct_answer,
                question_type="academic",
                max_marks=max_marks
            )
            
            # Simulate keyword-based evaluation (simple word matching)
            semantic_words = set(semantic_answer.lower().split())
            keyword_words = set(keyword_answer.lower().split())
            correct_words = set(correct_answer.lower().split())
            
            semantic_matches = len(semantic_words.intersection(correct_words)) / max(len(correct_words), 1)
            keyword_matches = len(keyword_words.intersection(correct_words)) / max(len(correct_words), 1)
            
            comparison_results.append({
                "question_id": int(q_id),
                "semantic_evaluation": {
                    "answer": semantic_answer,
                    "marks": semantic_result.marks_obtained,
                    "understanding_score": semantic_result.conceptual_understanding,
                    "feedback": semantic_result.detailed_feedback,
                    "method": "True semantic understanding"
                },
                "keyword_evaluation": {
                    "answer": keyword_answer,
                    "marks": int(keyword_matches * max_marks),
                    "word_match_score": keyword_matches,
                    "feedback": f"Keyword matching score: {keyword_matches:.2f}",
                    "method": "Simple word matching"
                },
                "difference_analysis": {
                    "semantic_advantage": semantic_result.marks_obtained - int(keyword_matches * max_marks),
                    "understanding_vs_matching": semantic_result.conceptual_understanding - keyword_matches,
                    "explanation": "Semantic evaluation understands meaning while keyword matching only counts word presence"
                }
            })
        
        return JSONResponse(content={
            "comparison_results": comparison_results,
            "summary": {
                "semantic_total": sum(r["semantic_evaluation"]["marks"] for r in comparison_results),
                "keyword_total": sum(r["keyword_evaluation"]["marks"] for r in comparison_results),
                "semantic_advantage": sum(r["difference_analysis"]["semantic_advantage"] for r in comparison_results),
                "conclusion": "Semantic evaluation provides more accurate assessment of student understanding"
            },
            "methodology_comparison": {
                "semantic_method": "Analyzes sentence meaning, context, and conceptual understanding",
                "keyword_method": "Counts presence of specific words without understanding context",
                "advantage": "Semantic method evaluates true comprehension rather than memorized keywords"
            }
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check for semantic evaluation service"""
    return JSONResponse(content={
        "status": "healthy",
        "service": "semantic_evaluation_api",
        "features": [
            "LangGraph workflow orchestration",
            "Semantic understanding analysis",
            "Intelligent partial marking",
            "Conceptual understanding assessment",
            "Pure Python NLP implementation"
        ],
        "version": "2.0"
    })