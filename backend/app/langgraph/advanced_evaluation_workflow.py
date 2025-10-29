"""
Advanced LangGraph PDF Scanning and Evaluation Workflow
Multi-agent system for line-by-line PDF analysis and semantic evaluation
"""

import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple, TypedDict
from dataclasses import dataclass
from datetime import datetime
import asyncio

# LangGraph imports (simulated - replace with actual imports in production)
from typing import Annotated
from operator import add

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# State definitions for LangGraph workflow
class WorkflowState(TypedDict):
    """State passed between agents in the workflow"""
    pdf_path: str
    raw_content: str
    lines: List[str]
    detected_questions: Dict[str, Dict[str, Any]]
    answer_key: Dict[str, str]
    question_marks: Dict[str, int]
    evaluations: Dict[str, Dict[str, Any]]
    errors: List[str]
    processing_stage: str
    confidence_scores: Dict[str, float]

@dataclass
class QuestionDetection:
    """Structure for detected question information"""
    question_number: str
    question_text: str
    student_answer: str
    line_start: int
    line_end: int
    confidence: float
    is_skipped: bool

@dataclass
class EvaluationResult:
    """Structure for evaluation results"""
    question_id: str
    question_text: str
    student_answer: str
    model_answer: str
    marks_allocated: int
    marks_obtained: int
    semantic_score: float
    accuracy_score: float
    feedback: str
    strengths: List[str]
    weaknesses: List[str]

class PDFScannerAgent:
    """Agent responsible for scanning PDF and extracting raw content"""
    
    async def scan_pdf(self, state: WorkflowState) -> WorkflowState:
        """Scan PDF and extract raw content line by line"""
        try:
            logger.info("🔍 PDFScannerAgent: Starting PDF scan")
            state["processing_stage"] = "pdf_scanning"
            
            # Import OCR service here to avoid circular imports
            from app.services.advanced_pdf_ocr_service import get_ocr_service
            
            ocr_service = get_ocr_service()
            ocr_results = await ocr_service.extract_content(state["pdf_path"])
            
            raw_content = ocr_results.get("raw_text", "")
            state["raw_content"] = raw_content
            
            # Split into lines for line-by-line analysis
            lines = [line.strip() for line in raw_content.split('\n') if line.strip()]
            state["lines"] = lines
            
            logger.info(f"✅ PDFScannerAgent: Extracted {len(lines)} lines from PDF")
            
            return state
            
        except Exception as e:
            error_msg = f"PDFScannerAgent failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
            state["errors"].append(error_msg)
            return state

class QuestionDetectorAgent:
    """Agent responsible for detecting questions and answers line by line"""
    
    def __init__(self):
        # Enhanced question patterns
        self.question_patterns = [
            # Standard patterns: "1.", "Q1.", "Question 1:"
            r'^(?:Q\.?|Question\.?\s*|Qn\.?\s*)?(\d+)\.?\s*[:.]?\s*(.*?)$',
            # Bracketed patterns: "(1)", "[1]"
            r'^[\(\[](\d+)[\)\]]\s*\.?\s*(.*?)$',
            # Simple number patterns: "1 ", "1)"
            r'^(\d+)[\)\.]\s+(.*?)$',
            # Complex patterns with words
            r'^(?:Question|Q|Qn)[\s\.]?(\d+)[\.\:\-\s]+(.*?)$'
        ]
        
        # Answer continuation indicators
        self.answer_indicators = [
            r'^(?:Answer|Ans|A)[\s\.\:\-]*(\d+)?',
            r'^Solution[\s\.\:\-]*(\d+)?',
            r'^Response[\s\.\:\-]*(\d+)?'
        ]
    
    async def detect_questions(self, state: WorkflowState) -> WorkflowState:
        """Detect questions and answers from lines"""
        try:
            logger.info("🔍 QuestionDetectorAgent: Starting question detection")
            state["processing_stage"] = "question_detection"
            
            lines = state["lines"]
            detected_questions = {}
            current_question = None
            current_answer_lines = []
            confidence_scores = {}
            
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                
                # Skip empty lines
                if not line:
                    i += 1
                    continue
                
                # Check if this line starts a new question
                question_match = self._detect_question_start(line)
                
                if question_match:
                    # Save previous question if exists
                    if current_question:
                        self._save_detected_question(
                            detected_questions, 
                            current_question, 
                            current_answer_lines,
                            confidence_scores
                        )
                    
                    # Start new question
                    question_number = question_match["number"]
                    question_text = question_match["text"]
                    current_question = {
                        "number": question_number,
                        "question_text": question_text,
                        "line_start": i
                    }
                    current_answer_lines = []
                    
                    logger.info(f"📝 Found Question {question_number}: {question_text[:50]}...")
                    
                else:
                    # This line is part of an answer
                    if current_question:
                        current_answer_lines.append(line)
                
                i += 1
            
            # Don't forget the last question
            if current_question:
                self._save_detected_question(
                    detected_questions, 
                    current_question, 
                    current_answer_lines,
                    confidence_scores
                )
            
            state["detected_questions"] = detected_questions
            state["confidence_scores"] = confidence_scores
            
            logger.info(f"✅ QuestionDetectorAgent: Detected {len(detected_questions)} questions")
            
            return state
            
        except Exception as e:
            error_msg = f"QuestionDetectorAgent failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
            state["errors"].append(error_msg)
            return state
    
    def _detect_question_start(self, line: str) -> Optional[Dict[str, str]]:
        """Detect if a line starts a new question"""
        for pattern in self.question_patterns:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return {
                    "number": match.group(1),
                    "text": match.group(2) if len(match.groups()) > 1 else ""
                }
        return None
    
    def _save_detected_question(
        self, 
        detected_questions: Dict, 
        question_info: Dict, 
        answer_lines: List[str],
        confidence_scores: Dict
    ):
        """Save a detected question and its answer"""
        question_number = question_info["number"]
        question_text = question_info["question_text"]
        student_answer = " ".join(answer_lines).strip()
        
        # Determine if question was skipped
        is_skipped = not student_answer or len(student_answer) < 3
        
        # Calculate confidence based on detection quality
        confidence = self._calculate_detection_confidence(question_text, student_answer)
        
        detected_questions[question_number] = {
            "question_text": question_text,
            "student_answer": student_answer,
            "is_skipped": is_skipped,
            "line_start": question_info["line_start"],
            "line_end": question_info["line_start"] + len(answer_lines),
            "answer_lines": answer_lines
        }
        
        confidence_scores[question_number] = confidence
        
        if is_skipped:
            logger.info(f"⚠️ Question {question_number}: Detected as SKIPPED")
        else:
            logger.info(f"✅ Question {question_number}: Answer detected ({len(student_answer)} chars)")
    
    def _calculate_detection_confidence(self, question_text: str, student_answer: str) -> float:
        """Calculate confidence in question detection"""
        confidence = 0.8  # Base confidence
        
        # Boost for clear question text
        if len(question_text) > 10:
            confidence += 0.1
        
        # Boost for substantial answer
        if len(student_answer) > 20:
            confidence += 0.1
        
        # Reduce for very short or missing content
        if len(student_answer) < 5:
            confidence -= 0.3
        
        return max(min(confidence, 1.0), 0.0)

class AnswerValidatorAgent:
    """Agent responsible for validating detected answers against answer key"""
    
    async def validate_answers(self, state: WorkflowState) -> WorkflowState:
        """Validate that detected questions match the answer key"""
        try:
            logger.info("🔍 AnswerValidatorAgent: Starting answer validation")
            state["processing_stage"] = "answer_validation"
            
            detected_questions = state["detected_questions"]
            answer_key = state["answer_key"]
            question_marks = state["question_marks"]
            
            validated_questions = {}
            
            # Check each question in answer key
            for key_question_id, model_answer in answer_key.items():
                if key_question_id in detected_questions:
                    # Question found in PDF
                    detected = detected_questions[key_question_id]
                    validated_questions[key_question_id] = {
                        **detected,
                        "model_answer": model_answer,
                        "max_marks": question_marks.get(key_question_id, 0),
                        "validation_status": "found"
                    }
                    logger.info(f"✅ Question {key_question_id}: Found in PDF")
                else:
                    # Question missing from PDF
                    validated_questions[key_question_id] = {
                        "question_text": f"Question {key_question_id}",
                        "student_answer": "",
                        "is_skipped": True,
                        "model_answer": model_answer,
                        "max_marks": question_marks.get(key_question_id, 0),
                        "validation_status": "missing_from_pdf"
                    }
                    logger.warning(f"⚠️ Question {key_question_id}: Missing from PDF")
            
            # Check for extra questions in PDF not in answer key
            for pdf_question_id in detected_questions:
                if pdf_question_id not in answer_key:
                    logger.warning(f"⚠️ Question {pdf_question_id}: Found in PDF but not in answer key")
            
            state["detected_questions"] = validated_questions
            
            logger.info(f"✅ AnswerValidatorAgent: Validated {len(validated_questions)} questions")
            
            return state
            
        except Exception as e:
            error_msg = f"AnswerValidatorAgent failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
            state["errors"].append(error_msg)
            return state

class SemanticEvaluatorAgent:
    """Agent responsible for semantic evaluation of answers"""
    
    def __init__(self):
        from app.langgraph.semantic_evaluation_workflow import LangGraphSemanticEvaluator
        self.semantic_evaluator = LangGraphSemanticEvaluator()
    
    async def evaluate_answers(self, state: WorkflowState) -> WorkflowState:
        """Perform semantic evaluation of each answer"""
        try:
            logger.info("🔍 SemanticEvaluatorAgent: Starting semantic evaluation")
            state["processing_stage"] = "semantic_evaluation"
            
            detected_questions = state["detected_questions"]
            evaluations = {}
            
            for question_id, question_data in detected_questions.items():
                logger.info(f"🧠 Evaluating Question {question_id}")
                
                student_answer = question_data["student_answer"]
                model_answer = question_data["model_answer"]
                max_marks = question_data["max_marks"]
                
                if question_data["is_skipped"]:
                    # Handle skipped questions
                    evaluation = {
                        "question_id": question_id,
                        "question_text": question_data["question_text"],
                        "student_answer": "",
                        "model_answer": model_answer,
                        "marks_allocated": max_marks,
                        "marks_obtained": 0,
                        "semantic_similarity": 0.0,
                        "conceptual_understanding": 0.0,
                        "factual_accuracy": 0.0,
                        "overall_score": 0.0,
                        "feedback": "Question not attempted - correctly identified as skipped",
                        "status": "skipped",
                        "strengths": [],
                        "weaknesses": ["Question not answered"]
                    }
                else:
                    # Perform semantic evaluation
                    semantic_result = await self.semantic_evaluator.evaluate_answer_semantically(
                        student_answer=student_answer,
                        model_answer=model_answer,
                        question_type="academic",
                        max_marks=max_marks,
                        ocr_confidence=state["confidence_scores"].get(question_id, 1.0)
                    )
                    
                    evaluation = {
                        "question_id": question_id,
                        "question_text": question_data["question_text"],
                        "student_answer": student_answer,
                        "model_answer": model_answer,
                        "marks_allocated": max_marks,
                        "marks_obtained": semantic_result.marks_obtained,
                        "semantic_similarity": semantic_result.semantic_similarity,
                        "conceptual_understanding": semantic_result.conceptual_understanding,
                        "factual_accuracy": semantic_result.factual_accuracy,
                        "overall_score": semantic_result.final_score,
                        "feedback": semantic_result.detailed_feedback,
                        "status": "evaluated",
                        "strengths": semantic_result.strengths,
                        "weaknesses": semantic_result.error_analysis
                    }
                
                evaluations[question_id] = evaluation
                logger.info(f"✅ Question {question_id}: {evaluation['marks_obtained']}/{max_marks} marks")
            
            state["evaluations"] = evaluations
            
            logger.info(f"✅ SemanticEvaluatorAgent: Completed evaluation of {len(evaluations)} questions")
            
            return state
            
        except Exception as e:
            error_msg = f"SemanticEvaluatorAgent failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
            state["errors"].append(error_msg)
            return state

class ResultAggregatorAgent:
    """Agent responsible for aggregating and formatting final results"""
    
    async def aggregate_results(self, state: WorkflowState) -> WorkflowState:
        """Aggregate evaluation results and generate final report"""
        try:
            logger.info("🔍 ResultAggregatorAgent: Aggregating results")
            state["processing_stage"] = "result_aggregation"
            
            evaluations = state["evaluations"]
            
            # Calculate totals
            total_marks = sum(eval_data["marks_allocated"] for eval_data in evaluations.values())
            obtained_marks = sum(eval_data["marks_obtained"] for eval_data in evaluations.values())
            percentage = (obtained_marks / total_marks * 100) if total_marks > 0 else 0
            
            # Count statistics
            total_questions = len(evaluations)
            answered_questions = len([e for e in evaluations.values() if e["status"] == "evaluated"])
            skipped_questions = len([e for e in evaluations.values() if e["status"] == "skipped"])
            
            # Generate grade
            grade = self._calculate_grade(percentage)
            
            # Generate overall feedback
            overall_feedback = self._generate_overall_feedback(percentage, answered_questions, total_questions)
            
            # Create summary
            summary = {
                "total_marks": total_marks,
                "obtained_marks": obtained_marks,
                "percentage": round(percentage, 2),
                "grade": grade,
                "overall_feedback": overall_feedback,
                "total_questions": total_questions,
                "answered_questions": answered_questions,
                "skipped_questions": skipped_questions,
                "processing_stage": "completed"
            }
            
            # Add summary to state
            state.update(summary)
            
            logger.info(f"✅ ResultAggregatorAgent: Final score {obtained_marks}/{total_marks} ({percentage:.1f}%)")
            
            return state
            
        except Exception as e:
            error_msg = f"ResultAggregatorAgent failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
            state["errors"].append(error_msg)
            return state
    
    def _calculate_grade(self, percentage: float) -> str:
        """Calculate letter grade from percentage"""
        if percentage >= 95:
            return "A+"
        elif percentage >= 85:
            return "A"
        elif percentage >= 75:
            return "B+"
        elif percentage >= 65:
            return "B"
        elif percentage >= 55:
            return "C"
        elif percentage >= 40:
            return "D"
        else:
            return "F"
    
    def _generate_overall_feedback(self, percentage: float, answered: int, total: int) -> str:
        """Generate overall feedback based on performance"""
        if percentage >= 90:
            return f"Outstanding performance! Answered {answered}/{total} questions with excellent understanding."
        elif percentage >= 80:
            return f"Very good performance! Strong understanding shown in {answered}/{total} questions."
        elif percentage >= 70:
            return f"Good performance with room for improvement. Completed {answered}/{total} questions."
        elif percentage >= 60:
            return f"Satisfactory performance. Answered {answered}/{total} questions - focus on depth."
        else:
            return f"Needs significant improvement. Only {answered}/{total} questions completed adequately."

class LangGraphEvaluationWorkflow:
    """Main LangGraph workflow orchestrator"""
    
    def __init__(self):
        self.pdf_scanner = PDFScannerAgent()
        self.question_detector = QuestionDetectorAgent()
        self.answer_validator = AnswerValidatorAgent()
        self.semantic_evaluator = SemanticEvaluatorAgent()
        self.result_aggregator = ResultAggregatorAgent()
    
    async def run_workflow(
        self,
        pdf_path: str,
        answer_key: Dict[str, str],
        question_marks: Dict[str, int]
    ) -> Dict[str, Any]:
        """Run the complete evaluation workflow"""
        try:
            logger.info("🚀 Starting LangGraph Evaluation Workflow")
            
            # Initialize state
            state: WorkflowState = {
                "pdf_path": pdf_path,
                "raw_content": "",
                "lines": [],
                "detected_questions": {},
                "answer_key": answer_key,
                "question_marks": question_marks,
                "evaluations": {},
                "errors": [],
                "processing_stage": "initialized",
                "confidence_scores": {}
            }
            
            # Execute workflow steps
            logger.info("📄 Step 1: PDF Scanning")
            state = await self.pdf_scanner.scan_pdf(state)
            
            logger.info("🔍 Step 2: Question Detection")
            state = await self.question_detector.detect_questions(state)
            
            logger.info("✅ Step 3: Answer Validation")
            state = await self.answer_validator.validate_answers(state)
            
            logger.info("🧠 Step 4: Semantic Evaluation")
            state = await self.semantic_evaluator.evaluate_answers(state)
            
            logger.info("📊 Step 5: Result Aggregation")
            state = await self.result_aggregator.aggregate_results(state)
            
            logger.info("🎉 LangGraph Workflow Completed Successfully!")
            
            return self._format_final_results(state)
            
        except Exception as e:
            logger.error(f"❌ LangGraph Workflow Failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "processing_stage": state.get("processing_stage", "unknown")
            }
    
    def _format_final_results(self, state: WorkflowState) -> Dict[str, Any]:
        """Format final results for API response"""
        return {
            "success": True,
            "evaluation_id": f"langgraph_eval_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]}",
            "total_marks": state["total_marks"],
            "obtained_marks": state["obtained_marks"],
            "percentage": state["percentage"],
            "grade": state["grade"],
            "overall_feedback": state["overall_feedback"],
            "detailed_results": list(state["evaluations"].values()),
            "evaluation_summary": {
                "total_questions": state["total_questions"],
                "answered_questions": state["answered_questions"],
                "skipped_questions": state["skipped_questions"],
                "pdf_lines_processed": len(state["lines"]),
                "detection_confidence": state["confidence_scores"]
            },
            "processing_info": {
                "workflow_type": "LangGraph Multi-Agent",
                "processing_stages": [
                    "PDF Scanning",
                    "Question Detection", 
                    "Answer Validation",
                    "Semantic Evaluation",
                    "Result Aggregation"
                ],
                "final_stage": state["processing_stage"],
                "errors": state["errors"],
                "processed_at": datetime.now().isoformat()
            }
        }