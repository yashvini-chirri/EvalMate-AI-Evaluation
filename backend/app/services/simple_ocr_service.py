"""
Simple OCR Service for Semantic Evaluation Testing
"""

import re
import json
from typing import Dict, List, Any, Tuple
import asyncio
from pathlib import Path

class SimpleOCRService:
    """Simplified OCR service for demonstration and testing"""
    
    def __init__(self):
        self.min_confidence = 0.7
        self.high_confidence = 0.9
    
    async def extract_content(self, pdf_path: str) -> Dict[str, Any]:
        """Extract content with simulated OCR for testing semantic evaluation"""
        
        # Simulate realistic OCR results based on actual answer content
        # This would be replaced with real OCR in production
        
        sample_answers = {
            "1": "Photosynthesis is the process by which green plants and some bacteria convert light energy into chemical energy. Plants use chlorophyll to capture sunlight and combine carbon dioxide from air with water from soil to produce glucose and oxygen.",
            
            "2": "The water cycle involves evaporation of water from oceans and rivers, condensation of water vapor into clouds, precipitation as rain or snow, and collection back into water bodies. This continuous process helps distribute water across the Earth.",
            
            "3": "Respiration is the process where living organisms break down glucose to release energy for cellular activities. It is the opposite of photosynthesis and produces carbon dioxide and water as waste products.",
            
            "4": "Gravity is a fundamental force that attracts objects with mass toward each other. On Earth, gravity pulls objects toward the center with an acceleration of approximately 9.8 meters per second squared.",
            
            "5": "Democracy is a system of government where power is held by the people through elected representatives. Citizens have the right to vote, express opinions freely, and participate in decision-making processes that affect their lives."
        }
        
        # Simulate some questions being skipped
        answered_questions = [1, 2, 3, 5]  # Question 4 is skipped
        
        extracted_content = {}
        confidence_scores = {}
        
        for q_num in range(1, 6):
            if q_num in answered_questions:
                extracted_content[str(q_num)] = sample_answers[str(q_num)]
                confidence_scores[str(q_num)] = 0.85 + (q_num * 0.02)  # Simulate varying confidence
            else:
                extracted_content[str(q_num)] = ""  # Skipped question
                confidence_scores[str(q_num)] = 0.0
        
        return {
            "extracted_text": extracted_content,
            "confidence_scores": confidence_scores,
            "total_questions_detected": 5,
            "answered_questions": answered_questions,
            "skipped_questions": [4],
            "quality_assessment": {
                "overall_quality": "good",
                "readability_score": 0.82,
                "handwriting_clarity": "clear"
            },
            "processing_info": {
                "method": "simulated_ocr_for_testing",
                "pages_processed": 4,
                "total_text_blocks": 15
            }
        }
    
    async def detect_skipped_questions(self, extracted_content: Dict[str, str]) -> List[int]:
        """Detect which questions were actually skipped vs OCR errors"""
        
        skipped = []
        for q_num, text in extracted_content.items():
            if not text or text.strip() == "":
                skipped.append(int(q_num))
            elif len(text.strip()) < 10:  # Very short text might be OCR error
                # Additional logic to determine if it's actually skipped
                if not any(word in text.lower() for word in ['the', 'is', 'and', 'a', 'to']):
                    skipped.append(int(q_num))
        
        return skipped
    
    def assess_content_quality(self, text: str) -> Dict[str, Any]:
        """Assess the quality of extracted text"""
        
        if not text:
            return {
                "quality": "empty",
                "confidence": 0.0,
                "issues": ["no_text_detected"]
            }
        
        # Basic quality metrics
        word_count = len(text.split())
        sentence_count = len([s for s in text.split('.') if s.strip()])
        avg_word_length = sum(len(word) for word in text.split()) / max(word_count, 1)
        
        quality_score = min(1.0, (word_count / 20) * 0.4 + (sentence_count / 3) * 0.3 + (avg_word_length / 6) * 0.3)
        
        quality_level = "excellent" if quality_score > 0.8 else "good" if quality_score > 0.6 else "fair" if quality_score > 0.4 else "poor"
        
        return {
            "quality": quality_level,
            "confidence": quality_score,
            "word_count": word_count,
            "sentence_count": sentence_count,
            "avg_word_length": round(avg_word_length, 2),
            "issues": [] if quality_score > 0.6 else ["low_content_quality"]
        }