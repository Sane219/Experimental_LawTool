"""
Secure logging module for the Legal Document Summarizer.
Ensures sensitive document content is never logged while maintaining debugging capabilities.
"""

import logging
import os
import re
import hashlib
from typing import Any, Dict, Optional, Union
from datetime import datetime
from pathlib import Path


class SecureFormatter(logging.Formatter):
    """
    Custom logging formatter that sanitizes sensitive information.
    """
    
    # Patterns to identify and redact sensitive information
    SENSITIVE_PATTERNS = [
        # Document content patterns
        (r'(?i)(document|text|content|summary)[\s]*[=:]\s*["\']([^"\']{50,})["\']', r'\1=<REDACTED_CONTENT>'),
        (r'(?i)(extracted|processed)_text[\s]*[=:]\s*["\']([^"\']{50,})["\']', r'\1_text=<REDACTED_TEXT>'),
        
        # File paths with potential sensitive names
        (r'(?i)(/[^/\s]+/)*([^/\s]*legal[^/\s]*|[^/\s]*confidential[^/\s]*|[^/\s]*private[^/\s]*)', r'<REDACTED_PATH>'),
        
        # Email addresses
        (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', r'<REDACTED_EMAIL>'),
        
        # Phone numbers
        (r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', r'<REDACTED_PHONE>'),
        
        # Social Security Numbers
        (r'\b\d{3}-\d{2}-\d{4}\b', r'<REDACTED_SSN>'),
        
        # Credit card numbers
        (r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', r'<REDACTED_CARD>'),
        
        # Large text blocks (potential document content)
        (r'["\']([^"\']{200,})["\']', r'"<REDACTED_LARGE_TEXT>"'),
    ]
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record while sanitizing sensitive information.
        
        Args:
            record: Log record to format
            
        Returns:
            Formatted and sanitized log message
        """
        # Get the original formatted message
        original_message = super().format(record)
        
        # Apply sanitization patterns
        sanitized_message = self._sanitize_message(original_message)
        
        return sanitized_message
    
    def _sanitize_message(self, message: str) -> str:
        """
        Sanitize a log message by removing sensitive information.
        
        Args:
            message: Original log message
            
        Returns:
            Sanitized log message
        """
        sanitized = message
        
        # Apply each sanitization pattern
        for pattern, replacement in self.SENSITIVE_PATTERNS:
            sanitized = re.sub(pattern, replacement, sanitized)
        
        return sanitized


class SecureLogger:
    """
    Secure logger that prevents logging of sensitive document content.
    """
    
    def __init__(self, name: str = "legal_summarizer", log_level: str = "INFO"):
        """
        Initialize secure logger.
        
        Args:
            name: Logger name
            log_level: Logging level
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self) -> None:
        """Setup logging handlers with secure formatting."""
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # File handler for application logs
        app_log_file = log_dir / "app.log"
        file_handler = logging.FileHandler(app_log_file)
        file_handler.setLevel(logging.INFO)
        
        # File handler for error logs
        error_log_file = log_dir / "error.log"
        error_handler = logging.FileHandler(error_log_file)
        error_handler.setLevel(logging.ERROR)
        
        # Console handler for development
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        
        # Use secure formatter for all handlers
        secure_formatter = SecureFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        file_handler.setFormatter(secure_formatter)
        error_handler.setFormatter(secure_formatter)
        console_handler.setFormatter(secure_formatter)
        
        # Add handlers to logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(error_handler)
        self.logger.addHandler(console_handler)
    
    def log_document_processing_start(self, filename: str, file_size: int) -> str:
        """
        Log the start of document processing with safe metadata only.
        
        Args:
            filename: Original filename (will be hashed for privacy)
            file_size: File size in bytes
            
        Returns:
            Processing session ID for correlation
        """
        # Create a hash of the filename for correlation without exposing the actual name
        filename_hash = hashlib.sha256(filename.encode()).hexdigest()[:16]
        session_id = f"proc_{filename_hash}_{int(datetime.now().timestamp())}"
        
        self.logger.info(
            f"Document processing started - Session: {session_id}, "
            f"Size: {file_size} bytes, Type: {Path(filename).suffix}"
        )
        
        return session_id
    
    def log_document_processing_complete(self, session_id: str, processing_time: float, 
                                       summary_length: int) -> None:
        """
        Log successful document processing completion.
        
        Args:
            session_id: Processing session ID
            processing_time: Time taken to process in seconds
            summary_length: Length of generated summary in characters
        """
        self.logger.info(
            f"Document processing completed - Session: {session_id}, "
            f"Time: {processing_time:.2f}s, Summary length: {summary_length} chars"
        )
    
    def log_security_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """
        Log security-related events.
        
        Args:
            event_type: Type of security event
            details: Event details (will be sanitized)
        """
        # Sanitize details to remove sensitive information
        safe_details = self._sanitize_dict(details)
        
        self.logger.warning(
            f"Security event - Type: {event_type}, Details: {safe_details}"
        )
    
    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Log an error with sanitized context information.
        
        Args:
            error: Exception that occurred
            context: Additional context (will be sanitized)
        """
        # Sanitize context to remove sensitive information
        safe_context = self._sanitize_dict(context) if context else {}
        
        self.logger.error(
            f"Error occurred - Type: {type(error).__name__}, "
            f"Message: {str(error)}, Context: {safe_context}",
            exc_info=True
        )
    
    def log_file_operation(self, operation: str, file_path: str, success: bool) -> None:
        """
        Log file operations with path sanitization.
        
        Args:
            operation: Type of file operation
            file_path: File path (will be sanitized)
            success: Whether operation was successful
        """
        # Sanitize file path to remove sensitive information
        safe_path = self._sanitize_file_path(file_path)
        
        level = logging.INFO if success else logging.ERROR
        self.logger.log(
            level,
            f"File operation - Type: {operation}, Path: {safe_path}, Success: {success}"
        )
    
    def log_cleanup_operation(self, operation_type: str, items_cleaned: int) -> None:
        """
        Log cleanup operations.
        
        Args:
            operation_type: Type of cleanup operation
            items_cleaned: Number of items cleaned up
        """
        self.logger.info(
            f"Cleanup operation - Type: {operation_type}, Items cleaned: {items_cleaned}"
        )
    
    def _sanitize_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize a dictionary by removing or redacting sensitive values.
        
        Args:
            data: Dictionary to sanitize
            
        Returns:
            Sanitized dictionary
        """
        if not isinstance(data, dict):
            return {}
        
        sanitized = {}
        
        for key, value in data.items():
            # Check if key suggests sensitive content
            if any(sensitive in key.lower() for sensitive in 
                   ['content', 'text', 'document', 'summary', 'password', 'token', 'key']):
                if isinstance(value, str) and len(value) > 50:
                    sanitized[key] = "<REDACTED_SENSITIVE_DATA>"
                else:
                    sanitized[key] = "<REDACTED>"
            elif isinstance(value, str):
                # Apply string sanitization
                sanitized[key] = self._sanitize_string(value)
            elif isinstance(value, dict):
                # Recursively sanitize nested dictionaries
                sanitized[key] = self._sanitize_dict(value)
            elif isinstance(value, (list, tuple)):
                # Sanitize lists/tuples
                sanitized[key] = [self._sanitize_string(str(item)) if isinstance(item, str) 
                                else item for item in value]
            else:
                sanitized[key] = value
        
        return sanitized
    
    def _sanitize_string(self, text: str) -> str:
        """
        Sanitize a string by applying sensitive data patterns.
        
        Args:
            text: String to sanitize
            
        Returns:
            Sanitized string
        """
        if not isinstance(text, str):
            return str(text)
        
        sanitized = text
        
        # Apply sanitization patterns
        for pattern, replacement in SecureFormatter.SENSITIVE_PATTERNS:
            sanitized = re.sub(pattern, replacement, sanitized)
        
        return sanitized
    
    def _sanitize_file_path(self, file_path: str) -> str:
        """
        Sanitize file path to remove sensitive directory/file names.
        
        Args:
            file_path: File path to sanitize
            
        Returns:
            Sanitized file path
        """
        if not file_path:
            return ""
        
        path = Path(file_path)
        
        # Replace sensitive directory names
        parts = []
        for part in path.parts:
            if any(sensitive in part.lower() for sensitive in 
                   ['legal', 'confidential', 'private', 'client', 'case']):
                parts.append("<REDACTED_DIR>")
            else:
                parts.append(part)
        
        # Replace sensitive filename
        if path.name and any(sensitive in path.name.lower() for sensitive in 
                           ['legal', 'confidential', 'private', 'client', 'case']):
            parts[-1] = f"<REDACTED_FILE>{path.suffix}"
        
        return str(Path(*parts))


# Global secure logger instance
_secure_logger: Optional[SecureLogger] = None


def get_secure_logger(name: str = "legal_summarizer") -> SecureLogger:
    """
    Get the global secure logger instance.
    
    Args:
        name: Logger name
        
    Returns:
        SecureLogger instance
    """
    global _secure_logger
    
    if _secure_logger is None:
        log_level = os.getenv("LOG_LEVEL", "INFO")
        _secure_logger = SecureLogger(name, log_level)
    
    return _secure_logger


def log_security_event(event_type: str, details: Dict[str, Any]) -> None:
    """
    Convenience function to log security events.
    
    Args:
        event_type: Type of security event
        details: Event details
    """
    logger = get_secure_logger()
    logger.log_security_event(event_type, details)


def log_document_processing(filename: str, file_size: int) -> str:
    """
    Convenience function to log document processing start.
    
    Args:
        filename: Document filename
        file_size: File size in bytes
        
    Returns:
        Processing session ID
    """
    logger = get_secure_logger()
    return logger.log_document_processing_start(filename, file_size)


if __name__ == "__main__":
    # Test secure logging
    logger = get_secure_logger()
    
    # Test various logging scenarios
    logger.log_document_processing_start("confidential_legal_document.pdf", 1024000)
    logger.log_security_event("file_upload", {"filename": "sensitive_case_file.pdf", "size": 2048})
    logger.log_error(Exception("Test error"), {"document_content": "This is sensitive legal content that should be redacted"})
    
    print("Secure logging test completed. Check logs/ directory for output.")