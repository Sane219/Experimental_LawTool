"""
Integration tests for the ErrorHandler in realistic scenarios.
"""

import pytest
from unittest.mock import Mock
from src.utils.error_handler import ErrorHandler, ErrorSeverity


class TestErrorHandlerIntegration:
    """Integration tests for ErrorHandler."""
    
    @pytest.fixture
    def error_handler(self):
        return ErrorHandler("integration_test")

    def test_document_processing_pipeline_with_errors(self, error_handler):
        """Test error handling in a realistic document processing pipeline."""
        
        # Simulate a document upload error
        upload_error = Exception("File size exceeds 10MB limit")
        upload_result = error_handler.handle_upload_error(upload_error, {"filename": "large_doc.pdf", "size": 15000000})
        
        assert upload_result.title == "File Too Large"
        assert upload_result.show_retry is True
        assert "Compress the document" in upload_result.suggested_actions[0]
        
        # Simulate a text extraction error
        extraction_error = Exception("No text found in document")
        extraction_result = error_handler.handle_extraction_error(extraction_error, {"filename": "scanned_doc.pdf"})
        
        assert extraction_result.title == "No Readable Content"
        assert extraction_result.show_retry is False
        assert extraction_result.severity == ErrorSeverity.MEDIUM
        
        # Simulate an AI model error with retry
        model_error = Exception("Out of memory error during processing")
        model_result = error_handler.handle_model_error(model_error, {"document_length": 50000})
        
        assert model_result.title == "Document Too Large for Processing"
        assert "chunks" in model_result.suggested_actions[0]
        assert model_result.show_retry is True

    def test_retry_mechanism_with_realistic_operation(self, error_handler):
        """Test retry mechanism with a realistic operation that might fail."""
        
        # Mock an operation that fails twice then succeeds
        mock_ai_operation = Mock(side_effect=[
            Exception("Temporary model unavailable"),
            Exception("Connection timeout"),
            {"summary": "This is a legal document summary", "confidence": 0.95}
        ])
        
        # Use retry mechanism
        result = error_handler.with_retry(mock_ai_operation, "ai_summarization", "document_text")
        
        assert result["summary"] == "This is a legal document summary"
        assert result["confidence"] == 0.95
        assert mock_ai_operation.call_count == 3
        assert error_handler.retry_counts["ai_summarization"] == 0  # Reset after success

    def test_error_statistics_tracking(self, error_handler):
        """Test that error statistics are properly tracked."""
        
        # Simulate multiple operations with different retry patterns
        mock_op1 = Mock(side_effect=Exception("Persistent failure"))
        mock_op2 = Mock(return_value="success")
        
        # First operation fails completely
        with pytest.raises(Exception):
            error_handler.with_retry(mock_op1, "failing_operation")
        
        # Second operation succeeds immediately
        error_handler.with_retry(mock_op2, "successful_operation")
        
        # Check statistics
        stats = error_handler.get_error_statistics()
        assert "retry_counts" in stats
        assert "timestamp" in stats
        assert stats["retry_counts"]["failing_operation"] == 3
        assert stats["retry_counts"]["successful_operation"] == 0

    def test_graceful_degradation_scenario(self, error_handler):
        """Test graceful degradation when multiple systems fail."""
        
        # Simulate cascade of failures
        errors_handled = []
        
        # Primary AI service fails
        ai_error = Exception("Primary AI model service unavailable")
        ai_result = error_handler.handle_model_error(ai_error)
        errors_handled.append(ai_result)
        
        # Fallback extraction service fails
        extraction_error = Exception("Backup text extraction service down")
        extraction_result = error_handler.handle_extraction_error(extraction_error)
        errors_handled.append(extraction_result)
        
        # System resources exhausted
        system_error = Exception("System disk space full")
        system_result = error_handler.handle_system_error(system_error)
        errors_handled.append(system_result)
        
        # Verify all errors provide user-friendly messages and recovery options
        for result in errors_handled:
            assert isinstance(result.title, str)
            assert len(result.title) > 0
            assert isinstance(result.message, str)
            assert len(result.message) > 0
            assert isinstance(result.suggested_actions, list)
            assert len(result.suggested_actions) > 0
            assert result.severity in [ErrorSeverity.MEDIUM, ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]

    def test_logging_integration(self, error_handler):
        """Test that errors are properly logged for monitoring."""
        
        # Generate various types of errors and ensure no exceptions are raised
        try:
            error_handler.handle_upload_error(Exception("Test upload error"))
            error_handler.handle_model_error(Exception("Test model error"))
            error_handler.handle_system_error(Exception("Test system error"))
            
            # If we get here without exceptions, logging is working
            assert True
        except Exception as e:
            pytest.fail(f"Logging integration failed with error: {e}")