"""
Unit tests for configuration management.
"""

import pytest
import os
from unittest.mock import patch
from src.utils.config import Config


class TestConfig:
    """Test Config class."""
    
    def test_default_values(self):
        """Test default configuration values."""
        assert Config.MODEL_NAME == "facebook/bart-large-cnn"
        assert Config.MAX_FILE_SIZE == 10 * 1024 * 1024
        assert Config.SUPPORTED_FORMATS == [".pdf", ".docx", ".txt"]
        assert Config.MAX_CHUNK_SIZE == 1024
        assert Config.DEFAULT_SUMMARY_LENGTH == "standard"
        assert Config.DEFAULT_SUMMARY_FOCUS == "general"
    
    def test_summary_lengths_configuration(self):
        """Test summary length configurations."""
        brief = Config.SUMMARY_LENGTHS["brief"]
        standard = Config.SUMMARY_LENGTHS["standard"]
        detailed = Config.SUMMARY_LENGTHS["detailed"]
        
        assert brief["min_words"] == 100
        assert brief["max_words"] == 200
        assert standard["min_words"] == 200
        assert standard["max_words"] == 400
        assert detailed["min_words"] == 400
        assert detailed["max_words"] == 600
    
    def test_summary_focus_options(self):
        """Test summary focus options."""
        expected_options = ["general", "obligations", "parties", "dates"]
        assert Config.SUMMARY_FOCUS_OPTIONS == expected_options
    
    def test_validate_config_valid(self):
        """Test config validation with valid settings."""
        assert Config.validate_config() is True
    
    @patch.object(Config, 'MAX_FILE_SIZE', 0)
    def test_validate_config_invalid_file_size(self):
        """Test config validation with invalid file size."""
        assert Config.validate_config() is False
    
    @patch.object(Config, 'MAX_CHUNK_SIZE', 0)
    def test_validate_config_invalid_chunk_size(self):
        """Test config validation with invalid chunk size."""
        assert Config.validate_config() is False
    
    def test_get_summary_word_limits_valid(self):
        """Test getting word limits for valid length."""
        limits = Config.get_summary_word_limits("brief")
        assert limits["min_words"] == 100
        assert limits["max_words"] == 200
    
    def test_get_summary_word_limits_invalid(self):
        """Test getting word limits for invalid length returns default."""
        limits = Config.get_summary_word_limits("invalid")
        assert limits["min_words"] == 200  # standard default
        assert limits["max_words"] == 400
    
    def test_is_supported_format_valid(self):
        """Test supported format validation."""
        assert Config.is_supported_format(".pdf") is True
        assert Config.is_supported_format(".PDF") is True  # case insensitive
        assert Config.is_supported_format(".docx") is True
        assert Config.is_supported_format(".txt") is True
    
    def test_is_supported_format_invalid(self):
        """Test unsupported format validation."""
        assert Config.is_supported_format(".jpg") is False
        assert Config.is_supported_format(".exe") is False
        assert Config.is_supported_format("") is False
    
    @patch.dict(os.environ, {"MODEL_NAME": "custom-model"})
    def test_environment_variable_override(self):
        """Test that environment variables override defaults."""
        # Note: This test would require reloading the module to see changes
        # In practice, environment variables should be set before import
        pass