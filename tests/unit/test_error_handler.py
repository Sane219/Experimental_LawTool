"""
Unit tests for the ErrorHandler class.
"""

import pytest
import logging
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


class TestErrorHandler:
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

    def test_initialization(self, error_handler):
        """Test ErrorHandler initialization."""
        assert error_handler.max_retries == 3
        assert error_handler.retry_delay == 1.0
        assert isinstance(error_handler.retry_counts, dict)
        assert len(error_handler.retry_counts) == 0

    def test_handle_upload_error_file_size(self, error_handler, mock_logger):
        """Test handling of file size upload errors."""
        error = Exception("File size exceeds limit")
        context = {"filename": "test.pdf", "size": 15000000}
        
        result = error_handler.handle_upload_error(error, context)
        
        assert isinstance(result, UserMessage)
        assert result.title == "File Too Large"
        assert "10MB" in result.message
        assert result.severity == ErrorSeverity.MEDIUM
        assert result.show_retry is True
        assert len(result.suggested_actions) > 0

    def test_handle_model_error_memory(self, error_handler, mock_logger):
        """Test handling of model memory errors."""
        error = Exception("Out of memory error")
        
        result = error_handler.handle_model_error(error)
        
        assert result.title == "Document Too Large for Processing"
        assert "chunks" in result.message
        assert result.severity == ErrorSeverity.MEDIUM
        assert result.show_retry is True

    def test_with_retry_success_first_attempt(self, error_handler):
        """Test retry mechanism with successful first attempt."""
        mock_operation = Mock(return_value="success")
        
        result = error_handler.with_retry(mock_operation, "test_op")
        
        assert result == "success"
        assert mock_operation.call_count == 1
        assert error_handler.retry_counts["test_op"] == 0

    def test_with_retry_max_retries_exceeded(self, error_handler):
        """Test retry mechanism when max retries are exceeded."""
        mock_operation = Mock(side_effect=Exception("persistent failure"))
        
        with patch('time.sleep'):
            with pytest.raises(Exception, match="persistent failure"):
                error_handler.with_retry(mock_operation, "test_op")
        
        assert mock_operation.call_count == 3
        assert error_handler.retry_counts["test_op"] == 3

    def test_reset_retry_count(self, error_handler):
        """Test resetting retry count for an operation."""
        error_handler.retry_counts["test_op"] = 2
        
        error_handler.reset_retry_count("test_op")
        
        assert "test_op" not in error_handler.retry_counts

    def test_get_error_statistics(self, error_handler):
        """Test getting error statistics."""
        error_handler.retry_counts = {"op1": 2, "op2": 1}
        
        stats = error_handler.get_error_statistics()
        
        assert "retry_counts" in stats
        assert "timestamp" in stats
        assert stats["retry_counts"] == {"op1": 2, "op2": 1}
        assert isinstance(stats["timestamp"], str)


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
    
    def test_user_message_creation(self):
        """Test creating UserMessage with all fields."""
        message = UserMessage(
            title="Test Error",
            message="Test message",
            suggested_actions=["Action 1", "Action 2"],
            severity=ErrorSeverity.HIGH,
            show_retry=True,
            show_contact_support=True
        )
        
        assert message.title == "Test Error"
        assert message.message == "Test message"
        assert message.suggested_actions == ["Action 1", "Action 2"]
        assert message.severity == ErrorSeverity.HIGH
        assert message.show_retry is True
        assert message.show_contact_support is True