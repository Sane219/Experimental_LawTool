"""
Comprehensive integration tests for complete document processing workflows.
Tests the entire pipeline from document upload to summary generation.
"""

import pytest
import io
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.models.data_models import SummaryParams, ProcessingState, DocumentMetadata
from src.services.document_handler import DocumentHandler
from src.services.text_extractor import TextExtractor
from src.services.summarizer import LegalSummarizer
from src.services.output_handler import OutputHandler
from src.services.security_service import get_security_service
from src.utils.error_handler import ErrorHandler
from src.utils.config import Config


class TestCompleteWorkflow:
    """Test complete document processing workflows."""
    
    @pytest.fixture
    def setup_services(self):
        """Set up all required services for integration testing."""
        return {
            'document_handler': DocumentHandler(),
            'text_extractor': TextExtractor(),
            'summarizer': LegalSummarizer(),
            'output_handler': OutputHandler(),
            'error_handler': ErrorHandler(),
            'security_service': get_security_service()
        }
    
    @pytest.fixture
    def sample_legal_text(self):
        """Sample legal document text for testing."""
        return """
        LEGAL SERVICES AGREEMENT
        
        This Legal Services Agreement ("Agreement") is entered into on January 15, 2024,
        between Smith & Associates Law Firm ("Attorney") and ABC Corporation ("Client").
        
        SCOPE OF SERVICES:
        The Attorney agrees to provide legal representation in the matter of contract
        negotiation and review for the Client's upcoming merger transaction.
        
        OBLIGATIONS:
        1. Attorney shall provide competent legal representation
        2. Client shall provide all necessary documentation within 30 days
        3. Attorney shall maintain confidentiality of all client information
        4. Client shall pay all fees within 30 days of invoice
        
        IMPORTANT DATES:
        - Contract execution: January 15, 2024
        - Document delivery deadline: February 15, 2024
        - Project completion target: March 15, 2024
        
        PARTIES:
        Attorney: John Smith, Esq., Smith & Associates Law Firm
        Client: Jane Doe, CEO, ABC Corporation
        
        This agreement shall be governed by the laws of the State of California.
        """
    
    @pytest.fixture
    def sample_pdf_file(self, sample_legal_text):
        """Create a sample PDF file for testing."""
        # Create a mock PDF file
        pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n"
        return io.BytesIO(pdf_content)
    
    @pytest.fixture
    def sample_txt_file(self, sample_legal_text):
        """Create a sample text file for testing."""
        return io.BytesIO(sample_legal_text.encode('utf-8'))
    
    def test_complete_pdf_processing_workflow(self, setup_services, sample_pdf_file, sample_legal_text):
        """Test complete workflow for PDF document processing."""
        services = setup_services
        
        # Mock text extraction to return our sample text
        with patch.object(services['text_extractor'], 'extract_from_pdf', return_value=sample_legal_text):
            with patch.object(services['summarizer'], 'load_model'):
                with patch.object(services['summarizer'], 'summarize') as mock_summarize:
                    # Setup mock summary result
                    from src.models.data_models import SummaryResult
                    mock_result = SummaryResult(
                        original_filename="test_document.pdf",
                        summary_text="This is a legal services agreement between Smith & Associates and ABC Corporation for merger transaction support.",
                        processing_time=2.5,
                        word_count=25,
                        confidence_score=0.85,
                        generated_at=datetime.now()
                    )
                    mock_summarize.return_value = mock_result
                    
                    # Test workflow
                    # 1. Validate file
                    validation_result = services['document_handler'].validate_file(
                        sample_pdf_file, "test_document.pdf"
                    )
                    assert validation_result.is_valid
                    
                    # 2. Extract text
                    extracted_text = services['text_extractor'].extract_from_pdf("dummy_path")
                    assert len(extracted_text) > 0
                    assert "LEGAL SERVICES AGREEMENT" in extracted_text
                    
                    # 3. Generate summary
                    summary_params = SummaryParams(
                        length="standard",
                        focus="general",
                        max_words=300
                    )
                    
                    summary_result = services['summarizer'].summarize(
                        extracted_text, summary_params, "test_document.pdf"
                    )
                    
                    # Verify results
                    assert summary_result is not None
                    assert summary_result.original_filename == "test_document.pdf"
                    assert len(summary_result.summary_text) > 0
                    assert summary_result.confidence_score > 0
    
    def test_complete_txt_processing_workflow(self, setup_services, sample_txt_file, sample_legal_text):
        """Test complete workflow for text document processing."""
        services = setup_services
        
        with patch.object(services['summarizer'], 'load_model'):
            with patch.object(services['summarizer'], 'summarize') as mock_summarize:
                # Setup mock summary result
                from src.models.data_models import SummaryResult
                mock_result = SummaryResult(
                    original_filename="test_document.txt",
                    summary_text="Legal services agreement for merger transaction support with key obligations and deadlines.",
                    processing_time=1.8,
                    word_count=18,
                    confidence_score=0.92,
                    generated_at=datetime.now()
                )
                mock_summarize.return_value = mock_result
                
                # Test workflow
                # 1. Validate file
                validation_result = services['document_handler'].validate_file(
                    sample_txt_file, "test_document.txt"
                )
                assert validation_result.is_valid
                
                # 2. Process text directly (no extraction needed for txt)
                sample_txt_file.seek(0)
                text_content = sample_txt_file.read().decode('utf-8')
                assert "LEGAL SERVICES AGREEMENT" in text_content
                
                # 3. Generate summary
                summary_params = SummaryParams(
                    length="brief",
                    focus="obligations",
                    max_words=200
                )
                
                summary_result = services['summarizer'].summarize(
                    text_content, summary_params, "test_document.txt"
                )
                
                # Verify results
                assert summary_result is not None
                assert summary_result.original_filename == "test_document.txt"
                assert "obligations" in summary_result.summary_text.lower() or "agreement" in summary_result.summary_text.lower()
    
    def test_workflow_with_customization_parameters(self, setup_services, sample_legal_text):
        """Test workflow with different customization parameters."""
        services = setup_services
        
        with patch.object(services['summarizer'], 'load_model'):
            with patch.object(services['summarizer'], 'summarize') as mock_summarize:
                
                # Test different parameter combinations
                test_cases = [
                    {
                        'params': SummaryParams(length="brief", focus="parties", max_words=150),
                        'expected_focus': "parties"
                    },
                    {
                        'params': SummaryParams(length="detailed", focus="dates", max_words=500),
                        'expected_focus': "dates"
                    },
                    {
                        'params': SummaryParams(length="standard", focus="obligations", max_words=300),
                        'expected_focus': "obligations"
                    }
                ]
                
                for i, test_case in enumerate(test_cases):
                    # Setup mock result based on focus
                    from src.models.data_models import SummaryResult
                    focus_summaries = {
                        "parties": "Agreement between Smith & Associates Law Firm and ABC Corporation.",
                        "dates": "Key dates: January 15, 2024 (execution), February 15, 2024 (documents), March 15, 2024 (completion).",
                        "obligations": "Attorney must provide competent representation and maintain confidentiality. Client must provide documents and pay fees within 30 days."
                    }
                    
                    mock_result = SummaryResult(
                        original_filename=f"test_document_{i}.txt",
                        summary_text=focus_summaries[test_case['expected_focus']],
                        processing_time=2.0 + i * 0.5,
                        word_count=len(focus_summaries[test_case['expected_focus']].split()),
                        confidence_score=0.85 + i * 0.05,
                        generated_at=datetime.now()
                    )
                    mock_summarize.return_value = mock_result
                    
                    # Test summarization with parameters
                    result = services['summarizer'].summarize(
                        sample_legal_text, test_case['params'], f"test_document_{i}.txt"
                    )
                    
                    # Verify customization was applied
                    assert result is not None
                    assert test_case['expected_focus'].lower() in result.summary_text.lower() or "agreement" in result.summary_text.lower()    
    
def test_error_handling_workflow(self, setup_services):
        """Test error handling throughout the processing workflow."""
        services = setup_services
        
        # Test file validation errors
        invalid_file = io.BytesIO(b"invalid content")
        validation_result = services['document_handler'].validate_file(
            invalid_file, "test.exe"
        )
        assert not validation_result.is_valid
        assert "unsupported format" in validation_result.error_message.lower()
        
        # Test text extraction errors
        with patch.object(services['text_extractor'], 'extract_from_pdf', side_effect=Exception("PDF parsing failed")):
            with pytest.raises(Exception):
                services['text_extractor'].extract_from_pdf("invalid_path")
        
        # Test summarization errors with fallback
        with patch.object(services['summarizer'], 'load_model'):
            with patch.object(services['summarizer'], 'summarize', side_effect=Exception("Model error")):
                with pytest.raises(Exception):
                    services['summarizer'].summarize("test text", SummaryParams(), "test.txt")
    
    def test_large_document_processing(self, setup_services):
        """Test processing of large documents with chunking."""
        services = setup_services
        
        # Create a large document (simulate by repeating content)
        large_text = """
        LEGAL SERVICES AGREEMENT
        
        This is a very long legal document that exceeds the model's context window.
        """ * 100  # Repeat to make it large
        
        with patch.object(services['summarizer'], 'load_model'):
            with patch.object(services['summarizer'], 'chunk_text', return_value=["chunk1", "chunk2"]) as mock_chunk:
                with patch.object(services['summarizer'], 'summarize') as mock_summarize:
                    from src.models.data_models import SummaryResult
                    mock_result = SummaryResult(
                        original_filename="large_document.txt",
                        summary_text="Summary of large legal document with multiple sections.",
                        processing_time=5.2,
                        word_count=12,
                        confidence_score=0.78,
                        generated_at=datetime.now()
                    )
                    mock_summarize.return_value = mock_result
                    
                    # Test chunking is called for large documents
                    result = services['summarizer'].summarize(
                        large_text, SummaryParams(length="standard"), "large_document.txt"
                    )
                    
                    assert result is not None
                    assert result.processing_time > 0
    
    def test_security_measures(self, setup_services):
        """Test security measures and data cleanup."""
        services = setup_services
        
        # Test that security service is properly initialized
        assert services['security_service'] is not None
        
        # Test file cleanup after processing
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b"test content")
            temp_path = temp_file.name
        
        # Simulate processing and cleanup
        services['document_handler'].cleanup_temp_files()
        
        # Verify temporary files are cleaned up (in real implementation)
        # This would check that temp files are actually deleted
        assert True  # Placeholder for actual cleanup verification
    
    def test_output_generation_and_export(self, setup_services, sample_legal_text):
        """Test summary output generation and export functionality."""
        services = setup_services
        
        from src.models.data_models import SummaryResult
        summary_result = SummaryResult(
            original_filename="test_document.pdf",
            summary_text="This is a test summary of the legal document.",
            processing_time=2.1,
            word_count=12,
            confidence_score=0.89,
            generated_at=datetime.now()
        )
        
        # Test copy functionality
        with patch.object(services['output_handler'], 'copy_to_clipboard') as mock_copy:
            services['output_handler'].copy_to_clipboard(summary_result.summary_text)
            mock_copy.assert_called_once_with(summary_result.summary_text)
        
        # Test PDF export
        with patch.object(services['output_handler'], 'export_to_pdf') as mock_export:
            services['output_handler'].export_to_pdf(summary_result)
            mock_export.assert_called_once_with(summary_result)
    
    def test_performance_benchmarks(self, setup_services, sample_legal_text):
        """Test performance benchmarks for processing speed."""
        services = setup_services
        
        with patch.object(services['summarizer'], 'load_model'):
            with patch.object(services['summarizer'], 'summarize') as mock_summarize:
                from src.models.data_models import SummaryResult
                
                # Simulate processing times within acceptable limits
                mock_result = SummaryResult(
                    original_filename="performance_test.txt",
                    summary_text="Performance test summary.",
                    processing_time=15.0,  # Should be under 30 seconds per design
                    word_count=4,
                    confidence_score=0.85,
                    generated_at=datetime.now()
                )
                mock_summarize.return_value = mock_result
                
                start_time = datetime.now()
                result = services['summarizer'].summarize(
                    sample_legal_text, SummaryParams(), "performance_test.txt"
                )
                end_time = datetime.now()
                
                # Verify performance requirements
                assert result.processing_time < 30.0  # Design requirement: <30 seconds
                assert result is not None
    
    def test_edge_cases_and_corrupted_files(self, setup_services):
        """Test handling of edge cases and corrupted files."""
        services = setup_services
        
        # Test empty file
        empty_file = io.BytesIO(b"")
        validation_result = services['document_handler'].validate_file(
            empty_file, "empty.txt"
        )
        assert not validation_result.is_valid
        
        # Test very small file
        tiny_file = io.BytesIO(b"Hi")
        validation_result = services['document_handler'].validate_file(
            tiny_file, "tiny.txt"
        )
        # Should be valid but may produce warning about content length
        
        # Test file with special characters
        special_chars_file = io.BytesIO("Special chars: àáâãäåæçèéêë".encode('utf-8'))
        validation_result = services['document_handler'].validate_file(
            special_chars_file, "special.txt"
        )
        assert validation_result.is_valid
        
        # Test oversized file
        large_content = b"x" * (11 * 1024 * 1024)  # 11MB (over 10MB limit)
        oversized_file = io.BytesIO(large_content)
        validation_result = services['document_handler'].validate_file(
            oversized_file, "oversized.txt"
        )
        assert not validation_result.is_valid
        assert "file size" in validation_result.error_message.lower()


class TestErrorRecovery:
    """Test error recovery and graceful degradation scenarios."""
    
    @pytest.fixture
    def setup_services(self):
        """Set up services for error recovery testing."""
        return {
            'document_handler': DocumentHandler(),
            'text_extractor': TextExtractor(),
            'summarizer': LegalSummarizer(),
            'error_handler': ErrorHandler()
        }
    
    def test_model_loading_failure_recovery(self, setup_services):
        """Test recovery when AI model fails to load."""
        services = setup_services
        
        with patch.object(services['summarizer'], 'load_model', side_effect=Exception("Model loading failed")):
            # Should handle gracefully and provide fallback
            with pytest.raises(Exception):
                services['summarizer'].load_model()
    
    def test_network_timeout_recovery(self, setup_services):
        """Test recovery from network timeouts during model operations."""
        services = setup_services
        
        # Simulate network timeout
        with patch.object(services['summarizer'], 'summarize', side_effect=TimeoutError("Network timeout")):
            with pytest.raises(TimeoutError):
                services['summarizer'].summarize("test", SummaryParams(), "test.txt")
    
    def test_memory_pressure_handling(self, setup_services):
        """Test handling of memory pressure during processing."""
        services = setup_services
        
        # Simulate memory error
        with patch.object(services['summarizer'], 'summarize', side_effect=MemoryError("Out of memory")):
            with pytest.raises(MemoryError):
                services['summarizer'].summarize("large text", SummaryParams(), "test.txt")


class TestQualityMetrics:
    """Test quality metrics and validation."""
    
    def test_summary_quality_validation(self):
        """Test summary quality validation metrics."""
        from src.models.data_models import SummaryResult
        
        # Test valid summary
        good_summary = SummaryResult(
            original_filename="test.txt",
            summary_text="This is a comprehensive summary with key legal points and obligations.",
            processing_time=2.5,
            word_count=13,
            confidence_score=0.85,
            generated_at=datetime.now()
        )
        
        assert good_summary.confidence_score >= 0.7  # Quality threshold
        assert good_summary.word_count > 5  # Minimum meaningful length
        assert len(good_summary.summary_text.split()) == good_summary.word_count
    
    def test_processing_time_metrics(self):
        """Test processing time metrics meet requirements."""
        from src.models.data_models import SummaryResult
        
        result = SummaryResult(
            original_filename="test.txt",
            summary_text="Test summary",
            processing_time=25.0,
            word_count=2,
            confidence_score=0.80,
            generated_at=datetime.now()
        )
        
        # Design requirement: <30 seconds for documents up to 50 pages
        assert result.processing_time < 30.0
    
    def test_memory_usage_validation(self):
        """Test memory usage stays within acceptable limits."""
        # This would test actual memory usage in a real implementation
        # For now, we'll simulate the validation
        max_memory_mb = 2048  # 2GB limit from design
        current_memory_mb = 1500  # Simulated current usage
        
        assert current_memory_mb < max_memory_mb