from typing import Dict, List, Any
import re
from difflib import SequenceMatcher
import openai
import os

class EvaluationService:
    """Service for evaluating student answers against answer keys and reference materials"""
    
    def __init__(self):
        self.openai_client = None
        self._initialize_ai_services()
    
    def _initialize_ai_services(self):
        """Initialize AI services for evaluation"""
        try:
            if os.getenv('OPENAI_API_KEY'):
                openai.api_key = os.getenv('OPENAI_API_KEY')
                self.openai_client = openai
                print("OpenAI API initialized")
        except Exception as e:
            print(f"OpenAI not available: {e}")
    
    def map_questions(self, question_text: str) -> Dict[str, str]:
        """Extract and map questions from question paper"""
        questions = {}
        
        # Split text into lines
        lines = [line.strip() for line in question_text.split('\n') if line.strip()]
        
        current_question = None
        current_content = []
        
        for line in lines:
            # Look for question numbers
            question_match = re.match(r'^(?:Q\.?\s*)?(\d+)[\.\)\:]?\s*(.*)', line, re.IGNORECASE)
            
            if question_match:
                # Save previous question if exists
                if current_question and current_content:
                    questions[current_question] = ' '.join(current_content).strip()
                
                # Start new question
                current_question = question_match.group(1)
                content_part = question_match.group(2)
                current_content = [content_part] if content_part else []
            else:
                # Continue current question
                if current_question:
                    current_content.append(line)
        
        # Save last question
        if current_question and current_content:
            questions[current_question] = ' '.join(current_content).strip()
        
        return questions
    
    def parse_answer_key(self, answer_key_text: str) -> Dict[str, str]:
        """Parse answer key text into question-answer mapping"""
        answers = {}
        
        # Split text into lines
        lines = [line.strip() for line in answer_key_text.split('\n') if line.strip()]
        
        current_question = None
        current_answer = []
        
        for line in lines:
            # Look for question numbers and answers
            answer_match = re.match(r'^(?:Q\.?\s*)?(\d+)[\.\)\:]?\s*(.*)', line, re.IGNORECASE)
            
            if answer_match:
                # Save previous answer if exists
                if current_question and current_answer:
                    answers[current_question] = ' '.join(current_answer).strip()
                
                # Start new answer
                current_question = answer_match.group(1)
                answer_part = answer_match.group(2)
                current_answer = [answer_part] if answer_part else []
            else:
                # Continue current answer
                if current_question:
                    current_answer.append(line)
        
        # Save last answer
        if current_question and current_answer:
            answers[current_question] = ' '.join(current_answer).strip()
        
        return answers
    
    def evaluate_answers(self, student_answers: Dict[str, str], 
                        answer_key: Dict[str, str], 
                        reference_content: str = "") -> Dict[str, Any]:
        """Evaluate student answers against answer key and reference materials"""
        
        evaluation_results = {
            'question_scores': {},
            'total_marks': 0,
            'obtained_marks': 0,
            'detailed_analysis': {}
        }
        
        # Assume each question is worth 10 marks for simplicity
        marks_per_question = 10
        total_questions = len(answer_key)
        evaluation_results['total_marks'] = total_questions * marks_per_question
        
        total_obtained = 0
        
        for question_num, correct_answer in answer_key.items():
            student_answer = student_answers.get(question_num, "")
            
            # Evaluate this question
            question_score = self._evaluate_single_answer(
                student_answer, correct_answer, reference_content, marks_per_question
            )
            
            evaluation_results['question_scores'][question_num] = question_score
            total_obtained += question_score['marks_obtained']
            
            # Detailed analysis
            evaluation_results['detailed_analysis'][question_num] = {
                'student_answer': student_answer,
                'correct_answer': correct_answer,
                'similarity_score': question_score['similarity'],
                'marks_obtained': question_score['marks_obtained'],
                'feedback': question_score['feedback']
            }
        
        evaluation_results['obtained_marks'] = total_obtained
        
        return evaluation_results
    
    def _evaluate_single_answer(self, student_answer: str, correct_answer: str, 
                               reference_content: str, max_marks: int) -> Dict[str, Any]:
        """Evaluate a single answer and provide detailed scoring"""
        
        if not student_answer.strip():
            return {
                'marks_obtained': 0,
                'similarity': 0,
                'feedback': 'No answer provided',
                'keyword_matches': []
            }
        
        # Calculate similarity score
        similarity = self._calculate_similarity(student_answer, correct_answer)
        
        # Extract keywords from correct answer
        correct_keywords = self._extract_keywords(correct_answer)
        student_keywords = self._extract_keywords(student_answer)
        
        # Find keyword matches
        keyword_matches = [kw for kw in correct_keywords if kw.lower() in student_answer.lower()]
        keyword_coverage = len(keyword_matches) / len(correct_keywords) if correct_keywords else 0
        
        # Calculate marks based on similarity and keyword coverage
        combined_score = (similarity + keyword_coverage) / 2
        
        # Apply scoring rubric
        if combined_score >= 0.9:
            marks_obtained = max_marks
        elif combined_score >= 0.8:
            marks_obtained = max_marks * 0.9
        elif combined_score >= 0.6:
            marks_obtained = max_marks * 0.7
        elif combined_score >= 0.4:
            marks_obtained = max_marks * 0.5
        else:
            marks_obtained = max_marks * combined_score
        
        # Generate feedback
        feedback = self._generate_answer_feedback(
            student_answer, correct_answer, similarity, keyword_matches, marks_obtained, max_marks
        )
        
        return {
            'marks_obtained': round(marks_obtained, 1),
            'similarity': round(similarity, 3),
            'keyword_coverage': round(keyword_coverage, 3),
            'feedback': feedback,
            'keyword_matches': keyword_matches
        }
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts"""
        # Normalize texts
        text1_norm = self._normalize_text(text1)
        text2_norm = self._normalize_text(text2)
        
        # Use sequence matcher for similarity
        similarity = SequenceMatcher(None, text1_norm, text2_norm).ratio()
        
        return similarity
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove punctuation
        text = re.sub(r'[^\w\s]', '', text)
        
        return text
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text"""
        # Simple keyword extraction
        words = self._normalize_text(text).split()
        
        # Filter out common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'}
        
        keywords = [word for word in words if len(word) > 2 and word not in stop_words]
        
        return keywords
    
    def _generate_answer_feedback(self, student_answer: str, correct_answer: str, 
                                 similarity: float, keyword_matches: List[str], 
                                 marks_obtained: float, max_marks: int) -> str:
        """Generate detailed feedback for an answer"""
        
        feedback_parts = []
        
        # Overall performance
        percentage = (marks_obtained / max_marks) * 100
        if percentage >= 90:
            feedback_parts.append("Excellent answer!")
        elif percentage >= 70:
            feedback_parts.append("Good answer with room for improvement.")
        elif percentage >= 50:
            feedback_parts.append("Partially correct answer.")
        else:
            feedback_parts.append("Answer needs significant improvement.")
        
        # Specific feedback
        if keyword_matches:
            feedback_parts.append(f"Correctly mentioned: {', '.join(keyword_matches[:3])}")
        
        if similarity < 0.5:
            feedback_parts.append("Consider reviewing the topic and key concepts.")
        
        # Improvement suggestions
        if percentage < 80:
            feedback_parts.append("Try to include more specific details and examples.")
        
        return " ".join(feedback_parts)