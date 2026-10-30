from typing import Dict, List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="CONTEXTCRAFT_",
        env_file=".env",
        extra="allow",
    )

    APP_NAME: str = "ContextCraft"
    API_V1_PREFIX: str = "/api/v1"
    DATABASE_URL: str = "sqlite:///./contextcraft.db"
    DEBUG: bool = True
    MOCK_MODE: bool = True
    
    # Optional external LLM configuration
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    
    # Default token budgets per agent role
    ROLE_TOKEN_BUDGETS: Dict[str, int] = {
        "supervisor": 200,
        "planner": 300,
        "retriever": 250,
        "executor": 400,
        "critic": 350,
    }

    # Role scoring weights: relevance, recency, importance, role_need
    ROLE_WEIGHTS: Dict[str, Dict[str, float]] = {
        "supervisor": {
            "relevance": 0.35,
            "recency": 0.20,
            "importance": 0.25,
            "role_need": 0.20,
        },
        "planner": {
            "relevance": 0.35,
            "recency": 0.15,
            "importance": 0.25,
            "role_need": 0.25,
        },
        "retriever": {
            "relevance": 0.45,
            "recency": 0.15,
            "importance": 0.20,
            "role_need": 0.20,
        },
        "executor": {
            "relevance": 0.30,
            "recency": 0.30,
            "importance": 0.20,
            "role_need": 0.20,
        },
        "critic": {
            "relevance": 0.25,
            "recency": 0.25,
            "importance": 0.25,
            "role_need": 0.25,
        },
    }

    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]


settings = Settings()
