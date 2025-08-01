"""
Comprehensive end-to-end integration tests for the legal document summarizer.
Tests complete workflows from document upload to summary export.
"""

import pytest
import io
from unittest.mock import patch
from datetime import datetime

from src.models.data_models import SummaryParams, SummaryResult
from src.services.document_handler import DocumentHandler
from src.services.text_extractor import TextExtractor
from src.services.summarizer import LegalSummarizer
from src.services.output_handler import OutputHandler
from src.utils.error_handler import ErrorHandler


class TestComprehensiveE2E:
    """Comprehensive end-to-end workflow tests."""
    
    @pytest.fixture
    def services(self):
        """Set up all services for testing."""
        return {
            'document_handler': DocumentHandler(),
            'text_extractor': TextExtractor(),
            'summarizer': LegalSummarizer(),
            'output_handler': OutputHandler(),
            'error_handler': ErrorHandler()
        }
    
    @pytest.fixture
    def sample_contract(self):
        """Sample legal contract for testing."""
        return """
        SOFTWARE LICENSE AGREEMENT
        
        This Agreement is entered into on March 1, 2024, between TechCorp Inc. 
        ("Licensor") and BusinessCorp LLC ("Licensee").
        
        OBLIGATIONS:
        1. Licensee shall not reverse engineer the Software
        2. Licensor shall provide 12 months technical support
        3. Payment due within 30 days of invoice
        
        PARTIES:
        Licensor: TechCorp Inc., John Smith, CEO
        Licensee: BusinessCorp LLC, Jane Doe, CTO
        """
    
    def test_complete_pdf_workflow(self, services, sample_contract):
        """Test complete PDF processing workflow."""
        pdf_file = io.BytesIO(sample_contract.encode('utf-8'))
        
        with patch.object(services['text_extractor'], 'extract_from_pdf', 
                         return_value=sample_contract):
            with patch.object(services['summarizer'], 'load_model'):
                with patch.object(services['summarizer'], 'summarize') as mock_summarize:
                    mock_result = SummaryResult(
                        original_filename="test.pdf",
                        summary_text="Software license agreement between TechCorp and BusinessCorp.",
                        processing_time=2.5,
                        word_count=10,
                        confidence_score=0.85,
                        generated_at=datetime.now()
                    )
                    mock_summarize.return_value = mock_result
                    
                    # Test validation
                    validation = services['document_handler'].validate_file(pdf_file, "test.pdf")
                    assert validation.is_valid
                    
                    # Test extraction
                    text = services['text_extractor'].extract_from_pdf("dummy_path")
                    assert "SOFTWARE LICENSE AGREEMENT" in text
                    
                    # Test summarization
                    params = SummaryParams(length="standard", focus="general", max_words=300)
                    result = services['summarizer'].summarize(text, params, "test.pdf")
                    
                    assert result is not None
                    assert result.confidence_score > 0.8
                    assert "license" in result.summary_text.lower()
    
    def test_error_recovery_workflow(self, services):
        """Test error recovery throughout workflow."""
        # Test invalid file
        invalid_file = io.BytesIO(b"invalid")
        validation = services['document_handler'].validate_file(invalid_file, "test.exe")
        assert not validation.is_valid
        
        # Test extraction error
        with patch.object(services['text_extractor'], 'extract_from_pdf', 
                         side_effect=Exception("Extraction failed")):
            with pytest.raises(Exception):
                services['text_extractor'].extract_from_pdf("bad.pdf")
    
    def test_export_workflow(self, services):
        """Test complete export workflow."""
        sample_result = SummaryResult(
            original_filename="test.pdf",
            summary_text="Test summary for export",
            processing_time=2.0,
            word_count=5,
            confidence_score=0.9,
            generated_at=datetime.now()
        )
        
        # Test PDF export
        with patch.object(services['output_handler'], 'generate_pdf_export') as mock_pdf:
            mock_pdf.return_value = io.BytesIO(b"PDF content")
            result = services['output_handler'].generate_pdf_export(sample_result)
            assert result is not None
            mock_pdf.assert_called_once()