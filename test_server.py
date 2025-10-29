#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse

# Simple FastAPI app for testing
app = FastAPI(title="EvalMate Test Server")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Test endpoint"""
    try:
        return FileResponse("webapp.html")
    except Exception as e:
        return HTMLResponse(f"<h1>EvalMate Server Running!</h1><p>Error loading webapp.html: {e}</p><p><a href='/demo.html'>Try Demo Page</a></p>")

@app.get("/demo.html")
async def demo():
    """Demo page"""
    try:
        return FileResponse("demo.html")
    except Exception as e:
        return HTMLResponse(f"<h1>Demo Page Error</h1><p>{e}</p>")

@app.get("/test")
async def test():
    """Simple test endpoint"""
    return {"status": "Server is working!", "message": "EvalMate is running"}

@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy", "working_directory": os.getcwd()}

if __name__ == "__main__":
    print("🚀 Starting EvalMate Test Server...")
    print("📍 Server: http://localhost:8000")
    print("🧪 Test: http://localhost:8000/test")
    print("💚 Health: http://localhost:8000/health")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False
    )