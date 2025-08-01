"""
Comprehensive error handling system for the Legal Document Summarizer.
"""

import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, Callable, Any
from datetime import datetime


class ErrorType(Enum):
    UPLOAD_ERROR = "upload_error"
    EXTRACTION_ERROR = "extraction_error"
    MODEL_ERROR = "model_error"
    SYSTEM_ERROR = "system_error"
    VALIDATION_ERROR = "validation_error"
    TIMEOUT_ERROR = "timeout_error"


class ErrorSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class UserMessage:
    title: str
    message: str
    suggested_actions: list[str]
    severity: ErrorSeverity
    show_retry: bool = False
    show_contact_support: bool = False


@dataclass
class ErrorContext:
    error_type: ErrorType
    timestamp: datetime
    user_action: str
    file_info: Optional[Dict[str, Any]] = None
    system_info: Optional[Dict[str, Any]] = None
    stack_trace: Optional[str] = None


class ErrorHandler:
    def __init__(self, logger_name: str = "legal_summarizer"):
        self.logger = self._setup_logger(logger_name)
        self.retry_counts: Dict[str, int] = {}
        self.max_retries = 3
        self.retry_delay = 1.0

    def _setup_logger(self, name: str) -> logging.Logger:
        """Set up logging configuration."""
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # File handler for detailed logs
            try:
                file_handler = logging.FileHandler('logs/error.log')
                file_handler.setLevel(logging.DEBUG)
                
                # Formatter
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
                console_handler.setFormatter(formatter)
                file_handler.setFormatter(formatter)
                
                logger.addHandler(console_handler)
                logger.addHandler(file_handler)
            except Exception:
                # If file logging fails, just use console
                logger.addHandler(console_handler)
            
        return logger

    def handle_upload_error(self, error: Exception, context: Optional[Dict] = None) -> UserMessage:
        """Handle file upload related errors."""
        error_context = ErrorContext(
            error_type=ErrorType.UPLOAD_ERROR,
            timestamp=datetime.now(),
            user_action="file_upload",
            file_info=context,
            stack_trace=str(error)
        )
        
        self._log_error(error, error_context)
        
        if "size" in str(error).lower():
            return UserMessage(
                title="File Too Large",
                message="The uploaded file exceeds the 10MB size limit. Please try a smaller file.",
                suggested_actions=[
                    "Compress the document if possible",
                    "Split large documents into smaller sections",
                    "Convert to a more efficient format (PDF to TXT)"
                ],
                severity=ErrorSeverity.MEDIUM,
                show_retry=True
            )
        elif "format" in str(error).lower() or "type" in str(error).lower():
            return UserMessage(
                title="Unsupported File Format",
                message="Please upload a PDF, DOCX, or TXT file.",
                suggested_actions=[
                    "Convert your document to PDF, DOCX, or TXT format",
                    "Ensure the file extension matches the actual file type"
                ],
                severity=ErrorSeverity.MEDIUM,
                show_retry=True
            )
        else:
            return UserMessage(
                title="Upload Failed",
                message="There was a problem uploading your file. Please try again.",
                suggested_actions=[
                    "Check your internet connection",
                    "Try uploading a different file",
                    "Refresh the page and try again"
                ],
                severity=ErrorSeverity.MEDIUM,
                show_retry=True
            )

    def handle_extraction_error(self, error: Exception, context: Optional[Dict] = None) -> UserMessage:
        """Handle text extraction related errors."""
        error_context = ErrorContext(
            error_type=ErrorType.EXTRACTION_ERROR,
            timestamp=datetime.now(),
            user_action="text_extraction",
            file_info=context,
            stack_trace=str(error)
        )
        
        self._log_error(error, error_context)
        
        if "empty" in str(error).lower() or "no text" in str(error).lower():
            return UserMessage(
                title="No Readable Content",
                message="The document appears to be empty or contains no readable text.",
                suggested_actions=[
                    "Ensure the document contains text (not just images)",
                    "Try a different version of the document",
                    "Check if the document is password protected"
                ],
                severity=ErrorSeverity.MEDIUM,
                show_retry=False
            )
        else:
            return UserMessage(
                title="Text Extraction Failed",
                message="Unable to extract text from the document. This may be due to formatting issues.",
                suggested_actions=[
                    "Try converting the document to a different format",
                    "Ensure the document is not password protected",
                    "Check if the document contains selectable text"
                ],
                severity=ErrorSeverity.HIGH,
                show_retry=True,
                show_contact_support=True
            )

    def handle_model_error(self, error: Exception, context: Optional[Dict] = None) -> UserMessage:
        """Handle AI model related errors."""
        error_context = ErrorContext(
            error_type=ErrorType.MODEL_ERROR,
            timestamp=datetime.now(),
            user_action="ai_summarization",
            file_info=context,
            stack_trace=str(error)
        )
        
        self._log_error(error, error_context)
        
        if "memory" in str(error).lower() or "out of memory" in str(error).lower():
            return UserMessage(
                title="Document Too Large for Processing",
                message="The document is too large for our AI model to process in one go.",
                suggested_actions=[
                    "The system will automatically try to process the document in smaller chunks",
                    "Consider splitting very large documents into sections",
                    "Try using the 'brief' summary option for large documents"
                ],
                severity=ErrorSeverity.MEDIUM,
                show_retry=True
            )
        elif "model" in str(error).lower() and "unavailable" in str(error).lower():
            return UserMessage(
                title="AI Service Temporarily Unavailable",
                message="The AI summarization service is currently unavailable. Estimated resolution time: 5-10 minutes.",
                suggested_actions=[
                    "Please try again in a few minutes",
                    "Check our status page for updates",
                    "Save your document and return later"
                ],
                severity=ErrorSeverity.HIGH,
                show_retry=True,
                show_contact_support=True
            )
        else:
            return UserMessage(
                title="AI Processing Error",
                message="There was an error generating the summary. Our team has been notified.",
                suggested_actions=[
                    "Try again in a few minutes",
                    "Try with a different document",
                    "Use different summary parameters"
                ],
                severity=ErrorSeverity.HIGH,
                show_retry=True,
                show_contact_support=True
            )

    def handle_system_error(self, error: Exception, context: Optional[Dict] = None) -> UserMessage:
        """Handle general system errors."""
        error_context = ErrorContext(
            error_type=ErrorType.SYSTEM_ERROR,
            timestamp=datetime.now(),
            user_action="system_operation",
            system_info=context,
            stack_trace=str(error)
        )
        
        self._log_error(error, error_context)
        
        return UserMessage(
            title="System Error",
            message="An unexpected system error occurred. Our team has been notified.",
            suggested_actions=[
                "Try refreshing the page",
                "Try again in a few minutes",
                "Contact support if the issue persists"
            ],
            severity=ErrorSeverity.CRITICAL,
            show_retry=True,
            show_contact_support=True
        )

    def handle_validation_error(self, error: Exception, context: Optional[Dict] = None) -> UserMessage:
        """Handle validation related errors."""
        error_context = ErrorContext(
            error_type=ErrorType.VALIDATION_ERROR,
            timestamp=datetime.now(),
            user_action="validation",
            file_info=context,
            stack_trace=str(error)
        )
        
        self._log_error(error, error_context)
        
        return UserMessage(
            title="Validation Error",
            message=f"Document validation failed: {str(error)}",
            suggested_actions=[
                "Ensure the document is a valid legal document",
                "Check that the file is not corrupted",
                "Try a different document format"
            ],
            severity=ErrorSeverity.MEDIUM,
            show_retry=True
        )

    def with_retry(self, operation: Callable, operation_id: str, *args, **kwargs) -> Any:
        """Execute an operation with retry logic."""
        if operation_id not in self.retry_counts:
            self.retry_counts[operation_id] = 0
            
        while self.retry_counts[operation_id] < self.max_retries:
            try:
                result = operation(*args, **kwargs)
                # Reset retry count on success
                self.retry_counts[operation_id] = 0
                return result
            except Exception as e:
                self.retry_counts[operation_id] += 1
                
                if self.retry_counts[operation_id] >= self.max_retries:
                    self.logger.error(
                        f"Operation {operation_id} failed after {self.max_retries} retries: {str(e)}"
                    )
                    raise e
                
                self.logger.warning(
                    f"Operation {operation_id} failed (attempt {self.retry_counts[operation_id]}), retrying in {self.retry_delay}s: {str(e)}"
                )
                time.sleep(self.retry_delay * self.retry_counts[operation_id])  # Exponential backoff
        
        raise Exception(f"Operation {operation_id} failed after maximum retries")

    def reset_retry_count(self, operation_id: str) -> None:
        if operation_id in self.retry_counts:
            del self.retry_counts[operation_id]

    def _log_error(self, error: Exception, context: ErrorContext) -> None:
        """Log error with context information."""
        log_message = f"Error Type: {context.error_type.value} | "
        log_message += f"User Action: {context.user_action} | "
        log_message += f"Error: {str(error)}"
        
        if context.file_info:
            log_message += f" | File Info: {context.file_info}"
        
        if context.system_info:
            log_message += f" | System Info: {context.system_info}"
            
        # Log at appropriate level based on error type
        if context.error_type in [ErrorType.SYSTEM_ERROR, ErrorType.MODEL_ERROR]:
            self.logger.error(log_message)
        elif context.error_type in [ErrorType.EXTRACTION_ERROR, ErrorType.VALIDATION_ERROR]:
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)
            
        # Log stack trace for debugging (only in debug mode)
        if context.stack_trace:
            self.logger.debug(f"Stack trace: {context.stack_trace}")

    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics for monitoring."""
        return {
            "retry_counts": self.retry_counts.copy(),
            "timestamp": datetime.now().isoformat()
        }

    def cleanup_old_retry_counts(self, max_age_hours: int = 24) -> None:
        """Clean up old retry counts to prevent memory leaks."""
        # This is a simple implementation - in production, you'd want to track timestamps
        if len(self.retry_counts) > 1000:  # Arbitrary limit
            self.retry_counts.clear()
            self.logger.info("Cleared old retry counts to prevent memory buildup")