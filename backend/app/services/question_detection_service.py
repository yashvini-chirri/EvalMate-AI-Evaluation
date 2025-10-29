"""
Improved Question Detection Service
Focuses on accurately detecting and counting questions from question papers
"""

import re
import logging
from typing import Dict, List, Tuple, Optional
import fitz  # PyMuPDF

logger = logging.getLogger(__name__)

class QuestionDetectionService:
    """Service specifically designed to accurately detect questions from question papers"""
    
    def __init__(self):
        self.name = "Question_Detection_Service"
    
    def analyze_question_paper(self, pdf_bytes: bytes) -> Dict[str, any]:
        """
        Analyze a question paper PDF to detect the correct number of questions
        Returns detailed information about detected questions
        """
        try:
            # Extract text from PDF
            full_text = self._extract_text_from_pdf(pdf_bytes)
            
            # Detect questions using multiple methods
            detected_questions = self._detect_questions_comprehensive(full_text)
            
            # Generate question structure
            question_structure = self._analyze_question_structure(detected_questions, full_text)
            
            result = {
                "total_questions_detected": len(detected_questions),
                "detected_questions": detected_questions,
                "question_structure": question_structure,
                "full_text": full_text,
                "analysis_method": "comprehensive_pattern_matching",
                "confidence_score": self._calculate_confidence(detected_questions, full_text)
            }
            
            logger.info(f"Question analysis complete: {len(detected_questions)} questions detected")
            return result
            
        except Exception as e:
            logger.error(f"Question paper analysis failed: {e}")
            return {
                "total_questions_detected": 0,
                "detected_questions": [],
                "error": str(e),
                "analysis_method": "failed"
            }
    
    def _extract_text_from_pdf(self, pdf_bytes: bytes) -> str:
        """Extract text from PDF with focus on preserving structure"""
        try:
            pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
            full_text = ""
            
            for page_num in range(pdf_document.page_count):
                page = pdf_document.get_page(page_num)
                
                # Extract text preserving layout
                page_text = page.get_text("text")
                
                if page_text.strip():
                    full_text += f"\n=== PAGE {page_num + 1} ===\n{page_text}\n"
                else:
                    # Try alternative extraction methods
                    blocks = page.get_text("dict")
                    page_text = self._extract_from_blocks(blocks)
                    full_text += f"\n=== PAGE {page_num + 1} (STRUCTURED) ===\n{page_text}\n"
            
            pdf_document.close()
            return full_text
            
        except Exception as e:
            logger.error(f"PDF text extraction failed: {e}")
            return ""
    
    def _extract_from_blocks(self, blocks_dict: dict) -> str:
        """Extract text from PyMuPDF blocks dictionary"""
        text = ""
        try:
            if "blocks" in blocks_dict:
                for block in blocks_dict["blocks"]:
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
            logger.warning(f"Block extraction failed: {e}")
        return text
    
    def _detect_questions_comprehensive(self, text: str) -> List[Dict[str, any]]:
        """Comprehensive question detection using multiple patterns"""
        detected_questions = []
        
        # Pattern 1: Standard numbered questions (1., 2., 3., etc.)
        pattern1_questions = self._detect_pattern1(text)
        
        # Pattern 2: Questions with Q prefix (Q1, Q2, Q3, etc.)
        pattern2_questions = self._detect_pattern2(text)
        
        # Pattern 3: Questions with brackets (1), (2), (3), etc.)
        pattern3_questions = self._detect_pattern3(text)
        
        # Pattern 4: Questions with "Question" word (Question 1, Question 2, etc.)
        pattern4_questions = self._detect_pattern4(text)
        
        # Pattern 5: Roman numerals (i., ii., iii., etc.)
        pattern5_questions = self._detect_pattern5(text)
        
        # Combine and deduplicate results
        all_patterns = [
            ("numbered_dots", pattern1_questions),
            ("q_prefix", pattern2_questions),
            ("brackets", pattern3_questions),
            ("question_word", pattern4_questions),
            ("roman_numerals", pattern5_questions)
        ]
        
        # Choose the pattern with most questions detected
        best_pattern = max(all_patterns, key=lambda x: len(x[1]))
        detected_questions = best_pattern[1]
        
        logger.info(f"Question detection patterns: {[(name, len(qs)) for name, qs in all_patterns]}")
        logger.info(f"Selected pattern: {best_pattern[0]} with {len(detected_questions)} questions")
        
        return detected_questions
    
    def _detect_pattern1(self, text: str) -> List[Dict[str, any]]:
        """Detect questions like: 1. What is...?, 2. Explain..., etc."""
        questions = []
        pattern = r'(?:^|\n)\s*(\d+)\.\s*([^0-9\n]*?)(?=\n\s*\d+\.|$)'
        
        matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL)
        for match in matches:
            q_num = match.group(1)
            q_text = match.group(2).strip()
            
            if len(q_text) > 5:  # Minimum question length
                questions.append({
                    "number": q_num,
                    "text": q_text[:200] + "..." if len(q_text) > 200 else q_text,
                    "pattern": "numbered_dots",
                    "start_pos": match.start(),
                    "full_text": q_text
                })
        
        return questions
    
    def _detect_pattern2(self, text: str) -> List[Dict[str, any]]:
        """Detect questions like: Q1, Q2, Q3, etc."""
        questions = []
        pattern = r'(?:^|\n)\s*Q\s*(\d+)[\.\:\s]*([^Q\n]*?)(?=\n\s*Q\s*\d+|$)'
        
        matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL | re.IGNORECASE)
        for match in matches:
            q_num = match.group(1)
            q_text = match.group(2).strip()
            
            if len(q_text) > 5:
                questions.append({
                    "number": q_num,
                    "text": q_text[:200] + "..." if len(q_text) > 200 else q_text,
                    "pattern": "q_prefix",
                    "start_pos": match.start(),
                    "full_text": q_text
                })
        
        return questions
    
    def _detect_pattern3(self, text: str) -> List[Dict[str, any]]:
        """Detect questions like: (1), (2), (3), etc."""
        questions = []
        pattern = r'(?:^|\n)\s*\((\d+)\)\s*([^\(\n]*?)(?=\n\s*\(\d+\)|$)'
        
        matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL)
        for match in matches:
            q_num = match.group(1)
            q_text = match.group(2).strip()
            
            if len(q_text) > 5:
                questions.append({
                    "number": q_num,
                    "text": q_text[:200] + "..." if len(q_text) > 200 else q_text,
                    "pattern": "brackets",
                    "start_pos": match.start(),
                    "full_text": q_text
                })
        
        return questions
    
    def _detect_pattern4(self, text: str) -> List[Dict[str, any]]:
        """Detect questions like: Question 1, Question 2, etc."""
        questions = []
        pattern = r'(?:^|\n)\s*Question\s*(\d+)[\.\:\s]*([^Q\n]*?)(?=\n\s*Question\s*\d+|$)'
        
        matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL | re.IGNORECASE)
        for match in matches:
            q_num = match.group(1)
            q_text = match.group(2).strip()
            
            if len(q_text) > 5:
                questions.append({
                    "number": q_num,
                    "text": q_text[:200] + "..." if len(q_text) > 200 else q_text,
                    "pattern": "question_word",
                    "start_pos": match.start(),
                    "full_text": q_text
                })
        
        return questions
    
    def _detect_pattern5(self, text: str) -> List[Dict[str, any]]:
        """Detect questions like: i., ii., iii., etc."""
        questions = []
        roman_numerals = ['i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x',
                         'xi', 'xii', 'xiii', 'xiv', 'xv', 'xvi', 'xvii', 'xviii', 'xix', 'xx']
        
        for idx, roman in enumerate(roman_numerals, 1):
            pattern = rf'(?:^|\n)\s*{roman}\.\s*([^ivx\n]*?)(?=\n\s*(?:i{{1,3}}|iv|v|vi{{1,3}}|ix|x)\.|$)'
            matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL | re.IGNORECASE)
            
            for match in matches:
                q_text = match.group(1).strip()
                
                if len(q_text) > 5:
                    questions.append({
                        "number": str(idx),
                        "text": q_text[:200] + "..." if len(q_text) > 200 else q_text,
                        "pattern": "roman_numerals",
                        "start_pos": match.start(),
                        "full_text": q_text,
                        "roman": roman
                    })
        
        return questions
    
    def _analyze_question_structure(self, questions: List[Dict], full_text: str) -> Dict[str, any]:
        """Analyze the structure and distribution of detected questions"""
        if not questions:
            return {"structure_type": "no_questions_detected"}
        
        # Check numbering sequence
        numbers = [int(q["number"]) for q in questions]
        numbers.sort()
        
        is_sequential = all(numbers[i] == numbers[i-1] + 1 for i in range(1, len(numbers)))
        
        # Detect marks pattern
        marks_pattern = self._detect_marks_pattern(full_text)
        
        structure = {
            "structure_type": "sequential" if is_sequential else "non_sequential",
            "numbering_pattern": questions[0]["pattern"] if questions else "unknown",
            "question_count": len(questions),
            "number_sequence": numbers,
            "is_sequential": is_sequential,
            "marks_pattern": marks_pattern,
            "average_question_length": sum(len(q["full_text"]) for q in questions) / len(questions) if questions else 0
        }
        
        return structure
    
    def _detect_marks_pattern(self, text: str) -> Dict[str, any]:
        """Detect marks allocation pattern in the question paper"""
        marks_patterns = []
        
        # Pattern: (5 marks), [5 marks], 5 marks, etc.
        patterns = [
            r'\((\d+)\s*marks?\)',
            r'\[(\d+)\s*marks?\]',
            r'(\d+)\s*marks?',
            r'\((\d+)m\)',
            r'\[(\d+)m\]',
            r'(\d+)m\b'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                marks_patterns.extend([int(m) for m in matches])
        
        if marks_patterns:
            return {
                "detected": True,
                "marks_found": marks_patterns,
                "total_marks": sum(marks_patterns),
                "average_marks": sum(marks_patterns) / len(marks_patterns),
                "unique_marks": list(set(marks_patterns))
            }
        else:
            return {"detected": False}
    
    def _calculate_confidence(self, questions: List[Dict], full_text: str) -> float:
        """Calculate confidence score for question detection"""
        if not questions:
            return 0.0
        
        confidence_factors = []
        
        # Factor 1: Sequential numbering
        numbers = [int(q["number"]) for q in questions]
        numbers.sort()
        is_sequential = all(numbers[i] == numbers[i-1] + 1 for i in range(1, len(numbers)))
        confidence_factors.append(0.3 if is_sequential else 0.1)
        
        # Factor 2: Consistent pattern
        patterns = [q["pattern"] for q in questions]
        pattern_consistency = len(set(patterns)) == 1
        confidence_factors.append(0.2 if pattern_consistency else 0.1)
        
        # Factor 3: Question length distribution
        lengths = [len(q["full_text"]) for q in questions]
        avg_length = sum(lengths) / len(lengths)
        length_consistency = all(10 < length < 1000 for length in lengths)
        confidence_factors.append(0.2 if length_consistency and avg_length > 20 else 0.1)
        
        # Factor 4: Marks pattern detection
        marks_pattern = self._detect_marks_pattern(full_text)
        confidence_factors.append(0.2 if marks_pattern["detected"] else 0.1)
        
        # Factor 5: Question count reasonableness
        reasonable_count = 1 <= len(questions) <= 50
        confidence_factors.append(0.1 if reasonable_count else 0.05)
        
        return min(1.0, sum(confidence_factors))

# Global instance
question_detection_service = QuestionDetectionService()