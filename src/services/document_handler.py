"""
Document upload and validation service for the Legal Document Summarizer.
"""

import os
import tempfile
from datetime import datetime
from typing import Optional, BinaryIO
from pathlib import Path

from src.models import DocumentMetadata, ValidationResult
from src.utils import Config
from src.services.security_service import get_security_service
from src.utils.secure_logging import get_secure_logger


class DocumentHandler:
    """Handles document upload, validation, and temporary file management."""
    
    def __init__(self):
        """Initialize the document handler."""
        self._temp_files = []
        self.security_service = get_security_service()
        self.logger = get_secure_logger()
    
    def validate_file(self, file_data: BinaryIO, filename: str) -> ValidationResult:
        """
        Validate uploaded file for security and format compliance.
        
        Args:
            file_data: Binary file data
            filename: Original filename
            
        Returns:
            ValidationResult with validation status and metadata
        """
        try:
            # Extract file extension
            file_extension = Path(filename).suffix.lower()
            
            # Check if format is supported
            if not Config.is_supported_format(file_extension):
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Unsupported file format. Supported formats: {', '.join(Config.SUPPORTED_FORMATS)}",
                    file_info=None
                )
            
            # Get file size
            file_data.seek(0, 2)  # Seek to end
            file_size = file_data.tell()
            file_data.seek(0)  # Reset to beginning
            
            # Check file size
            if file_size > Config.MAX_FILE_SIZE:
                size_mb = file_size / (1024 * 1024)
                max_size_mb = Config.MAX_FILE_SIZE / (1024 * 1024)
                return ValidationResult(
                    is_valid=False,
                    error_message=f"File too large ({size_mb:.1f}MB). Maximum size: {max_size_mb:.1f}MB",
                    file_info=None
                )
            
            # Check if file is empty
            if file_size == 0:
                return ValidationResult(
                    is_valid=False,
                    error_message="File is empty",
                    file_info=None
                )
            
            # Basic security check - ensure filename doesn't contain dangerous characters
            if self._contains_dangerous_chars(filename):
                return ValidationResult(
                    is_valid=False,
                    error_message="Filename contains invalid characters",
                    file_info=None
                )
            
            # Create metadata for valid file
            metadata = DocumentMetadata(
                filename=filename,
                file_size=file_size,
                file_type=file_extension,
                upload_timestamp=datetime.now()
            )
            
            return ValidationResult(
                is_valid=True,
                error_message=None,
                file_info=metadata
            )
            
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                error_message=f"File validation error: {str(e)}",
                file_info=None
            )
    
    def extract_metadata(self, file_data: BinaryIO, filename: str) -> Optional[DocumentMetadata]:
        """
        Extract metadata from uploaded file.
        
        Args:
            file_data: Binary file data
            filename: Original filename
            
        Returns:
            DocumentMetadata if successful, None otherwise
        """
        validation_result = self.validate_file(file_data, filename)
        return validation_result.file_info if validation_result.is_valid else None
    
    def save_temp_file(self, file_data: BinaryIO, filename: str) -> Optional[str]:
        """
        Save uploaded file to temporary location for processing.
        
        Args:
            file_data: Binary file data
            filename: Original filename
            
        Returns:
            Path to temporary file if successful, None otherwise
        """
        try:
            # Validate file first
            validation_result = self.validate_file(file_data, filename)
            if not validation_result.is_valid:
                self.logger.log_security_event("file_validation_failed", {
                    "filename": filename,
                    "error": validation_result.error_message
                })
                return None
            
            # Create secure temporary file using security service
            file_extension = Path(filename).suffix.lower()
            temp_file_path = self.security_service.create_secure_temp_file(
                suffix=file_extension,
                prefix="legal_doc_"
            )
            
            # Write file data
            file_data.seek(0)
            with open(temp_file_path, 'wb') as temp_file:
                temp_file.write(file_data.read())
            
            # Track temp file for cleanup (both locally and in security service)
            self._temp_files.append(temp_file_path)
            
            # Log file operation (path will be sanitized)
            self.logger.log_file_operation("temp_file_created", temp_file_path, True)
            
            return temp_file_path
            
        except Exception as e:
            self.logger.log_error(e, {"operation": "save_temp_file", "filename": filename})
            return None
    
    def cleanup_temp_files(self) -> None:
        """Remove all temporary files created by this handler."""
        cleaned_count = 0
        
        for temp_file_path in self._temp_files:
            try:
                if os.path.exists(temp_file_path):
                    # Use security service for secure deletion
                    self.security_service.cleanup_temp_files([temp_file_path])
                    cleaned_count += 1
                    self.logger.log_file_operation("temp_file_deleted", temp_file_path, True)
            except Exception as e:
                self.logger.log_file_operation("temp_file_delete_failed", temp_file_path, False)
                self.logger.log_error(e, {"operation": "cleanup_temp_files", "file": temp_file_path})
        
        self._temp_files.clear()
        
        # Log cleanup operation
        if cleaned_count > 0:
            self.logger.log_cleanup_operation("temp_files", cleaned_count)
    
    def _contains_dangerous_chars(self, filename: str) -> bool:
        """
        Check if filename contains potentially dangerous characters.
        
        Args:
            filename: Filename to check
            
        Returns:
            True if filename contains dangerous characters
        """
        dangerous_chars = ['..', '/', '\\', ':', '*', '?', '"', '<', '>', '|']
        return any(char in filename for char in dangerous_chars)
    
    def get_file_info(self, file_path: str) -> Optional[DocumentMetadata]:
        """
        Get metadata for a file at the given path.
        
        Args:
            file_path: Path to the file
            
        Returns:
            DocumentMetadata if file exists, None otherwise
        """
        try:
            if not os.path.exists(file_path):
                return None
            
            path_obj = Path(file_path)
            file_size = os.path.getsize(file_path)
            
            return DocumentMetadata(
                filename=path_obj.name,
                file_size=file_size,
                file_type=path_obj.suffix.lower(),
                upload_timestamp=datetime.fromtimestamp(os.path.getctime(file_path))
            )
            
        except Exception:
            return None
    
    def __del__(self):
        """Cleanup temporary files when handler is destroyed."""
        try:
            self.cleanup_temp_files()
        except Exception:
            # Ignore errors during cleanup in destructor
            pass