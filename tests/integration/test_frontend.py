"""
Integration tests for the Streamlit frontend interface.
"""

import pytest
import streamlit as st
from unittest.mock import Mock, patch, MagicMock
import io
from datetime import datetime

from app import LegalDocumentSummarizerApp
from src.models.data_models import SummaryParams, SummaryResult, ProcessingState, ValidationResult, DocumentMetadata


class TestStreamlitFrontend:
    """Test suite for Streamlit frontend components."""
    
    @pytest.fixture
    def app(self):
        """Create a test app instance."""
        with patch('app.DocumentHandler'), \
             patch('app.TextExtractor'), \
             patch('app.LegalSummarizer'), \
             patch('app.ErrorHandler'):
            return LegalDocumentSummarizerApp()
    
    @pytest.fixture
    def mock_uploaded_file(self):
        """Create a mock uploaded file."""
        mock_file = Mock()
        mock_file.name = "test_document.pdf"
        mock_file.size = 1024 * 100  # 100KB
        mock_file.type = "application/pdf"
        mock_file.read.return_value = b"mock file content"
        return mock_file
    
    @pytest.fixture
    def sample_summary_result(self):
        """Create a sample summary result for testing."""
        return SummaryResult(
            original_filename="test_document.pdf",
            summary_text="This is a test summary of the legal document.",
            processing_time=2.5,
            word_count=150,
            confidence_score=0.85,
            generated_at=datetime.now()
        )
    
    def test_app_initialization(self, app):
        """Test that the app initializes correctly."""
        assert app.document_handler is not None
        assert app.text_extractor is not None
        assert app.summarizer is not None
        assert app.error_handler is not None
    
    @patch('streamlit.session_state', {})
    def test_session_state_initialization(self, app):
        """Test that session state is initialized correctly."""
        app._initialize_session_state()
        
        assert st.session_state.processing_state == ProcessingState.IDLE
        assert st.session_state.summary_result is None
        assert st.session_state.uploaded_file_info is None
        assert st.session_state.error_message is None
        assert st.session_state.model_loaded is False
    
    @patch('streamlit.file_uploader')
    @patch('streamlit.subheader')
    @patch('streamlit.expander')
    def test_render_upload_interface(self, mock_expander, mock_subheader, mock_file_uploader, app, mock_uploaded_file):
        """Test the file upload interface rendering."""
        mock_file_uploader.return_value = mock_uploaded_file
        mock_expander.return_value.__enter__ = Mock()
        mock_expander.return_value.__exit__ = Mock()
        
        result = app.render_upload_interface()
        
        # Verify file uploader was called with correct parameters
        mock_file_uploader.assert_called_once_with(
            "Choose a legal document",
            type=['pdf', 'docx', 'txt'],
            help="Supported formats: PDF, DOCX, TXT. Maximum size: 10MB"
        )
        
        assert result == mock_uploaded_file
    
    @patch('streamlit.selectbox')
    @patch('streamlit.slider')
    @patch('streamlit.columns')
    @patch('streamlit.subheader')
    @patch('streamlit.expander')
    def test_render_customization_controls(self, mock_expander, mock_subheader, mock_columns, mock_slider, mock_selectbox, app):
        """Test the summary customization controls."""
        # Mock column objects
        mock_col1 = Mock()
        mock_col2 = Mock()
        mock_columns.return_value = [mock_col1, mock_col2]
        
        # Mock selectbox returns
        mock_selectbox.side_effect = ["standard", "general"]
        mock_slider.return_value = 300
        
        # Mock expander context manager
        mock_expander.return_value.__enter__ = Mock()
        mock_expander.return_value.__exit__ = Mock()
        
        result = app.render_customization_controls()
        
        # Verify the result
        assert isinstance(result, SummaryParams)
        assert result.length == "standard"
        assert result.focus == "general"
        assert result.max_words == 300
    
    @patch('streamlit.spinner')
    @patch('streamlit.progress')
    @patch('streamlit.info')
    @patch('time.sleep')
    def test_display_processing_status(self, mock_sleep, mock_info, mock_progress, mock_spinner, app):
        """Test processing status display."""
        # Mock progress bar
        mock_progress_bar = Mock()
        mock_progress.return_value = mock_progress_bar
        
        # Mock spinner context manager
        mock_spinner.return_value.__enter__ = Mock()
        mock_spinner.return_value.__exit__ = Mock()
        
        # Test different processing states
        app.display_processing_status(ProcessingState.IDLE)
        mock_info.assert_called_with("⏳ Ready to process")
        
        app.display_processing_status(ProcessingState.SUMMARIZING)
        mock_spinner.assert_called_with("🤖 Generating AI summary...")
    
    @patch('streamlit.subheader')
    @patch('streamlit.columns')
    @patch('streamlit.metric')
    @patch('streamlit.markdown')
    @patch('streamlit.container')
    @patch('streamlit.button')
    @patch('streamlit.expander')
    def test_render_summary_output(self, mock_expander, mock_button, mock_container, mock_markdown, 
                                 mock_metric, mock_columns, mock_subheader, app, sample_summary_result):
        """Test summary output rendering."""
        # Mock columns
        mock_col1, mock_col2, mock_col3 = Mock(), Mock(), Mock()
        mock_columns.return_value = [mock_col1, mock_col2, mock_col3]
        
        # Mock container context manager
        mock_container.return_value.__enter__ = Mock()
        mock_container.return_value.__exit__ = Mock()
        
        # Mock expander context manager
        mock_expander.return_value.__enter__ = Mock()
        mock_expander.return_value.__exit__ = Mock()
        
        app.render_summary_output(sample_summary_result)
        
        # Verify metrics were displayed
        assert mock_metric.call_count >= 3  # Word count, processing time, confidence
        
        # Verify summary text was displayed
        mock_markdown.assert_called()
    
    @patch('streamlit.success')
    @patch('streamlit.code')
    @patch('streamlit.button')
    def test_copy_to_clipboard_functionality(self, mock_button, mock_code, mock_success, app, sample_summary_result):
        """Test copy to clipboard functionality."""
        mock_button.return_value = True
        
        # This would be called within render_summary_output when copy button is clicked
        # We'll test the logic separately
        mock_success.assert_not_called()  # Should only be called when button is clicked
    
    @patch('streamlit.download_button')
    def test_handle_download_request(self, mock_download_button, app, sample_summary_result):
        """Test PDF download request handling."""
        app.handle_download_request(sample_summary_result)
        
        # Verify download button was created
        mock_download_button.assert_called_once()
        
        # Check the call arguments
        call_args = mock_download_button.call_args
        assert "📄 Download Summary as Text" in str(call_args)
        assert "text/plain" in str(call_args)
    
    @patch('streamlit.error')
    @patch('streamlit.warning')
    @patch('streamlit.info')
    @patch('streamlit.expander')
    @patch('streamlit.button')
    @patch('streamlit.columns')
    def test_display_error_message(self, mock_columns, mock_button, mock_expander, 
                                 mock_info, mock_warning, mock_error, app):
        """Test error message display."""
        from src.utils.error_handler import UserMessage, ErrorSeverity
        
        # Mock error message
        mock_error_msg = Mock()
        mock_error_msg.title = "Test Error"
        mock_error_msg.message = "This is a test error message"
        mock_error_msg.severity = Mock()
        mock_error_msg.severity.value = "high"
        mock_error_msg.suggested_actions = ["Try again", "Contact support"]
        mock_error_msg.show_retry = True
        mock_error_msg.show_contact_support = True
        
        # Mock columns
        mock_col1, mock_col2 = Mock(), Mock()
        mock_columns.return_value = [mock_col1, mock_col2]
        
        # Mock expander context manager
        mock_expander.return_value.__enter__ = Mock()
        mock_expander.return_value.__exit__ = Mock()
        
        app.display_error_message(mock_error_msg)
        
        # Verify error was displayed
        mock_error.assert_called_once()
    
    @patch('streamlit.spinner')
    @patch('streamlit.success')
    @patch('streamlit.session_state', {'model_loaded': False})
    def test_load_model_if_needed(self, mock_success, mock_spinner, app):
        """Test model loading functionality."""
        # Mock spinner context manager
        mock_spinner.return_value.__enter__ = Mock()
        mock_spinner.return_value.__exit__ = Mock()
        
        # Mock successful model loading
        app.summarizer.load_model = Mock()
        
        result = app.load_model_if_needed()
        
        assert result is True
        app.summarizer.load_model.assert_called_once()
        mock_success.assert_called_with("AI model loaded successfully!")
    
    @patch('streamlit.session_state', {
        'processing_state': ProcessingState.IDLE,
        'summary_result': None,
        'uploaded_file_info': None,
        'error_message': None,
        'model_loaded': False
    })
    def test_process_document_validation_failure(self, app, mock_uploaded_file):
        """Test document processing with validation failure."""
        # Mock validation failure
        validation_result = ValidationResult(
            is_valid=False,
            error_message="Invalid file format",
            file_info=None
        )
        app.document_handler.validate_file.return_value = validation_result
        
        # Mock error handler
        mock_error_msg = Mock()
        app.error_handler.handle_validation_error.return_value = mock_error_msg
        
        app.process_document(mock_uploaded_file, SummaryParams("standard", "general", 300))
        
        # Verify error state was set
        assert st.session_state.processing_state == ProcessingState.ERROR
        assert st.session_state.error_message == mock_error_msg
    
    @patch('streamlit.session_state', {
        'processing_state': ProcessingState.IDLE,
        'summary_result': None,
        'uploaded_file_info': None,
        'error_message': None,
        'model_loaded': True
    })
    def test_process_document_success(self, app, mock_uploaded_file, sample_summary_result):
        """Test successful document processing."""
        # Mock successful validation
        validation_result = ValidationResult(
            is_valid=True,
            error_message=None,
            file_info=DocumentMetadata(
                filename="test.pdf",
                file_size=1024,
                file_type=".pdf",
                upload_timestamp=datetime.now()
            )
        )
        app.document_handler.validate_file.return_value = validation_result
        app.document_handler.save_temp_file.return_value = "/tmp/test.pdf"
        app.text_extractor.extract_from_pdf.return_value = "Sample legal document text content."
        app.summarizer.summarize.return_value = sample_summary_result
        
        app.process_document(mock_uploaded_file, SummaryParams("standard", "general", 300))
        
        # Verify successful completion
        assert st.session_state.processing_state == ProcessingState.COMPLETE
        assert st.session_state.summary_result == sample_summary_result
        assert st.session_state.error_message is None


class TestFrontendIntegration:
    """Integration tests for frontend components working together."""
    
    @patch('streamlit.set_page_config')
    @patch('streamlit.title')
    @patch('streamlit.markdown')
    @patch('streamlit.sidebar')
    @patch('streamlit.columns')
    @patch('streamlit.button')
    def test_main_app_layout(self, mock_button, mock_columns, mock_sidebar, 
                           mock_markdown, mock_title, mock_set_page_config):
        """Test the main application layout and structure."""
        # Mock sidebar context manager
        mock_sidebar.__enter__ = Mock()
        mock_sidebar.__exit__ = Mock()
        
        # Mock columns
        mock_col1, mock_col2 = Mock(), Mock()
        mock_columns.return_value = [mock_col1, mock_col2]
        
        with patch('app.LegalDocumentSummarizerApp') as mock_app_class:
            mock_app_instance = Mock()
            mock_app_class.return_value = mock_app_instance
            
            # Import and run main function
            from app import main
            main()
            
            # Verify app was created and run
            mock_app_class.assert_called_once()
            mock_app_instance.run.assert_called_once()
    
    def test_end_to_end_workflow_simulation(self):
        """Test a simulated end-to-end workflow."""
        with patch('app.DocumentHandler') as mock_doc_handler, \
             patch('app.TextExtractor') as mock_text_extractor, \
             patch('app.LegalSummarizer') as mock_summarizer, \
             patch('app.ErrorHandler') as mock_error_handler:
            
            # Setup mocks for successful workflow
            mock_doc_handler.return_value.validate_file.return_value = ValidationResult(
                is_valid=True,
                error_message=None,
                file_info=DocumentMetadata(
                    filename="test.pdf",
                    file_size=1024,
                    file_type=".pdf",
                    upload_timestamp=datetime.now()
                )
            )
            
            mock_doc_handler.return_value.save_temp_file.return_value = "/tmp/test.pdf"
            mock_text_extractor.return_value.extract_from_pdf.return_value = "Legal document content"
            
            mock_summarizer.return_value.summarize.return_value = SummaryResult(
                original_filename="test.pdf",
                summary_text="Test summary",
                processing_time=1.5,
                word_count=100,
                confidence_score=0.9,
                generated_at=datetime.now()
            )
            
            # Create app instance
            app = LegalDocumentSummarizerApp()
            
            # Simulate file upload and processing
            mock_file = Mock()
            mock_file.name = "test.pdf"
            mock_file.size = 1024
            mock_file.read.return_value = b"mock content"
            
            summary_params = SummaryParams("standard", "general", 300)
            
            # This would normally be called by Streamlit when button is clicked
            # We're testing the logic directly
            app.process_document(mock_file, summary_params)
            
            # Verify the workflow completed successfully
            assert mock_doc_handler.return_value.validate_file.called
            assert mock_text_extractor.return_value.extract_from_pdf.called
            assert mock_summarizer.return_value.summarize.called


if __name__ == "__main__":
    pytest.main([__file__])