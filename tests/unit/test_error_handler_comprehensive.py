"""
Comprehensive tests for the ErrorHandler class.
"""

import pytest
import time
from unittest.mock import Mock, patch
from datetime import datetime

from src.utils.error_handler import (
    ErrorHandler, 
    ErrorType, 
    ErrorSeverity, 
    UserMessage, 
    ErrorContext
)


class TestErrorHandlerComprehensive:
    """Test cases for ErrorHandler class."""
    
    @pytest.fixture
    def error_handler(self):
        """Create an ErrorHandler instance for testing."""
        return ErrorHandler("test_logger")
    
    @pytest.fixture
    def mock_logger(self, error_handler):
        """Mock the logger for testing."""
        with patch.object(error_handler, 'logger') as mock_log:
            yield mock_log

    def test_handle_upload_error_file_format(self, error_handler, mock_logger):
        """Test handling of file format upload errors."""
        error = Exception("Unsupported file format")
        context = {"filename": "test.xyz", "type": "unknown"}
        
        result = error_handler.handle_upload_error(error, context)
        
        assert result.title == "Unsupported File Format"
        assert "PDF, DOCX, or TXT" in result.message
        assert result.severity == ErrorSeverity.MEDIUM
        assert result.show_retry is True

    def test_handle_extraction_error_empty_document(self, error_handler, mock_logger):
        """Test handling of empty document extraction errors."""
        error = Exception("No text found in document")
        context = {"filename": "empty.pdf"}
        
        result = error_handler.handle_extraction_error(error, context)
        
        assert result.title == "No Readable Content"
        assert "empty" in result.message
        assert result.severity == ErrorSeverity.MEDIUM
        assert result.show_retry is False

    def test_handle_extraction_error_generic(self, error_handler, mock_logger):
        """Test handling of generic extraction errors."""
        error = Exception("Generic extraction error")
        
        result = error_handler.handle_extraction_error(error)
        
        assert result.title == "Text Extraction Failed"
        assert result.severity == ErrorSeverity.HIGH
        assert result.show_retry is True
        assert result.show_contact_support is True

    def test_handle_model_error_unavailable(self, error_handler, mock_logger):
        """Test handling of model unavailable errors."""
        error = Exception("Model service unavailable")
        
        result = error_handler.handle_model_error(error)
        
        assert result.title == "AI Service Temporarily Unavailable"
        assert "5-10 minutes" in result.message
        assert result.severity == ErrorSeverity.HIGH
        assert result.show_contact_support is True

    def test_handle_system_error(self, error_handler, mock_logger):
        """Test handling of system errors."""
        error = Exception("System failure")
        context = {"memory": "8GB"}
        
        result = error_handler.handle_system_error(error, context)
        
        assert result.title == "System Error"
        assert result.severity == ErrorSeverity.CRITICAL
        assert result.show_retry is True
        assert result.show_contact_support is True

    def test_handle_validation_error(self, error_handler, mock_logger):
        """Test handling of validation errors."""
        error = Exception("Invalid document format")
        context = {"filename": "test.pdf"}
        
        result = error_handler.handle_validation_error(error, context)
        
        assert result.title == "Validation Error"
        assert "validation failed" in result.message
        assert result.severity == ErrorSeverity.MEDIUM
        assert result.show_retry is True

    def test_with_retry_exponential_backoff(self, error_handler):
        """Test that retry delay increases exponentially."""
        mock_operation = Mock(side_effect=[Exception("fail"), Exception("fail"), "success"])
        
        with patch('time.sleep') as mock_sleep:
            result = error_handler.with_retry(mock_operation, "test_op")
        
        assert result == "success"
        # Check that sleep was called with increasing delays
        expected_calls = [
            ((1.0,),),  # First retry: delay * 1
            ((2.0,),),  # Second retry: delay * 2
        ]
        assert mock_sleep.call_args_list == expected_calls

    def test_log_error_different_levels(self, error_handler, mock_logger):
        """Test that different error types log at appropriate levels."""
        error = Exception("Test error")
        
        # Test system error (should log at error level)
        context_system = ErrorContext(
            error_type=ErrorType.SYSTEM_ERROR,
            timestamp=datetime.now(),
            user_action="test"
        )
        error_handler._log_error(error, context_system)
        mock_logger.error.assert_called()
        
        # Reset mock
        mock_logger.reset_mock()
        
        # Test extraction error (should log at warning level)
        context_extraction = ErrorContext(
            error_type=ErrorType.EXTRACTION_ERROR,
            timestamp=datetime.now(),
            user_action="test"
        )
        error_handler._log_error(error, context_extraction)
        mock_logger.warning.assert_called()

    def test_cleanup_old_retry_counts(self, error_handler, mock_logger):
        """Test cleanup of old retry counts."""
        # Fill with many retry counts to trigger cleanup
        for i in range(1001):
            error_handler.retry_counts[f"op_{i}"] = 1
        
        error_handler.cleanup_old_retry_counts()
        
        assert len(error_handler.retry_counts) == 0
        mock_logger.info.assert_called_with("Cleared old retry counts to prevent memory buildup")


class TestErrorContext:
    """Test cases for ErrorContext dataclass."""
    
    def test_error_context_creation(self):
        """Test creating ErrorContext with all fields."""
        timestamp = datetime.now()
        context = ErrorContext(
            error_type=ErrorType.MODEL_ERROR,
            timestamp=timestamp,
            user_action="test_action",
            file_info={"filename": "test.pdf"},
            system_info={"memory": "8GB"},
            stack_trace="test trace"
        )
        
        assert context.error_type == ErrorType.MODEL_ERROR
        assert context.timestamp == timestamp
        assert context.user_action == "test_action"
        assert context.file_info == {"filename": "test.pdf"}
        assert context.system_info == {"memory": "8GB"}
        assert context.stack_trace == "test trace"


class TestUserMessage:
    """Test cases for UserMessage dataclass."""
    
    def test_user_message_defaults(self):
        """Test UserMessage with default values."""
        message = UserMessage(
            title="Test Error",
            message="Test message",
            suggested_actions=["Action 1"],
            severity=ErrorSeverity.LOW
        )
        
        assert message.show_retry is False  # Default value
        assert message.show_contact_support is False  # Default value