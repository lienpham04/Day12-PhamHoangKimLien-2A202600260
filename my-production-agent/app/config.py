from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Settings
    PORT: int = 8000
    ENVIRONMENT: str = "production"
    
    # Security
    AGENT_API_KEY: str = "lienpham04"
    
    # Redis (for Stateless design)
    REDIS_URL: Optional[str] = None
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 10
    
    # Budgeting
    MONTHLY_BUDGET_USD: float = 10.0
    
    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"

settings = Settings()
