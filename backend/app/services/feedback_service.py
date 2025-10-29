from typing import Dict, List, Any
import openai
import os

class FeedbackService:
    """Service for generating personalized feedback using AI"""
    
    def __init__(self):
        self.openai_client = None
        self._initialize_ai_services()
    
    def _initialize_ai_services(self):
        """Initialize AI services"""
        try:
            if os.getenv('OPENAI_API_KEY'):
                openai.api_key = os.getenv('OPENAI_API_KEY')
                self.openai_client = openai
                print("OpenAI API initialized for feedback generation")
        except Exception as e:
            print(f"OpenAI not available for feedback: {e}")
    
    def generate_feedback(self, evaluation_results: Dict[str, Any], 
                         student_answers: Dict[str, str],
                         answer_key: Dict[str, str], 
                         percentage: float) -> str:
        """Generate comprehensive personalized feedback"""
        
        if self.openai_client:
            return self._generate_ai_feedback(evaluation_results, student_answers, answer_key, percentage)
        else:
            return self._generate_rule_based_feedback(evaluation_results, percentage)
    
    def _generate_ai_feedback(self, evaluation_results: Dict[str, Any], 
                             student_answers: Dict[str, str],
                             answer_key: Dict[str, str], 
                             percentage: float) -> str:
        """Generate AI-powered personalized feedback"""
        
        try:
            # Prepare prompt for AI
            prompt = self._create_feedback_prompt(evaluation_results, student_answers, answer_key, percentage)
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert teacher providing constructive feedback on student answers. Be encouraging, specific, and helpful."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"AI feedback generation failed: {e}")
            return self._generate_rule_based_feedback(evaluation_results, percentage)
    
    def _create_feedback_prompt(self, evaluation_results: Dict[str, Any], 
                               student_answers: Dict[str, str],
                               answer_key: Dict[str, str], 
                               percentage: float) -> str:
        """Create prompt for AI feedback generation"""
        
        prompt_parts = [
            f"Student scored {percentage:.1f}% on this test.",
            "\nDetailed Analysis:"
        ]
        
        detailed_analysis = evaluation_results.get('detailed_analysis', {})
        
        for question_num, analysis in detailed_analysis.items():
            marks_obtained = analysis.get('marks_obtained', 0)
            max_marks = 10  # Assuming 10 marks per question
            
            prompt_parts.append(f"\nQuestion {question_num} ({marks_obtained}/{max_marks} marks):")
            prompt_parts.append(f"Student Answer: '{analysis.get('student_answer', 'No answer')}'")
            prompt_parts.append(f"Correct Answer: '{analysis.get('correct_answer', 'Not available')}'")
            prompt_parts.append(f"Similarity Score: {analysis.get('similarity_score', 0):.2f}")
        
        prompt_parts.append(f"\nPlease provide personalized feedback that:")
        prompt_parts.append("1. Acknowledges what the student did well")
        prompt_parts.append("2. Identifies specific areas for improvement")
        prompt_parts.append("3. Suggests study strategies")
        prompt_parts.append("4. Encourages continued learning")
        prompt_parts.append("5. Is constructive and supportive in tone")
        
        return " ".join(prompt_parts)
    
    def _generate_rule_based_feedback(self, evaluation_results: Dict[str, Any], percentage: float) -> str:
        """Generate rule-based feedback when AI is not available"""
        
        feedback_parts = []
        
        # Overall performance feedback
        if percentage >= 90:
            feedback_parts.append("🌟 Excellent work! You have demonstrated outstanding understanding of the subject matter.")
        elif percentage >= 80:
            feedback_parts.append("👍 Great job! You have a strong grasp of most concepts.")
        elif percentage >= 70:
            feedback_parts.append("✅ Good effort! You understand the basics well.")
        elif percentage >= 60:
            feedback_parts.append("👌 Decent work, but there's room for improvement.")
        elif percentage >= 50:
            feedback_parts.append("📈 You're on the right track, but need to strengthen your understanding.")
        else:
            feedback_parts.append("💪 Don't give up! Focus on building fundamental concepts.")
        
        # Analyze performance by question
        detailed_analysis = evaluation_results.get('detailed_analysis', {})
        strong_areas = []
        weak_areas = []
        
        for question_num, analysis in detailed_analysis.items():
            marks_obtained = analysis.get('marks_obtained', 0)
            max_marks = 10
            question_percentage = (marks_obtained / max_marks) * 100
            
            if question_percentage >= 80:
                strong_areas.append(f"Question {question_num}")
            elif question_percentage < 50:
                weak_areas.append(f"Question {question_num}")
        
        # Strengths
        if strong_areas:
            feedback_parts.append(f"\n🎯 Strengths: You performed well on {', '.join(strong_areas[:3])}.")
        
        # Areas for improvement
        if weak_areas:
            feedback_parts.append(f"\n📚 Focus Areas: Review concepts related to {', '.join(weak_areas[:3])}.")
        
        # Study recommendations
        feedback_parts.append(f"\n📖 Study Recommendations:")
        
        if percentage < 70:
            feedback_parts.append("• Review fundamental concepts and practice more examples")
            feedback_parts.append("• Create concept maps to connect different topics")
            feedback_parts.append("• Seek help from teachers or peers for challenging areas")
        
        if percentage >= 70:
            feedback_parts.append("• Focus on accuracy and completeness in your answers")
            feedback_parts.append("• Practice explaining concepts in your own words")
            feedback_parts.append("• Attempt more challenging problems to deepen understanding")
        
        # Encouragement
        feedback_parts.append(f"\n🚀 Keep working hard and you'll continue to improve!")
        
        return " ".join(feedback_parts)
    
    def generate_question_feedback(self, student_answer: str, correct_answer: str, 
                                  marks_obtained: float, max_marks: int) -> str:
        """Generate feedback for individual questions"""
        
        percentage = (marks_obtained / max_marks) * 100
        
        if percentage == 100:
            return "Perfect answer! ✅"
        elif percentage >= 80:
            return "Very good answer with minor gaps. 👍"
        elif percentage >= 60:
            return "Good attempt, but missing some key points. 📝"
        elif percentage >= 40:
            return "Partially correct, needs more detail. 📈"
        else:
            return "Needs significant improvement. Review the topic. 📚"
    
    def get_improvement_suggestions(self, weak_areas: List[str]) -> List[str]:
        """Get specific improvement suggestions based on weak areas"""
        
        suggestions = [
            "📅 Create a study schedule and stick to it",
            "📝 Practice writing detailed answers regularly",
            "🤝 Form study groups with classmates",
            "❓ Ask questions when you don't understand",
            "🔄 Review previous tests and assignments",
            "📖 Use multiple textbooks and resources",
            "🎯 Focus on understanding concepts, not just memorizing",
            "⏰ Practice time management during tests"
        ]
        
        return suggestions[:4]  # Return top 4 suggestions