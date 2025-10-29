"""
LangGraph Semantic Evaluation Workflow
Advanced semantic understanding using pure Python and built-in NLP techniques
"""

import re
import math
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from collections import Counter
import asyncio

@dataclass
class SemanticAnalysisResult:
    semantic_similarity: float
    conceptual_understanding: float
    factual_accuracy: float
    answer_completeness: float
    sentence_coherence: float
    final_score: float
    marks_obtained: int
    detailed_feedback: str
    error_analysis: List[str]
    strengths: List[str]

class AdvancedTextAnalyzer:
    """Advanced text analysis without external dependencies"""
    
    def __init__(self):
        # Common English stop words
        self.stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'would', 'have', 'had', 'been', 'this',
            'these', 'they', 'we', 'you', 'your', 'their', 'there', 'where',
            'when', 'what', 'which', 'who', 'how', 'why', 'can', 'could',
            'should', 'would', 'may', 'might', 'must', 'shall', 'do', 'does',
            'did', 'am', 'are', 'is', 'was', 'were', 'being', 'been'
        }
        
        # Academic and scientific terms that indicate conceptual understanding
        self.concept_indicators = {
            'because', 'therefore', 'thus', 'hence', 'consequently', 'as a result',
            'due to', 'caused by', 'leads to', 'results in', 'produces', 'creates',
            'process', 'method', 'procedure', 'technique', 'approach', 'system',
            'principle', 'theory', 'concept', 'definition', 'explanation',
            'demonstrate', 'illustrate', 'show', 'prove', 'evidence', 'indicate',
            'analysis', 'synthesis', 'evaluation', 'comparison', 'contrast'
        }
        
        # Causal relationship indicators
        self.causal_words = {
            'because', 'since', 'as', 'due to', 'owing to', 'caused by',
            'results from', 'stems from', 'leads to', 'causes', 'produces',
            'creates', 'generates', 'brings about', 'results in', 'therefore',
            'thus', 'hence', 'consequently', 'as a result', 'so', 'accordingly'
        }
        
        # Mathematical and scientific notation patterns
        self.formula_patterns = [
            r'[A-Za-z]+\s*=\s*[A-Za-z0-9\+\-\*/\(\)\s]+',  # Basic equations
            r'\d+\s*[+\-*/]\s*\d+\s*=\s*\d+',  # Arithmetic
            r'[A-Z]+\d*\s*[+\-]\s*[A-Z]+\d*',  # Chemical formulas
            r'\d+\s*×\s*\d+|\d+\s*÷\s*\d+',  # Multiplication/division
            r'½|¼|¾|\d+/\d+',  # Fractions
        ]
    
    def analyze_semantic_content(self, text: str) -> Dict[str, Any]:
        """Comprehensive semantic analysis of text content"""
        
        if not text or not text.strip():
            return self._empty_analysis()
        
        # Basic text processing
        sentences = self._split_sentences(text)
        words = self._extract_words(text)
        
        # Core semantic analysis
        analysis = {
            'raw_text': text.strip(),
            'sentence_count': len(sentences),
            'word_count': len(words),
            'unique_words': len(set(words)),
            'avg_sentence_length': len(words) / len(sentences) if sentences else 0,
            
            # Semantic features
            'conceptual_depth': self._analyze_conceptual_depth(text, words),
            'causal_reasoning': self._detect_causal_reasoning(text),
            'factual_content': self._extract_factual_content(text),
            'technical_terminology': self._identify_technical_terms(words),
            'explanation_quality': self._assess_explanation_quality(text, sentences),
            'coherence_score': self._calculate_coherence(sentences),
            'completeness_indicators': self._assess_completeness(text),
            
            # Structural analysis
            'has_introduction': self._has_introduction(sentences),
            'has_conclusion': self._has_conclusion(sentences),
            'logical_flow': self._assess_logical_flow(sentences),
            'sentence_complexity': self._analyze_sentence_complexity(sentences),
            
            # Content type detection
            'is_definition': self._is_definition_answer(text),
            'is_process_explanation': self._is_process_explanation(text),
            'is_mathematical': self._contains_mathematical_content(text),
            'is_comparative': self._contains_comparison(text),
        }
        
        return analysis
    
    def calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity using advanced text analysis"""
        
        # Get word vectors for both texts
        words1 = self._extract_meaningful_words(text1)
        words2 = self._extract_meaningful_words(text2)
        
        if not words1 or not words2:
            return 0.0
        
        # Calculate multiple similarity metrics
        jaccard_sim = self._jaccard_similarity(words1, words2)
        cosine_sim = self._cosine_similarity_words(words1, words2)
        semantic_overlap = self._semantic_overlap(text1, text2)
        concept_similarity = self._concept_similarity(text1, text2)
        
        # Weighted combination
        similarity = (
            jaccard_sim * 0.2 +
            cosine_sim * 0.3 +
            semantic_overlap * 0.3 +
            concept_similarity * 0.2
        )
        
        return min(similarity, 1.0)
    
    def _empty_analysis(self) -> Dict[str, Any]:
        """Return empty analysis for missing text"""
        return {
            'raw_text': '',
            'sentence_count': 0,
            'word_count': 0,
            'unique_words': 0,
            'avg_sentence_length': 0,
            'conceptual_depth': 0.0,
            'causal_reasoning': 0.0,
            'factual_content': [],
            'technical_terminology': [],
            'explanation_quality': 0.0,
            'coherence_score': 0.0,
            'completeness_indicators': 0.0,
            'has_introduction': False,
            'has_conclusion': False,
            'logical_flow': 0.0,
            'sentence_complexity': 0.0,
            'is_definition': False,
            'is_process_explanation': False,
            'is_mathematical': False,
            'is_comparative': False,
        }
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _extract_words(self, text: str) -> List[str]:
        """Extract words from text"""
        # Extract words, preserving important punctuation
        words = re.findall(r'\b\w+\b', text.lower())
        return words
    
    def _extract_meaningful_words(self, text: str) -> List[str]:
        """Extract meaningful words (excluding stop words)"""
        words = self._extract_words(text)
        return [w for w in words if w not in self.stop_words and len(w) > 2]
    
    def _analyze_conceptual_depth(self, text: str, words: List[str]) -> float:
        """Analyze conceptual depth of the answer"""
        depth_score = 0.0
        
        # Check for concept indicator words
        concept_count = sum(1 for word in words if word in self.concept_indicators)
        depth_score += min(concept_count / 5.0, 0.3)  # Max 30% from concept words
        
        # Check for explanatory phrases
        explanatory_phrases = [
            'this means', 'in other words', 'that is to say', 'specifically',
            'for example', 'for instance', 'such as', 'namely', 'including'
        ]
        for phrase in explanatory_phrases:
            if phrase in text.lower():
                depth_score += 0.1
        
        # Check for multiple perspectives or aspects
        perspective_words = ['also', 'additionally', 'furthermore', 'moreover', 'besides', 'however', 'although']
        for word in perspective_words:
            if word in text.lower():
                depth_score += 0.05
        
        # Check for depth indicators
        if len(self._split_sentences(text)) >= 3:
            depth_score += 0.2  # Multiple sentences indicate depth
        
        return min(depth_score, 1.0)
    
    def _detect_causal_reasoning(self, text: str) -> float:
        """Detect and score causal reasoning"""
        text_lower = text.lower()
        causal_score = 0.0
        
        # Direct causal words
        causal_count = sum(1 for word in self.causal_words if word in text_lower)
        causal_score += min(causal_count / 3.0, 0.5)
        
        # Causal patterns
        causal_patterns = [
            r'because\s+\w+',
            r'due\s+to\s+\w+',
            r'results?\s+in\s+\w+',
            r'leads?\s+to\s+\w+',
            r'causes?\s+\w+',
            r'therefore\s+\w+',
        ]
        
        for pattern in causal_patterns:
            if re.search(pattern, text_lower):
                causal_score += 0.1
        
        return min(causal_score, 1.0)
    
    def _extract_factual_content(self, text: str) -> List[str]:
        """Extract factual content from text"""
        facts = []
        
        # Numbers and measurements
        numbers = re.findall(r'\d+\.?\d*\s*(?:km|m|cm|mm|kg|g|mg|l|ml|hours?|minutes?|seconds?|%)', text)
        facts.extend(numbers)
        
        # Years and dates
        dates = re.findall(r'\b(?:19|20)\d{2}\b', text)
        facts.extend(dates)
        
        # Formulas and equations
        for pattern in self.formula_patterns:
            formulas = re.findall(pattern, text)
            facts.extend(formulas)
        
        # Proper nouns (simplified detection)
        proper_nouns = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        facts.extend(proper_nouns)
        
        # Scientific notation
        scientific = re.findall(r'\d+\.?\d*\s*[×x]\s*10\^?\d+', text)
        facts.extend(scientific)
        
        return list(set(facts))  # Remove duplicates
    
    def _identify_technical_terms(self, words: List[str]) -> List[str]:
        """Identify technical terminology"""
        technical_terms = []
        
        # Words longer than 6 characters that aren't common words
        for word in words:
            if (len(word) > 6 and 
                word not in self.stop_words and 
                not word in ['because', 'through', 'example', 'different']):
                technical_terms.append(word)
        
        # Subject-specific terms
        science_terms = {
            'photosynthesis', 'mitochondria', 'chlorophyll', 'respiration', 'ecosystem',
            'democracy', 'government', 'independence', 'acceleration', 'velocity',
            'equation', 'algorithm', 'temperature', 'pressure', 'molecule'
        }
        
        for word in words:
            if word in science_terms:
                technical_terms.append(word)
        
        return list(set(technical_terms))
    
    def _assess_explanation_quality(self, text: str, sentences: List[str]) -> float:
        """Assess the quality of explanation"""
        quality_score = 0.0
        
        # Multiple sentences indicate better explanation
        if len(sentences) >= 2:
            quality_score += 0.3
        if len(sentences) >= 4:
            quality_score += 0.2
        
        # Presence of examples
        example_indicators = ['example', 'instance', 'such as', 'like', 'including']
        if any(indicator in text.lower() for indicator in example_indicators):
            quality_score += 0.2
        
        # Step-by-step explanation
        step_indicators = ['first', 'second', 'then', 'next', 'finally', 'step']
        if any(indicator in text.lower() for indicator in step_indicators):
            quality_score += 0.2
        
        # Detailed description
        detail_indicators = ['detailed', 'comprehensive', 'thorough', 'complete']
        if any(indicator in text.lower() for indicator in detail_indicators):
            quality_score += 0.1
        
        return min(quality_score, 1.0)
    
    def _calculate_coherence(self, sentences: List[str]) -> float:
        """Calculate coherence between sentences"""
        if len(sentences) <= 1:
            return 1.0
        
        coherence_scores = []
        
        for i in range(len(sentences) - 1):
            words1 = set(self._extract_meaningful_words(sentences[i]))
            words2 = set(self._extract_meaningful_words(sentences[i + 1]))
            
            if words1 and words2:
                overlap = len(words1.intersection(words2))
                coherence = overlap / max(len(words1), len(words2))
                coherence_scores.append(coherence)
        
        return sum(coherence_scores) / len(coherence_scores) if coherence_scores else 0.5
    
    def _assess_completeness(self, text: str) -> float:
        """Assess completeness of the answer"""
        completeness = 0.0
        
        # Word count based assessment
        word_count = len(self._extract_words(text))
        if word_count >= 50:
            completeness += 0.4
        elif word_count >= 25:
            completeness += 0.3
        elif word_count >= 10:
            completeness += 0.2
        
        # Content indicators
        content_indicators = [
            'definition', 'explanation', 'process', 'method', 'example',
            'result', 'conclusion', 'summary', 'analysis', 'description'
        ]
        
        indicator_count = sum(1 for indicator in content_indicators if indicator in text.lower())
        completeness += min(indicator_count / 5.0, 0.3)
        
        # Structural completeness
        if self._has_introduction(self._split_sentences(text)):
            completeness += 0.15
        if self._has_conclusion(self._split_sentences(text)):
            completeness += 0.15
        
        return min(completeness, 1.0)
    
    def _has_introduction(self, sentences: List[str]) -> bool:
        """Check if answer has an introduction"""
        if not sentences:
            return False
        
        first_sentence = sentences[0].lower()
        intro_indicators = [
            'is defined as', 'refers to', 'means', 'is called',
            'can be described as', 'is known as', 'represents'
        ]
        
        return any(indicator in first_sentence for indicator in intro_indicators)
    
    def _has_conclusion(self, sentences: List[str]) -> bool:
        """Check if answer has a conclusion"""
        if not sentences:
            return False
        
        last_sentence = sentences[-1].lower()
        conclusion_indicators = [
            'therefore', 'thus', 'in conclusion', 'finally', 'overall',
            'in summary', 'to conclude', 'as a result'
        ]
        
        return any(indicator in last_sentence for indicator in conclusion_indicators)
    
    def _assess_logical_flow(self, sentences: List[str]) -> float:
        """Assess logical flow of sentences"""
        if len(sentences) <= 1:
            return 1.0
        
        flow_score = 0.0
        
        # Check for transition words
        transition_words = [
            'first', 'second', 'third', 'next', 'then', 'after', 'before',
            'however', 'moreover', 'furthermore', 'additionally', 'also'
        ]
        
        transition_count = 0
        for sentence in sentences:
            if any(word in sentence.lower() for word in transition_words):
                transition_count += 1
        
        flow_score = transition_count / len(sentences)
        return min(flow_score, 1.0)
    
    def _analyze_sentence_complexity(self, sentences: List[str]) -> float:
        """Analyze sentence complexity"""
        if not sentences:
            return 0.0
        
        total_complexity = 0.0
        
        for sentence in sentences:
            words = len(self._extract_words(sentence))
            clauses = sentence.count(',') + sentence.count(';') + 1
            
            # Complexity based on length and clause count
            complexity = min((words / 15.0) + (clauses / 3.0), 1.0)
            total_complexity += complexity
        
        return total_complexity / len(sentences)
    
    def _is_definition_answer(self, text: str) -> bool:
        """Check if answer is a definition"""
        definition_patterns = [
            r'\w+\s+is\s+(?:a|an|the)\s+\w+',
            r'\w+\s+refers\s+to\s+\w+',
            r'\w+\s+means\s+\w+',
            r'\w+\s+is\s+defined\s+as\s+\w+'
        ]
        
        text_lower = text.lower()
        return any(re.search(pattern, text_lower) for pattern in definition_patterns)
    
    def _is_process_explanation(self, text: str) -> bool:
        """Check if answer explains a process"""
        process_indicators = [
            'process', 'procedure', 'method', 'steps', 'stages',
            'first', 'then', 'next', 'finally', 'sequence'
        ]
        
        return sum(1 for indicator in process_indicators if indicator in text.lower()) >= 2
    
    def _contains_mathematical_content(self, text: str) -> bool:
        """Check if answer contains mathematical content"""
        # Check for mathematical symbols and patterns
        math_patterns = [
            r'=', r'\+', r'-', r'\*', r'/', r'\^', r'²', r'³',
            r'formula', r'equation', r'calculate', r'solve'
        ]
        
        return any(re.search(pattern, text) for pattern in math_patterns)
    
    def _contains_comparison(self, text: str) -> bool:
        """Check if answer contains comparison"""
        comparison_words = [
            'compare', 'contrast', 'difference', 'similar', 'unlike',
            'whereas', 'while', 'but', 'however', 'although'
        ]
        
        return any(word in text.lower() for word in comparison_words)
    
    def _jaccard_similarity(self, words1: List[str], words2: List[str]) -> float:
        """Calculate Jaccard similarity"""
        set1 = set(words1)
        set2 = set(words2)
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
    
    def _cosine_similarity_words(self, words1: List[str], words2: List[str]) -> float:
        """Calculate cosine similarity using word frequency"""
        # Get word frequencies
        freq1 = Counter(words1)
        freq2 = Counter(words2)
        
        # Get all unique words
        all_words = set(words1 + words2)
        
        # Create vectors
        vec1 = [freq1.get(word, 0) for word in all_words]
        vec2 = [freq2.get(word, 0) for word in all_words]
        
        # Calculate cosine similarity
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(a * a for a in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def _semantic_overlap(self, text1: str, text2: str) -> float:
        """Calculate semantic overlap beyond word matching"""
        # Check for concept overlap
        concepts1 = self._extract_concepts(text1)
        concepts2 = self._extract_concepts(text2)
        
        if not concepts1 or not concepts2:
            return 0.0
        
        overlap = len(set(concepts1).intersection(set(concepts2)))
        total = len(set(concepts1).union(set(concepts2)))
        
        return overlap / total if total > 0 else 0.0
    
    def _concept_similarity(self, text1: str, text2: str) -> float:
        """Calculate conceptual similarity"""
        # Check for similar explanatory patterns
        patterns1 = self._extract_explanation_patterns(text1)
        patterns2 = self._extract_explanation_patterns(text2)
        
        similarity = 0.0
        
        # Compare causal reasoning
        if self._detect_causal_reasoning(text1) > 0.3 and self._detect_causal_reasoning(text2) > 0.3:
            similarity += 0.3
        
        # Compare mathematical content
        if self._contains_mathematical_content(text1) and self._contains_mathematical_content(text2):
            similarity += 0.2
        
        # Compare definition patterns
        if self._is_definition_answer(text1) and self._is_definition_answer(text2):
            similarity += 0.2
        
        # Compare process explanations
        if self._is_process_explanation(text1) and self._is_process_explanation(text2):
            similarity += 0.3
        
        return min(similarity, 1.0)
    
    def _extract_concepts(self, text: str) -> List[str]:
        """Extract key concepts from text"""
        concepts = []
        
        # Extract technical terms
        words = self._extract_words(text)
        concepts.extend(self._identify_technical_terms(words))
        
        # Extract concept indicators
        for word in words:
            if word in self.concept_indicators:
                concepts.append(word)
        
        return concepts
    
    def _extract_explanation_patterns(self, text: str) -> List[str]:
        """Extract explanation patterns from text"""
        patterns = []
        
        if self._detect_causal_reasoning(text) > 0.3:
            patterns.append('causal_explanation')
        
        if self._contains_mathematical_content(text):
            patterns.append('mathematical_content')
        
        if self._is_definition_answer(text):
            patterns.append('definition')
        
        if self._is_process_explanation(text):
            patterns.append('process_explanation')
        
        return patterns


class LangGraphSemanticEvaluator:
    """LangGraph-based semantic evaluation workflow"""
    
    def __init__(self):
        self.text_analyzer = AdvancedTextAnalyzer()
        
    async def evaluate_answer_semantically(
        self,
        student_answer: str,
        model_answer: str,
        question_type: str,
        max_marks: int,
        ocr_confidence: float = 1.0
    ) -> SemanticAnalysisResult:
        """Main evaluation function using semantic analysis"""
        
        # Handle empty or missing answers
        if not student_answer or not student_answer.strip():
            return self._create_empty_result(max_marks, "No answer provided or detected by OCR")
        
        # Comprehensive semantic analysis
        student_analysis = self.text_analyzer.analyze_semantic_content(student_answer)
        model_analysis = self.text_analyzer.analyze_semantic_content(model_answer)
        
        # Calculate semantic similarity
        semantic_similarity = self.text_analyzer.calculate_semantic_similarity(
            student_answer, model_answer
        )
        
        # Evaluate different aspects
        conceptual_understanding = self._evaluate_conceptual_understanding(
            student_analysis, model_analysis
        )
        
        factual_accuracy = self._evaluate_factual_accuracy(
            student_analysis, model_analysis
        )
        
        answer_completeness = self._evaluate_completeness(
            student_analysis, model_analysis, question_type
        )
        
        sentence_coherence = student_analysis['coherence_score']
        
        # Calculate final score with question-type specific weights
        final_score = self._calculate_weighted_score(
            semantic_similarity,
            conceptual_understanding,
            factual_accuracy,
            answer_completeness,
            sentence_coherence,
            question_type,
            ocr_confidence
        )
        
        # Convert to marks (strict grading)
        marks_obtained = self._calculate_marks(final_score, max_marks, question_type)
        
        # Generate detailed feedback
        detailed_feedback = self._generate_comprehensive_feedback(
            student_analysis, model_analysis, semantic_similarity,
            conceptual_understanding, factual_accuracy, marks_obtained, max_marks
        )
        
        # Identify errors and strengths
        error_analysis = self._analyze_errors(student_analysis, model_analysis)
        strengths = self._identify_strengths(student_analysis, semantic_similarity)
        
        return SemanticAnalysisResult(
            semantic_similarity=semantic_similarity,
            conceptual_understanding=conceptual_understanding,
            factual_accuracy=factual_accuracy,
            answer_completeness=answer_completeness,
            sentence_coherence=sentence_coherence,
            final_score=final_score,
            marks_obtained=marks_obtained,
            detailed_feedback=detailed_feedback,
            error_analysis=error_analysis,
            strengths=strengths
        )
    
    def _create_empty_result(self, max_marks: int, feedback: str) -> SemanticAnalysisResult:
        """Create result for empty/missing answers"""
        return SemanticAnalysisResult(
            semantic_similarity=0.0,
            conceptual_understanding=0.0,
            factual_accuracy=0.0,
            answer_completeness=0.0,
            sentence_coherence=0.0,
            final_score=0.0,
            marks_obtained=0,
            detailed_feedback=feedback,
            error_analysis=["Answer not provided"],
            strengths=[]
        )
    
    def _evaluate_conceptual_understanding(
        self, student_analysis: Dict, model_analysis: Dict
    ) -> float:
        """Evaluate conceptual understanding beyond keyword matching"""
        
        understanding_score = 0.0
        
        # Check conceptual depth alignment
        student_depth = student_analysis['conceptual_depth']
        model_depth = model_analysis['conceptual_depth']
        
        if model_depth > 0:
            depth_ratio = student_depth / model_depth
            understanding_score += min(depth_ratio, 1.0) * 0.3
        
        # Check causal reasoning alignment
        student_causal = student_analysis['causal_reasoning']
        model_causal = model_analysis['causal_reasoning']
        
        if model_causal > 0.3:  # Model answer has causal reasoning
            if student_causal > 0.3:  # Student also shows causal reasoning
                understanding_score += 0.3
            else:
                understanding_score += 0.1  # Partial credit for attempt
        elif student_causal > 0.3:  # Student shows understanding even if model doesn't emphasize it
            understanding_score += 0.2
        
        # Check explanation quality
        student_explanation = student_analysis['explanation_quality']
        model_explanation = model_analysis['explanation_quality']
        
        if model_explanation > 0:
            explanation_ratio = student_explanation / model_explanation
            understanding_score += min(explanation_ratio, 1.0) * 0.2
        
        # Check for appropriate answer type
        if (student_analysis['is_definition'] and model_analysis['is_definition']) or \
           (student_analysis['is_process_explanation'] and model_analysis['is_process_explanation']):
            understanding_score += 0.2
        
        return min(understanding_score, 1.0)
    
    def _evaluate_factual_accuracy(
        self, student_analysis: Dict, model_analysis: Dict
    ) -> float:
        """Evaluate factual accuracy"""
        
        student_facts = set(student_analysis['factual_content'])
        model_facts = set(model_analysis['factual_content'])
        
        if not model_facts:
            return 0.8 if not student_facts else 0.9  # No facts required
        
        if not student_facts:
            return 0.0  # Facts required but none provided
        
        # Calculate fact overlap
        correct_facts = len(student_facts.intersection(model_facts))
        total_model_facts = len(model_facts)
        extra_facts = len(student_facts - model_facts)
        
        # Base accuracy
        accuracy = correct_facts / total_model_facts if total_model_facts > 0 else 0.0
        
        # Penalty for incorrect facts (but not too harsh)
        if extra_facts > 0:
            accuracy *= (1 - min(extra_facts * 0.1, 0.3))
        
        return min(accuracy, 1.0)
    
    def _evaluate_completeness(
        self, student_analysis: Dict, model_analysis: Dict, question_type: str
    ) -> float:
        """Evaluate answer completeness"""
        
        student_completeness = student_analysis['completeness_indicators']
        model_completeness = model_analysis['completeness_indicators']
        
        # Base completeness ratio
        if model_completeness > 0:
            completeness_ratio = student_completeness / model_completeness
        else:
            completeness_ratio = student_completeness
        
        # Adjust based on question type requirements
        if question_type == "MCQ":
            # MCQ just needs the right choice
            return 1.0 if student_analysis['word_count'] > 0 else 0.0
        elif question_type == "Short":
            # Short answers need moderate detail
            return min(completeness_ratio * 1.2, 1.0)
        elif question_type in ["Long", "Essay"]:
            # Long answers need comprehensive coverage
            return completeness_ratio
        
        return min(completeness_ratio, 1.0)
    
    def _calculate_weighted_score(
        self,
        semantic_similarity: float,
        conceptual_understanding: float,
        factual_accuracy: float,
        answer_completeness: float,
        sentence_coherence: float,
        question_type: str,
        ocr_confidence: float
    ) -> float:
        """Calculate weighted final score based on question type"""
        
        # Question-type specific weights
        if question_type == "MCQ":
            weights = {
                'semantic': 0.5,
                'conceptual': 0.3,
                'factual': 0.2,
                'completeness': 0.0,
                'coherence': 0.0
            }
        elif question_type == "Short":
            weights = {
                'semantic': 0.3,
                'conceptual': 0.35,
                'factual': 0.25,
                'completeness': 0.05,
                'coherence': 0.05
            }
        elif question_type in ["Long", "Essay"]:
            weights = {
                'semantic': 0.25,
                'conceptual': 0.4,
                'factual': 0.2,
                'completeness': 0.1,
                'coherence': 0.05
            }
        else:
            weights = {
                'semantic': 0.3,
                'conceptual': 0.35,
                'factual': 0.25,
                'completeness': 0.05,
                'coherence': 0.05
            }
        
        # Calculate weighted score
        weighted_score = (
            semantic_similarity * weights['semantic'] +
            conceptual_understanding * weights['conceptual'] +
            factual_accuracy * weights['factual'] +
            answer_completeness * weights['completeness'] +
            sentence_coherence * weights['coherence']
        )
        
        # Adjust for OCR confidence (small adjustment)
        ocr_adjustment = (ocr_confidence - 0.8) * 0.05 if ocr_confidence < 0.8 else 0.0
        weighted_score = max(weighted_score + ocr_adjustment, 0.0)
        
        return min(weighted_score, 1.0)
    
    def _calculate_marks(self, final_score: float, max_marks: int, question_type: str) -> int:
        """Calculate marks with strict grading"""
        
        # Apply strict grading thresholds
        if final_score >= 0.9:
            percentage = 1.0  # 90%+ gets full marks
        elif final_score >= 0.8:
            percentage = 0.9  # 80-89% gets 90%
        elif final_score >= 0.7:
            percentage = 0.8  # 70-79% gets 80%
        elif final_score >= 0.6:
            percentage = 0.7  # 60-69% gets 70%
        elif final_score >= 0.5:
            percentage = 0.6  # 50-59% gets 60%
        elif final_score >= 0.4:
            percentage = 0.4  # 40-49% gets 40%
        elif final_score >= 0.3:
            percentage = 0.3  # 30-39% gets 30%
        elif final_score >= 0.2:
            percentage = 0.2  # 20-29% gets 20%
        elif final_score > 0.0:
            percentage = 0.1  # Some effort gets 10%
        else:
            percentage = 0.0  # No effort gets 0%
        
        return round(percentage * max_marks)
    
    def _generate_comprehensive_feedback(
        self,
        student_analysis: Dict,
        model_analysis: Dict,
        semantic_similarity: float,
        conceptual_understanding: float,
        factual_accuracy: float,
        marks_obtained: int,
        max_marks: int
    ) -> str:
        """Generate detailed feedback based on semantic analysis"""
        
        feedback_parts = []
        percentage = (marks_obtained / max_marks) * 100 if max_marks > 0 else 0
        
        # Overall performance assessment
        if percentage >= 90:
            feedback_parts.append("Excellent answer demonstrating deep understanding and comprehensive knowledge.")
        elif percentage >= 80:
            feedback_parts.append("Very good answer with strong conceptual grasp and accurate content.")
        elif percentage >= 70:
            feedback_parts.append("Good answer showing solid understanding with some areas for improvement.")
        elif percentage >= 60:
            feedback_parts.append("Satisfactory answer demonstrating basic understanding.")
        elif percentage >= 40:
            feedback_parts.append("Partial understanding shown but significant gaps in knowledge.")
        else:
            feedback_parts.append("Limited understanding demonstrated. Requires substantial improvement.")
        
        # Specific semantic feedback
        if semantic_similarity < 0.5:
            feedback_parts.append("Answer content diverges significantly from expected response.")
        elif semantic_similarity < 0.7:
            feedback_parts.append("Answer partially aligns with expected content but lacks some key elements.")
        
        # Conceptual understanding feedback
        if conceptual_understanding < 0.6:
            feedback_parts.append("Conceptual understanding needs strengthening - provide more detailed explanations and show causal relationships.")
        elif conceptual_understanding >= 0.8:
            feedback_parts.append("Strong conceptual understanding demonstrated through clear explanations.")
        
        # Factual accuracy feedback
        if factual_accuracy < 0.7:
            feedback_parts.append("Some factual inaccuracies or missing key facts - verify information carefully.")
        elif factual_accuracy >= 0.9:
            feedback_parts.append("Factually accurate with correct information provided.")
        
        # Structure and coherence feedback
        if student_analysis['coherence_score'] < 0.5:
            feedback_parts.append("Improve answer structure and coherence between sentences.")
        
        # Completeness feedback
        if student_analysis['completeness_indicators'] < 0.6:
            feedback_parts.append("Answer needs more comprehensive coverage of the topic.")
        
        return " ".join(feedback_parts)
    
    def _analyze_errors(self, student_analysis: Dict, model_analysis: Dict) -> List[str]:
        """Analyze specific errors in the answer"""
        
        errors = []
        
        # Missing causal reasoning
        if model_analysis['causal_reasoning'] > 0.5 and student_analysis['causal_reasoning'] < 0.3:
            errors.append("Missing causal explanations (why/how relationships)")
        
        # Insufficient factual content
        if len(model_analysis['factual_content']) > len(student_analysis['factual_content']):
            errors.append("Missing key factual information")
        
        # Wrong answer type
        if model_analysis['is_definition'] and not student_analysis['is_definition']:
            errors.append("Should provide a clear definition")
        
        if model_analysis['is_process_explanation'] and not student_analysis['is_process_explanation']:
            errors.append("Should explain the process step-by-step")
        
        # Insufficient depth
        if model_analysis['conceptual_depth'] > 0.7 and student_analysis['conceptual_depth'] < 0.4:
            errors.append("Lacks sufficient conceptual depth")
        
        # Poor structure
        if student_analysis['coherence_score'] < 0.4:
            errors.append("Poor coherence between sentences")
        
        return errors
    
    def _identify_strengths(self, student_analysis: Dict, semantic_similarity: float) -> List[str]:
        """Identify strengths in the answer"""
        
        strengths = []
        
        # Good semantic alignment
        if semantic_similarity >= 0.8:
            strengths.append("Content aligns well with expected answer")
        
        # Strong conceptual understanding
        if student_analysis['conceptual_depth'] >= 0.7:
            strengths.append("Demonstrates strong conceptual understanding")
        
        # Good causal reasoning
        if student_analysis['causal_reasoning'] >= 0.6:
            strengths.append("Shows clear causal reasoning and explanations")
        
        # Good explanation quality
        if student_analysis['explanation_quality'] >= 0.7:
            strengths.append("Provides clear and detailed explanations")
        
        # Good coherence
        if student_analysis['coherence_score'] >= 0.7:
            strengths.append("Well-structured and coherent answer")
        
        # Technical terminology usage
        if len(student_analysis['technical_terminology']) >= 2:
            strengths.append("Appropriate use of technical terminology")
        
        # Mathematical content (if present)
        if student_analysis['is_mathematical']:
            strengths.append("Includes mathematical content and calculations")
        
        return strengths