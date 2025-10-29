import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.routes import auth, tests, evaluations, students, examiners
from app.api.routes.semantic_evaluation import router as semantic_router
from app.core.config import settings
from app.db.database import engine
from app.db.models import Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="EvalMate API - Advanced Semantic Evaluation System",
    description="""
    Advanced semantic evaluation system using LangGraph workflow for true understanding.
    
    Features:
    - Pure Python semantic analysis (no external dependencies)
    - Sentence-level understanding vs keyword matching
    - Conceptual understanding assessment
    - Factual accuracy verification
    - Proper skipped question detection
    - Intelligent partial marking
    """,
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers first
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(tests.router, prefix="/api/tests", tags=["tests"])
app.include_router(evaluations.router, prefix="/api/evaluations", tags=["evaluations"])
app.include_router(students.router, prefix="/api/students", tags=["students"])
app.include_router(examiners.router, prefix="/api/examiners", tags=["examiners"])
app.include_router(semantic_router, prefix="/api/advanced", tags=["Advanced Semantic Evaluation"])

# Static file routes (must come after API routes to avoid conflicts)
@app.get("/")
async def root():
    """Serve the main web application"""
    return FileResponse("webapp.html")

@app.get("/webapp.html")
async def webapp():
    """Serve the main web application"""
    return FileResponse("webapp.html")

@app.get("/demo.html")
async def demo_page():
    """Serve the semantic evaluation demo page"""
    return FileResponse("demo.html")

@app.get("/api")
async def api_root():
    return {
        "message": "EvalMate API - Advanced Semantic Evaluation System",
        "version": "2.0.0",
        "features": {
            "semantic_understanding": "True sentence-level comprehension using LangGraph workflow",
            "keyword_matching": "Eliminated in favor of semantic analysis",
            "ocr_engine": "Advanced multi-engine OCR with confidence scoring",
            "evaluation_method": "Pure Python NLP with conceptual understanding",
            "skipped_detection": "Intelligent detection vs OCR errors",
            "partial_marking": "Sophisticated partial credit based on understanding level"
        },
        "evaluation_capabilities": [
            "Semantic similarity calculation",
            "Conceptual understanding assessment", 
            "Factual accuracy verification",
            "Causal reasoning detection",
            "Answer completeness evaluation",
            "Sentence coherence analysis",
            "Technical terminology recognition",
            "Mathematical content detection"
        ],
        "endpoints": {
            "/api/advanced/evaluate-semantic": "Main semantic evaluation endpoint",
            "/api/advanced/evaluation-results/{id}": "Get detailed evaluation results",
            "/api/advanced/compare-evaluations": "Compare semantic vs keyword approaches"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "evaluation_system": "semantic_analysis_ready"}

if __name__ == "__main__":
    try:
        print("🚀 Starting EvalMate Server...")
        print("📍 Server will be available at: http://localhost:8000")
        print("🔧 API Documentation: http://localhost:8000/docs")
        print("🎯 Demo Page: http://localhost:8000/demo.html")
        print("📱 Web App: http://localhost:8000/webapp.html")
        
        uvicorn.run(
            "main:app",  # Use string reference for proper reload
            host="0.0.0.0",  # Use 0.0.0.0 for all interfaces
            port=8000,  # Use port 8000 as requested
            reload=False,  # Disable reload for stability
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        print("💡 Try using a different port or check if port 8080 is already in use")
        print("🔍 Run: lsof -i :8080 to check what's using the port")