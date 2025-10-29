import os
from typing import Optional

class Settings:
    # Database
    DATABASE_URL: str = "sqlite:///./evalmate.db"  # Local to backend directory
    
    # JWT
    SECRET_KEY: str = "evalmate-secret-key-for-development-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # AI Model Configuration
    AI_MODEL_PROVIDER: str = os.getenv("AI_MODEL_PROVIDER", "ollama")  # ollama, huggingface, anthropic, openai
    AI_MODEL_NAME: str = os.getenv("AI_MODEL_NAME", "llama3.1:8b")  # Default to Llama 3.1 8B
    
    # Ollama Configuration (Local AI)
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    # Hugging Face Configuration
    HUGGINGFACE_API_KEY: str = os.getenv("HUGGINGFACE_API_KEY", "")
    HUGGINGFACE_MODEL: str = os.getenv("HUGGINGFACE_MODEL", "microsoft/DialoGPT-large")
    
    # Anthropic Configuration
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    
    # OpenAI Configuration (Alternative option)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Google Cloud Vision
    GOOGLE_APPLICATION_CREDENTIALS: str = None
    
    # File Storage
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # LangGraph
    LANGGRAPH_API_KEY: str = None

settings = Settings()