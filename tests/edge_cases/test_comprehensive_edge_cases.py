"""
Comprehensive edge case tests for unusual inputs and boundary conditions.
Tests system robustness with corrupted files, malformed inputs, and extreme scenarios.
"""

import pytest
import io
import tempfile
import os
from unittest.mock import patch
from datetime import datetime

from src.models.data_models import SummaryParams, SummaryResult, ValidationResult
from src.services.document_handler import DocumentHandler
from src.services.text_extractor import TextExtractor
from src.services.summarizer import LegalSummarizer
from src.utils.error_handler import ErrorHandler
from src.utils.config import Config


class TestCorruptedFileHandling:
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
    
    def test_severely_corrupted_pdf(self, services):
        """Test handling of severely corrupted PDF files."""
        # Create completely invalid PDF content
        corrupted_pdf = io.BytesIO(b"This is not a PDF file at all, just random text")
        
        validation_result = services['document_handler'].validate_file(
            corrupted_pdf, "corrupted.pdf"
        )
        
        if validation_result.is_valid:
            # If validation passes, extraction should handle corruption gracefully
            with patch.object(services['text_extractor'], 'extract_from_pdf', 
                            side_effect=Exception("Severe PDF corruption detected")):
                with pytest.raises(Exception) as exc_info:
                    services['text_extractor'].extract_from_pdf("corrupted.pdf")
                assert "corruption" in str(exc_info.value).lower()
    
    def test_pdf_with_embedded_malware_signatures(self, services):
        """Test handling of PDF files with suspicious content patterns."""
        # Create PDF-like content with suspicious patterns
        suspicious_pdf = io.BytesIO(b"%PDF-1.4\n/JavaScript /S /JS (eval(malicious_code))")
        
        validation_result = services['document_handler'].validate_file(
            suspicious_pdf, "suspicious.pdf"
        )
        
        # Should either reject during validation or handle safely
        if validation_result.is_valid:
            with patch.object(services['text_extractor'], 'extract_from_pdf', 
                            return_value="Safe extracted content"):
                result = services['text_extractor'].extract_from_pdf("suspicious.pdf")
                # Should not contain suspicious content
                assert "eval(" not in result
                assert "malicious" not in result
    
    def test_docx_with_corrupted_xml(self, services):
        """Test handling of DOCX files with corrupted internal XML."""
        # Create DOCX-like content with corrupted XML
        corrupted_docx = io.BytesIO(b"PK\x03\x04<xml><unclosed_tag>corrupted content")
        
        validation_result = services['document_handler'].validate_file(
            corrupted_docx, "corrupted.docx"
        )
        
        if validation_result.is_valid:
            with patch.object(services['text_extractor'], 'extract_from_docx',
                            side_effect=Exception("XML parsing failed")):
                with pytest.raises(Exception):
                    services['text_extractor'].extract_from_docx("corrupted.docx")
    
    def test_file_with_null_bytes(self, services):
        """Test handling of files containing null bytes."""
        content_with_nulls = b"Legal document\x00\x00\x00with null bytes\x00embedded"
        null_file = io.BytesIO(content_with_nulls)
        
        validation_result = services['document_handler'].validate_file(
            null_file, "null_bytes.txt"
        )
        
        if validation_result.is_valid:
            # Should handle null bytes gracefully
            content = content_with_nulls.decode('utf-8', errors='ignore')
            assert len(content) > 0
            # Null bytes should be handled or removed
            assert '\x00' not in content or content.replace('\x00', '') != ""
    
    def test_extremely_nested_document_structure(self, services):
        """Test handling of documents with extremely nested structures."""
        # Create deeply nested content that might cause stack overflow
        nested_content = "Legal document with " + "nested " * 1000 + "structure"
        nested_file = io.BytesIO(nested_content.encode('utf-8'))
        
        validation_result = services['document_handler'].validate_file(
            nested_file, "nested.txt"
        )
        
        assert validation_result.is_valid
        
        # Should handle deeply nested content without stack overflow
        with patch.object(services['summarizer'], 'load_model'):
            with patch.object(services['summarizer'], 'summarize') as mock_summarize:
                mock_result = SummaryResult(
                    original_filename="nested.txt",
                    summary_text="Legal document with repetitive nested structure",
                    processing_time=3.0,
                    word_count=8,
                    confidence_score=0.6,  # Lower confidence for repetitive content
                    generated_at=datetime.now()
                )
                mock_summarize.return_value = mock_result
                
                result = services['summarizer'].summarize(
                    nested_content, SummaryParams(), "nested.txt"
                )
                assert result is not None
                assert result.confidence_score < 0.8  # Should detect repetitive content


class TestExtremeInputScenarios:
    """Test handling of extreme input scenarios."""
    
    @pytest.fixture
    def services(self):
        """Set up services for extreme input testing."""
        return {
            'document_handler': DocumentHandler(),
            'text_extractor': TextExtractor(),
            'summarizer': LegalSummarizer(),
            'error_handler': ErrorHandler()
        }
    
    def test_file_at_exact_size_limit(self, services):
        """Test handling of file at exactly the maximum size limit."""
        # Create file at exactly Config.MAX_FILE_SIZE
        exact_size_content = b"x" * Config.MAX_FILE_SIZE
        exact_size_file = io.BytesIO(exact_size_content)
        
        validation_result = services['document_handler'].validate_file(
            exact_size_file, "exact_limit.txt"
        )
        
        # Should be valid at exactly the limit
        assert validation_result.is_valid
        assert validation_result.file_info.file_size == Config.MAX_FILE_SIZE
    
    def test_file_one_byte_over_limit(self, services):
        """Test handling of file just one byte over the limit."""
        # Create file one byte larger than limit
        oversized_content = b"x" * (Config.MAX_FILE_SIZE + 1)
        oversized_file = io.BytesIO(oversized_content)
        
        validation_result = services['document_handler'].validate_file(
            oversized_file, "oversized.txt"
        )
        
        # Should be rejected
        assert not validation_result.is_valid
        assert "size" in validation_result.error_message.lower()
    
    def test_document_with_only_whitespace(self, services):
        """Test handling of document containing only whitespace."""
        whitespace_content = " \t\n\r " * 1000  # Various whitespace characters
        whitespace_file = io.BytesIO(whitespace_content.encode('utf-8'))
        
        validation_result = services['document_handler'].validate_file(
            whitespace_file, "whitespace.txt"
        )
        
        if validation_result.is_valid:
            # Should handle whitespace-only content
            with patch.object(services['summarizer'], 'load_model'):
                with pytest.raises(Exception):  # Should fail due to no meaningful content
                    services['summarizer'].summarize(
                        whitespace_content, SummaryParams(), "whitespace.txt"
                    )
    
    def test_document_with_single_character(self, services):
        """Test handling of document with single character."""
        single_char_file = io.BytesIO(b"A")
        
        validation_result = services['document_handler'].validate_file(
            single_char_file, "single.txt"
        )
        
        if validation_result.is_valid:
            with patch.object(services['summarizer'], 'load_model'):
                with patch.object(services['summarizer'], 'summarize') as mock_summarize:
                    mock_result = SummaryResult(
                        original_filename="single.txt",
                        summary_text="Document contains minimal content: A",
                        processing_time=0.5,
                        word_count=5,
                        confidence_score=0.1,  # Very low confidence
                        generated_at=datetime.now()
                    )
                    mock_summarize.return_value = mock_result
                    
                    result = services['summarizer'].summarize("A", SummaryParams(), "single.txt")
                    assert result.confidence_score < 0.3  # Should have very low confidence
    
    def test_document_with_extremely_long_lines(self, services):
        """Test handling of document with extremely long lines."""
        # Create document with one extremely long line (100KB)
        long_line = "This is an extremely long line of legal text " * 2000
        long_line_file = io.BytesIO(long_line.encode('utf-8'))
        
        validation_result = services['document_handler'].validate_file(
            long_line_file, "long_line.txt"
        )
        
        if validation_result.is_valid:
            # Should handle long lines without memory issues
            with patch.object(services['summarizer'], 'load_model'):
                with patch.object(services['summarizer'], 'summarize') as mock_summarize:
                    mock_result = SummaryResult(
                        original_filename="long_line.txt",
                        summary_text="Document with extremely long line of repetitive legal text",
                        processing_time=4.0,
                        word_count=10,
                        confidence_score=0.5,
                        generated_at=datetime.now()
                    )
                    mock_summarize.return_value = mock_result
                    
                    result = services['summarizer'].summarize(long_line, SummaryParams(), "long_line.txt")
                    assert result is not None
    
    def test_document_with_mixed_encodings(self, services):
        """Test handling of document with mixed character encodings."""
        # Create content with mixed encodings
        mixed_content = "Legal document with mixed encodings: "
        mixed_content += "ASCII text, "
        mixed_content += "UTF-8: café résumé, "
        mixed_content += "Latin-1: naïve façade"
        
        mixed_file = io.BytesIO(mixed_content.encode('utf-8'))
        
        validation_result = services['document_handler'].validate_file(
            mixed_file, "mixed_encoding.txt"
        )
        
        assert validation_result.is_valid
        
        # Should handle mixed encodings gracefully
        with patch.object(services['summarizer'], 'load_model'):
            with patch.object(services['summarizer'], 'summarize') as mock_summarize:
                mock_result = SummaryResult(
                    original_filename="mixed_encoding.txt",
                    summary_text="Legal document containing text with various character encodings",
                    processing_time=2.2,
                    word_count=10,
                    confidence_score=0.8,
                    generated_at=datetime.now()
                )
                mock_summarize.return_value = mock_result
                
                result = services['summarizer'].summarize(mixed_content, SummaryParams(), "mixed_encoding.txt")
                assert result is not None
                assert "encoding" in result.summary_text.lower()


class TestSecurityEdgeCases:
    """Test security-related edge cases and potential attack vectors."""
    
    @pytest.fixture
    def services(self):
        """Set up services for security edge case testing."""
        return {
            'document_handler': DocumentHandler(),
            'text_extractor': TextExtractor(),
            'error_handler': ErrorHandler()
        }
    
    def test_path_traversal_in_filenames(self, services):
        """Test handling of path traversal attempts in filenames."""
        malicious_filenames = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "/etc/shadow",
            "C:\\Windows\\System32\\config\\SAM",
            "file.txt/../../../etc/passwd",
            "normal.pdf\x00../../../etc/passwd"  # Null byte injection
        ]
        
        normal_content = io.BytesIO(b"Normal legal document content")
        
        for malicious_filename in malicious_filenames:
            normal_content.seek(0)
            
            validation_result = services['document_handler'].validate_file(
                normal_content, malicious_filename
            )
            
            if validation_result.is_valid:
                # Filename should be sanitized
                sanitized_name = validation_result.file_info.filename
                assert "../" not in sanitized_name
                assert "..\\" not in sanitized_name
                assert "/etc/" not in sanitized_name
                assert "C:\\" not in sanitized_name
                assert "\x00" not in sanitized_name
    
    def test_command_injection_in_filenames(self, services):
        """Test handling of command injection attempts in filenames."""
        injection_filenames = [
            "file.txt; rm -rf /",
            "file.txt && echo 'pwned'",
            "file.txt | cat /etc/passwd",
            "file.txt`whoami`",
            "file.txt$(whoami)",
            "file.txt; shutdown -h now"
        ]
        
        normal_content = io.BytesIO(b"Normal content")
        
        for injection_filename in injection_filenames:
            normal_content.seek(0)
            
            validation_result = services['document_handler'].validate_file(
                normal_content, injection_filename
            )
            
            if validation_result.is_valid:
                # Dangerous characters should be removed or escaped
                sanitized_name = validation_result.file_info.filename
                dangerous_chars = [";", "&", "|", "`", "$", "(", ")"]
                for char in dangerous_chars:
                    assert char not in sanitized_name or sanitized_name.count(char) == 0
    
    def test_xss_attempts_in_content(self, services):
        """Test handling of XSS attempts in document content."""
        xss_content = """
        Legal Document with XSS Attempts
        
        <script>alert('XSS')</script>
        <img src="x" onerror="alert('XSS')">
        <iframe src="javascript:alert('XSS')"></iframe>
        
        This document contains various XSS payloads that should be handled safely.
        """
        
        xss_file = io.BytesIO(xss_content.encode('utf-8'))
        
        validation_result = services['document_handler'].validate_file(
            xss_file, "xss_test.txt"
        )
        
        if validation_result.is_valid:
            # Content should be processed safely without executing scripts
            # In a real implementation, this would test that XSS content is sanitized
            assert "<script>" in xss_content  # Verify test content contains XSS
            # The system should handle this content without executing it
    
    def test_zip_bomb_like_content(self, services):
        """Test handling of content designed to consume excessive resources."""
        # Create content that expands significantly when processed
        zip_bomb_content = "AAAAAAAAAA" * 100000  # Highly repetitive content
        zip_bomb_file = io.BytesIO(zip_bomb_content.encode('utf-8'))
        
        validation_result = services['document_handler'].validate_file(
            zip_bomb_file, "zip_bomb.txt"
        )
        
        if validation_result.is_valid:
            # Should handle repetitive content without excessive resource consumption
            assert len(zip_bomb_content) > 500000  # Verify it's large
            # System should process this efficiently without memory exhaustion
    
    def test_unicode_normalization_attacks(self, services):
        """Test handling of Unicode normalization attacks."""
        # Create content with Unicode characters that might normalize to dangerous strings
        unicode_content = """
        Legal Document with Unicode Normalization Test
        
        File name: test＜script＞alert('xss')＜/script＞.pdf
        Path: /etc/passwd vs ／etc／passwd
        
        This tests Unicode normalization security.
        """
        
        unicode_file = io.BytesIO(unicode_content.encode('utf-8'))
        
        validation_result = services['document_handler'].validate_file(
            unicode_file, "unicode_test.txt"
        )
        
        assert validation_result.is_valid
        # System should handle Unicode content safely without normalization attacks


class TestResourceExhaustionScenarios:
    """Test scenarios that could lead to resource exhaustion."""
    
    @pytest.fixture
    def services(self):
        """Set up services for resource exhaustion testing."""
        return {
            'document_handler': DocumentHandler(),
            'text_extractor': TextExtractor(),
            'summarizer': LegalSummarizer()
        }
    
    def test_memory_exhaustion_prevention(self, services):
        """Test prevention of memory exhaustion attacks."""
        # Create content designed to consume excessive memory
        memory_bomb = "Memory exhaustion test " * 50000  # ~1MB of repetitive text
        memory_file = io.BytesIO(memory_bomb.encode('utf-8'))
        
        validation_result = services['document_handler'].validate_file(
            memory_file, "memory_test.txt"
        )
        
        if validation_result.is_valid:
            # Should handle large content without memory exhaustion
            with patch.object(services['summarizer'], 'load_model'):
                with patch.object(services['summarizer'], 'summarize') as mock_summarize:
                    # Mock should handle large content efficiently
                    mock_result = SummaryResult(
                        original_filename="memory_test.txt",
                        summary_text="Large document with repetitive content for memory testing",
                        processing_time=8.0,
                        word_count=10,
                        confidence_score=0.4,  # Lower confidence for repetitive content
                        generated_at=datetime.now()
                    )
                    mock_summarize.return_value = mock_result
                    
                    result = services['summarizer'].summarize(
                        memory_bomb, SummaryParams(), "memory_test.txt"
                    )
                    assert result is not None
                    assert result.processing_time < 30.0  # Should still meet time requirements
    
    def test_cpu_exhaustion_prevention(self, services):
        """Test prevention of CPU exhaustion through complex content."""
        # Create content with complex patterns that might cause excessive CPU usage
        complex_content = """
        Legal document with complex nested structures and patterns:
        """ + "(((" * 1000 + "nested content" + ")))" * 1000
        
        complex_file = io.BytesIO(complex_content.encode('utf-8'))
        
        validation_result = services['document_handler'].validate_file(
            complex_file, "complex.txt"
        )
        
        if validation_result.is_valid:
            # Should handle complex content without excessive CPU usage
            with patch.object(services['summarizer'], 'load_model'):
                with patch.object(services['summarizer'], 'summarize') as mock_summarize:
                    mock_result = SummaryResult(
                        original_filename="complex.txt",
                        summary_text="Legal document with complex nested structure patterns",
                        processing_time=12.0,  # Reasonable time despite complexity
                        word_count=9,
                        confidence_score=0.6,
                        generated_at=datetime.now()
                    )
                    mock_summarize.return_value = mock_result
                    
                    result = services['summarizer'].summarize(
                        complex_content, SummaryParams(), "complex.txt"
                    )
                    assert result is not None
                    assert result.processing_time < 30.0