"""
Tesseract OCR + Custom Parser Evaluation Service
Cost-effective alternative to GPT-4 using open-source tools
"""

import re
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid
import json
from pathlib import Path
import difflib

# OCR and PDF processing
import fitz  # PyMuPDF
try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    print("Warning: pytesseract not available, using basic OCR fallback")

import io

# Text processing - make NLTK optional
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.stem import PorterStemmer
    NLTK_AVAILABLE = True
    
    # Try to download required NLTK data
    try:
        nltk.data.find('tokenizers/punkt')
        nltk.data.find('corpora/stopwords')
    except LookupError:
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
        except:
            pass
except ImportError:
    NLTK_AVAILABLE = False
    print("Warning: NLTK not available, using basic text processing")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TesseractOCRService:
    """Advanced OCR service using PyMuPDF with fallback (no system Tesseract required)"""
    
    def __init__(self):
        self.name = "PyMuPDF_OCR_Service"
        self.tesseract_available = TESSERACT_AVAILABLE
    
    def extract_text_from_pdf(self, pdf_bytes: bytes) -> str:
        """Extract text from PDF using PyMuPDF (works without system Tesseract)"""
        try:
            pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
            full_text = ""
            
            for page_num in range(pdf_document.page_count):
                page = pdf_document.get_page(page_num)
                
                # Extract digital text first
                digital_text = page.get_text()
                
                if digital_text.strip():
                    # If digital text exists, use it
                    full_text += f"\n--- Page {page_num + 1} ---\n{digital_text}"
                    logger.info(f"Digital text extracted from page {page_num + 1}")
                else:
                    # Try PyMuPDF's built-in OCR-like features
                    try:
                        # Get text with different methods
                        text_dict = page.get_text("dict")
                        extracted_text = self._extract_from_text_dict(text_dict)
                        
                        if extracted_text.strip():
                            full_text += f"\n--- Page {page_num + 1} (PyMuPDF) ---\n{extracted_text}"
                        else:
                            # If still no text, try image extraction with basic processing
                            if self.tesseract_available:
                                ocr_text = self._ocr_page_with_tesseract(page, page_num + 1)
                                full_text += f"\n--- Page {page_num + 1} (OCR) ---\n{ocr_text}"
                            else:
                                # Fallback: indicate that this page needs manual input
                                full_text += f"\n--- Page {page_num + 1} (Manual Input Required) ---\n[No text detected - please provide answers manually]"
                                
                        logger.info(f"Text extracted from page {page_num + 1} using fallback methods")
                    except Exception as e:
                        logger.warning(f"Text extraction failed for page {page_num + 1}: {e}")
                        full_text += f"\n--- Page {page_num + 1} (Error) ---\n[Text extraction failed]"
            
            pdf_document.close()
            return full_text
            
        except Exception as e:
            logger.error(f"PDF text extraction failed: {e}")
            return ""
    
    def _extract_from_text_dict(self, text_dict: dict) -> str:
        """Extract text from PyMuPDF text dictionary"""
        text = ""
        try:
            if "blocks" in text_dict:
                for block in text_dict["blocks"]:
                    if "lines" in block:
                        for line in block["lines"]:
                            if "spans" in line:
                                line_text = ""
                                for span in line["spans"]:
                                    if "text" in span:
                                        line_text += span["text"]
                                if line_text.strip():
                                    text += line_text + "\n"
        except Exception as e:
            logger.warning(f"Text dictionary extraction failed: {e}")
        
        return text
    
    def _ocr_page_with_tesseract(self, page, page_num: int) -> str:
        """Extract text from a single page using Tesseract OCR (if available)"""
        if not self.tesseract_available:
            return "[Tesseract not available - manual input required]"
            
        try:
            # Convert page to image
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x scaling for better OCR
            img_data = pix.tobytes("png")
            
            # Convert to PIL Image
            image = Image.open(io.BytesIO(img_data))
            
            # Preprocess image for better OCR
            image = self._preprocess_image(image)
            
            # Run Tesseract OCR
            text = pytesseract.image_to_string(image, config='--oem 3 --psm 6')
            
            return text
            
        except Exception as e:
            logger.error(f"OCR failed for page {page_num}: {e}")
            return f"[OCR Error on page {page_num} - manual input required]"
    
    def _preprocess_image(self, image) -> any:
        """Preprocess image for better OCR accuracy (if PIL available)"""
        try:
            # Convert to grayscale
            if hasattr(image, 'mode') and image.mode != 'L':
                image = image.convert('L')
            return image
        except Exception as e:
            logger.warning(f"Image preprocessing failed: {e}")
            return image

class CustomAnswerParser:
    """Custom parser for extracting answers from OCR text (works without NLTK)"""
    
    def __init__(self):
        self.name = "Custom_Answer_Parser"
        self.nltk_available = NLTK_AVAILABLE
        
        # Initialize NLTK components if available
        if self.nltk_available:
            try:
                self.stemmer = PorterStemmer()
                self.stop_words = set(stopwords.words('english'))
            except:
                self.nltk_available = False
                self._init_fallback()
        else:
            self._init_fallback()
    
    def _init_fallback(self):
        """Initialize fallback text processing without NLTK"""
        self.stemmer = None
        # Common English stop words
        self.stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'were', 'will', 'with', 'or', 'but', 'this', 'they',
            'have', 'had', 'what', 'when', 'where', 'who', 'which', 'why', 'how'
        }
    
    def extract_answers(self, text: str, question_marks: Dict[str, int]) -> Dict[str, str]:
        """Parse OCR text to extract answers by question numbers"""
        answers = {}
        
        # Clean and normalize text
        cleaned_text = self._clean_text(text)
        
        # Multiple patterns for question detection
        for q_num in question_marks.keys():
            answer = self._extract_single_answer(cleaned_text, q_num)
            answers[q_num] = answer
            
        logger.info(f"Parser extracted {len(answers)} answers")
        return answers
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize OCR text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Fix common OCR errors
        text = text.replace('|', 'I')  # Common OCR mistake
        text = text.replace('0', 'O')  # In some contexts (but be careful)
        text = text.replace('@', 'a')  # Common mistake
        text = text.replace('rn', 'm')  # Common OCR error
        text = text.replace('li', 'h')  # Common OCR error
        text = text.replace('1', 'l')  # In text contexts
        
        # Fix spacing around punctuation
        text = re.sub(r'\s+([.!?])', r'\1', text)
        text = re.sub(r'([.!?])\s*([A-Z])', r'\1 \2', text)
        
        return text.strip()
    
    def _extract_single_answer(self, text: str, q_num: str) -> str:
        """Extract answer for a specific question number"""
        
        # Multiple question patterns to try
        patterns = [
            # Standard patterns - more flexible
            rf"(?:^|\n)\s*{q_num}[\.\)\:\s]+(.*?)(?=\n\s*(?:\d+[\.\)\:]|\Z))",
            rf"(?:^|\n)\s*Q[\s\.]?{q_num}[\.\)\:\s]+(.*?)(?=\n\s*(?:Q[\s\.]?\d+|\Z))",
            rf"(?:^|\n)\s*Question[\s\.]?{q_num}[\.\)\:\s]+(.*?)(?=\n\s*(?:Question[\s\.]?\d+|\Z))",
            
            # More flexible patterns with answer keywords
            rf"(?:^|\n)\s*{q_num}[\.\)\:\s]+.*?(?:ans|answer|solution)[\:\.\s]*(.*?)(?=\n\s*\d+[\.\)\:]|\Z)",
            rf"(?:^|\n)[^\w]*{q_num}[^\w]+(.*?)(?=\n[^\w]*\d+[^\w]|\Z)",
            
            # Pattern for handwritten/OCR text with common errors
            rf"(?:^|\n)\s*[O0]?{q_num}[\.\)\:\s]+(.*?)(?=\n\s*(?:[O0]?\d+[\.\)\:]|\Z))",
        ]
        
        for pattern in patterns:
            try:
                match = re.search(pattern, text, re.DOTALL | re.IGNORECASE | re.MULTILINE)
                if match:
                    answer = match.group(1).strip()
                    if answer and len(answer) > 3:  # Minimum answer length
                        # Clean up the extracted answer
                        answer = self._clean_answer(answer)
                        if answer:
                            return answer
            except Exception as e:
                logger.warning(f"Pattern matching failed for Q{q_num}: {e}")
                continue
        
        # If no pattern matches, try alternative extraction
        return self._fallback_extraction(text, q_num)
    
    def _clean_answer(self, answer: str) -> str:
        """Clean extracted answer text"""
        # Remove leading/trailing punctuation and whitespace
        answer = re.sub(r'^[\s\.\-\:\)]+', '', answer)
        answer = re.sub(r'[\s\.\-\:]+$', '', answer)
        
        # Remove question numbers from the beginning of answers
        answer = re.sub(r'^\d+[\.\)\:\s]+', '', answer)
        
        # Limit answer length (prevent extracting multiple questions)
        if self.nltk_available:
            try:
                sentences = sent_tokenize(answer)
            except:
                sentences = self._basic_sentence_split(answer)
        else:
            sentences = self._basic_sentence_split(answer)
            
        if len(sentences) > 5:  # Limit to 5 sentences max
            answer = ' '.join(sentences[:5])
        
        return answer.strip()
    
    def _basic_sentence_split(self, text: str) -> list:
        """Basic sentence splitting without NLTK"""
        if not text:
            return []
        
        # Split on sentence endings
        import re
        sentences = re.split(r'[.!?]+', text)
        # Clean up and filter empty sentences
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences
    
    def _fallback_extraction(self, text: str, q_num: str) -> str:
        """Fallback method when standard patterns fail"""
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            # Look for question number in line
            if re.search(rf'\b{q_num}\b', line):
                # Extract text from this line and next few lines
                answer_lines = []
                for j in range(i, min(i + 5, len(lines))):
                    if j > i and re.search(r'\b\d+\b', lines[j]) and not answer_lines:
                        # Stop if we hit another question number
                        break
                    answer_lines.append(lines[j])
                
                if answer_lines:
                    answer = ' '.join(answer_lines)
                    # Remove the question number part
                    answer = re.sub(rf'\b{q_num}[\.\)\:\s]*', '', answer, count=1)
                    return self._clean_answer(answer)
        
        return ""

class IntelligentEvaluator:
    """Custom evaluation engine using text similarity and keyword matching (works without NLTK)"""
    
    def __init__(self):
        self.name = "Intelligent_Evaluator"
        self.nltk_available = NLTK_AVAILABLE
        
        # Initialize NLTK components if available
        if self.nltk_available:
            try:
                self.stemmer = PorterStemmer()
                self.stop_words = set(stopwords.words('english'))
            except:
                self.nltk_available = False
                self._init_fallback()
        else:
            self._init_fallback()
    
    def _init_fallback(self):
        """Initialize fallback text processing without NLTK"""
        self.stemmer = None
        # Common English stop words
        self.stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'were', 'will', 'with', 'or', 'but', 'this', 'they',
            'have', 'had', 'what', 'when', 'where', 'who', 'which', 'why', 'how'
        }
    
    def evaluate_answer(self, question_num: str, student_answer: str, model_answer: str, 
                       question_context: str, max_marks: int) -> Dict[str, Any]:
        """Evaluate student answer using intelligent text analysis"""
        
        if not student_answer.strip():
            return self._empty_answer_result(max_marks)
        
        # Normalize texts
        student_normalized = self._normalize_text(student_answer)
        model_normalized = self._normalize_text(model_answer)
        
        # Calculate similarity scores
        similarity_score = self._calculate_similarity(student_normalized, model_normalized)
        keyword_score = self._calculate_keyword_match(student_normalized, model_normalized)
        concept_score = self._calculate_concept_score(student_normalized, model_normalized)
        completeness_score = self._calculate_completeness(student_answer, model_answer)
        
        # Combine scores with weights
        overall_score = (
            similarity_score * 0.3 +      # 30% text similarity
            keyword_score * 0.25 +        # 25% keyword matching
            concept_score * 0.25 +        # 25% concept matching
            completeness_score * 0.2      # 20% completeness
        )
        
        # Calculate marks
        marks_obtained = max(0, min(max_marks, int(overall_score * max_marks)))
        
        # Generate feedback
        feedback = self._generate_feedback(
            similarity_score, keyword_score, concept_score, 
            completeness_score, overall_score, marks_obtained, max_marks
        )
        
        # Identify strengths and weaknesses
        strengths, weaknesses = self._analyze_strengths_weaknesses(
            student_normalized, model_normalized, similarity_score, 
            keyword_score, concept_score, completeness_score
        )
        
        return {
            "marks_obtained": marks_obtained,
            "conceptual_understanding": concept_score,
            "factual_accuracy": keyword_score,
            "completeness": completeness_score,
            "clarity_expression": similarity_score,
            "overall_score": overall_score,
            "detailed_feedback": feedback,
            "strengths": strengths,
            "areas_for_improvement": weaknesses,
            "is_attempted": True,
            "evaluation_method": "Tesseract_OCR_Custom_Parser"
        }
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison (works with or without NLTK)"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove punctuation and extra whitespace
        import re
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        
        # Tokenize and remove stop words
        if self.nltk_available:
            try:
                words = word_tokenize(text)
                words = [self.stemmer.stem(word) for word in words if word not in self.stop_words and len(word) > 2]
                return ' '.join(words)
            except:
                # Fall back to basic processing
                pass
        
        # Basic processing without NLTK
        words = text.split()
        words = [word for word in words if word not in self.stop_words and len(word) > 2]
        return ' '.join(words)
    
    def _calculate_similarity(self, student_text: str, model_text: str) -> float:
        """Calculate text similarity using difflib"""
        return difflib.SequenceMatcher(None, student_text, model_text).ratio()
    
    def _calculate_keyword_match(self, student_text: str, model_text: str) -> float:
        """Calculate keyword matching score"""
        student_words = set(student_text.split())
        model_words = set(model_text.split())
        
        if not model_words:
            return 0.0
        
        common_words = student_words.intersection(model_words)
        return len(common_words) / len(model_words)
    
    def _calculate_concept_score(self, student_text: str, model_text: str) -> float:
        """Calculate conceptual understanding score"""
        # Extract important concepts (longer words, technical terms)
        student_concepts = set([word for word in student_text.split() if len(word) > 4])
        model_concepts = set([word for word in model_text.split() if len(word) > 4])
        
        if not model_concepts:
            return 0.7  # Default score if no concepts identified
        
        common_concepts = student_concepts.intersection(model_concepts)
        concept_score = len(common_concepts) / len(model_concepts)
        
        # Bonus for using additional relevant concepts
        if len(student_concepts) > len(model_concepts):
            concept_score = min(1.0, concept_score * 1.1)
        
        return concept_score
    
    def _calculate_completeness(self, student_answer: str, model_answer: str) -> float:
        """Calculate answer completeness"""
        student_length = len(student_answer.split())
        model_length = len(model_answer.split())
        
        if model_length == 0:
            return 0.5
        
        ratio = student_length / model_length
        
        # Optimal range is 70-130% of model answer length
        if 0.7 <= ratio <= 1.3:
            return 1.0
        elif ratio < 0.7:
            return ratio / 0.7  # Penalize short answers
        else:
            return max(0.5, 1.3 / ratio)  # Penalize overly long answers
    
    def _generate_feedback(self, similarity: float, keyword: float, concept: float, 
                          completeness: float, overall: float, marks: int, max_marks: int) -> str:
        """Generate detailed feedback based on scores"""
        feedback_parts = []
        
        feedback_parts.append(f"Score: {marks}/{max_marks} marks ({overall*100:.1f}%)")
        
        if overall >= 0.9:
            feedback_parts.append("Excellent answer demonstrating strong understanding.")
        elif overall >= 0.7:
            feedback_parts.append("Good answer with solid understanding.")
        elif overall >= 0.5:
            feedback_parts.append("Adequate answer showing basic understanding.")
        else:
            feedback_parts.append("Answer needs significant improvement.")
        
        # Specific feedback
        if similarity >= 0.8:
            feedback_parts.append("Well-structured and clearly expressed.")
        elif similarity < 0.5:
            feedback_parts.append("Consider improving clarity and organization.")
        
        if keyword >= 0.7:
            feedback_parts.append("Good use of key terminology.")
        elif keyword < 0.5:
            feedback_parts.append("Include more relevant keywords and terminology.")
        
        if concept >= 0.7:
            feedback_parts.append("Strong conceptual understanding demonstrated.")
        elif concept < 0.5:
            feedback_parts.append("Focus on understanding core concepts.")
        
        return " ".join(feedback_parts)
    
    def _analyze_strengths_weaknesses(self, student_text: str, model_text: str, 
                                    similarity: float, keyword: float, concept: float, 
                                    completeness: float) -> tuple:
        """Identify strengths and areas for improvement"""
        strengths = []
        weaknesses = []
        
        # Analyze strengths
        if similarity >= 0.7:
            strengths.append("Clear and well-organized response")
        if keyword >= 0.7:
            strengths.append("Good use of relevant terminology")
        if concept >= 0.7:
            strengths.append("Strong conceptual understanding")
        if completeness >= 0.8:
            strengths.append("Comprehensive answer")
        if len(student_text.split()) >= 10:
            strengths.append("Detailed explanation provided")
        
        # Analyze weaknesses
        if similarity < 0.5:
            weaknesses.append("Improve answer structure and clarity")
        if keyword < 0.5:
            weaknesses.append("Include more specific terminology")
        if concept < 0.5:
            weaknesses.append("Strengthen understanding of key concepts")
        if completeness < 0.6:
            weaknesses.append("Provide more detailed explanation")
        
        # Default entries if none found
        if not strengths:
            strengths.append("Answer was attempted")
        if not weaknesses:
            weaknesses.append("Continue practicing to maintain quality")
        
        return strengths, weaknesses
    
    def _empty_answer_result(self, max_marks: int) -> Dict[str, Any]:
        """Return result for empty/not attempted answers"""
        return {
            "marks_obtained": 0,
            "conceptual_understanding": 0.0,
            "factual_accuracy": 0.0,
            "completeness": 0.0,
            "clarity_expression": 0.0,
            "overall_score": 0.0,
            "detailed_feedback": "Question not attempted",
            "strengths": [],
            "areas_for_improvement": ["Attempt the question", "Read question carefully"],
            "is_attempted": False,
            "evaluation_method": "Tesseract_OCR_Custom_Parser"
        }

class TesseractEvaluationService:
    """Main service combining Tesseract OCR and custom evaluation"""
    
    def __init__(self):
        self.ocr_service = TesseractOCRService()
        self.parser = CustomAnswerParser()
        self.evaluator = IntelligentEvaluator()
    
    def evaluate(self, pdf_file: Optional[bytes], answer_key: Dict[str, str], 
                question_marks: Dict[str, int], question_texts: Optional[Dict[str, str]] = None,
                manual_answers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Complete evaluation using Tesseract OCR and custom parser"""
        
        start_time = datetime.now()
        evaluation_id = f"tesseract_eval_{start_time.strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        processing_logs = []
        errors = []
        
        try:
            # Step 1: Extract text using Tesseract OCR
            if pdf_file:
                processing_logs.append(f"[{datetime.now()}] Starting Tesseract OCR extraction")
                raw_text = self.ocr_service.extract_text_from_pdf(pdf_file)
                
                # Step 2: Parse answers from extracted text
                processing_logs.append(f"[{datetime.now()}] Parsing answers from OCR text")
                extracted_answers = self.parser.extract_answers(raw_text, question_marks)
            else:
                # Use manual answers if provided
                extracted_answers = manual_answers or {}
                raw_text = "Manual input mode"
                processing_logs.append(f"[{datetime.now()}] Processing manual input")
            
            # Step 3: Evaluate each answer
            processing_logs.append(f"[{datetime.now()}] Starting intelligent evaluation")
            evaluations = []
            
            for question_num, expected_answer in answer_key.items():
                student_answer = extracted_answers.get(question_num, "")
                max_marks = question_marks.get(question_num, 0)
                question_context = question_texts.get(question_num, f"Question {question_num}") if question_texts else f"Question {question_num}"
                
                # Evaluate using custom evaluator
                evaluation = self.evaluator.evaluate_answer(
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
                    "evaluation_method": "Tesseract_OCR_Custom_Parser"
                }
                
                evaluations.append(result)
                processing_logs.append(f"[{datetime.now()}] Q{question_num}: {evaluation['marks_obtained']}/{max_marks} marks")
            
            # Calculate totals
            total_marks = sum(question_marks.values())
            obtained_marks = sum([eval_result["marks_obtained"] for eval_result in evaluations])
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
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Format final result
            result = {
                "evaluation_id": evaluation_id,
                "total_marks": total_marks,
                "obtained_marks": obtained_marks,
                "percentage": percentage,
                "grade": grade,
                "overall_feedback": f"Evaluation completed using Tesseract OCR and intelligent custom parser. Processing time: {processing_time:.2f} seconds.",
                "detailed_results": evaluations,
                "evaluation_summary": {
                    "total_questions": len(question_marks),
                    "answered_questions": len([e for e in evaluations if e["status"] != "skipped"]),
                    "skipped_questions": len([e for e in evaluations if e["status"] == "skipped"]),
                    "processing_stages": ["Tesseract OCR", "Custom Parser", "Intelligent Evaluator"]
                },
                "processing_info": {
                    "workflow_type": "Tesseract_OCR_Custom_Parser",
                    "ocr_engine": "Tesseract",
                    "evaluation_method": "Custom_Intelligent_Evaluator",
                    "processing_time_seconds": processing_time,
                    "processed_at": datetime.now().isoformat(),
                    "processing_logs": processing_logs,
                    "errors": errors,
                    "api_version": "6.0-tesseract-parser",
                    "cost": "Free - No API costs"
                }
            }
            
            logger.info(f"✅ Tesseract evaluation completed: {obtained_marks}/{total_marks} ({percentage}%)")
            return result
            
        except Exception as e:
            error_msg = f"Tesseract evaluation failed: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)
            
            return {
                "evaluation_id": evaluation_id,
                "error": error_msg,
                "workflow_type": "Tesseract_OCR_Custom_Parser",
                "status": "failed",
                "processing_logs": processing_logs,
                "errors": errors
            }

# Global service instance
tesseract_evaluation_service = TesseractEvaluationService()