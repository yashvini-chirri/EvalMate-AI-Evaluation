"""
Evaluation Validator Service
Ensures accurate question numbering, score calculation, and result consistency
"""

from typing import Dict, List, Any, Tuple, Optional
import json
import re

class EvaluationValidator:
    """Validates and ensures accuracy of evaluation results"""
    
    def __init__(self):
        self.validation_errors = []
        self.corrected_results = []
    
    def validate_and_correct_evaluation(
        self, 
        student_answers: Dict[str, str],
        answer_key: Dict[str, str], 
        question_marks: Dict[str, int],
        evaluation_results: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Validate evaluation results and correct any inconsistencies
        
        Returns:
            Tuple of (corrected_results, validation_errors)
        """
        
        self.validation_errors = []
        self.corrected_results = []
        
        # Validate input consistency
        self._validate_input_consistency(student_answers, answer_key, question_marks)
        
        # Process each question systematically
        for question_id_str in student_answers.keys():
            try:
                question_id = self._normalize_question_id(question_id_str)
                
                # Get all relevant data for this question
                student_answer = student_answers.get(question_id_str, "").strip()
                correct_answer = answer_key.get(question_id_str, "")
                max_marks = self._parse_marks(question_marks.get(question_id_str, 0))
                
                # Find corresponding evaluation result
                eval_result = self._find_evaluation_result(evaluation_results, question_id, question_id_str)
                
                if eval_result:
                    # Validate and correct the result
                    corrected_result = self._validate_result(
                        eval_result, student_answer, correct_answer, max_marks, question_id
                    )
                    self.corrected_results.append(corrected_result)
                else:
                    # Create missing result
                    self.validation_errors.append(f"Missing evaluation result for question {question_id}")
                    self.corrected_results.append(self._create_missing_result(
                        question_id, student_answer, correct_answer, max_marks
                    ))
                    
            except Exception as e:
                self.validation_errors.append(f"Error processing question {question_id_str}: {str(e)}")
        
        # Sort results by question ID
        self.corrected_results.sort(key=lambda x: x['question_id'])
        
        # Final consistency check
        self._final_consistency_check()
        
        return self.corrected_results, self.validation_errors
    
    def _validate_input_consistency(
        self, 
        student_answers: Dict[str, str],
        answer_key: Dict[str, str],
        question_marks: Dict[str, int]
    ):
        """Validate that all input dictionaries have consistent keys"""
        
        student_keys = set(student_answers.keys())
        answer_keys = set(answer_key.keys())
        marks_keys = set(question_marks.keys())
        
        if student_keys != answer_keys:
            self.validation_errors.append(
                f"Student answers keys {student_keys} don't match answer key keys {answer_keys}"
            )
        
        if student_keys != marks_keys:
            self.validation_errors.append(
                f"Student answers keys {student_keys} don't match marks keys {marks_keys}"
            )
    
    def _normalize_question_id(self, question_id_str: str) -> int:
        """Convert question ID string to integer"""
        try:
            return int(question_id_str)
        except ValueError:
            # Handle cases like "Q1", "question_1", etc.
            numbers = re.findall(r'\d+', question_id_str)
            if numbers:
                return int(numbers[0])
            else:
                raise ValueError(f"Cannot extract question number from '{question_id_str}'")
    
    def _parse_marks(self, marks_value: Any) -> int:
        """Parse marks value ensuring it's an integer"""
        if isinstance(marks_value, str):
            try:
                return int(marks_value)
            except ValueError:
                self.validation_errors.append(f"Invalid marks value: {marks_value}")
                return 0
        elif isinstance(marks_value, (int, float)):
            return int(marks_value)
        else:
            self.validation_errors.append(f"Unexpected marks type: {type(marks_value)}")
            return 0
    
    def _find_evaluation_result(
        self, 
        evaluation_results: List[Dict[str, Any]], 
        question_id: int, 
        question_id_str: str
    ) -> Optional[Dict[str, Any]]:
        """Find evaluation result for given question ID"""
        
        # Try exact question_id match first
        for result in evaluation_results:
            if result.get('question_id') == question_id:
                return result
        
        # Try string key match
        for result in evaluation_results:
            if str(result.get('question_id')) == question_id_str:
                return result
        
        return None
    
    def _validate_result(
        self, 
        eval_result: Dict[str, Any],
        student_answer: str,
        correct_answer: str,
        max_marks: int,
        question_id: int
    ) -> Dict[str, Any]:
        """Validate and correct a single evaluation result"""
        
        corrected_result = eval_result.copy()
        
        # Ensure correct question ID
        corrected_result['question_id'] = question_id
        
        # Validate answer consistency
        if eval_result.get('student_answer', '').strip() != student_answer:
            self.validation_errors.append(
                f"Q{question_id}: Student answer mismatch in evaluation result"
            )
            corrected_result['student_answer'] = student_answer
        
        # Validate marks allocation
        if eval_result.get('marks_allocated', 0) != max_marks:
            self.validation_errors.append(
                f"Q{question_id}: Marks allocation mismatch - expected {max_marks}, got {eval_result.get('marks_allocated', 0)}"
            )
            corrected_result['marks_allocated'] = max_marks
        
        # Validate skipped question handling
        if not student_answer or student_answer == "":
            # Should be marked as skipped with 0 marks
            if eval_result.get('marks_obtained', 0) != 0:
                self.validation_errors.append(
                    f"Q{question_id}: Skipped question incorrectly awarded {eval_result.get('marks_obtained', 0)} marks"
                )
                corrected_result.update({
                    'marks_obtained': 0,
                    'status': 'skipped',
                    'semantic_similarity': 0.0,
                    'conceptual_understanding': 0.0,
                    'factual_accuracy': 0.0,
                    'overall_score': 0.0,
                    'feedback': 'Question not attempted - correctly identified as skipped',
                    'answer_completeness': 0.0,
                    'sentence_coherence': 0.0,
                    'strengths': [],
                    'error_analysis': ['Question not answered']
                })
        else:
            # Validate marks range
            marks_obtained = eval_result.get('marks_obtained', 0)
            if marks_obtained < 0 or marks_obtained > max_marks:
                self.validation_errors.append(
                    f"Q{question_id}: Invalid marks {marks_obtained} (should be 0-{max_marks})"
                )
                corrected_result['marks_obtained'] = max(0, min(marks_obtained, max_marks))
            
            # Ensure status is 'evaluated' for answered questions
            corrected_result['status'] = 'evaluated'
            
            # Validate score consistency
            if 'overall_score' in eval_result and max_marks > 0:
                expected_percentage = marks_obtained / max_marks
                actual_score = eval_result.get('overall_score', 0.0)
                if abs(expected_percentage - actual_score) > 0.1:  # Allow 10% tolerance
                    self.validation_errors.append(
                        f"Q{question_id}: Score inconsistency - marks suggest {expected_percentage:.2f}, overall_score is {actual_score:.2f}"
                    )
        
        # Ensure all required fields are present
        required_fields = [
            'question_id', 'student_answer', 'correct_answer', 'marks_allocated',
            'marks_obtained', 'status', 'evaluation_method'
        ]
        
        for field in required_fields:
            if field not in corrected_result:
                self.validation_errors.append(f"Q{question_id}: Missing required field '{field}'")
                corrected_result[field] = self._get_default_value(field, correct_answer, max_marks)
        
        return corrected_result
    
    def _create_missing_result(
        self, 
        question_id: int, 
        student_answer: str, 
        correct_answer: str, 
        max_marks: int
    ) -> Dict[str, Any]:
        """Create a missing evaluation result"""
        
        if not student_answer or student_answer == "":
            return {
                'question_id': question_id,
                'student_answer': '',
                'correct_answer': correct_answer,
                'marks_allocated': max_marks,
                'marks_obtained': 0,
                'status': 'skipped',
                'semantic_similarity': 0.0,
                'conceptual_understanding': 0.0,
                'factual_accuracy': 0.0,
                'overall_score': 0.0,
                'feedback': 'Question not attempted',
                'evaluation_method': 'validation_service',
                'answer_completeness': 0.0,
                'sentence_coherence': 0.0,
                'strengths': [],
                'error_analysis': ['Question not answered']
            }
        else:
            return {
                'question_id': question_id,
                'student_answer': student_answer,
                'correct_answer': correct_answer,
                'marks_allocated': max_marks,
                'marks_obtained': 0,
                'status': 'evaluation_failed',
                'semantic_similarity': 0.0,
                'conceptual_understanding': 0.0,
                'factual_accuracy': 0.0,
                'overall_score': 0.0,
                'feedback': 'Evaluation failed - result missing',
                'evaluation_method': 'validation_service',
                'answer_completeness': 0.0,
                'sentence_coherence': 0.0,
                'strengths': [],
                'error_analysis': ['Evaluation system error']
            }
    
    def _get_default_value(self, field: str, correct_answer: str, max_marks: int) -> Any:
        """Get default value for missing field"""
        defaults = {
            'question_id': 0,
            'student_answer': '',
            'correct_answer': correct_answer,
            'marks_allocated': max_marks,
            'marks_obtained': 0,
            'status': 'unknown',
            'evaluation_method': 'validation_service',
            'semantic_similarity': 0.0,
            'conceptual_understanding': 0.0,
            'factual_accuracy': 0.0,
            'overall_score': 0.0,
            'feedback': 'Default value - validation error',
            'answer_completeness': 0.0,
            'sentence_coherence': 0.0,
            'strengths': [],
            'error_analysis': ['Missing field']
        }
        return defaults.get(field, '')
    
    def _final_consistency_check(self):
        """Perform final consistency checks on all results"""
        
        total_answered = 0
        total_skipped = 0
        total_marks_obtained = 0
        total_marks_allocated = 0
        
        question_ids = set()
        
        for result in self.corrected_results:
            # Check for duplicate question IDs
            q_id = result['question_id']
            if q_id in question_ids:
                self.validation_errors.append(f"Duplicate question ID: {q_id}")
            question_ids.add(q_id)
            
            # Count statistics
            if result['status'] == 'skipped':
                total_skipped += 1
            elif result['status'] == 'evaluated':
                total_answered += 1
            
            total_marks_obtained += result.get('marks_obtained', 0)
            total_marks_allocated += result.get('marks_allocated', 0)
            
            # Validate individual result consistency
            if result['status'] == 'skipped' and result.get('marks_obtained', 0) > 0:
                self.validation_errors.append(
                    f"Q{q_id}: Skipped question has non-zero marks"
                )
        
        # Update summary information
        self.evaluation_summary = {
            'total_questions': len(self.corrected_results),
            'answered_questions': total_answered,
            'skipped_questions': total_skipped,
            'total_marks_obtained': total_marks_obtained,
            'total_marks_allocated': total_marks_allocated,
            'percentage': (total_marks_obtained / total_marks_allocated * 100) if total_marks_allocated > 0 else 0
        }
    
    def get_validation_report(self) -> Dict[str, Any]:
        """Get detailed validation report"""
        return {
            'validation_passed': len(self.validation_errors) == 0,
            'total_errors': len(self.validation_errors),
            'errors': self.validation_errors,
            'corrected_results_count': len(self.corrected_results),
            'evaluation_summary': getattr(self, 'evaluation_summary', {}),
            'validation_timestamp': str(json.dumps({}))  # Current timestamp would go here
        }