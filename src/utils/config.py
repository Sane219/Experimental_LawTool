"""
Configuration management for the Legal Document Summarizer.
"""

import os
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration settings."""
    
    # Model configuration
    MODEL_NAME: str = os.getenv("MODEL_NAME", "facebook/bart-large-cnn")
    
    # File handling configuration
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", 10 * 1024 * 1024))  # 10MB
    SUPPORTED_FORMATS: List[str] = [".pdf", ".docx", ".txt"]
    
    # Text processing configuration
    MAX_CHUNK_SIZE: int = int(os.getenv("MAX_CHUNK_SIZE", 1024))
    MIN_TEXT_LENGTH: int = 50
    MAX_TEXT_LENGTH: int = 100000
    
    # Summary configuration
    DEFAULT_SUMMARY_LENGTH: str = "standard"
    DEFAULT_SUMMARY_FOCUS: str = "general"
    
    SUMMARY_LENGTHS = {
        "brief": {"min_words": 100, "max_words": 200},
        "standard": {"min_words": 200, "max_words": 400},
        "detailed": {"min_words": 400, "max_words": 600}
    }
    
    SUMMARY_FOCUS_OPTIONS = [
        "general",
        "obligations", 
        "parties",
        "dates"
    ]
    
    # Logging configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Cache configuration
    CACHE_DIR: str = os.getenv("CACHE_DIR", "./model_cache")
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate configuration settings."""
        try:
            # Validate file size is positive
            if cls.MAX_FILE_SIZE <= 0:
                return False
                
            # Validate chunk size is reasonable
            if cls.MAX_CHUNK_SIZE <= 0 or cls.MAX_CHUNK_SIZE > 4096:
                return False
                
            # Validate summary length configuration
            for length_config in cls.SUMMARY_LENGTHS.values():
                if length_config["min_words"] >= length_config["max_words"]:
                    return False
                    
            return True
        except Exception:
            return False
    
    @classmethod
    def get_summary_word_limits(cls, length: str) -> dict:
        """Get word limits for a given summary length."""
        return cls.SUMMARY_LENGTHS.get(length, cls.SUMMARY_LENGTHS[cls.DEFAULT_SUMMARY_LENGTH])
    
    @classmethod
    def is_supported_format(cls, file_extension: str) -> bool:
        """Check if file format is supported."""
        return file_extension.lower() in cls.SUPPORTED_FORMATS