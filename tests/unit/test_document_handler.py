"""
Unit tests for document handler service.
"""

import pytest
import tempfile
import os
from io import BytesIO
from unittest.mock import patch, MagicMock
from datetime import datetime

from src.services.document_handler import DocumentHandler
from src.models import DocumentMetadata, ValidationResult
from src.utils import Config


class TestDocumentHandler:
    """Test DocumentHandler class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.handler = DocumentHandler()
    
    def teardown_method(self):
        """Clean up after tests."""
        self.handler.cleanup_temp_files()
    
    def test_validate_file_valid_pdf(self):
        """Test validation of valid PDF file."""
        file_data = BytesIO(b"PDF content here")
        filename = "test_document.pdf"
        
        result = self.handler.validate_file(file_data, filename)
        
        assert result.is_valid is True
        assert result.error_message is None
        assert result.file_info is not None
        assert result.file_info.filename == filename
        assert result.file_info.file_type == ".pdf"
        assert result.file_info.file_size == len(b"PDF content here")
    
    def test_validate_file_valid_docx(self):
        """Test validation of valid DOCX file."""
        file_data = BytesIO(b"DOCX content here")
        filename = "contract.docx"
        
        result = self.handler.validate_file(file_data, filename)
        
        assert result.is_valid is True
        assert result.file_info.file_type == ".docx"
    
    def test_validate_file_valid_txt(self):
        """Test validation of valid TXT file."""
        file_data = BytesIO(b"Text content here")
        filename = "document.txt"
        
        result = self.handler.validate_file(file_data, filename)
        
        assert result.is_valid is True
        assert result.file_info.file_type == ".txt"
    
    def test_validate_file_unsupported_format(self):
        """Test validation of unsupported file format."""
        file_data = BytesIO(b"Image content")
        filename = "image.jpg"
        
        result = self.handler.validate_file(file_data, filename)
        
        assert result.is_valid is False
        assert "Unsupported file format" in result.error_message
        assert result.file_info is None
    
    def test_validate_file_too_large(self):
        """Test validation of file that's too large."""
        # Create file data larger than max size
        large_content = b"x" * (Config.MAX_FILE_SIZE + 1)
        file_data = BytesIO(large_content)
        filename = "large_file.pdf"
        
        result = self.handler.validate_file(file_data, filename)
        
        assert result.is_valid is False
        assert "File too large" in result.error_message
        assert result.file_info is None
    
    def test_validate_file_empty(self):
        """Test validation of empty file."""
        file_data = BytesIO(b"")
        filename = "empty.pdf"
        
        result = self.handler.validate_file(file_data, filename)
        
        assert result.is_valid is False
        assert "File is empty" in result.error_message
        assert result.file_info is None
    
    def test_validate_file_dangerous_filename(self):
        """Test validation of file with dangerous filename."""
        file_data = BytesIO(b"Content")
        filename = "../../../malicious.pdf"
        
        result = self.handler.validate_file(file_data, filename)
        
        assert result.is_valid is False
        assert "invalid characters" in result.error_message
        assert result.file_info is None
    
    def test_extract_metadata_valid_file(self):
        """Test metadata extraction from valid file."""
        file_data = BytesIO(b"Test content")
        filename = "test.pdf"
        
        metadata = self.handler.extract_metadata(file_data, filename)
        
        assert metadata is not None
        assert metadata.filename == filename
        assert metadata.file_size == len(b"Test content")
        assert metadata.file_type == ".pdf"
        assert isinstance(metadata.upload_timestamp, datetime)
    
    def test_extract_metadata_invalid_file(self):
        """Test metadata extraction from invalid file."""
        file_data = BytesIO(b"Content")
        filename = "test.jpg"  # Unsupported format
        
        metadata = self.handler.extract_metadata(file_data, filename)
        
        assert metadata is None
    
    def test_save_temp_file_valid(self):
        """Test saving valid file to temporary location."""
        content = b"Test PDF content"
        file_data = BytesIO(content)
        filename = "test.pdf"
        
        temp_path = self.handler.save_temp_file(file_data, filename)
        
        assert temp_path is not None
        assert os.path.exists(temp_path)
        assert temp_path.endswith(".pdf")
        
        # Verify content
        with open(temp_path, 'rb') as f:
            saved_content = f.read()
        assert saved_content == content
    
    def test_save_temp_file_invalid(self):
        """Test saving invalid file returns None."""
        file_data = BytesIO(b"Content")
        filename = "test.jpg"  # Unsupported format
        
        temp_path = self.handler.save_temp_file(file_data, filename)
        
        assert temp_path is None
    
    def test_cleanup_temp_files(self):
        """Test cleanup of temporary files."""
        # Create a temp file
        content = b"Test content"
        file_data = BytesIO(content)
        filename = "test.pdf"
        
        temp_path = self.handler.save_temp_file(file_data, filename)
        assert os.path.exists(temp_path)
        
        # Cleanup
        self.handler.cleanup_temp_files()
        assert not os.path.exists(temp_path)
        assert len(self.handler._temp_files) == 0
    
    def test_contains_dangerous_chars(self):
        """Test dangerous character detection."""
        # Test safe filenames
        assert not self.handler._contains_dangerous_chars("document.pdf")
        assert not self.handler._contains_dangerous_chars("contract_v2.docx")
        assert not self.handler._contains_dangerous_chars("legal-doc.txt")
        
        # Test dangerous filenames
        assert self.handler._contains_dangerous_chars("../file.pdf")
        assert self.handler._contains_dangerous_chars("file/path.pdf")
        assert self.handler._contains_dangerous_chars("file\\path.pdf")
        assert self.handler._contains_dangerous_chars("file:stream.pdf")
        assert self.handler._contains_dangerous_chars("file*.pdf")
        assert self.handler._contains_dangerous_chars("file?.pdf")
        assert self.handler._contains_dangerous_chars('file".pdf')
        assert self.handler._contains_dangerous_chars("file<.pdf")
        assert self.handler._contains_dangerous_chars("file>.pdf")
        assert self.handler._contains_dangerous_chars("file|.pdf")
    
    def test_get_file_info_existing_file(self):
        """Test getting file info for existing file."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file.write(b"Test content")
            temp_path = temp_file.name
        
        try:
            file_info = self.handler.get_file_info(temp_path)
            
            assert file_info is not None
            assert file_info.file_size == len(b"Test content")
            assert file_info.file_type == ".pdf"
            assert isinstance(file_info.upload_timestamp, datetime)
        finally:
            os.unlink(temp_path)
    
    def test_get_file_info_nonexistent_file(self):
        """Test getting file info for non-existent file."""
        file_info = self.handler.get_file_info("/nonexistent/file.pdf")
        assert file_info is None
    
    @patch('src.services.document_handler.tempfile.NamedTemporaryFile')
    def test_save_temp_file_exception_handling(self, mock_temp_file):
        """Test exception handling in save_temp_file."""
        mock_temp_file.side_effect = Exception("Temp file creation failed")
        
        file_data = BytesIO(b"Content")
        filename = "test.pdf"
        
        temp_path = self.handler.save_temp_file(file_data, filename)
        assert temp_path is None