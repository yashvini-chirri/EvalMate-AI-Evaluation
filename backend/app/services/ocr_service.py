import os
from typing import Dict, List, Optional
from google.cloud import vision
import cv2
import numpy as np
from PIL import Image
import pytesseract
import re

class OCRService:
    """Service for optical character recognition and text extraction"""
    
    def __init__(self):
        self.vision_client = None
        self._initialize_ocr()
    
    def _initialize_ocr(self):
        """Initialize OCR services"""
        try:
            # Try to initialize Google Cloud Vision
            if os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
                self.vision_client = vision.ImageAnnotatorClient()
                print("Google Cloud Vision initialized")
        except Exception as e:
            print(f"Google Cloud Vision not available: {e}")
            print("Falling back to Tesseract OCR")
    
    def extract_text(self, image_path: str) -> str:
        """Extract text from image using available OCR service"""
        try:
            if self.vision_client:
                return self._extract_with_google_vision(image_path)
            else:
                return self._extract_with_tesseract(image_path)
        except Exception as e:
            print(f"OCR Error for {image_path}: {e}")
            return ""
    
    def _extract_with_google_vision(self, image_path: str) -> str:
        """Extract text using Google Cloud Vision API"""
        with open(image_path, 'rb') as image_file:
            content = image_file.read()
        
        image = vision.Image(content=content)
        response = self.vision_client.text_detection(image=image)
        texts = response.text_annotations
        
        if texts:
            return texts[0].description
        return ""
    
    def _extract_with_tesseract(self, image_path: str) -> str:
        """Extract text using Tesseract OCR with preprocessing"""
        # Preprocess image for better OCR
        processed_image = self._preprocess_image(image_path)
        
        # Extract text
        text = pytesseract.image_to_string(processed_image, config='--psm 6')
        return text
    
    def _preprocess_image(self, image_path: str) -> np.ndarray:
        """Preprocess image for better OCR accuracy"""
        # Read image
        image = cv2.imread(image_path)
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply gaussian blur
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply threshold
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Denoise
        denoised = cv2.medianBlur(thresh, 3)
        
        return denoised
    
    def parse_answers(self, text: str) -> Dict[str, str]:
        """Parse extracted text to identify question-answer pairs"""
        answers = {}
        
        # Split text into lines
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        current_question = None
        current_answer = []
        
        for line in lines:
            # Look for question numbers (patterns like "1.", "Q1:", "1)", etc.)
            question_match = re.match(r'^(?:Q\.?\s*)?(\d+)[\.\)\:]?\s*(.*)', line, re.IGNORECASE)
            
            if question_match:
                # Save previous answer if exists
                if current_question and current_answer:
                    answers[current_question] = ' '.join(current_answer).strip()
                
                # Start new question
                current_question = question_match.group(1)
                answer_part = question_match.group(2)
                current_answer = [answer_part] if answer_part else []
            else:
                # Continue current answer
                if current_question:
                    current_answer.append(line)
        
        # Save last answer
        if current_question and current_answer:
            answers[current_question] = ' '.join(current_answer).strip()
        
        return answers
    
    def extract_handwriting_regions(self, image_path: str) -> List[Dict]:
        """Identify and extract handwritten regions from the image"""
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Find contours that might represent handwritten text
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        regions = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            # Filter out very small regions
            if w > 50 and h > 20:
                regions.append({
                    'x': x, 'y': y, 'width': w, 'height': h,
                    'area': w * h
                })
        
        # Sort regions by position (top to bottom, left to right)
        regions.sort(key=lambda r: (r['y'], r['x']))
        
        return regions