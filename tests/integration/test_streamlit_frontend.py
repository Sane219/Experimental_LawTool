"""
Integration tests for the Streamlit frontend interface.
"""

import pytest
import streamlit as st
from unittest.mock import Mock, patch, MagicMock, PropertyMock
import io
from datetime import datetime

from src.models.data_models import SummaryParams, SummaryResult, ValidationResult, DocumentMetadata, ProcessingState
from src.utils.error_handler import UserMessage, ErrorSeverity
from app import LegalDocumentSummarizerApp


class MockSessionState:
    """Mock class for Streamlit session state."""
    
    def __init__(self, initial_state=None):
        self._state = initial_state or {}
    
    def __getattr__(self, name):
        return self._state.get(name)
    
    def __setattr__(self, name, value):
        if name.startswith('_'):
            super().__setattr__(name, value)
        else:
            self._state[name] = value
    
    def __contains__(self, name):
        return name in self._state
    
    def get(self, name, default=None):
        return self._state.get(name, default)
    
    def __contains__(self, name):
        return name in self._state


class TestStreamlitFrontend:
    """Test suite for Streamlit frontend components."""
    
    @pytest.fixture
    def app(self):
        """Create app instance for testing."""
        with patch('app.DocumentHandler'), \
             patch('app.TextExtractor'), \
             patch('app.LegalSummarizer'), \
             patch('app.ErrorHandler'):
            return LegalDocumentSummarizerApp()
    
    @pytest.fixture
    def mock_uploaded_file(self):
        """Create mock uploaded file for testing."""
        mock_file = Mock()
        mock_file.name = "test_document.pdf"
        mock_file.size = 1024 * 100  # 100KB
        mock_file.type = "application/pdf"
        mock_file.read.return_value = b"mock file content"
        return mock_file
    
    @pytest.fixture
    def sample_summary_result(self):
        """Create sample summary result for testing."""
        return SummaryResult(
            original_filename="test_document.pdf",
            summary_text="This is a test summary of the legal document.",
            processing_time=2.5,
            word_count=10,
            confidence_score=0.85,
            generated_at=datetime.now()
        )
    
    def test_initialize_session_state(self, app):
        """Test session state initialization."""
        mock_session = MockSessionState({})
        with patch('streamlit.session_state', mock_session):
            app._initialize_session_state()
            
            # Check that all required session state variables are initialized
            assert 'processing_state' in mock_session
            assert 'summary_result' in mock_session
            assert 'uploaded_file_info' in mock_session
            assert 'error_message' in mock_session
            assert 'model_loaded' in mock_session
            
            # Check default values
            assert mock_session.processing_state == ProcessingState.IDLE
            assert mock_session.summary_result is None
            assert mock_session.uploaded_file_info is None
            assert mock_session.error_message is None
            assert mock_session.model_loaded is False
    
    @patch('streamlit.file_uploader')
    @patch('streamlit.subheader')
    def test_render_upload_interface(self, mock_subheader, mock_file_uploader, app, mock_uploaded_file):
        """Test file upload interface rendering."""
        mock_file_uploader.return_value = mock_uploaded_file
        
        result = app.render_upload_interface()
        
        # Check that file uploader is called with correct parameters
        mock_file_uploader.assert_called_once()
        call_args = mock_file_uploader.call_args
        assert 'type' in call_args.kwargs
        assert call_args.kwargs['type'] == ['pdf', 'docx', 'txt']
        
        # Check that result is the uploaded file
        assert result == mock_uploaded_file
    
    @patch('streamlit.expander')
    @patch('streamlit.selectbox')
    @patch('streamlit.slider')
    @patch('streamlit.columns')
    @patch('streamlit.subheader')
    def test_render_customization_controls(self, mock_subheader, mock_columns, mock_slider, mock_selectbox, mock_expander, app):
        """Test summary customization controls rendering."""
        # Mock column objects with context manager support
        mock_col1 = Mock()
        mock_col1.__enter__ = Mock(return_value=mock_col1)
        mock_col1.__exit__ = Mock(return_value=None)
        
        mock_col2 = Mock()
        mock_col2.__enter__ = Mock(return_value=mock_col2)
        mock_col2.__exit__ = Mock(return_value=None)
        
        mock_columns.return_value = [mock_col1, mock_col2]
        
        # Mock expander context manager
        mock_exp = Mock()
        mock_exp.__enter__ = Mock(return_value=mock_exp)
        mock_exp.__exit__ = Mock(return_value=None)
        mock_expander.return_value = mock_exp
        
        # Mock selectbox returns
        mock_selectbox.side_effect = ["standard", "general"]
        mock_slider.return_value = 300
        
        result = app.render_customization_controls()
        
        # Check that result is SummaryParams object
        assert isinstance(result, SummaryParams)
        assert result.length == "standard"
        assert result.focus == "general"
        assert result.max_words == 300
        assert result.length == "standard"
        assert result.focus == "general"
        assert result.max_words == 300
        
        # Check that selectbox was called twice (length and focus)
        assert mock_selectbox.call_count == 2
        mock_slider.assert_called_once()
    
    @patch('streamlit.spinner')
    @patch('streamlit.progress')
    @patch('streamlit.info')
    def test_display_processing_status(self, mock_info, mock_progress, mock_spinner, app):
        """Test processing status display."""
        # Test idle state
        app.display_processing_status(ProcessingState.IDLE)
        mock_info.assert_called_with("⏳ Ready to process")
        
        # Test processing state with spinner
        mock_progress_bar = Mock()
        mock_progress.return_value = mock_progress_bar
        
        app.display_processing_status(ProcessingState.SUMMARIZING)
        mock_spinner.assert_called()
    
    @patch('streamlit.expander')
    @patch('streamlit.container')
    @patch('streamlit.subheader')
    @patch('streamlit.columns')
    @patch('streamlit.metric')
    @patch('streamlit.markdown')
    @patch('streamlit.button')
    def test_render_summary_output(self, mock_button, mock_markdown, mock_metric, mock_columns, mock_subheader, mock_container, mock_expander, app, sample_summary_result):
        """Test summary output rendering."""
        # Mock columns with context manager support
        mock_col1 = Mock()
        mock_col1.__enter__ = Mock(return_value=mock_col1)
        mock_col1.__exit__ = Mock(return_value=None)
        
        mock_col2 = Mock()
        mock_col2.__enter__ = Mock(return_value=mock_col2)
        mock_col2.__exit__ = Mock(return_value=None)
        
        mock_col3 = Mock()
        mock_col3.__enter__ = Mock(return_value=mock_col3)
        mock_col3.__exit__ = Mock(return_value=None)
        
        mock_columns.return_value = [mock_col1, mock_col2, mock_col3]
        
        # Mock container context manager
        mock_cont = Mock()
        mock_cont.__enter__ = Mock(return_value=mock_cont)
        mock_cont.__exit__ = Mock(return_value=None)
        mock_container.return_value = mock_cont
        
        # Mock expander context manager
        mock_exp = Mock()
        mock_exp.__enter__ = Mock(return_value=mock_exp)
        mock_exp.__exit__ = Mock(return_value=None)
        mock_expander.return_value = mock_exp
        
        mock_button.return_value = False
        
        app.render_summary_output(sample_summary_result)
        
        # Check that metrics are displayed
        assert mock_metric.call_count == 3  # Word count, processing time, confidence
        
        # Check that summary text is displayed
        mock_markdown.assert_called()
        
        # Check that buttons are rendered
        assert mock_button.call_count >= 2  # Copy and Download buttons
        assert mock_button.call_count >= 2  # Copy and download buttons
    
    @patch('streamlit.success')
    @patch('streamlit.code')
    @patch('streamlit.button')
    def test_handle_download_request(self, mock_button, mock_code, mock_success, app, sample_summary_result):
        """Test download request handling."""
        with patch('streamlit.download_button') as mock_download:
            app.handle_download_request(sample_summary_result)
            
            # Check that download button is created
            mock_download.assert_called_once()
            call_args = mock_download.call_args
            assert 'data' in call_args.kwargs
            assert 'file_name' in call_args.kwargs
            assert 'mime' in call_args.kwargs
    
    @patch('streamlit.info')
    @patch('streamlit.warning')
    @patch('streamlit.error')
    @patch('streamlit.expander')
    def test_display_error_message(self, mock_expander, mock_error, mock_warning, mock_info, app):
        """Test error message display."""
        # Create test error message
        error_msg = UserMessage(
            title="Test Error",
            message="This is a test error message",
            suggested_actions=["Action 1", "Action 2"],
            severity=ErrorSeverity.MEDIUM,
            show_retry=True,
            show_contact_support=False
        )
        
        # Mock expander
        mock_expander_obj = Mock()
        mock_expander.return_value.__enter__ = Mock(return_value=mock_expander_obj)
        mock_expander.return_value.__exit__ = Mock(return_value=None)
        
        app.display_error_message(error_msg)
        
        # Check that appropriate alert function is called based on severity
        mock_warning.assert_called_once()
        
        # Check that expander is created for suggested actions
        mock_expander.assert_called_with("💡 Suggested Actions", expanded=True)
    
    def test_load_model_if_needed_success(self, app):
        """Test successful model loading."""
        mock_session = MockSessionState({'model_loaded': False})
        with patch('streamlit.session_state', mock_session), \
             patch('streamlit.spinner'), \
             patch('streamlit.success') as mock_success:
            
            app.summarizer.load_model = Mock()
            
            result = app.load_model_if_needed()
            
            assert result is True
            app.summarizer.load_model.assert_called_once()
            assert mock_session.model_loaded is True
            mock_success.assert_called_with("AI model loaded successfully!")
    
    def test_load_model_if_needed_failure(self, app):
        """Test model loading failure."""
        mock_session = MockSessionState({'model_loaded': False, 'error_message': None})
        with patch('streamlit.session_state', mock_session), \
             patch('streamlit.spinner'):
            
            app.summarizer.load_model = Mock(side_effect=Exception("Model loading failed"))
            app.error_handler.handle_model_error = Mock(return_value=Mock())
            
            result = app.load_model_if_needed()
            
            assert result is False
            assert mock_session.error_message is not None
    
    def test_process_document_success(self, app, mock_uploaded_file):
        """Test successful document processing."""
        mock_session = MockSessionState({
            'processing_state': ProcessingState.IDLE,
            'summary_result': None,
            'uploaded_file_info': None,
            'error_message': None
        })
        with patch('streamlit.session_state', mock_session):
            
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
            app.document_handler.validate_file = Mock(return_value=validation_result)
            app.document_handler.save_temp_file = Mock(return_value="/tmp/test.pdf")
            app.document_handler.cleanup_temp_files = Mock()
            
            # Mock text extraction with sufficient content
            app.text_extractor.extract_from_pdf = Mock(return_value="This is a long extracted text content from the legal document that contains sufficient information for processing and summarization. It has more than 50 characters to pass the validation check.")
            
            # Mock summarization
            summary_result = SummaryResult(
                original_filename="test.pdf",
                summary_text="Test summary",
                processing_time=1.0,
                word_count=5,
                confidence_score=0.9,
                generated_at=datetime.now()
            )
            app.summarizer.summarize = Mock(return_value=summary_result)
            
            # Create summary params
            summary_params = SummaryParams(length="standard", focus="general", max_words=300)
            
            app.process_document(mock_uploaded_file, summary_params)
            
            # Check that processing completed successfully
            assert mock_session.processing_state == ProcessingState.COMPLETE
            assert mock_session.summary_result == summary_result
            assert mock_session.error_message is None
    
    def test_process_document_validation_failure(self, app, mock_uploaded_file):
        """Test document processing with validation failure."""
        mock_session = MockSessionState({
            'processing_state': ProcessingState.IDLE,
            'error_message': None
        })
        with patch('streamlit.session_state', mock_session):
            
            # Mock validation failure
            validation_result = ValidationResult(
                is_valid=False,
                error_message="File too large",
                file_info=None
            )
            app.document_handler.validate_file = Mock(return_value=validation_result)
            app.error_handler.handle_validation_error = Mock(return_value=Mock())
            
            summary_params = SummaryParams(length="standard", focus="general", max_words=300)
            
            app.process_document(mock_uploaded_file, summary_params)
            
            # Check that error state is set
            assert mock_session.processing_state == ProcessingState.ERROR
            assert mock_session.error_message is not None
    
    def test_process_document_extraction_failure(self, app, mock_uploaded_file):
        """Test document processing with text extraction failure."""
        mock_session = MockSessionState({
            'processing_state': ProcessingState.IDLE,
            'error_message': None
        })
        with patch('streamlit.session_state', mock_session):
            
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
            app.document_handler.validate_file = Mock(return_value=validation_result)
            app.document_handler.save_temp_file = Mock(return_value="/tmp/test.pdf")
            app.document_handler.cleanup_temp_files = Mock()
            
            # Mock extraction failure
            app.text_extractor.extract_from_pdf = Mock(side_effect=Exception("Extraction failed"))
            app.error_handler.handle_extraction_error = Mock(return_value=Mock())
            
            summary_params = SummaryParams(length="standard", focus="general", max_words=300)
            
            app.process_document(mock_uploaded_file, summary_params)
            
            # Check that error state is set and cleanup is called
            assert mock_session.processing_state == ProcessingState.ERROR
            assert mock_session.error_message is not None
            app.document_handler.cleanup_temp_files.assert_called()
    
    @patch('streamlit.header')
    @patch('streamlit.success')
    @patch('streamlit.warning')
    @patch('streamlit.button')
    @patch('streamlit.set_page_config')
    @patch('streamlit.title')
    @patch('streamlit.markdown')
    @patch('streamlit.sidebar')
    @patch('streamlit.columns')
    def test_run_method(self, mock_columns, mock_sidebar, mock_markdown, mock_title, mock_set_page_config, mock_button, mock_warning, mock_success, mock_header, app):
        """Test main run method."""
        mock_session = MockSessionState({
            'processing_state': ProcessingState.IDLE,
            'summary_result': None,
            'uploaded_file_info': None,
            'error_message': None,
            'model_loaded': False
        })
        
        with patch('streamlit.session_state', mock_session):
            
            # Mock columns with context manager support
            mock_col1 = Mock()
            mock_col1.__enter__ = Mock(return_value=mock_col1)
            mock_col1.__exit__ = Mock(return_value=None)
            
            mock_col2 = Mock()
            mock_col2.__enter__ = Mock(return_value=mock_col2)
            mock_col2.__exit__ = Mock(return_value=None)
            
            mock_columns.return_value = [mock_col1, mock_col2]
            
            # Mock sidebar context manager
            mock_sidebar_ctx = Mock()
            mock_sidebar_ctx.__enter__ = Mock(return_value=mock_sidebar_ctx)
            mock_sidebar_ctx.__exit__ = Mock(return_value=None)
            mock_sidebar.return_value = mock_sidebar_ctx
            
            # Mock other methods
            app.render_upload_interface = Mock(return_value=None)
            app.render_customization_controls = Mock(return_value=SummaryParams("standard", "general", 300))
            app.display_processing_status = Mock()
            app.render_summary_output = Mock()
            app.display_error_message = Mock()
            
            mock_button.return_value = False
            
            app.run()
            
            # Check that page config is set
            mock_set_page_config.assert_called_once()
            
            # Check that title and description are displayed
            mock_title.assert_called_once()
            assert mock_markdown.call_count >= 2  # Description and footer
            mock_title.assert_called_with("⚖️ AI-Powered Legal Document Summarizer")
            mock_markdown.assert_called()


class TestStreamlitIntegration:
    """Integration tests for complete Streamlit workflows."""
    
    @pytest.fixture
    def app_with_real_components(self):
        """Create app with real components for integration testing."""
        return LegalDocumentSummarizerApp()
    
    def test_complete_workflow_integration(self, app_with_real_components):
        """Test complete document processing workflow."""
        app = app_with_real_components
        
        # Mock session state
        mock_session = MockSessionState({
            'processing_state': ProcessingState.IDLE,
            'summary_result': None,
            'uploaded_file_info': None,
            'error_message': None,
            'model_loaded': True
        })
        
        with patch('streamlit.session_state', mock_session):
            
            # Create mock file
            mock_file = Mock()
            mock_file.name = "test.txt"
            mock_file.size = 1000
            mock_file.type = "text/plain"
            mock_file.read.return_value = b"This is a test legal document with sufficient content for processing."
            
            # Mock the components to avoid actual AI processing
            with patch.object(app.document_handler, 'validate_file') as mock_validate, \
                 patch.object(app.document_handler, 'save_temp_file') as mock_save, \
                 patch.object(app.document_handler, 'cleanup_temp_files') as mock_cleanup, \
                 patch.object(app.summarizer, 'summarize') as mock_summarize:
                
                # Setup mocks
                mock_validate.return_value = ValidationResult(
                    is_valid=True,
                    error_message=None,
                    file_info=DocumentMetadata("test.txt", 1000, ".txt", datetime.now())
                )
                mock_save.return_value = "/tmp/test.txt"
                mock_summarize.return_value = SummaryResult(
                    original_filename="test.txt",
                    summary_text="Test summary",
                    processing_time=1.0,
                    word_count=5,
                    confidence_score=0.9,
                    generated_at=datetime.now()
                )
                
                # Mock file reading with sufficient content
                with patch('builtins.open', mock_open(read_data="This is a comprehensive test legal document content that contains sufficient information for processing and summarization. It has more than 50 characters to pass the validation check and should trigger the summarization process.")):
                    summary_params = SummaryParams("standard", "general", 300)
                    app.process_document(mock_file, summary_params)
                
                # Verify the workflow
                mock_validate.assert_called_once()
                mock_save.assert_called_once()
                mock_summarize.assert_called_once()
                mock_cleanup.assert_called_once()


def mock_open(read_data=""):
    """Helper function to create mock open context manager."""
    mock_file = Mock()
    mock_file.read.return_value = read_data
    mock_file.__enter__ = Mock(return_value=mock_file)
    mock_file.__exit__ = Mock(return_value=None)
    return Mock(return_value=mock_file)