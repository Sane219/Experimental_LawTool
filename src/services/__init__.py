# Services package

from .document_handler import DocumentHandler
from .text_extractor import TextExtractor
from .summarizer import LegalSummarizer

__all__ = ["DocumentHandler", "TextExtractor", "LegalSummarizer"]