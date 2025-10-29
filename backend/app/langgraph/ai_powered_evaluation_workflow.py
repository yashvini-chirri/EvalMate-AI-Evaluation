"""
AI-Powered LangGraph Evaluation Workflow
Complete rebuild with AI models for text extraction and intelligent evaluation
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid
import re
from pathlib import Path

# LangGraph imports
from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict

# AI Model imports
import openai
from openai import OpenAI

# OCR and PDF processing
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io

# Configuration
from app.core.config import settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client with API key
client = OpenAI(api_key=settings.OPENAI_API_KEY)

class EvaluationState(TypedDict):
    """State passed between AI agents in the workflow"""
    pdf_file: Optional[bytes]
    raw_text: str
    extracted_answers: Dict[str, str]
    answer_key: Dict[str, str]
    question_marks: Dict[str, int]
    question_texts: Dict[str, str]
    evaluations: List[Dict[str, Any]]
    processing_logs: List[str]
    errors: List[str]
    workflow_complete: bool
    evaluation_id: str
    start_time: datetime
    current_stage: str

class AITextExtractionAgent:
    """AI Agent for intelligent text extraction and question identification"""
    
    def __init__(self):
        self.name = "AI_Text_Extractor"
        self.model = "gpt-4"
    
    def extract_text_from_pdf(self, pdf_bytes: bytes) -> str:
        """Extract text from PDF using multiple methods"""
        try:
            # Method 1: PyMuPDF for digital text
            pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
            text = ""
            
            for page_num in range(pdf_document.page_count):
                page = pdf_document.get_page(page_num)
                page_text = page.get_text()
                text += f"\n--- Page {page_num + 1} ---\n{page_text}"
            
            pdf_document.close()
            
            # If no text found, use OCR
            if not text.strip():
                logger.info("No digital text found, using OCR")
                text = self._ocr_extraction(pdf_bytes)
            
            return text
        except Exception as e:
            logger.error(f"PDF text extraction failed: {e}")
            return ""
    
    def _ocr_extraction(self, pdf_bytes: bytes) -> str:
        """OCR extraction for scanned PDFs - fallback to basic text extraction if Tesseract unavailable"""
        try:
            # Try basic text extraction first
            pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
            text = ""
            
            for page_num in range(pdf_document.page_count):
                page = pdf_document.get_page(page_num)
                page_text = page.get_text()
                if page_text.strip():
                    text += f"\n--- Page {page_num + 1} ---\n{page_text}"
                else:
                    # If no digital text, try basic image extraction
                    try:
                        import pytesseract
                        pix = page.get_pixmap()
                        img_data = pix.tobytes("png")
                        
                        # Convert to PIL Image
                        image = Image.open(io.BytesIO(img_data))
                        
                        # OCR with Tesseract
                        page_text = pytesseract.image_to_string(image)
                        text += f"\n--- Page {page_num + 1} (OCR) ---\n{page_text}"
                    except Exception as ocr_error:
                        logger.warning(f"OCR failed for page {page_num + 1}: {ocr_error}")
                        text += f"\n--- Page {page_num + 1} (No text extracted) ---\n"
            
            pdf_document.close()
            return text
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return ""
    
    def ai_extract_answers(self, text: str, question_marks: Dict[str, int]) -> Dict[str, str]:
        """Use AI to intelligently extract answers by question numbers"""
        
        prompt = f"""
You are an AI text analysis expert. Extract student answers from the following text by identifying question numbers.

TEXT TO ANALYZE:
{text}

EXPECTED QUESTIONS: {list(question_marks.keys())}

INSTRUCTIONS:
1. Find each question number (1, 2, 3, etc. or Q1, Q2, etc.)
2. Extract the complete answer text that follows each question
3. Return ONLY the answer content, not the question number
4. If a question is not found or has no answer, return empty string

Return a JSON object with question numbers as keys and answers as values.
Example: {{"1": "answer text here", "2": "another answer", "3": ""}}

IMPORTANT: Extract the FULL answer text, including all sentences and explanations.
"""

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at extracting student answers from exam papers. Be thorough and accurate."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            result = response.choices[0].message.content.strip()
            
            # Parse JSON response
            try:
                answers = json.loads(result)
                logger.info(f"AI extracted {len(answers)} answers")
                return answers
            except json.JSONDecodeError:
                # Fallback: try to extract from response
                logger.warning("AI response not valid JSON, using fallback extraction")
                return self._fallback_extraction(text, question_marks)
                
        except Exception as e:
            logger.error(f"AI extraction failed: {e}")
            return self._fallback_extraction(text, question_marks)
    
    def _fallback_extraction(self, text: str, question_marks: Dict[str, int]) -> Dict[str, str]:
        """Fallback method for answer extraction"""
        answers = {}
        
        for q_num in question_marks.keys():
            # Multiple patterns for question detection
            patterns = [
                rf"(?:^|\n)\s*{q_num}[\.\)\:]?\s*(.*?)(?=\n\s*(?:\d+[\.\)\:]|\Z))",
                rf"(?:^|\n)\s*Q\s*{q_num}[\.\)\:]?\s*(.*?)(?=\n\s*(?:Q\s*\d+|\Z))",
                rf"(?:^|\n)\s*Question\s*{q_num}[\.\)\:]?\s*(.*?)(?=\n\s*(?:Question\s*\d+|\Z))"
            ]
            
            answer = ""
            for pattern in patterns:
                match = re.search(pattern, text, re.DOTALL | re.IGNORECASE | re.MULTILINE)
                if match:
                    answer = match.group(1).strip()
                    break
            
            answers[q_num] = answer
        
        return answers
    
    def process(self, state: EvaluationState) -> EvaluationState:
        """Main processing function for AI text extraction"""
        logger.info("🤖 AI Text Extraction Agent started")
        
        state["current_stage"] = "AI Text Extraction"
        state["processing_logs"].append(f"[{datetime.now()}] AI Text Extraction Agent processing")
        
        try:
            if state["pdf_file"]:
                # Extract text using AI-powered methods
                raw_text = self.extract_text_from_pdf(state["pdf_file"])
                state["raw_text"] = raw_text
                
                # Use AI to extract answers intelligently
                extracted_answers = self.ai_extract_answers(raw_text, state["question_marks"])
                state["extracted_answers"] = extracted_answers
                
                state["processing_logs"].append(f"[{datetime.now()}] AI extracted {len(extracted_answers)} answers from PDF")
                logger.info(f"AI extraction complete: {len(extracted_answers)} answers found")
            else:
                # For manual input, check if we already have answers in the extracted_answers
                if not state["extracted_answers"]:
                    state["errors"].append("No PDF file provided for AI extraction")
                    # Initialize with empty answers based on question_marks
                    state["extracted_answers"] = {q_id: "" for q_id in state["question_marks"].keys()}
                
                state["processing_logs"].append(f"[{datetime.now()}] Processing manual input - {len(state['extracted_answers'])} questions")
                logger.info(f"Manual input processing: {len(state['extracted_answers'])} questions")
                
        except Exception as e:
            error_msg = f"AI Text Extraction failed: {str(e)}"
            state["errors"].append(error_msg)
            logger.error(error_msg)
        
        return state

class AIIntelligentEvaluator:
    """AI Agent for intelligent answer evaluation with contextual understanding"""
    
    def __init__(self):
        self.name = "AI_Intelligent_Evaluator"
        self.model = "gpt-4"
    
    def ai_evaluate_answer(self, question_num: str, student_answer: str, model_answer: str, 
                          question_context: str, max_marks: int) -> Dict[str, Any]:
        """Use AI to intelligently evaluate a single answer"""
        
        # Demo mode when no valid API key is available
        if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "sk-demo-key-for-testing":
            return self._demo_ai_evaluation(student_answer, model_answer, max_marks)
        
        prompt = f"""
You are an expert teacher evaluating student answers. Provide detailed, fair evaluation.

QUESTION NUMBER: {question_num}
QUESTION CONTEXT: {question_context}
MODEL ANSWER: {model_answer}
STUDENT ANSWER: {student_answer}
MAXIMUM MARKS: {max_marks}

EVALUATION CRITERIA:
1. Conceptual Understanding (25%) - Does student understand the core concepts?
2. Factual Accuracy (25%) - Are the facts and details correct?
3. Completeness (25%) - Is the answer complete and comprehensive?
4. Clarity & Expression (25%) - Is the answer well-structured and clear?

INSTRUCTIONS:
- If student answer is empty or clearly not attempted, give 0 marks
- Be fair but thorough in evaluation
- Consider partial credit for partially correct answers
- Provide specific feedback explaining the marks awarded

Return a JSON object with this exact structure:
{{
    "marks_obtained": <number between 0 and {max_marks}>,
    "conceptual_understanding": <score 0.0 to 1.0>,
    "factual_accuracy": <score 0.0 to 1.0>,
    "completeness": <score 0.0 to 1.0>,
    "clarity_expression": <score 0.0 to 1.0>,
    "overall_score": <score 0.0 to 1.0>,
    "detailed_feedback": "Specific explanation of marks awarded",
    "strengths": ["strength 1", "strength 2"],
    "areas_for_improvement": ["improvement 1", "improvement 2"],
    "is_attempted": true/false
}}
"""

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an experienced teacher who evaluates student answers fairly and provides constructive feedback."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )
            
            result = response.choices[0].message.content.strip()
            
            try:
                evaluation = json.loads(result)
                return evaluation
            except json.JSONDecodeError:
                # Fallback evaluation
                logger.warning(f"AI evaluation response not valid JSON for Q{question_num}")
                return self._fallback_evaluation(student_answer, max_marks)
                
        except Exception as e:
            logger.error(f"AI evaluation failed for Q{question_num}: {e}")
            return self._fallback_evaluation(student_answer, max_marks)
    
    def _demo_ai_evaluation(self, student_answer: str, model_answer: str, max_marks: int) -> Dict[str, Any]:
        """Demo AI evaluation when API key is not available"""
        if not student_answer.strip():
            return {
                "marks_obtained": 0,
                "conceptual_understanding": 0.0,
                "factual_accuracy": 0.0,
                "completeness": 0.0,
                "clarity_expression": 0.0,
                "overall_score": 0.0,
                "detailed_feedback": "Question not attempted",
                "strengths": [],
                "areas_for_improvement": ["Attempt the question"],
                "is_attempted": False
            }
        
        # Demo intelligent evaluation based on keyword overlap and similarity
        student_words = set(student_answer.lower().split())
        model_words = set(model_answer.lower().split())
        
        # Key concepts detection
        key_concepts = {"photosynthesis", "sunlight", "light", "food", "plants", "produce", "make", "energy", "glucose", "chlorophyll"}
        student_concepts = student_words.intersection(key_concepts)
        model_concepts = model_words.intersection(key_concepts)
        
        # Calculate scores
        concept_score = len(student_concepts) / max(len(model_concepts), 1) if model_concepts else 0.5
        word_overlap = len(student_words.intersection(model_words)) / max(len(model_words), 1)
        
        # Adjust scores
        conceptual_understanding = min(concept_score, 1.0)
        factual_accuracy = min((concept_score + word_overlap) / 2, 1.0)
        completeness = min(len(student_answer) / max(len(model_answer), 1), 1.0) if len(student_answer) < len(model_answer) * 1.5 else 0.8
        clarity = 0.8 if len(student_answer.split()) > 3 else 0.6
        
        overall_score = (conceptual_understanding + factual_accuracy + completeness + clarity) / 4
        marks = int(overall_score * max_marks)
        
        # Generate feedback
        strengths = []
        improvements = []
        
        if student_concepts:
            strengths.append(f"Identified key concepts: {', '.join(student_concepts)}")
        if word_overlap > 0.3:
            strengths.append("Good factual accuracy")
        if len(student_answer.split()) > 5:
            strengths.append("Adequate detail provided")
            
        if concept_score < 0.7:
            improvements.append("Include more key scientific concepts")
        if completeness < 0.7:
            improvements.append("Provide more complete explanation")
        if len(student_answer.split()) < 5:
            improvements.append("Add more detail to the answer")
        
        feedback = f"Demo AI evaluation: {marks}/{max_marks} marks. "
        if overall_score > 0.8:
            feedback += "Excellent understanding demonstrated."
        elif overall_score > 0.6:
            feedback += "Good understanding with room for improvement."
        elif overall_score > 0.4:
            feedback += "Basic understanding shown, needs more development."
        else:
            feedback += "Limited understanding demonstrated."
        
        return {
            "marks_obtained": marks,
            "conceptual_understanding": conceptual_understanding,
            "factual_accuracy": factual_accuracy,
            "completeness": completeness,
            "clarity_expression": clarity,
            "overall_score": overall_score,
            "detailed_feedback": feedback,
            "strengths": strengths,
            "areas_for_improvement": improvements,
            "is_attempted": True
        }
    
    def _fallback_evaluation(self, student_answer: str, max_marks: int) -> Dict[str, Any]:
        """Fallback evaluation when AI fails"""
        if not student_answer.strip():
            return {
                "marks_obtained": 0,
                "conceptual_understanding": 0.0,
                "factual_accuracy": 0.0,
                "completeness": 0.0,
                "clarity_expression": 0.0,
                "overall_score": 0.0,
                "detailed_feedback": "Question not attempted",
                "strengths": [],
                "areas_for_improvement": ["Attempt the question"],
                "is_attempted": False
            }
        else:
            # Basic evaluation for fallback
            marks = max_marks // 2  # Give 50% for attempting
            return {
                "marks_obtained": marks,
                "conceptual_understanding": 0.5,
                "factual_accuracy": 0.5,
                "completeness": 0.5,
                "clarity_expression": 0.5,
                "overall_score": 0.5,
                "detailed_feedback": "Fallback evaluation - AI evaluation unavailable",
                "strengths": ["Answer attempted"],
                "areas_for_improvement": ["AI evaluation recommended"],
                "is_attempted": True
            }
    
    def process(self, state: EvaluationState) -> EvaluationState:
        """Main processing function for AI intelligent evaluation"""
        logger.info("🧠 AI Intelligent Evaluator started")
        
        state["current_stage"] = "AI Intelligent Evaluation"
        state["processing_logs"].append(f"[{datetime.now()}] AI Intelligent Evaluator processing")
        
        evaluations = []
        
        try:
            for question_num, expected_answer in state["answer_key"].items():
                student_answer = state["extracted_answers"].get(question_num, "")
                max_marks = state["question_marks"].get(question_num, 0)
                question_context = state["question_texts"].get(question_num, f"Question {question_num}")
                
                # AI evaluation for each answer
                evaluation = self.ai_evaluate_answer(
                    question_num, student_answer, expected_answer, 
                    question_context, max_marks
                )
                
                # Format result
                result = {
                    "question_id": int(question_num),
                    "question_text": question_context,
                    "student_answer": student_answer,
                    "model_answer": expected_answer,
                    "marks_allocated": max_marks,
                    "marks_obtained": evaluation["marks_obtained"],
                    "conceptual_understanding": evaluation["conceptual_understanding"],
                    "factual_accuracy": evaluation["factual_accuracy"],
                    "completeness": evaluation["completeness"],
                    "clarity_expression": evaluation["clarity_expression"],
                    "overall_score": evaluation["overall_score"],
                    "feedback": evaluation["detailed_feedback"],
                    "strengths": evaluation["strengths"],
                    "weaknesses": evaluation["areas_for_improvement"],
                    "status": "skipped" if not evaluation["is_attempted"] else "evaluated",
                    "ai_evaluation": True
                }
                
                evaluations.append(result)
                
                state["processing_logs"].append(
                    f"[{datetime.now()}] Q{question_num}: {evaluation['marks_obtained']}/{max_marks} marks"
                )
        
            state["evaluations"] = evaluations
            logger.info(f"AI evaluation complete: {len(evaluations)} questions evaluated")
            
        except Exception as e:
            error_msg = f"AI Intelligent Evaluation failed: {str(e)}"
            state["errors"].append(error_msg)
            logger.error(error_msg)
        
        return state

class AIWorkflowManager:
    """Main workflow manager for AI-powered evaluation"""
    
    def __init__(self):
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the complete AI-powered LangGraph workflow"""
        
        workflow = StateGraph(EvaluationState)
        
        # Initialize agents
        text_extractor = AITextExtractionAgent()
        evaluator = AIIntelligentEvaluator()
        
        # Add nodes
        workflow.add_node("ai_text_extraction", text_extractor.process)
        workflow.add_node("ai_evaluation", evaluator.process)
        workflow.add_node("finalize", self._finalize_results)
        
        # Define workflow edges
        workflow.set_entry_point("ai_text_extraction")
        workflow.add_edge("ai_text_extraction", "ai_evaluation")
        workflow.add_edge("ai_evaluation", "finalize")
        workflow.add_edge("finalize", END)
        
        return workflow.compile()
    
    def _finalize_results(self, state: EvaluationState) -> EvaluationState:
        """Finalize the evaluation results"""
        state["current_stage"] = "Finalizing Results"
        state["workflow_complete"] = True
        state["processing_logs"].append(f"[{datetime.now()}] AI workflow completed")
        
        return state
    
    def evaluate(self, pdf_file: Optional[bytes], answer_key: Dict[str, str], 
                question_marks: Dict[str, int], question_texts: Optional[Dict[str, str]] = None,
                manual_answers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Run the complete AI-powered evaluation workflow"""
        
        # Initialize state
        initial_state = EvaluationState(
            pdf_file=pdf_file,
            raw_text="",
            extracted_answers=manual_answers or {},
            answer_key=answer_key,
            question_marks=question_marks,
            question_texts=question_texts or {num: f"Question {num}" for num in question_marks.keys()},
            evaluations=[],
            processing_logs=[],
            errors=[],
            workflow_complete=False,
            evaluation_id=f"ai_eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}",
            start_time=datetime.now(),
            current_stage="Initializing"
        )
        
        try:
            # Run workflow
            logger.info("🚀 Starting AI-powered evaluation workflow")
            final_state = self.workflow.invoke(initial_state)
            
            # Calculate totals
            total_marks = sum(question_marks.values())
            obtained_marks = sum([eval_result["marks_obtained"] for eval_result in final_state["evaluations"]])
            percentage = round((obtained_marks / total_marks * 100), 2) if total_marks > 0 else 0
            
            # Determine grade
            if percentage >= 90:
                grade = "A+"
            elif percentage >= 80:
                grade = "A"
            elif percentage >= 70:
                grade = "B"
            elif percentage >= 60:
                grade = "C"
            elif percentage >= 50:
                grade = "D"
            else:
                grade = "F"
            
            # Format final result
            result = {
                "evaluation_id": final_state["evaluation_id"],
                "total_marks": total_marks,
                "obtained_marks": obtained_marks,
                "percentage": percentage,
                "grade": grade,
                "overall_feedback": f"AI-powered evaluation completed. Processed with advanced AI models for accuracy.",
                "detailed_results": final_state["evaluations"],
                "evaluation_summary": {
                    "total_questions": len(question_marks),
                    "answered_questions": len([e for e in final_state["evaluations"] if e["status"] != "skipped"]),
                    "skipped_questions": len([e for e in final_state["evaluations"] if e["status"] == "skipped"]),
                    "ai_processing_stages": ["AI Text Extraction", "AI Intelligent Evaluation"]
                },
                "processing_info": {
                    "workflow_type": "AI-Powered LangGraph Workflow",
                    "ai_models_used": ["gpt-4 for text extraction", "gpt-4 for evaluation"],
                    "processing_time_seconds": (datetime.now() - final_state["start_time"]).total_seconds(),
                    "processed_at": datetime.now().isoformat(),
                    "processing_logs": final_state["processing_logs"],
                    "errors": final_state["errors"],
                    "api_version": "5.0-ai-powered",
                    "cache_policy": "no_cache_fresh_ai_processing_only"
                }
            }
            
            logger.info(f"✅ AI evaluation completed: {obtained_marks}/{total_marks} ({percentage}%)")
            return result
            
        except Exception as e:
            logger.error(f"❌ AI workflow failed: {e}")
            return {
                "evaluation_id": initial_state["evaluation_id"],
                "error": str(e),
                "workflow_type": "AI-Powered LangGraph Workflow",
                "status": "failed"
            }

# Global workflow instance
ai_workflow_manager = AIWorkflowManager()