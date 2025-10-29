import os
from typing import Optional

class Settings:
    # Database
    DATABASE_URL: str = "sqlite:///./evalmate.db"  # Local to backend directory
    
    # JWT
    SECRET_KEY: str = "evalmate-secret-key-for-development-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # OpenAI - Required for AI-powered evaluation
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "sk-demo-key-for-testing")
    
    # Google Cloud Vision
    GOOGLE_APPLICATION_CREDENTIALS: str = None
    
    # File Storage
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # LangGraph
    LANGGRAPH_API_KEY: str = None

settings = Settings()