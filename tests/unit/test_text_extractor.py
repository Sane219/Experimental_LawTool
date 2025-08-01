"""
Unit tests for text extraction service.
"""

import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path

from src.services.text_extractor import TextExtractor


class TestTextExtractor:
    """Test TextExtractor class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.extractor = TextExtractor()
    
    def test_clean_text_basic(self):
        """Test basic text cleaning functionality."""
        raw_text = "  This   is    a   test   text  \n\n\n  with   extra   spaces  "
        cleaned = self.extractor.clean_text(raw_text)
        
        assert cleaned == "This is a test text\n\nwith extra spaces"
    
    def test_clean_text_control_characters(self):
        """Test removal of control characters."""
        raw_text = "Text\x00with\x08control\x1Fcharacters"
        cleaned = self.extractor.clean_text(raw_text)
        
        assert cleaned == "Textwithcontrolcharacters"
    
    def test_clean_text_line_breaks(self):
        """Test normalization of line breaks."""
        raw_text = "Line 1\r\nLine 2\rLine 3\nLine 4"
        cleaned = self.extractor.clean_text(raw_text)
        
        assert cleaned == "Line 1\nLine 2\nLine 3\nLine 4"
    
    def test_clean_text_excessive_line_breaks(self):
        """Test removal of excessive line breaks."""
        raw_text = "Paragraph 1\n\n\n\n\nParagraph 2"
        cleaned = self.extractor.clean_text(raw_text)
        
        assert cleaned == "Paragraph 1\n\nParagraph 2"
    
    def test_clean_text_empty_input(self):
        """Test cleaning empty or None input."""
        assert self.extractor.clean_text("") == ""
        assert self.extractor.clean_text(None) == ""
        assert self.extractor.clean_text("   ") == ""
    
    def test_validate_legal_content_valid(self):
        """Test validation of valid legal content."""
        legal_text = """
        This Agreement is entered into between the parties whereas the plaintiff
        shall comply with all applicable laws and regulations. The contract
        contains clauses regarding liability and termination effective date.
        """
        
        assert self.extractor.validate_legal_content(legal_text) is True
    
    def test_validate_legal_content_with_patterns(self):
        """Test validation with legal patterns."""
        legal_text = """
        Section 1: The parties hereby agree to the terms.
        Article 2: Governing law shall be applicable.
        Clause 3: Effective date of execution.
        """
        
        assert self.extractor.validate_legal_content(legal_text) is True
    
    def test_validate_legal_content_invalid_short(self):
        """Test validation of too short text."""
        short_text = "Short text"
        
        assert self.extractor.validate_legal_content(short_text) is False
    
    def test_validate_legal_content_invalid_no_keywords(self):
        """Test validation of text without legal keywords."""
        non_legal_text = """
        This is a regular document about cooking recipes and gardening tips.
        It contains no legal terminology or patterns that would indicate
        it is a legal document of any kind.
        """
        
        assert self.extractor.validate_legal_content(non_legal_text) is False
    
    def test_validate_legal_content_empty(self):
        """Test validation of empty content."""
        assert self.extractor.validate_legal_content("") is False
        assert self.extractor.validate_legal_content(None) is False
    
    def test_extract_from_txt_success(self):
        """Test successful text extraction from TXT file."""
        content = "This is a test legal contract with parties and obligations."
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name
        
        try:
            extracted = self.extractor.extract_from_txt(temp_path)
            assert extracted == content
        finally:
            os.unlink(temp_path)
    
    def test_extract_from_txt_different_encodings(self):
        """Test TXT extraction with different encodings."""
        content = "Contract with special characters: café, naïve"
        
        # Test UTF-8
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name
        
        try:
            extracted = self.extractor.extract_from_txt(temp_path)
            assert "café" in extracted
        finally:
            os.unlink(temp_path)
    
    def test_extract_from_txt_file_not_found(self):
        """Test TXT extraction with non-existent file."""
        with pytest.raises(FileNotFoundError):
            self.extractor.extract_from_txt("/nonexistent/file.txt")
    
    @patch('src.services.text_extractor.Document')
    def test_extract_from_docx_success(self, mock_document_class):
        """Test successful DOCX extraction."""
        # Mock document structure
        mock_paragraph1 = MagicMock()
        mock_paragraph1.text = "This is paragraph 1 of the contract."
        mock_paragraph2 = MagicMock()
        mock_paragraph2.text = "This is paragraph 2 with obligations."
        
        mock_doc = MagicMock()
        mock_doc.paragraphs = [mock_paragraph1, mock_paragraph2]
        mock_doc.tables = []
        
        mock_document_class.return_value = mock_doc
        
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            extracted = self.extractor.extract_from_docx(temp_path)
            expected = "This is paragraph 1 of the contract.\n\nThis is paragraph 2 with obligations."
            assert extracted == expected
        finally:
            os.unlink(temp_path)
    
    @patch('src.services.text_extractor.Document')
    def test_extract_from_docx_with_tables(self, mock_document_class):
        """Test DOCX extraction with tables."""
        # Mock table structure
        mock_cell1 = MagicMock()
        mock_cell1.text = "Party A"
        mock_cell2 = MagicMock()
        mock_cell2.text = "Party B"
        
        mock_row = MagicMock()
        mock_row.cells = [mock_cell1, mock_cell2]
        
        mock_table = MagicMock()
        mock_table.rows = [mock_row]
        
        mock_doc = MagicMock()
        mock_doc.paragraphs = []
        mock_doc.tables = [mock_table]
        
        mock_document_class.return_value = mock_doc
        
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            extracted = self.extractor.extract_from_docx(temp_path)
            assert "Party A | Party B" in extracted
        finally:
            os.unlink(temp_path)
    
    def test_extract_from_docx_file_not_found(self):
        """Test DOCX extraction with non-existent file."""
        with pytest.raises(FileNotFoundError):
            self.extractor.extract_from_docx("/nonexistent/file.docx")
    
    @patch('src.services.text_extractor.Document', None)
    def test_extract_from_docx_library_not_available(self):
        """Test DOCX extraction when library is not available."""
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            with pytest.raises(ImportError, match="python-docx library not available"):
                self.extractor.extract_from_docx(temp_path)
        finally:
            os.unlink(temp_path)
    
    @patch('src.services.text_extractor.pdfplumber')
    def test_extract_from_pdf_with_pdfplumber(self, mock_pdfplumber):
        """Test PDF extraction using pdfplumber."""
        # Mock pdfplumber
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "This is page content from PDF"
        
        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=None)
        
        mock_pdfplumber.open.return_value = mock_pdf
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            extracted = self.extractor.extract_from_pdf(temp_path)
            assert "This is page content from PDF" in extracted
        finally:
            os.unlink(temp_path)
    
    @patch('src.services.text_extractor.pdfplumber', None)
    @patch('src.services.text_extractor.PyPDF2')
    def test_extract_from_pdf_with_pypdf2_fallback(self, mock_pypdf2):
        """Test PDF extraction fallback to PyPDF2."""
        # Mock PyPDF2
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "PyPDF2 extracted content"
        
        mock_reader = MagicMock()
        mock_reader.pages = [mock_page]
        
        mock_pypdf2.PdfReader.return_value = mock_reader
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            extracted = self.extractor.extract_from_pdf(temp_path)
            assert "PyPDF2 extracted content" in extracted
        finally:
            os.unlink(temp_path)
    
    def test_extract_from_pdf_file_not_found(self):
        """Test PDF extraction with non-existent file."""
        with pytest.raises(FileNotFoundError):
            self.extractor.extract_from_pdf("/nonexistent/file.pdf")
    
    def test_extract_text_dispatcher(self):
        """Test the main extract_text method dispatcher."""
        with patch.object(self.extractor, 'extract_from_pdf') as mock_pdf:
            mock_pdf.return_value = "PDF content"
            
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                temp_path = temp_file.name
            
            try:
                result = self.extractor.extract_text(temp_path)
                assert result == "PDF content"
                mock_pdf.assert_called_once_with(temp_path)
            finally:
                os.unlink(temp_path)
    
    def test_extract_text_unsupported_format(self):
        """Test extract_text with unsupported file format."""
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            with pytest.raises(Exception, match="Unsupported file format"):
                self.extractor.extract_text(temp_path)
        finally:
            os.unlink(temp_path)