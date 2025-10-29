# EvalMate - AI-powered Answer Sheet Evaluation System

## Project Overview
This is an AI-powered Answer Sheet Evaluation System built with LangGraph framework for educational assessments. The system automates grading by analyzing handwritten/printed answer sheets and providing detailed feedback.

## Tech Stack
- **Backend**: FastAPI (Python)
- **Frontend**: React.js with Material-UI
- **AI Framework**: LangGraph for multi-agent evaluation workflow
- **Database**: PostgreSQL for structured data, file storage for documents
- **OCR**: Google Cloud Vision API / Tesseract OCR
- **LLM**: OpenAI GPT-4 for evaluation and feedback generation

## Architecture
- Dual authentication system (Examiners and Students)
- Multi-agent LangGraph workflow for AI evaluation
- RESTful API design with async processing
- Role-based access control
- File upload and storage system

## Development Guidelines
- Use FastAPI for backend API development
- Implement LangGraph agents for OCR, evaluation, and feedback
- Create responsive React components for dashboards
- Follow RESTful API conventions
- Implement proper error handling and logging
- Use environment variables for configuration

## Database Schema
- Students: 10th, 11th, 12th standards (2 sections each, 20 students per section)
- Tests: Metadata for question papers, answer keys, reference materials
- Evaluations: AI evaluation results and feedback
- File uploads: Answer sheets and reference documents