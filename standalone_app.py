"""
Standalone Streamlit application for the AI-Powered Legal Document Summarizer.
This version includes all essential components inline to avoid import issues.
"""

import streamlit as st
import time
import io
import os
import tempfile
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from typing import Optional
import PyPDF2
import docx
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import json

# ============================================================================
# DATA MODELS (Inline)
# ============================================================================

class ProcessingState(Enum):
    """States of the document processing pipeline."""
    IDLE = "idle"
    UPLOADING = "uploading"
    EXTRACTING = "extracting_text"
    SUMMARIZING = "generating_summary"
    COMPLETE = "complete"
    ERROR = "error"

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
class DocumentMetadata:
    """Metadata for uploaded documents."""
    filename: str
    file_size: int
    file_type: str
    upload_timestamp: datetime

@dataclass
class ValidationResult:
    """Result of file validation."""
    is_valid: bool
    error_message: Optional[str]
    file_info: Optional[DocumentMetadata]

# ============================================================================
# CONFIGURATION (Inline)
# ============================================================================

class Config:
    """Application configuration."""
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    SUPPORTED_FORMATS = ['.pdf', '.docx', '.txt']
    MAX_CHUNK_SIZE = 1024
    SUMMARY_LENGTHS = {
        'brief': {'min_words': 100, 'max_words': 200},
        'standard': {'min_words': 200, 'max_words': 400},
        'detailed': {'min_words': 400, 'max_words': 600}
    }

# ============================================================================
# CORE SERVICES (Inline)
# ============================================================================

class DocumentHandler:
    """Handles document upload and validation."""
    
    def validate_file(self, file_data: io.BytesIO, filename: str) -> ValidationResult:
        """Validate uploaded file."""
        try:
            # Check file size
            file_size = len(file_data.getvalue())
            if file_size > Config.MAX_FILE_SIZE:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"File size ({file_size / (1024*1024):.1f}MB) exceeds maximum allowed size ({Config.MAX_FILE_SIZE / (1024*1024)}MB)",
                    file_info=None
                )
            
            # Check file extension
            file_extension = os.path.splitext(filename)[1].lower()
            if file_extension not in Config.SUPPORTED_FORMATS:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Unsupported file format: {file_extension}. Supported formats: {', '.join(Config.SUPPORTED_FORMATS)}",
                    file_info=None
                )
            
            # Create file metadata
            file_info = DocumentMetadata(
                filename=filename,
                file_size=file_size,
                file_type=file_extension,
                upload_timestamp=datetime.now()
            )
            
            return ValidationResult(
                is_valid=True,
                error_message=None,
                file_info=file_info
            )
            
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                error_message=f"File validation error: {str(e)}",
                file_info=None
            )

class TextExtractor:
    """Extracts text from various document formats."""
    
    def extract_from_pdf(self, file_data: io.BytesIO) -> str:
        """Extract text from PDF file."""
        try:
            pdf_reader = PyPDF2.PdfReader(file_data)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"PDF extraction failed: {str(e)}")
    
    def extract_from_docx(self, file_data: io.BytesIO) -> str:
        """Extract text from DOCX file."""
        try:
            doc = docx.Document(file_data)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"DOCX extraction failed: {str(e)}")
    
    def extract_from_txt(self, file_data: io.BytesIO) -> str:
        """Extract text from TXT file."""
        try:
            text = file_data.getvalue().decode('utf-8')
            return text.strip()
        except Exception as e:
            raise Exception(f"TXT extraction failed: {str(e)}")

class SimpleSummarizer:
    """Simple text summarizer (mock implementation for demo)."""
    
    def summarize(self, text: str, params: SummaryParams, filename: str) -> SummaryResult:
        """Generate a simple summary (mock implementation)."""
        start_time = time.time()
        
        # Simple extractive summarization (first few sentences)
        sentences = text.split('.')
        
        # Determine number of sentences based on length preference
        if params.length == "brief":
            num_sentences = min(3, len(sentences))
        elif params.length == "detailed":
            num_sentences = min(8, len(sentences))
        else:  # standard
            num_sentences = min(5, len(sentences))
        
        # Create summary based on focus
        if params.focus == "parties":
            # Look for sentences with party-related keywords
            party_keywords = ["party", "parties", "company", "corporation", "LLC", "Inc", "agreement between"]
            relevant_sentences = []
            for sentence in sentences[:20]:  # Check first 20 sentences
                if any(keyword.lower() in sentence.lower() for keyword in party_keywords):
                    relevant_sentences.append(sentence.strip())
            summary_sentences = relevant_sentences[:num_sentences] if relevant_sentences else sentences[:num_sentences]
        
        elif params.focus == "dates":
            # Look for sentences with date-related keywords
            date_keywords = ["date", "deadline", "expires", "effective", "term", "duration"]
            relevant_sentences = []
            for sentence in sentences[:20]:
                if any(keyword.lower() in sentence.lower() for keyword in date_keywords):
                    relevant_sentences.append(sentence.strip())
            summary_sentences = relevant_sentences[:num_sentences] if relevant_sentences else sentences[:num_sentences]
        
        elif params.focus == "obligations":
            # Look for sentences with obligation-related keywords
            obligation_keywords = ["shall", "must", "required", "obligation", "duty", "responsible", "agree"]
            relevant_sentences = []
            for sentence in sentences[:20]:
                if any(keyword.lower() in sentence.lower() for keyword in obligation_keywords):
                    relevant_sentences.append(sentence.strip())
            summary_sentences = relevant_sentences[:num_sentences] if relevant_sentences else sentences[:num_sentences]
        
        else:  # general
            summary_sentences = sentences[:num_sentences]
        
        # Join sentences and clean up
        summary_text = '. '.join([s.strip() for s in summary_sentences if s.strip()])
        if summary_text and not summary_text.endswith('.'):
            summary_text += '.'
        
        # Add focus-specific prefix
        focus_prefixes = {
            "parties": "Key Parties and Entities: ",
            "dates": "Important Dates and Deadlines: ",
            "obligations": "Key Obligations and Requirements: ",
            "general": "Document Summary: "
        }
        
        summary_text = focus_prefixes.get(params.focus, "") + summary_text
        
        # Calculate metrics
        processing_time = time.time() - start_time
        word_count = len(summary_text.split())
        confidence_score = 0.75  # Mock confidence score
        
        return SummaryResult(
            original_filename=filename,
            summary_text=summary_text,
            processing_time=processing_time,
            word_count=word_count,
            confidence_score=confidence_score,
            generated_at=datetime.now()
        )

class OutputHandler:
    """Handles output formatting and export."""
    
    def format_summary_for_clipboard(self, summary_result: SummaryResult) -> str:
        """Format summary for clipboard copying."""
        return f"""Legal Document Summary
========================

Original File: {summary_result.original_filename}
Generated: {summary_result.generated_at.strftime('%Y-%m-%d %H:%M:%S')}
Word Count: {summary_result.word_count}
Confidence: {summary_result.confidence_score:.0%}

Summary:
{summary_result.summary_text}

---
Generated by AI-Powered Legal Document Summarizer"""
    
    def generate_pdf_export(self, summary_result: SummaryResult) -> io.BytesIO:
        """Generate PDF export of summary."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title = Paragraph("Legal Document Summary", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Metadata
        metadata = f"""
        <b>Original File:</b> {summary_result.original_filename}<br/>
        <b>Generated:</b> {summary_result.generated_at.strftime('%Y-%m-%d %H:%M:%S')}<br/>
        <b>Word Count:</b> {summary_result.word_count}<br/>
        <b>Confidence:</b> {summary_result.confidence_score:.0%}
        """
        meta_para = Paragraph(metadata, styles['Normal'])
        story.append(meta_para)
        story.append(Spacer(1, 12))
        
        # Summary
        summary_title = Paragraph("Summary", styles['Heading2'])
        story.append(summary_title)
        summary_para = Paragraph(summary_result.summary_text, styles['Normal'])
        story.append(summary_para)
        
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def create_json_export(self, summary_result: SummaryResult) -> str:
        """Create JSON export of summary."""
        data = {
            "original_filename": summary_result.original_filename,
            "summary_text": summary_result.summary_text,
            "processing_time": summary_result.processing_time,
            "word_count": summary_result.word_count,
            "confidence_score": summary_result.confidence_score,
            "generated_at": summary_result.generated_at.isoformat()
        }
        return json.dumps(data, indent=2)
    
    def generate_filename(self, summary_result: SummaryResult, extension: str) -> str:
        """Generate filename for export."""
        base_name = os.path.splitext(summary_result.original_filename)[0]
        timestamp = summary_result.generated_at.strftime('%Y%m%d_%H%M%S')
        return f"{base_name}_summary_{timestamp}.{extension}"

# ============================================================================
# MAIN APPLICATION
# ============================================================================

class LegalDocumentSummarizerApp:
    """Standalone Streamlit application class."""
    
    def __init__(self):
        """Initialize the application with required services."""
        self.document_handler = DocumentHandler()
        self.text_extractor = TextExtractor()
        self.summarizer = SimpleSummarizer()
        self.output_handler = OutputHandler()
        
        # Initialize session state
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """Initialize Streamlit session state variables."""
        if 'processing_state' not in st.session_state:
            st.session_state.processing_state = ProcessingState.IDLE
        if 'summary_result' not in st.session_state:
            st.session_state.summary_result = None
        if 'error_message' not in st.session_state:
            st.session_state.error_message = None
    
    def render_upload_interface(self):
        """Render the file upload interface."""
        st.subheader("📄 Upload Legal Document")
        
        uploaded_file = st.file_uploader(
            "Choose a legal document",
            type=['pdf', 'docx', 'txt'],
            help=f"Supported formats: PDF, DOCX, TXT. Maximum size: {Config.MAX_FILE_SIZE // (1024*1024)}MB"
        )
        
        if uploaded_file is not None:
            file_details = {
                "Filename": uploaded_file.name,
                "File size": f"{uploaded_file.size / 1024:.1f} KB",
                "File type": uploaded_file.type
            }
            
            with st.expander("📋 File Details", expanded=False):
                for key, value in file_details.items():
                    st.write(f"**{key}:** {value}")
        
        return uploaded_file
    
    def render_customization_controls(self) -> SummaryParams:
        """Render summary customization controls."""
        st.subheader("⚙️ Summary Customization")
        
        col1, col2 = st.columns(2)
        
        with col1:
            length_options = {
                "brief": "Brief (100-200 words)",
                "standard": "Standard (200-400 words)", 
                "detailed": "Detailed (400-600 words)"
            }
            
            selected_length = st.selectbox(
                "Summary Length",
                options=list(length_options.keys()),
                format_func=lambda x: length_options[x],
                index=1,
                help="Choose how detailed you want the summary to be"
            )
        
        with col2:
            focus_options = {
                "general": "General Overview",
                "obligations": "Key Obligations & Duties",
                "parties": "Parties & Relationships",
                "dates": "Important Dates & Deadlines"
            }
            
            selected_focus = st.selectbox(
                "Summary Focus",
                options=list(focus_options.keys()),
                format_func=lambda x: focus_options[x],
                index=0,
                help="Choose what aspect of the document to emphasize"
            )
        
        with st.expander("🔧 Advanced Options", expanded=False):
            max_words = st.slider(
                "Maximum Words",
                min_value=50,
                max_value=1000,
                value=300,
                step=50,
                help="Set the maximum number of words in the summary"
            )
        
        return SummaryParams(
            length=selected_length,
            focus=selected_focus,
            max_words=max_words
        )
    
    def display_processing_status(self, status: ProcessingState):
        """Display processing status with progress indicators."""
        status_messages = {
            ProcessingState.IDLE: ("⏳", "Ready to process"),
            ProcessingState.UPLOADING: ("📤", "Uploading document..."),
            ProcessingState.EXTRACTING: ("📝", "Extracting text from document..."),
            ProcessingState.SUMMARIZING: ("🤖", "Generating AI summary..."),
            ProcessingState.COMPLETE: ("✅", "Summary generated successfully!"),
            ProcessingState.ERROR: ("❌", "An error occurred during processing")
        }
        
        icon, message = status_messages.get(status, ("⏳", "Processing..."))
        
        if status in [ProcessingState.UPLOADING, ProcessingState.EXTRACTING, ProcessingState.SUMMARIZING]:
            with st.spinner(f"{icon} {message}"):
                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.01)
                    progress_bar.progress(i + 1)
                progress_bar.empty()
        else:
            st.info(f"{icon} {message}")
    
    def render_summary_output(self, summary_result: SummaryResult):
        """Render the summary output with formatting and actions."""
        if summary_result is None:
            return
        
        st.subheader("📋 Generated Summary")
        
        # Summary metadata
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Word Count", summary_result.word_count)
        with col2:
            st.metric("Processing Time", f"{summary_result.processing_time:.1f}s")
        with col3:
            confidence_percentage = int(summary_result.confidence_score * 100)
            st.metric("Confidence", f"{confidence_percentage}%")
        
        # Summary text display
        st.markdown("### Summary")
        st.markdown(
            f"""
            <div style="
                background-color: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
                border-left: 4px solid #007bff;
                margin: 10px 0;
            ">
                {summary_result.summary_text}
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Action buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📋 Copy to Clipboard", use_container_width=True):
                clipboard_text = self.output_handler.format_summary_for_clipboard(summary_result)
                st.success("Summary formatted for clipboard!")
                
                with st.expander("📋 Formatted Text (Select All & Copy)", expanded=True):
                    st.code(clipboard_text, language=None)
        
        with col2:
            if st.button("📄 Download PDF", use_container_width=True):
                try:
                    pdf_buffer = self.output_handler.generate_pdf_export(summary_result)
                    pdf_filename = self.output_handler.generate_filename(summary_result, "pdf")
                    
                    st.download_button(
                        label="📄 Download PDF",
                        data=pdf_buffer.getvalue(),
                        file_name=pdf_filename,
                        mime="application/pdf",
                        help="Download a professionally formatted PDF of the summary"
                    )
                    st.success("PDF generated successfully!")
                except Exception as e:
                    st.error(f"PDF generation failed: {str(e)}")
        
        # Additional export options
        with st.expander("📤 Additional Export Options", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📝 Download as Text", use_container_width=True):
                    text_content = self.output_handler.format_summary_for_clipboard(summary_result)
                    text_filename = self.output_handler.generate_filename(summary_result, "txt")
                    
                    st.download_button(
                        label="📝 Download Text File",
                        data=text_content,
                        file_name=text_filename,
                        mime="text/plain",
                        help="Download as plain text file"
                    )
            
            with col2:
                if st.button("📊 Download as JSON", use_container_width=True):
                    json_content = self.output_handler.create_json_export(summary_result)
                    json_filename = self.output_handler.generate_filename(summary_result, "json")
                    
                    st.download_button(
                        label="📊 Download JSON File",
                        data=json_content,
                        file_name=json_filename,
                        mime="application/json",
                        help="Download structured data as JSON"
                    )
        
        # Document information
        with st.expander("📄 Document Information", expanded=False):
            st.write(f"**Original File:** {summary_result.original_filename}")
            st.write(f"**Generated:** {summary_result.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
            st.write(f"**Processing Time:** {summary_result.processing_time:.2f} seconds")
            st.write(f"**Confidence Score:** {summary_result.confidence_score:.2f}")
    
    def process_document(self, uploaded_file, summary_params: SummaryParams):
        """Process the uploaded document and generate summary."""
        try:
            # Update processing state
            st.session_state.processing_state = ProcessingState.UPLOADING
            
            # Read file data
            file_data = io.BytesIO(uploaded_file.read())
            
            # Validate file
            validation_result = self.document_handler.validate_file(file_data, uploaded_file.name)
            
            if not validation_result.is_valid:
                st.session_state.error_message = validation_result.error_message
                st.session_state.processing_state = ProcessingState.ERROR
                return
            
            # Extract text
            st.session_state.processing_state = ProcessingState.EXTRACTING
            
            file_extension = validation_result.file_info.file_type.lower()
            file_data.seek(0)  # Reset file pointer
            
            if file_extension == '.pdf':
                extracted_text = self.text_extractor.extract_from_pdf(file_data)
            elif file_extension == '.docx':
                extracted_text = self.text_extractor.extract_from_docx(file_data)
            elif file_extension == '.txt':
                extracted_text = self.text_extractor.extract_from_txt(file_data)
            else:
                raise Exception(f"Unsupported file type: {file_extension}")
            
            if not extracted_text or len(extracted_text.strip()) < 10:
                raise Exception("No readable text found in document")
            
            # Generate summary
            st.session_state.processing_state = ProcessingState.SUMMARIZING
            
            summary_result = self.summarizer.summarize(
                extracted_text,
                summary_params,
                uploaded_file.name
            )
            
            # Store result and update state
            st.session_state.summary_result = summary_result
            st.session_state.processing_state = ProcessingState.COMPLETE
            st.session_state.error_message = None
            
        except Exception as e:
            st.session_state.error_message = str(e)
            st.session_state.processing_state = ProcessingState.ERROR
    
    def run(self):
        """Main application run method."""
        # Page configuration
        st.set_page_config(
            page_title="Legal Document Summarizer",
            page_icon="⚖️",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Main title and description
        st.title("⚖️ AI-Powered Legal Document Summarizer")
        st.markdown("""
        Upload legal documents and get AI-generated summaries instantly. 
        This standalone version works without complex dependencies and provides 
        basic summarization functionality for testing purposes.
        """)
        
        # Sidebar with information
        with st.sidebar:
            st.header("ℹ️ About")
            st.markdown("""
            This is a standalone version of the Legal Document Summarizer 
            designed to work reliably on Streamlit Cloud.
            
            **Supported formats:**
            - PDF documents
            - Word documents (.docx)
            - Text files (.txt)
            
            **Features:**
            - Basic text extraction
            - Simple summarization
            - Multiple export formats
            - Secure processing
            """)
            
            st.header("🔧 Technical Info")
            st.success("✅ All modules loaded")
            st.info("📦 Standalone version")
        
        # Display error message if any
        if st.session_state.error_message:
            st.error(f"❌ Error: {st.session_state.error_message}")
            if st.button("🔄 Clear Error"):
                st.session_state.error_message = None
                st.session_state.processing_state = ProcessingState.IDLE
                st.rerun()
        
        # Main content area
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # File upload interface
            uploaded_file = self.render_upload_interface()
            
            # Summary customization controls
            summary_params = self.render_customization_controls()
            
            # Process button
            if uploaded_file is not None:
                if st.button("🚀 Generate Summary", type="primary", use_container_width=True):
                    self.process_document(uploaded_file, summary_params)
        
        with col2:
            # Processing status
            if st.session_state.processing_state != ProcessingState.IDLE:
                self.display_processing_status(st.session_state.processing_state)
            
            # Summary output
            if st.session_state.summary_result:
                self.render_summary_output(st.session_state.summary_result)
        
        # Footer
        st.markdown("---")
        st.markdown(
            """
            <div style="text-align: center; color: #666; font-size: 0.8em;">
                🚀 Standalone Legal Document Summarizer<br>
                Designed for reliable deployment on Streamlit Cloud
            </div>
            """,
            unsafe_allow_html=True
        )

def main():
    """Main application entry point."""
    app = LegalDocumentSummarizerApp()
    app.run()

if __name__ == "__main__":
    main()