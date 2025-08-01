"""
End-to-end processing pipeline for the Legal Document Summarizer.
This module orchestrates the complete document processing workflow.
"""

import io
import time
from typing import Optional, Callable, Any, BinaryIO
from datetime import datetime

from ..models.data_models import (
    ProcessingState, 
    SummaryParams, 
    SummaryResult, 
    ValidationResult,
    DocumentMetadata
)
from ..services.document_handler import DocumentHandler
from ..services.text_extractor import TextExtractor
from ..services.summarizer import LegalSummarizer
from ..services.output_handler import OutputHandler
from ..utils.error_handler import ErrorHandler, ErrorType
from ..utils.config import Config


class ProcessingPipeline:
    """
    End-to-end processing pipeline that orchestrates the complete document 
    processing workflow from upload to summary generation.
    """
    
    def __init__(self):
        """Initialize the processing pipeline with all required components."""
        self.document_handler = DocumentHandler()
        self.text_extractor = TextExtractor()
        self.summarizer = LegalSummarizer()
        self.output_handler = OutputHandler()
        self.error_handler = ErrorHandler()
        
        self.current_state = ProcessingState.IDLE
        self.status_callback: Optional[Callable[[ProcessingState, str], None]] = None
        self.progress_callback: Optional[Callable[[int], None]] = None
        
        # Pipeline statistics
        self.processing_stats = {
            "documents_processed": 0,
            "total_processing_time": 0.0,
            "average_processing_time": 0.0,
            "errors_encountered": 0,
            "last_processed": None
        }
    
    def set_status_callback(self, callback: Callable[[ProcessingState, str], None]) -> None:
        """
        Set callback function for status updates.
        
        Args:
            callback: Function to call with (state, message) updates
        """
        self.status_callback = callback
    
    def set_progress_callback(self, callback: Callable[[int], None]) -> None:
        """
        Set callback function for progress updates.
        
        Args:
            callback: Function to call with progress percentage (0-100)
        """
        self.progress_callback = callback
    
    def _update_status(self, state: ProcessingState, message: str = "") -> None:
        """Update processing status and notify callback if set."""
        self.current_state = state
        if self.status_callback:
            self.status_callback(state, message)
    
    def _update_progress(self, percentage: int) -> None:
        """Update processing progress and notify callback if set."""
        if self.progress_callback:
            self.progress_callback(max(0, min(100, percentage)))
    
    def process_document(
        self, 
        file_data: BinaryIO, 
        filename: str, 
        summary_params: SummaryParams
    ) -> SummaryResult:
        """
        Process a document through the complete pipeline.
        
        Args:
            file_data: Binary file data
            filename: Original filename
            summary_params: Parameters for summary customization
            
        Returns:
            SummaryResult containing the generated summary and metadata
            
        Raises:
            Exception: If processing fails at any stage
        """
        start_time = time.time()
        temp_file_path = None
        
        try:
            # Stage 1: Document Upload and Validation (0-20%)
            self._update_status(ProcessingState.UPLOADING, "Validating document...")
            self._update_progress(5)
            
            validation_result = self._validate_document(file_data, filename)
            if not validation_result.is_valid:
                raise Exception(validation_result.error_message)
            
            self._update_progress(10)
            
            # Save to temporary file for processing
            temp_file_path = self._save_temp_file(file_data, filename)
            if not temp_file_path:
                raise Exception("Failed to save document for processing")
            
            self._update_progress(20)
            
            # Stage 2: Text Extraction (20-40%)
            self._update_status(ProcessingState.EXTRACTING, "Extracting text from document...")
            self._update_progress(25)
            
            extracted_text = self._extract_text(temp_file_path)
            if not extracted_text.strip():
                raise Exception("No readable text found in document")
            
            self._update_progress(35)
            
            # Validate legal content
            if not self._validate_legal_content(extracted_text):
                self._update_status(ProcessingState.EXTRACTING, "Warning: Document may not be legal content")
            
            self._update_progress(40)
            
            # Stage 3: AI Summarization (40-90%)
            self._update_status(ProcessingState.SUMMARIZING, "Generating AI summary...")
            self._update_progress(45)
            
            # Ensure model is loaded
            if not self.summarizer.is_model_loaded():
                self._update_status(ProcessingState.SUMMARIZING, "Loading AI model...")
                self._load_model()
                self._update_progress(60)
            
            # Generate summary
            self._update_status(ProcessingState.SUMMARIZING, "Processing document with AI...")
            summary_result = self._generate_summary(extracted_text, summary_params, filename)
            
            self._update_progress(90)
            
            # Stage 4: Finalization (90-100%)
            self._update_status(ProcessingState.COMPLETE, "Processing complete!")
            self._update_progress(100)
            
            # Update statistics
            processing_time = time.time() - start_time
            self._update_processing_stats(processing_time)
            
            return summary_result
            
        except Exception as e:
            self._update_status(ProcessingState.ERROR, f"Processing failed: {str(e)}")
            self._update_progress(0)
            self.processing_stats["errors_encountered"] += 1
            
            # Handle error based on current stage
            if self.current_state == ProcessingState.UPLOADING:
                user_message = self.error_handler.handle_upload_error(e, {"filename": filename})
            elif self.current_state == ProcessingState.EXTRACTING:
                user_message = self.error_handler.handle_extraction_error(e, {"filename": filename})
            elif self.current_state == ProcessingState.SUMMARIZING:
                user_message = self.error_handler.handle_model_error(e, {"filename": filename})
            else:
                user_message = self.error_handler.handle_system_error(e, {"stage": self.current_state.value})
            
            # Re-raise with user-friendly message
            raise Exception(user_message.message)
            
        finally:
            # Cleanup temporary files
            if temp_file_path:
                try:
                    self.document_handler.cleanup_temp_files()
                except Exception as cleanup_error:
                    # Log cleanup error but don't fail the main operation
                    self.error_handler._log_error(
                        cleanup_error, 
                        self.error_handler.ErrorContext(
                            error_type=ErrorType.SYSTEM_ERROR,
                            timestamp=datetime.now(),
                            user_action="cleanup",
                            file_info={"temp_file": temp_file_path}
                        )
                    )
    
    def _validate_document(self, file_data: BinaryIO, filename: str) -> ValidationResult:
        """Validate uploaded document with retry logic."""
        return self.error_handler.with_retry(
            self.document_handler.validate_file,
            "document_validation",
            file_data,
            filename
        )
    
    def _save_temp_file(self, file_data: BinaryIO, filename: str) -> Optional[str]:
        """Save document to temporary file with retry logic."""
        return self.error_handler.with_retry(
            self.document_handler.save_temp_file,
            "temp_file_save",
            file_data,
            filename
        )
    
    def _extract_text(self, file_path: str) -> str:
        """Extract text from document with retry logic."""
        return self.error_handler.with_retry(
            self.text_extractor.extract_text,
            "text_extraction",
            file_path
        )
    
    def _validate_legal_content(self, text: str) -> bool:
        """Validate that extracted text appears to be legal content."""
        try:
            return self.text_extractor.validate_legal_content(text)
        except Exception:
            # If validation fails, assume it's legal content to avoid blocking
            return True
    
    def _load_model(self) -> None:
        """Load AI model with retry logic."""
        self.error_handler.with_retry(
            self.summarizer.load_model,
            "model_loading"
        )
    
    def _generate_summary(
        self, 
        text: str, 
        params: SummaryParams, 
        filename: str
    ) -> SummaryResult:
        """Generate summary with retry logic."""
        return self.error_handler.with_retry(
            self.summarizer.summarize,
            "summary_generation",
            text,
            params,
            filename
        )
    
    def _update_processing_stats(self, processing_time: float) -> None:
        """Update pipeline processing statistics."""
        self.processing_stats["documents_processed"] += 1
        self.processing_stats["total_processing_time"] += processing_time
        self.processing_stats["average_processing_time"] = (
            self.processing_stats["total_processing_time"] / 
            self.processing_stats["documents_processed"]
        )
        self.processing_stats["last_processed"] = datetime.now().isoformat()
    
    def get_processing_stats(self) -> dict:
        """Get current processing statistics."""
        return self.processing_stats.copy()
    
    def reset_stats(self) -> None:
        """Reset processing statistics."""
        self.processing_stats = {
            "documents_processed": 0,
            "total_processing_time": 0.0,
            "average_processing_time": 0.0,
            "errors_encountered": 0,
            "last_processed": None
        }
    
    def get_current_state(self) -> ProcessingState:
        """Get current processing state."""
        return self.current_state
    
    def is_processing(self) -> bool:
        """Check if pipeline is currently processing a document."""
        return self.current_state not in [ProcessingState.IDLE, ProcessingState.COMPLETE, ProcessingState.ERROR]
    
    def cleanup(self) -> None:
        """Cleanup pipeline resources."""
        try:
            self.document_handler.cleanup_temp_files()
            self._update_status(ProcessingState.IDLE, "Pipeline cleaned up")
        except Exception as e:
            self.error_handler._log_error(
                e,
                self.error_handler.ErrorContext(
                    error_type=ErrorType.SYSTEM_ERROR,
                    timestamp=datetime.now(),
                    user_action="pipeline_cleanup"
                )
            )


class PipelineManager:
    """
    Manager class for handling multiple pipeline instances and providing
    a simplified interface for document processing.
    """
    
    def __init__(self):
        """Initialize the pipeline manager."""
        self.pipeline = ProcessingPipeline()
        self.error_handler = ErrorHandler()
    
    def process_document_with_callbacks(
        self,
        file_data: BinaryIO,
        filename: str,
        summary_params: SummaryParams,
        status_callback: Optional[Callable[[ProcessingState, str], None]] = None,
        progress_callback: Optional[Callable[[int], None]] = None
    ) -> SummaryResult:
        """
        Process document with optional status and progress callbacks.
        
        Args:
            file_data: Binary file data
            filename: Original filename
            summary_params: Summary customization parameters
            status_callback: Optional callback for status updates
            progress_callback: Optional callback for progress updates
            
        Returns:
            SummaryResult containing the generated summary
        """
        # Set callbacks
        if status_callback:
            self.pipeline.set_status_callback(status_callback)
        if progress_callback:
            self.pipeline.set_progress_callback(progress_callback)
        
        try:
            return self.pipeline.process_document(file_data, filename, summary_params)
        finally:
            # Reset callbacks
            self.pipeline.set_status_callback(None)
            self.pipeline.set_progress_callback(None)
    
    def get_pipeline_status(self) -> dict:
        """Get current pipeline status and statistics."""
        return {
            "current_state": self.pipeline.get_current_state().value,
            "is_processing": self.pipeline.is_processing(),
            "statistics": self.pipeline.get_processing_stats(),
            "model_loaded": self.pipeline.summarizer.is_model_loaded()
        }
    
    def preload_model(self) -> None:
        """Preload the AI model for faster processing."""
        if not self.pipeline.summarizer.is_model_loaded():
            self.pipeline._load_model()
    
    def cleanup_all(self) -> None:
        """Cleanup all pipeline resources."""
        self.pipeline.cleanup()