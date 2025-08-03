"""
Core data models for the Legal Document Summarizer.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


@dataclass
class DocumentMetadata:
    """Metadata for uploaded documents."""
    filename: str
    file_size: int
    file_type: str
    upload_timestamp: datetime


@dataclass
class SummaryParams:
    """Parameters for customizing summary generation."""
    length: str = "standard"  # "brief", "standard", "detailed"
    focus: str = "general"    # "general", "obligations", "parties", "dates"
    max_words: int = 300


@dataclass
class SummaryResult:
    """Result of document summarization."""
    original_filename: str
    summary_text: str
    processing_time: float
    word_count: int
    confidence_score: float
    generated_at: datetime


@dataclass
class ValidationResult:
    """Result of file validation."""
    is_valid: bool
    error_message: Optional[str]
    file_info: Optional[DocumentMetadata]


class ProcessingState(Enum):
    """States of the document processing pipeline."""
    IDLE = "idle"
    UPLOADING = "uploading"
    EXTRACTING = "extracting_text"
    SUMMARIZING = "generating_summary"
    COMPLETE = "complete"
    ERROR = "error"