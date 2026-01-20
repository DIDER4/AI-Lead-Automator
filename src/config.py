"""
Configuration Management Module
Handles all application configuration with security best practices
"""

import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
import logging

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Security files
KEY_FILE = DATA_DIR / "secret.key"
CONFIG_FILE = DATA_DIR / "config.encrypted"
LEADS_FILE = DATA_DIR / "leads_data.json"

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = LOGS_DIR / "app.log"


@dataclass
class AppConfig:
    """Application configuration data class"""
    
    # API Keys (never log these)
    firecrawl_api_key: str = ""
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    
    # AI Provider
    ai_provider: str = "OpenAI"  # OpenAI or Anthropic
    
    # User Profile
    my_website: str = ""
    my_value_proposition: str = ""
    my_icp: str = ""
    
    # API Settings
    firecrawl_timeout: int = 60
    ai_timeout: int = 60
    max_retries: int = 3
    
    # Rate Limiting
    rate_limit_delay: float = 1.0  # seconds between bulk requests
    
    # Security
    min_password_length: int = 8
    session_timeout: int = 3600  # seconds
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        if self.ai_provider not in ["OpenAI", "Anthropic"]:
            raise ValueError(f"Invalid AI provider: {self.ai_provider}")
    
    def has_valid_firecrawl_key(self) -> bool:
        """Check if Firecrawl API key is configured"""
        return bool(self.firecrawl_api_key and len(self.firecrawl_api_key) > 10)
    
    def has_valid_ai_key(self) -> bool:
        """Check if AI API key is configured"""
        if self.ai_provider == "OpenAI":
            return bool(self.openai_api_key and len(self.openai_api_key) > 10)
        elif self.ai_provider == "Anthropic":
            return bool(self.anthropic_api_key and len(self.anthropic_api_key) > 10)
        return False
    
    def is_profile_complete(self) -> bool:
        """Check if user profile is configured"""
        return bool(
            self.my_website and 
            self.my_value_proposition and 
            self.my_icp
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary (safe for logging - excludes keys)"""
        return {
            'ai_provider': self.ai_provider,
            'has_firecrawl_key': self.has_valid_firecrawl_key(),
            'has_ai_key': self.has_valid_ai_key(),
            'profile_complete': self.is_profile_complete()
        }


# API Endpoints
class APIEndpoints:
    """API endpoint constants"""
    FIRECRAWL_BASE = "https://api.firecrawl.dev/v1"
    FIRECRAWL_SCRAPE = f"{FIRECRAWL_BASE}/scrape"
    
    OPENAI_BASE = "https://api.openai.com/v1"
    OPENAI_CHAT = f"{OPENAI_BASE}/chat/completions"
    
    ANTHROPIC_BASE = "https://api.anthropic.com/v1"
    ANTHROPIC_MESSAGES = f"{ANTHROPIC_BASE}/messages"


# Constants
class Constants:
    """Application constants"""
    APP_NAME = "AI Lead Automator"
    APP_VERSION = "2.0.0"
    
    # Lead scoring thresholds
    QUALIFIED_SCORE = 70
    WARM_SCORE = 60
    
    # UI Constants
    PAGE_TITLE = "AI Lead Automator"
    PAGE_ICON = "🚀"
    LAYOUT = "wide"
    
    # AI Models
    OPENAI_MODEL = "gpt-4o-mini"
    ANTHROPIC_MODEL = "claude-3-5-sonnet-20241022"
    ANTHROPIC_VERSION = "2023-06-01"
    
    # Limits
    MAX_CONTENT_LENGTH = 8000  # characters for AI analysis
    MAX_BULK_URLS = 50
    
    # GDPR
    REDACTED_TEXT = "[REDACTED - GDPR]"


def get_logger(name: str) -> logging.Logger:
    """Get configured logger instance"""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(LOG_LEVEL)
        
        # File handler
        file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
        file_handler.setLevel(LOG_LEVEL)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(LOG_LEVEL)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger
