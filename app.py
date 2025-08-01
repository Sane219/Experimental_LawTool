"""
Main Streamlit application for the AI-Powered Legal Document Summarizer.
This is the entry point for the web application.
"""

import streamlit as st
import time
import io
import sys
import os
from datetime import datetime
from typing import Optional

# Multiple strategies to fix import issues on Streamlit Cloud
def fix_imports():
    """Fix import paths for Streamlit Cloud compatibility."""
    # Strategy 1: Add current directory and parent directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    
    for path in [current_dir, parent_dir]:
        if path not in sys.path:
            sys.path.insert(0, path)
    
    # Strategy 2: Add src directory explicitly
    src_dir = os.path.join(current_dir, 'src')
    if os.path.exists(src_dir) and src_dir not in sys.path:
        sys.path.insert(0, src_dir)
    
    # Strategy 3: Set PYTHONPATH environment variable
    current_pythonpath = os.environ.get('PYTHONPATH', '')
    new_paths = [current_dir, src_dir]
    for path in new_paths:
        if path not in current_pythonpath:
            current_pythonpath = f"{path}:{current_pythonpath}" if current_pythonpath else path
    os.environ['PYTHONPATH'] = current_pythonpath

# Apply import fixes
fix_imports()

# Import with multiple fallback strategies
def safe_import():
    """Safely import modules with multiple strategies."""
    import_errors = []
    
    # Strategy 1: Direct imports
    try:
        from src.models.data_models import SummaryParams, ProcessingState
        from src.services.document_handler import DocumentHandler
        from src.services.text_extractor import TextExtractor
        from src.services.summarizer import LegalSummarizer
        from src.services.output_handler import OutputHandler
        from src.services.security_service import get_security_service
        from src.utils.error_handler import ErrorHandler
        from src.utils.config import Config
        from src.utils.secure_logging import get_secure_logger
        from src.utils.https_config import setup_streamlit_https
        return {
            'SummaryParams': SummaryParams,
            'ProcessingState': ProcessingState,
            'DocumentHandler': DocumentHandler,
            'TextExtractor': TextExtractor,
            'LegalSummarizer': LegalSummarizer,
            'OutputHandler': OutputHandler,
            'get_security_service': get_security_service,
            'ErrorHandler': ErrorHandler,
            'Config': Config,
            'get_secure_logger': get_secure_logger,
            'setup_streamlit_https': setup_streamlit_https
        }
    except ImportError as e:
        import_errors.append(f"Strategy 1 failed: {e}")
    
    # Strategy 2: Relative imports
    try:
        import src.models.data_models as data_models
        import src.services.document_handler as document_handler
        import src.services.text_extractor as text_extractor
        import src.services.summarizer as summarizer
        import src.services.output_handler as output_handler
        import src.services.security_service as security_service
        import src.utils.error_handler as error_handler
        import src.utils.config as config
        import src.utils.secure_logging as secure_logging
        import src.utils.https_config as https_config
        
        return {
            'SummaryParams': data_models.SummaryParams,
            'ProcessingState': data_models.ProcessingState,
            'DocumentHandler': document_handler.DocumentHandler,
            'TextExtractor': text_extractor.TextExtractor,
            'LegalSummarizer': summarizer.LegalSummarizer,
            'OutputHandler': output_handler.OutputHandler,
            'get_security_service': security_service.get_security_service,
            'ErrorHandler': error_handler.ErrorHandler,
            'Config': config.Config,
            'get_secure_logger': secure_logging.get_secure_logger,
            'setup_streamlit_https': https_config.setup_streamlit_https
        }
    except ImportError as e:
        import_errors.append(f"Strategy 2 failed: {e}")
    
    # Strategy 3: Add src to path and try again
    try:
        import importlib.util
        import sys
        
        # Dynamically load modules
        modules = {}
        module_paths = {
            'data_models': 'src/models/data_models.py',
            'document_handler': 'src/services/document_handler.py',
            'text_extractor': 'src/services/text_extractor.py',
            'summarizer': 'src/services/summarizer.py',
            'output_handler': 'src/services/output_handler.py',
            'security_service': 'src/services/security_service.py',
            'error_handler': 'src/utils/error_handler.py',
            'config': 'src/utils/config.py',
            'secure_logging': 'src/utils/secure_logging.py',
            'https_config': 'src/utils/https_config.py'
        }
        
        for module_name, module_path in module_paths.items():
            if os.path.exists(module_path):
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                modules[module_name] = module
        
        if len(modules) == len(module_paths):
            return {
                'SummaryParams': modules['data_models'].SummaryParams,
                'ProcessingState': modules['data_models'].ProcessingState,
                'DocumentHandler': modules['document_handler'].DocumentHandler,
                'TextExtractor': modules['text_extractor'].TextExtractor,
                'LegalSummarizer': modules['summarizer'].LegalSummarizer,
                'OutputHandler': modules['output_handler'].OutputHandler,
                'get_security_service': modules['security_service'].get_security_service,
                'ErrorHandler': modules['error_handler'].ErrorHandler,
                'Config': modules['config'].Config,
                'get_secure_logger': modules['secure_logging'].get_secure_logger,
                'setup_streamlit_https': modules['https_config'].setup_streamlit_https
            }
    except Exception as e:
        import_errors.append(f"Strategy 3 failed: {e}")
    
    # If all strategies fail, show detailed error information
    st.error("❌ **Import Error**: Unable to load required modules")
    st.error("**Debugging Information:**")
    
    with st.expander("🔍 Import Error Details", expanded=True):
        st.write("**Python Path:**")
        for i, path in enumerate(sys.path[:10]):
            st.write(f"{i+1}. {path}")
        
        st.write("**Current Directory:**", os.getcwd())
        st.write("**File Location:**", os.path.dirname(os.path.abspath(__file__)))
        
        st.write("**Import Attempts:**")
        for error in import_errors:
            st.write(f"• {error}")
        
        st.write("**Available Files:**")
        for root, dirs, files in os.walk('.'):
            if 'src' in root and any(f.endswith('.py') for f in files):
                st.write(f"📁 {root}: {[f for f in files if f.endswith('.py')]}")
    
    st.info("💡 **Suggested Solutions:**")
    st.write("1. Try using `standalone_app.py` as the main file")
    st.write("2. Check that all source files are properly uploaded to the repository")
    st.write("3. Verify the directory structure matches the expected layout")
    
    st.stop()

# Perform safe import
imported_modules = safe_import()

# Extract imported modules
SummaryParams = imported_modules['SummaryParams']
ProcessingState = imported_modules['ProcessingState']
DocumentHandler = imported_modules['DocumentHandler']
TextExtractor = imported_modules['TextExtractor']
LegalSummarizer = imported_modules['LegalSummarizer']
OutputHandler = imported_modules['OutputHandler']
get_security_service = imported_modules['get_security_service']
ErrorHandler = imported_modules['ErrorHandler']
Config = imported_modules['Config']
get_secure_logger = imported_modules['get_secure_logger']
setup_streamlit_https = imported_modules['setup_streamlit_https']


class LegalDocumentSummarizerApp:
    """Main Streamlit application class for the Legal Document Summarizer."""
    
    def __init__(self):
        """Initialize the application with required services."""
        self.document_handler = DocumentHandler()
        self.text_extractor = TextExtractor()
        self.summarizer = LegalSummarizer()
        self.output_handler = OutputHandler()
        self.error_handler = ErrorHandler()
        self.security_service = get_security_service()
        self.logger = get_secure_logger()
        
        # Initialize session state
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """Initialize Streamlit session state variables."""
        if 'processing_state' not in st.session_state:
            st.session_state.processing_state = ProcessingState.IDLE
        if 'summary_result' not in st.session_state:
            st.session_state.summary_result = None
        if 'uploaded_file_info' not in st.session_state:
            st.session_state.uploaded_file_info = None
        if 'error_message' not in st.session_state:
            st.session_state.error_message = None
        if 'model_loaded' not in st.session_state:
            st.session_state.model_loaded = False
        if 'session_id' not in st.session_state:
            st.session_state.session_id = self.security_service.generate_session_id()
        if 'processing_session_id' not in st.session_state:
            st.session_state.processing_session_id = None
    
    def render_upload_interface(self):
        """Render the file upload interface."""
        st.subheader("📄 Upload Legal Document")
        
        # File upload widget
        uploaded_file = st.file_uploader(
            "Choose a legal document",
            type=['pdf', 'docx', 'txt'],
            help=f"Supported formats: PDF, DOCX, TXT. Maximum size: {Config.MAX_FILE_SIZE // (1024*1024)}MB"
        )
        
        # Display file information if uploaded
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
            # Summary length selection
            length_options = {
                "brief": "Brief (100-200 words)",
                "standard": "Standard (200-400 words)", 
                "detailed": "Detailed (400-600 words)"
            }
            
            selected_length = st.selectbox(
                "Summary Length",
                options=list(length_options.keys()),
                format_func=lambda x: length_options[x],
                index=1,  # Default to "standard"
                help="Choose how detailed you want the summary to be"
            )
        
        with col2:
            # Summary focus selection
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
                index=0,  # Default to "general"
                help="Choose what aspect of the document to emphasize"
            )
        
        # Advanced options in expander
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
                # Show progress bar for active processing
                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.01)  # Simulate progress
                    progress_bar.progress(i + 1)
                progress_bar.empty()
        else:
            st.info(f"{icon} {message}")
    
    def render_summary_output(self, summary_result):
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
        summary_container = st.container()
        with summary_container:
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
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("📋 Copy to Clipboard", use_container_width=True):
                # Format text for clipboard
                clipboard_text = self.output_handler.format_summary_for_clipboard(summary_result)
                st.success("Summary formatted for clipboard!")
                
                # Display formatted text in an expandable code block
                with st.expander("📋 Formatted Text (Select All & Copy)", expanded=True):
                    st.code(clipboard_text, language=None)
        
        with col2:
            if st.button("📄 Download PDF", use_container_width=True):
                self.handle_pdf_download(summary_result)
        
        # Additional export options
        self.render_additional_export_options(summary_result)
        
        # Document information
        with st.expander("📄 Document Information", expanded=False):
            st.write(f"**Original File:** {summary_result.original_filename}")
            st.write(f"**Generated:** {summary_result.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
            st.write(f"**Processing Time:** {summary_result.processing_time:.2f} seconds")
            st.write(f"**Confidence Score:** {summary_result.confidence_score:.2f}")
    
    def handle_pdf_download(self, summary_result):
        """Handle PDF download request with proper formatting."""
        try:
            # Generate PDF using OutputHandler
            pdf_buffer = self.output_handler.generate_pdf_export(summary_result)
            pdf_filename = self.output_handler.generate_filename(summary_result, "pdf")
            
            # Provide PDF download
            st.download_button(
                label="📄 Download PDF",
                data=pdf_buffer.getvalue(),
                file_name=pdf_filename,
                mime="application/pdf",
                help="Download a professionally formatted PDF of the summary"
            )
            
            st.success("PDF generated successfully!")
            
        except Exception as e:
            error_msg = self.error_handler.handle_system_error(e)
            st.error(f"PDF generation failed: {error_msg.message}")
    
    def render_additional_export_options(self, summary_result):
        """Render additional export options for summaries."""
        with st.expander("📤 Additional Export Options", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                # Text export
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
                # JSON export
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
    
    def display_error_message(self, error_message):
        """Display error message with appropriate styling and actions."""
        if error_message is None:
            return
        
        # Choose alert type based on severity
        severity_styles = {
            "low": st.info,
            "medium": st.warning,
            "high": st.error,
            "critical": st.error
        }
        
        alert_func = severity_styles.get(error_message.severity.value, st.error)
        
        # Display main error message
        alert_func(f"**{error_message.title}**\n\n{error_message.message}")
        
        # Display suggested actions
        if error_message.suggested_actions:
            with st.expander("💡 Suggested Actions", expanded=True):
                for action in error_message.suggested_actions:
                    st.write(f"• {action}")
        
        # Action buttons
        col1, col2 = st.columns(2)
        
        if error_message.show_retry:
            with col1:
                if st.button("🔄 Try Again", use_container_width=True):
                    st.session_state.error_message = None
                    st.session_state.processing_state = ProcessingState.IDLE
                    st.rerun()
        
        if error_message.show_contact_support:
            with col2:
                st.button("📞 Contact Support", use_container_width=True, disabled=True)
    
    def load_model_if_needed(self):
        """Load the AI model if not already loaded."""
        if not st.session_state.model_loaded:
            try:
                with st.spinner("🤖 Loading AI model... This may take a moment."):
                    self.summarizer.load_model()
                    st.session_state.model_loaded = True
                    st.success("AI model loaded successfully!")
            except Exception as e:
                error_msg = self.error_handler.handle_model_error(e)
                st.session_state.error_message = error_msg
                return False
        return True
    
    def process_document(self, uploaded_file, summary_params: SummaryParams):
        """Process the uploaded document and generate summary."""
        processing_session_id = None
        
        try:
            # Start secure document processing logging
            processing_session_id = self.logger.log_document_processing_start(
                uploaded_file.name, 
                uploaded_file.size
            )
            st.session_state.processing_session_id = processing_session_id
            
            # Update processing state
            st.session_state.processing_state = ProcessingState.UPLOADING
            
            # Validate file
            file_data = io.BytesIO(uploaded_file.read())
            validation_result = self.document_handler.validate_file(file_data, uploaded_file.name)
            
            if not validation_result.is_valid:
                self.logger.log_security_event("file_validation_failed", {
                    "session_id": processing_session_id,
                    "filename": uploaded_file.name,
                    "error": validation_result.error_message
                })
                error_msg = self.error_handler.handle_validation_error(
                    Exception(validation_result.error_message)
                )
                st.session_state.error_message = error_msg
                st.session_state.processing_state = ProcessingState.ERROR
                return
            
            # Store file info in secure session storage
            self.security_service.store_session_data(
                st.session_state.session_id,
                "uploaded_file_info",
                validation_result.file_info,
                ttl_minutes=30
            )
            st.session_state.uploaded_file_info = validation_result.file_info
            
            # Extract text
            st.session_state.processing_state = ProcessingState.EXTRACTING
            
            # Save temporary file for text extraction (using secure temp file)
            temp_file_path = self.document_handler.save_temp_file(file_data, uploaded_file.name)
            if not temp_file_path:
                raise Exception("Failed to save temporary file")
            
            # Extract text based on file type
            file_extension = validation_result.file_info.file_type.lower()
            
            if file_extension == '.pdf':
                extracted_text = self.text_extractor.extract_from_pdf(temp_file_path)
            elif file_extension == '.docx':
                extracted_text = self.text_extractor.extract_from_docx(temp_file_path)
            elif file_extension == '.txt':
                with open(temp_file_path, 'r', encoding='utf-8') as f:
                    extracted_text = f.read()
            else:
                raise Exception(f"Unsupported file type: {file_extension}")
            
            # Immediately clean up temporary file after text extraction
            self.document_handler.cleanup_temp_files()
            
            if not extracted_text or len(extracted_text.strip()) < 50:
                raise Exception("No readable text found in document")
            
            # Generate summary
            st.session_state.processing_state = ProcessingState.SUMMARIZING
            
            # Process text in memory only - do not store extracted text
            summary_result = self.summarizer.summarize(
                extracted_text,
                summary_params,
                uploaded_file.name
            )
            
            # Clear extracted text from memory immediately
            del extracted_text
            
            # Store result in secure session storage
            self.security_service.store_session_data(
                st.session_state.session_id,
                "summary_result",
                summary_result,
                ttl_minutes=60
            )
            
            # Store result and update state
            st.session_state.summary_result = summary_result
            st.session_state.processing_state = ProcessingState.COMPLETE
            st.session_state.error_message = None
            
            # Log successful completion
            if processing_session_id:
                self.logger.log_document_processing_complete(
                    processing_session_id,
                    summary_result.processing_time,
                    len(summary_result.summary_text)
                )
            
        except Exception as e:
            # Log error with sanitized context
            self.logger.log_error(e, {
                "session_id": processing_session_id,
                "processing_state": st.session_state.processing_state.value,
                "filename": uploaded_file.name if uploaded_file else "unknown"
            })
            
            # Handle different types of errors
            if "extract" in str(e).lower():
                error_msg = self.error_handler.handle_extraction_error(e)
            elif "model" in str(e).lower() or "summariz" in str(e).lower():
                error_msg = self.error_handler.handle_model_error(e)
            else:
                error_msg = self.error_handler.handle_system_error(e)
            
            st.session_state.error_message = error_msg
            st.session_state.processing_state = ProcessingState.ERROR
            
            # Clean up on error
            self.document_handler.cleanup_temp_files()
            
        finally:
            # Force memory cleanup
            import gc
            gc.collect()
    
    def cleanup_session_data(self):
        """Clean up sensitive session data."""
        try:
            # Clear sensitive data from Streamlit session
            self.security_service.clear_streamlit_session()
            
            # Clear data from secure session storage
            if hasattr(st.session_state, 'session_id'):
                self.security_service.clear_session_data(st.session_state.session_id)
            
            # Clean up any remaining temp files
            self.document_handler.cleanup_temp_files()
            
            # Log cleanup
            self.logger.log_cleanup_operation("session_data", 1)
            
        except Exception as e:
            self.logger.log_error(e, {"operation": "cleanup_session_data"})

    def run(self):
        """Main application run method."""
        # Setup HTTPS configuration
        try:
            setup_streamlit_https()
        except Exception as e:
            self.logger.log_error(e, {"operation": "https_setup"})
        
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
        Our advanced AI analyzes your documents and provides concise, accurate summaries 
        tailored to your specific needs.
        """)
        
        # Sidebar with information
        with st.sidebar:
            st.header("ℹ️ About")
            st.markdown("""
            This tool uses advanced AI to summarize legal documents quickly and accurately.
            
            **Supported formats:**
            - PDF documents
            - Word documents (.docx)
            - Text files (.txt)
            
            **Features:**
            - Customizable summary length
            - Focus on specific aspects
            - Copy and download summaries
            - Secure processing (no data stored)
            """)
            
            # Model status
            st.header("🤖 AI Model Status")
            if st.session_state.model_loaded:
                st.success("✅ Model Ready")
            else:
                st.warning("⏳ Model Not Loaded")
        
        # Display error message if any
        if st.session_state.error_message:
            self.display_error_message(st.session_state.error_message)
        
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
                    # Load model if needed
                    if self.load_model_if_needed():
                        self.process_document(uploaded_file, summary_params)
        
        with col2:
            # Processing status
            if st.session_state.processing_state != ProcessingState.IDLE:
                self.display_processing_status(st.session_state.processing_state)
            
            # Summary output
            if st.session_state.summary_result:
                self.render_summary_output(st.session_state.summary_result)
        
        # Session cleanup controls in sidebar
        with st.sidebar:
            st.markdown("---")
            st.header("🔒 Security Controls")
            
            if st.button("🗑️ Clear Session Data", help="Clear all document data from memory"):
                self.cleanup_session_data()
                st.success("Session data cleared successfully!")
                st.rerun()
            
            # Security status
            security_status = self.security_service.get_security_status()
            with st.expander("🛡️ Security Status", expanded=False):
                st.write(f"**Active Sessions:** {security_status['active_sessions']}")
                st.write(f"**Temp Files:** {security_status['temp_files_tracked']}")
                st.write(f"**Cleanup Active:** {'✅' if security_status['cleanup_thread_active'] else '❌'}")
        
        # Footer
        st.markdown("---")
        st.markdown(
            """
            <div style="text-align: center; color: #666; font-size: 0.8em;">
                🔒 Your documents are processed securely in memory and are never stored permanently.<br>
                All temporary files are automatically cleaned up and session data expires automatically.
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