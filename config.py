"""
Configuration management for Job Hunter application.
"""
import os
from typing import Optional

# Optional dotenv import
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed. Environment variables will be read directly from system.")

class Config:
    """Configuration class for the Job Hunter application."""
    
    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///job_hunter.db")
    
    # Application Directories
    APPLICATIONS_DIR: str = os.path.join(os.getcwd(), "Applications")
    TEMPLATES_DIR: str = os.path.join(os.getcwd(), "templates")
    DATA_DIR: str = os.path.join(os.getcwd(), "data")
    
    # Job Search Configuration
    DEFAULT_LOCATION: str = os.getenv("DEFAULT_LOCATION", "Remote")
    MAX_JOBS_PER_SEARCH: int = int(os.getenv("MAX_JOBS_PER_SEARCH", "50"))
    
    # Agent Configuration
    AGENT_TEMPERATURE: float = float(os.getenv("AGENT_TEMPERATURE", "0.7"))
    AGENT_MAX_TOKENS: int = int(os.getenv("AGENT_MAX_TOKENS", "2000"))
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate that required configuration is present."""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        return True