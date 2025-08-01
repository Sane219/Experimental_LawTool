"""
Unit tests for data models.
"""

import pytest
from datetime import datetime
from src.models.data_models import (
    DocumentMetadata,
    SummaryParams,
    SummaryResult,
    ValidationResult,
    ProcessingState
)


class TestDocumentMetadata:
    """Test DocumentMetadata data class."""
    
    def test_document_metadata_creation(self):
        """Test creating DocumentMetadata instance."""
        timestamp = datetime.now()
        metadata = DocumentMetadata(
            filename="test.pdf",
            file_size=1024,
            file_type=".pdf",
            upload_timestamp=timestamp
        )
        
        assert metadata.filename == "test.pdf"
        assert metadata.file_size == 1024
        assert metadata.file_type == ".pdf"
        assert metadata.upload_timestamp == timestamp


class TestSummaryParams:
    """Test SummaryParams data class."""
    
    def test_summary_params_creation(self):
        """Test creating SummaryParams instance."""
        params = SummaryParams(
            length="standard",
            focus="general",
            max_words=300
        )
        
        assert params.length == "standard"
        assert params.focus == "general"
        assert params.max_words == 300
    
    def test_summary_params_default_max_words(self):
        """Test default max_words value."""
        params = SummaryParams(
            length="brief",
            focus="parties"
        )
        
        assert params.max_words == 300


class TestSummaryResult:
    """Test SummaryResult data class."""
    
    def test_summary_result_creation(self):
        """Test creating SummaryResult instance."""
        timestamp = datetime.now()
        result = SummaryResult(
            original_filename="contract.pdf",
            summary_text="This is a summary.",
            processing_time=2.5,
            word_count=4,
            confidence_score=0.85,
            generated_at=timestamp
        )
        
        assert result.original_filename == "contract.pdf"
        assert result.summary_text == "This is a summary."
        assert result.processing_time == 2.5
        assert result.word_count == 4
        assert result.confidence_score == 0.85
        assert result.generated_at == timestamp


class TestValidationResult:
    """Test ValidationResult data class."""
    
    def test_validation_result_valid(self):
        """Test creating valid ValidationResult."""
        metadata = DocumentMetadata("test.pdf", 1024, ".pdf", datetime.now())
        result = ValidationResult(
            is_valid=True,
            error_message=None,
            file_info=metadata
        )
        
        assert result.is_valid is True
        assert result.error_message is None
        assert result.file_info == metadata
    
    def test_validation_result_invalid(self):
        """Test creating invalid ValidationResult."""
        result = ValidationResult(
            is_valid=False,
            error_message="File too large",
            file_info=None
        )
        
        assert result.is_valid is False
        assert result.error_message == "File too large"
        assert result.file_info is None


class TestProcessingState:
    """Test ProcessingState enum."""
    
    def test_processing_state_values(self):
        """Test ProcessingState enum values."""
        assert ProcessingState.IDLE.value == "idle"
        assert ProcessingState.UPLOADING.value == "uploading"
        assert ProcessingState.EXTRACTING.value == "extracting_text"
        assert ProcessingState.SUMMARIZING.value == "generating_summary"
        assert ProcessingState.COMPLETE.value == "complete"
        assert ProcessingState.ERROR.value == "error"