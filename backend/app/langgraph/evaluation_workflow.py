from typing import Dict, Any, List
import json

class EvaluationState:
    """State object for the evaluation workflow"""
    def __init__(self):
        self.answer_sheet_path: str = ""
        self.question_paper_path: str = ""
        self.answer_key_path: str = ""
        self.reference_book_path: str = ""
        self.test_id: int = 0
        self.student_id: int = 0
        
        # Processing results
        self.ocr_text: str = ""
        self.extracted_answers: Dict[str, str] = {}
        self.question_mapping: Dict[str, str] = {}
        self.answer_key_mapping: Dict[str, str] = {}
        self.evaluation_results: Dict[str, Any] = {}
        self.feedback: str = ""
        self.total_marks: float = 0
        self.obtained_marks: float = 0
        self.percentage: float = 0
        self.grade: str = ""
        
        # Error handling
        self.errors: List[str] = []
        self.status: str = "pending"

class EvaluationWorkflow:
    """Simplified evaluation workflow without LangGraph for development"""
    
    def __init__(self):
        pass
    
    async def run_evaluation(self, evaluation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run a simplified evaluation workflow"""
        
        print(f"Starting evaluation workflow for Test {evaluation_data['test_id']}, Student {evaluation_data['student_id']}")
        
        # Simulate evaluation process
        try:
            # Simulate OCR extraction
            ocr_text = "Sample extracted text from answer sheet"
            
            # Simulate evaluation
            total_marks = 100
            # Random score for demo (replace with actual evaluation logic)
            import random
            obtained_marks = random.randint(60, 95)
            percentage = (obtained_marks / total_marks) * 100
            grade = self._calculate_grade(percentage)
            
            # Generate sample feedback
            feedback = f"Good performance! You scored {obtained_marks}/{total_marks} ({percentage:.1f}%). "
            if percentage >= 80:
                feedback += "Excellent work! Keep it up."
            elif percentage >= 70:
                feedback += "Good effort! Try to improve on weaker areas."
            else:
                feedback += "There's room for improvement. Focus on understanding the concepts better."
            
            return {
                "status": "completed",
                "total_marks": total_marks,
                "obtained_marks": obtained_marks,
                "percentage": percentage,
                "grade": grade,
                "feedback": feedback,
                "evaluation_details": json.dumps({
                    "question_scores": {"1": 8, "2": 9, "3": 7, "4": 8, "5": 9},
                    "detailed_analysis": {
                        "1": {"marks": 8, "feedback": "Good answer"},
                        "2": {"marks": 9, "feedback": "Excellent"},
                        "3": {"marks": 7, "feedback": "Could be better"},
                        "4": {"marks": 8, "feedback": "Well explained"},
                        "5": {"marks": 9, "feedback": "Perfect answer"}
                    }
                }),
                "ocr_text": ocr_text,
                "errors": []
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "total_marks": 0,
                "obtained_marks": 0,
                "percentage": 0,
                "grade": "F",
                "feedback": f"Evaluation failed: {str(e)}",
                "evaluation_details": "{}",
                "ocr_text": "",
                "errors": [str(e)]
            }
    
    def _calculate_grade(self, percentage: float) -> str:
        """Calculate letter grade based on percentage"""
        if percentage >= 90:
            return "A+"
        elif percentage >= 80:
            return "A"
        elif percentage >= 70:
            return "B"
        elif percentage >= 60:
            return "C"
        elif percentage >= 50:
            return "D"
        else:
            return "F"