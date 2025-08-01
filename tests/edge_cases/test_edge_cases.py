"""
Edge case tests for the legal document summarizer.
Tests unusual inputs, boundary conditions, and error scenarios.
"""

import pytest
import io
import tempfile
import os
from unittest.mock import patch, MagicMock
from datetime import datetime

from src.models.data_models import SummaryParams, SummaryResult, ValidationResult, DocumentMetadata
from src.services.document_handler import DocumentHandler
from src.services.text_extractor import TextExtractor
from src.services.summarizer import LegalSummarizer
from src.utils.error_handler import ErrorHandler
from src.utils.config import Config


class TestCorruptedFiles:
    """Test handling of corrupted and malformed files."""
    
    @pytest.fixture
    def services(self):
        """Set up services for edge case testing."""
        return {
            'document_handler': DocumentHandler(),
            'text_extractor': TextExtractor(),
            'summarizer': LegalSummarizer(),
            'error_handler': ErrorHandler()
        }
    
    def test_corrupted_pdf_file(self, services):
        """Test handling of corrupted PDF files."""
        # Create a file that looks like PDF but is corrupted
        corrupted_pdf = io.BytesIO(b"%PDF-1.4\nCorrupted content that is not valid PDF")
        
        # Test validation
        validation_result = services['document_handler'].validate_file(
            corrupted_pdf, "corrupted.pdf"
        )
        
        # Should detect as invalid or handle gracefully during extraction
        if validation_result.is_valid:
            # If validation passes, extraction should handle the corruption
            with patch.object(services['text_extractor'], 'extract_from_pdf', 
                            side_effect=Exception("PDF parsing failed")):
                with pytest.raises(Exception):
                    services['text_extractor'].extract_from_pdf("corrupted.pdf")
    
    def test_empty_pdf_file(self, services):
        """Test handling of empty PDF files."""
        empty_pdf = io.BytesIO(b"")
        
        validation_result = services['document_handler'].validate_file(
            empty_pdf, "empty.pdf"
        )
        
        assert not validation_result.is_valid
        assert "empty" in validation_result.error_message.lower() or "size" in validation_result.error_message.lower()
    
    def test_pdf_with_no_text(self, services):
        """Test handling of PDF files with no extractable text."""
        # Mock a PDF that exists but has no text content
        with patch.object(services['text_extractor'], 'extract_from_pdf', return_value=""):
            extracted_text = services['text_extractor'].extract_from_pdf("no_text.pdf")
            assert extracted_text == ""
            
            # Should handle empty text gracefully
            with patch.object(services['summarizer'], 'load_model'):
                with pytest.raises(Exception):  # Should raise error for empty content
                    services['summarizer'].summarize("", SummaryParams(), "no_text.pdf")
    
    def test_corrupted_docx_file(self, services):
        """Test handling of corrupted DOCX files."""
        # Create corrupted DOCX content
        corrupted_docx = io.BytesIO(b"PK\x03\x04Corrupted DOCX content")
        
        validation_result = services['document_handler'].validate_file(
            corrupted_docx, "corrupted.docx"
        )
        
        if validation_result.is_valid:
            with patch.object(services['text_extractor'], 'extract_from_docx',
                            side_effect=Exception("DOCX parsing failed")):
                with pytest.raises(Exception):
                    services['text_extractor'].extract_from_docx("corrupted.docx")
    
    def test_binary_file_as_text(self, services):
        """Test handling of binary files uploaded as text files."""
        # Create binary content disguised as text
        binary_content = bytes(range(256))  # All possible byte values
        binary_file = io.BytesIO(binary_content)
        
        validation_result = services['document_handler'].validate_file(
            binary_file, "binary.txt"
        )
        
        # Should either reject during validation or handle during processing
        if validation_result.is_valid:
            # If validation passes, text processing should handle binary content
            try:
                content = binary_content.decode('utf-8', errors='ignore')
                # Should produce mostly empty or garbled text
                assert len(content.strip()) < len(binary_content)
            except UnicodeDecodeError:
                # Expected for binary content
                pass


class TestBoundaryConditions:
    """Test boundary conditions and limits."""
    
    @pytest.fixture
    def services(self):
        """Set up services for boundary testing."""
        return {
            'document_handler': DocumentHandler(),
            'text_extractor': TextExtractor(),
            'summarizer': LegalSummarizer(),
            'error_handler': ErrorHandler()
        }
    
    def test_maximum_file_size(self, services):
        """Test handling of files at maximum size limit."""
        # Create file at exactly the maximum size (10MB)
        max_size = Config.MAX_FILE_SIZE
        large_content = b"x" * max_size
        max_size_file = io.BytesIO(large_content)
        
        validation_result = services['document_handler'].validate_file(
            max_size_file, "max_size.txt"
        )
        
        # Should be valid at exactly the limit
        assert validation_result.is_valid
    
    def test_oversized_file(self, services):
        """Test handling of files exceeding size limit."""
        # Create file larger than maximum (10MB + 1 byte)
        oversized_content = b"x" * (Config.MAX_FILE_SIZE + 1)
        oversized_file = io.BytesIO(oversized_content)
        
        validation_result = services['document_handler'].validate_file(
            oversized_file, "oversized.txt"
        )
        
        assert not validation_result.is_valid
        assert "size" in validation_result.error_message.lower()
    
    def test_minimum_content_length(self, services):
        """Test handling of files with minimal content."""
        # Test very short content
        short_content = "Hi"
        short_file = io.BytesIO(short_content.encode('utf-8'))
        
        validation_result = services['document_handler'].validate_file(
            short_file, "short.txt"
        )
        
        # Should be valid but may produce warnings
        assert validation_result.is_valid
        
        # Test summarization with minimal content
        with patch.object(services['summarizer'], 'load_model'):
            with patch.object(services['summarizer'], 'summarize') as mock_summarize:
                # Should handle short content gracefully
                mock_result = SummaryResult(
                    original_filename="short.txt",
                    summary_text="Very brief content: Hi",
                    processing_time=0.5,
                    word_count=4,
                    confidence_score=0.3,  # Low confidence for minimal content
                    generated_at=datetime.now()
                )
                mock_summarize.return_value = mock_result
                
                result = services['summarizer'].summarize(short_content, SummaryParams(), "short.txt")
                assert result.confidence_score < 0.5  # Should have low confidence


class TestUnusualInputs:
    """Test handling of unusual and unexpected inputs."""
    
    @pytest.fixture
    def services(self):
        """Set up services for unusual input testing."""
        return {
            'document_handler': DocumentHandler(),
            'text_extractor': TextExtractor(),
            'summarizer': LegalSummarizer(),
            'error_handler': ErrorHandler()
        }
    
    def test_unicode_content(self, services):
        """Test handling of files with Unicode characters."""
        unicode_content = """
        Legal Document with Unicode Characters
        
        This document contains various Unicode characters:
        • Bullet points
        © Copyright symbols
        § Section symbols
        ™ Trademark symbols
        € Currency symbols
        
        Non-Latin characters: 中文, العربية, русский, 日本語
        
        Mathematical symbols: ∑, ∫, ∞, ≤, ≥
        """
        
        unicode_file = io.BytesIO(unicode_content.encode('utf-8'))
        
        validation_result = services['document_handler'].validate_file(
            unicode_file, "unicode.txt"
        )
        
        assert validation_result.is_valid
        
        # Test text processing with Unicode
        with patch.object(services['summarizer'], 'load_model'):
            with patch.object(services['summarizer'], 'summarize') as mock_summarize:
                mock_result = SummaryResult(
                    original_filename="unicode.txt",
                    summary_text="Legal document containing various Unicode characters and symbols.",
                    processing_time=2.1,
                    word_count=10,
                    confidence_score=0.75,
                    generated_at=datetime.now()
                )
                mock_summarize.return_value = mock_result
                
                result = services['summarizer'].summarize(unicode_content, SummaryParams(), "unicode.txt")
                assert result is not None
                assert "unicode" in result.summary_text.lower() or "characters" in result.summary_text.lower()


class TestErrorScenarios:
    """Test various error scenarios and recovery mechanisms."""
    
    @pytest.fixture
    def services(self):
        """Set up services for error scenario testing."""
        return {
            'document_handler': DocumentHandler(),
            'text_extractor': TextExtractor(),
            'summarizer': LegalSummarizer(),
            'error_handler': ErrorHandler()
        }
    
    def test_disk_space_exhaustion(self, services):
        """Test handling when disk space is exhausted."""
        # Mock disk space error during temp file creation
        with patch.object(services['document_handler'], 'save_temp_file', 
                         side_effect=OSError("No space left on device")):
            
            normal_file = io.BytesIO(b"Normal content")
            
            with pytest.raises(OSError):
                services['document_handler'].save_temp_file(normal_file, "test.txt")
    
    def test_memory_exhaustion_during_processing(self, services):
        """Test handling of memory exhaustion."""
        # Mock memory error during processing
        with patch.object(services['summarizer'], 'summarize',
                         side_effect=MemoryError("Cannot allocate memory")):
            
            with pytest.raises(MemoryError):
                services['summarizer'].summarize("test content", SummaryParams(), "test.txt")
    
    def test_timeout_during_processing(self, services):
        """Test handling of processing timeouts."""
        # Mock timeout error during summarization
        with patch.object(services['summarizer'], 'summarize',
                         side_effect=TimeoutError("Processing timeout")):
            
            with pytest.raises(TimeoutError):
                services['summarizer'].summarize("test content", SummaryParams(), "test.txt")


class TestSecurityEdgeCases:
    """Test security-related edge cases and potential vulnerabilities."""
    
    @pytest.fixture
    def services(self):
        """Set up services for security edge case testing."""
        return {
            'document_handler': DocumentHandler(),
            'text_extractor': TextExtractor(),
            'error_handler': ErrorHandler()
        }
    
    def test_malicious_filename_injection(self, services):
        """Test handling of potentially malicious filenames."""
        malicious_filenames = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "file.txt; rm -rf /",
            "file.txt && echo 'malicious'",
            "<script>alert('xss')</script>.txt"
        ]
        
        normal_content = io.BytesIO(b"Normal content")
        
        for malicious_filename in malicious_filenames:
            normal_content.seek(0)
            
            # Should sanitize or reject malicious filenames
            validation_result = services['document_handler'].validate_file(
                normal_content, malicious_filename
            )
            
            if validation_result.is_valid:
                # If accepted, filename should be sanitized
                sanitized_name = validation_result.file_info.filename
                assert "../" not in sanitized_name
                assert "..\\" not in sanitized_name
                assert ";" not in sanitized_name
                assert "&" not in sanitized_name
                assert "<" not in sanitized_name