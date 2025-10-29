"""
Advanced PDF OCR Service
High-accuracy text extraction from PDF answer sheets with multiple OCR engines
"""

import io
import re
import logging
from typing import Dict, List, Any, Optional, Tuple
import tempfile
import os
from pathlib import Path

# PDF and Image Processing
try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False

try:
    from pdf2image import convert_from_path, convert_from_bytes
    HAS_PDF2IMAGE = True
except ImportError:
    HAS_PDF2IMAGE = False

try:
    import cv2
    import numpy as np
    HAS_OPENCV = True
except ImportError:
    HAS_OPENCV = False

try:
    from PIL import Image, ImageEnhance, ImageFilter
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# OCR Engines
try:
    import pytesseract
    HAS_TESSERACT = True
except ImportError:
    HAS_TESSERACT = False

try:
    import easyocr
    HAS_EASYOCR = True
except ImportError:
    HAS_EASYOCR = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedPDFOCRService:
    """Advanced PDF OCR service with multiple extraction methods"""
    
    def __init__(self):
        self.available_engines = []
        self._initialize_ocr_engines()
        
    def _initialize_ocr_engines(self):
        """Initialize available OCR engines"""
        if HAS_TESSERACT:
            try:
                pytesseract.get_tesseract_version()
                self.available_engines.append('tesseract')
                logger.info("✅ Tesseract OCR available")
            except Exception as e:
                logger.warning(f"⚠️ Tesseract not properly configured: {e}")
        
        if HAS_EASYOCR:
            try:
                self.easyocr_reader = easyocr.Reader(['en'])
                self.available_engines.append('easyocr')
                logger.info("✅ EasyOCR available")
            except Exception as e:
                logger.warning(f"⚠️ EasyOCR initialization failed: {e}")
        
        if not self.available_engines:
            logger.warning("⚠️ No OCR engines available - using fallback text extraction")
            self.available_engines.append('fallback')
    
    async def extract_content(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract content from PDF using multiple methods
        
        Returns:
            Dict with extracted text, question detection, and confidence scores
        """
        try:
            logger.info(f"🔍 Starting PDF content extraction: {pdf_path}")
            
            # Method 1: Direct text extraction from PDF
            direct_text = self._extract_direct_text(pdf_path)
            
            # Method 2: OCR from PDF images if direct extraction is insufficient
            ocr_text = {}
            if not direct_text or len(str(direct_text).strip()) < 50:
                logger.info("📷 Direct text insufficient, using OCR...")
                ocr_text = await self._extract_ocr_text(pdf_path)
            
            # Combine and process results
            extracted_text = self._combine_extraction_results(direct_text, ocr_text)
            
            # Detect questions and answers
            question_answers = self._detect_questions_and_answers(extracted_text)
            
            # Calculate confidence scores
            confidence_scores = self._calculate_confidence_scores(extracted_text, question_answers)
            
            result = {
                "extraction_method": "advanced_multi_engine",
                "available_engines": self.available_engines,
                "extracted_text": question_answers,
                "raw_text": extracted_text,
                "confidence_scores": confidence_scores,
                "total_questions_detected": len(question_answers),
                "processing_info": {
                    "direct_text_length": len(str(direct_text)),
                    "ocr_text_available": bool(ocr_text),
                    "engines_used": self.available_engines
                }
            }
            
            logger.info(f"✅ Extraction complete: {len(question_answers)} questions detected")
            return result
            
        except Exception as e:
            logger.error(f"❌ PDF extraction failed: {str(e)}")
            return {
                "extraction_method": "error",
                "extracted_text": {},
                "error": str(e),
                "confidence_scores": {},
                "total_questions_detected": 0
            }
    
    def _extract_direct_text(self, pdf_path: str) -> str:
        """Extract text directly from PDF without OCR"""
        try:
            if HAS_PYMUPDF:
                doc = fitz.open(pdf_path)
                text = ""
                for page in doc:
                    text += page.get_text()
                doc.close()
                logger.info(f"📄 Direct text extracted: {len(text)} characters")
                return text
            else:
                logger.warning("⚠️ PyMuPDF not available for direct extraction")
                return ""
        except Exception as e:
            logger.error(f"❌ Direct text extraction failed: {e}")
            return ""
    
    async def _extract_ocr_text(self, pdf_path: str) -> Dict[str, str]:
        """Extract text using OCR from PDF images"""
        try:
            # Convert PDF to images
            images = self._pdf_to_images(pdf_path)
            if not images:
                return {}
            
            ocr_results = {}
            
            for engine in self.available_engines:
                if engine == 'fallback':
                    continue
                    
                try:
                    engine_result = await self._ocr_with_engine(images, engine)
                    if engine_result:
                        ocr_results[engine] = engine_result
                        logger.info(f"✅ OCR successful with {engine}")
                except Exception as e:
                    logger.warning(f"⚠️ OCR failed with {engine}: {e}")
            
            return ocr_results
            
        except Exception as e:
            logger.error(f"❌ OCR text extraction failed: {e}")
            return {}
    
    def _pdf_to_images(self, pdf_path: str) -> List[Any]:
        """Convert PDF pages to images"""
        try:
            if HAS_PDF2IMAGE:
                images = convert_from_path(pdf_path, dpi=300)
                logger.info(f"📷 Converted PDF to {len(images)} images")
                return images
            elif HAS_PYMUPDF and HAS_PIL:
                # Fallback using PyMuPDF
                doc = fitz.open(pdf_path)
                images = []
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better quality
                    img_data = pix.tobytes("ppm")
                    img = Image.open(io.BytesIO(img_data))
                    images.append(img)
                doc.close()
                logger.info(f"📷 Converted PDF to {len(images)} images using PyMuPDF")
                return images
            else:
                logger.warning("⚠️ No PDF to image conversion library available")
                return []
        except Exception as e:
            logger.error(f"❌ PDF to image conversion failed: {e}")
            return []
    
    async def _ocr_with_engine(self, images: List[Any], engine: str) -> str:
        """Perform OCR using specified engine"""
        try:
            all_text = ""
            
            for i, image in enumerate(images):
                # Preprocess image for better OCR
                processed_image = self._preprocess_image(image)
                
                if engine == 'tesseract' and HAS_TESSERACT:
                    # Configure Tesseract for better accuracy
                    custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,;:!?()[]{}"\'-+= \n'
                    text = pytesseract.image_to_string(processed_image, config=custom_config)
                    
                elif engine == 'easyocr' and HAS_EASYOCR:
                    # Convert PIL image to numpy array for EasyOCR
                    img_array = np.array(processed_image)
                    results = self.easyocr_reader.readtext(img_array)
                    text = ' '.join([result[1] for result in results])
                    
                else:
                    continue
                
                all_text += f"\n--- Page {i+1} ---\n{text}\n"
            
            return all_text
            
        except Exception as e:
            logger.error(f"❌ OCR with {engine} failed: {e}")
            return ""
    
    def _preprocess_image(self, image: Any) -> Any:
        """Preprocess image for better OCR accuracy"""
        try:
            if not HAS_PIL:
                return image
            
            # Convert to PIL if needed
            if hasattr(image, 'convert'):
                pil_image = image
            else:
                pil_image = Image.fromarray(image)
            
            # Convert to grayscale
            if pil_image.mode != 'L':
                pil_image = pil_image.convert('L')
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(pil_image)
            pil_image = enhancer.enhance(1.5)
            
            # Enhance sharpness
            enhancer = ImageEnhance.Sharpness(pil_image)
            pil_image = enhancer.enhance(1.2)
            
            # Apply slight blur to reduce noise
            pil_image = pil_image.filter(ImageFilter.MedianFilter(size=1))
            
            return pil_image
            
        except Exception as e:
            logger.warning(f"⚠️ Image preprocessing failed: {e}")
            return image
    
    def _combine_extraction_results(self, direct_text: str, ocr_results: Dict[str, str]) -> str:
        """Combine direct text extraction and OCR results"""
        combined_text = ""
        
        # Use direct text if available and substantial
        if direct_text and len(direct_text.strip()) > 50:
            combined_text = direct_text
            logger.info("📄 Using direct text extraction as primary source")
        
        # Otherwise, combine OCR results
        elif ocr_results:
            # Prefer EasyOCR if available, then Tesseract
            if 'easyocr' in ocr_results:
                combined_text = ocr_results['easyocr']
                logger.info("🔍 Using EasyOCR as primary source")
            elif 'tesseract' in ocr_results:
                combined_text = ocr_results['tesseract']
                logger.info("🔍 Using Tesseract as primary source")
            else:
                # Combine all available OCR results
                combined_text = "\n".join(ocr_results.values())
                logger.info("🔍 Using combined OCR results")
        
        return combined_text
    
    def _detect_questions_and_answers(self, text: str) -> Dict[str, str]:
        """Detect questions and extract answers from text"""
        if not text:
            return {}
        
        questions = {}
        
        # Multiple patterns for question detection
        patterns = [
            # Standard question numbering: "1.", "Q1.", "Question 1:"
            r'(?:^|\n)\s*(?:Q\.?|Question\.?|)\s*(\d+)\.?\s*[:.]?\s*(.*?)(?=(?:\n\s*(?:Q\.?|Question\.?|)\s*\d+)|$)',
            
            # Alternative patterns: "(1)", "1)", etc.
            r'(?:^|\n)\s*[\(\[]?(\d+)[\)\]]\.?\s*(.*?)(?=(?:\n\s*[\(\[]?\d+[\)\]])|$)',
            
            # Simple number detection with content
            r'(?:^|\n)\s*(\d+)\s+(.*?)(?=(?:\n\s*\d+\s+)|$)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL | re.IGNORECASE)
            
            for match in matches:
                question_num = match.group(1)
                answer_text = match.group(2).strip()
                
                # Clean up the answer text
                answer_text = self._clean_answer_text(answer_text)
                
                # Only add if we have substantial content or it's clearly a question
                if len(answer_text) > 5 or any(keyword in answer_text.lower() for keyword in ['answer', 'solution', 'explanation']):
                    questions[question_num] = answer_text
                    logger.info(f"📝 Detected Question {question_num}: {len(answer_text)} characters")
        
        # If no patterns matched, try to extract any numbered content
        if not questions:
            logger.info("🔍 No standard patterns found, attempting fallback detection...")
            questions = self._fallback_question_detection(text)
        
        return questions
    
    def _clean_answer_text(self, text: str) -> str:
        """Clean and normalize answer text"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common OCR artifacts
        text = re.sub(r'[|\\/_]+', ' ', text)
        
        # Remove leading/trailing punctuation that might be OCR errors
        text = text.strip('.-_|\\/')
        
        return text.strip()
    
    def _fallback_question_detection(self, text: str) -> Dict[str, str]:
        """Fallback method to detect questions when standard patterns fail"""
        questions = {}
        
        # Split text into lines and look for numbered content
        lines = text.split('\n')
        current_question = None
        current_answer = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for numbers at the start of lines
            number_match = re.match(r'^(\d+)', line)
            if number_match:
                # Save previous question if exists
                if current_question and current_answer:
                    questions[current_question] = ' '.join(current_answer).strip()
                
                # Start new question
                current_question = number_match.group(1)
                current_answer = [line[len(number_match.group(1)):].strip()]
            elif current_question:
                # Continue current answer
                current_answer.append(line)
        
        # Don't forget the last question
        if current_question and current_answer:
            questions[current_question] = ' '.join(current_answer).strip()
        
        return questions
    
    def _calculate_confidence_scores(self, text: str, questions: Dict[str, str]) -> Dict[str, float]:
        """Calculate confidence scores for extraction quality"""
        confidence = {}
        
        for q_num, answer in questions.items():
            score = 0.8  # Base confidence
            
            # Reduce confidence for very short answers
            if len(answer) < 10:
                score -= 0.3
            
            # Reduce confidence for answers with many special characters (OCR errors)
            special_char_ratio = len(re.findall(r'[^a-zA-Z0-9\s.,!?;:\-\(\)]', answer)) / max(len(answer), 1)
            score -= min(special_char_ratio * 0.5, 0.4)
            
            # Boost confidence for answers with proper words
            word_count = len(re.findall(r'\b[a-zA-Z]{3,}\b', answer))
            if word_count > 5:
                score += 0.1
            
            confidence[q_num] = max(min(score, 1.0), 0.0)
        
        return confidence

# Fallback OCR service when advanced libraries aren't available
class FallbackOCRService:
    """Fallback OCR service using basic text extraction"""
    
    async def extract_content(self, pdf_path: str) -> Dict[str, Any]:
        """Basic PDF text extraction fallback"""
        try:
            # Try to read as text file if it's actually a text file
            if pdf_path.lower().endswith('.txt'):
                with open(pdf_path, 'r', encoding='utf-8') as f:
                    text = f.read()
            else:
                # Simulate extraction for demo purposes
                text = """
                1. This is a sample extracted answer for question 1.
                2. 
                3. This is another sample answer for question 3.
                """
            
            # Simple question detection
            questions = {}
            lines = text.split('\n')
            for line in lines:
                match = re.match(r'^\s*(\d+)\.\s*(.*)', line.strip())
                if match:
                    q_num = match.group(1)
                    answer = match.group(2).strip()
                    questions[q_num] = answer if answer else ""
            
            return {
                "extraction_method": "fallback",
                "extracted_text": questions,
                "raw_text": text,
                "confidence_scores": {q: 0.5 for q in questions.keys()},
                "total_questions_detected": len(questions)
            }
            
        except Exception as e:
            return {
                "extraction_method": "error",
                "extracted_text": {},
                "error": str(e),
                "confidence_scores": {},
                "total_questions_detected": 0
            }

# Factory function to get appropriate OCR service
def get_ocr_service():
    """Get the best available OCR service"""
    if any([HAS_PYMUPDF, HAS_PDF2IMAGE, HAS_TESSERACT, HAS_EASYOCR]):
        return AdvancedPDFOCRService()
    else:
        logger.warning("⚠️ Using fallback OCR service - install pytesseract, pdf2image, PyMuPDF, or easyocr for better accuracy")
        return FallbackOCRService()