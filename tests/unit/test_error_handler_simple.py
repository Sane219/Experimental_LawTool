"""
Simple tests for error handling functionality.
"""

import pytest
from unittest.mock import Mock
from src.utils.error_handler_simple import ErrorHandler, ErrorSeverity, UserMessage


class TestErrorHandlerSimple:
    
    @pytest.fixture
    def error_handler(self):
        return ErrorHandler("test_logger")

    def test_handle_upload_error_file_size(self, error_handler):
        error = Exception("File size exceeds limit")
        result = error_handler.handle_upload_error(error)
        
        assert isinstance(result, UserMessage)
        assert result.title == "File Too Large"
        assert result.severity == ErrorSeverity.MEDIUM
        assert result.show_retry is True

    def test_handle_model_error_memory(self, error_handler):
        error = Exception("Out of memory error")
        result = error_handler.handle_model_error(error)
        
        assert result.title == "Document Too Large for Processing"
        assert result.severity == ErrorSeverity.MEDIUM
        assert result.show_retry is True

    def test_with_retry_success(self, error_handler):
        mock_operation = Mock(return_value="success")
        result = error_handler.with_retry(mock_operation, "test_op")
        
        assert result == "success"
        assert mock_operation.call_count == 1
        assert error_handler.retry_counts["test_op"] == 0

    def test_with_retry_max_retries_exceeded(self, error_handler):
        mock_operation = Mock(side_effect=Exception("persistent failure"))
        
        with pytest.raises(Exception, match="persistent failure"):
            error_handler.with_retry(mock_operation, "test_op")
        
        assert mock_operation.call_count == 3
        assert error_handler.retry_counts["test_op"] == 3

    def test_reset_retry_count(self, error_handler):
        error_handler.retry_counts["test_op"] = 2
        error_handler.reset_retry_count("test_op")
        assert "test_op" not in error_handler.retry_counts

    def test_get_error_statistics(self, error_handler):
        error_handler.retry_counts = {"op1": 2, "op2": 1}
        stats = error_handler.get_error_statistics()
        
        assert "retry_counts" in stats
        assert "timestamp" in stats
        assert stats["retry_counts"] == {"op1": 2, "op2": 1}