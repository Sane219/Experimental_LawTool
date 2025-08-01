# Integration Test Suite

Integration tests for component interaction and workflows

## Statistics

- **Test Files**: 10
- **Total Tests**: 118
- **Test Classes**: 13

## Test Files

### test_complete_workflow.py

**Error**: Failed to analyze: unindent does not match any outer indentation level (<unknown>, line 250)

### test_comprehensive_e2e.py

Comprehensive end-to-end integration tests for the legal document summarizer.
Tests complete workflows from document upload to summary export.

**Statistics:**
- Tests: 6
- Classes: 1
- Documented: 6
- Undocumented: 0

**Fixtures:**
- `services` (scope: function): Set up all services for testing....
- `sample_contract` (scope: function): Sample legal contract for testing....

**Test Classes:**

#### TestComprehensiveE2E

Comprehensive end-to-end workflow tests.

**Methods:**
- `test_complete_pdf_workflow`: Test complete PDF processing workflow....
- `test_error_recovery_workflow`: Test error recovery throughout workflow....
- `test_export_workflow`: Test complete export workflow....

**Test Functions:**

##### test_complete_pdf_workflow

Test complete PDF processing workflow.

**Parameters:** self, services, sample_contract
**Decorators:** 

##### test_error_recovery_workflow

Test error recovery throughout workflow.

**Parameters:** self, services
**Decorators:** 

##### test_export_workflow

Test complete export workflow.

**Parameters:** self, services
**Decorators:** 

### test_comprehensive_workflows.py

**Error**: Failed to analyze: unterminated triple-quoted string literal (detected at line 1) (<unknown>, line 1)

### test_end_to_end_workflows.py

**Error**: Failed to analyze: unexpected indent (<unknown>, line 114)

### test_error_handler_integration.py

Integration tests for the ErrorHandler in realistic scenarios.

**Statistics:**
- Tests: 10
- Classes: 1
- Documented: 10
- Undocumented: 0

**Fixtures:**
- `error_handler` (scope: function): ...

**Test Classes:**

#### TestErrorHandlerIntegration

Integration tests for ErrorHandler.

**Methods:**
- `test_document_processing_pipeline_with_errors`: Test error handling in a realistic document processing pipeline....
- `test_retry_mechanism_with_realistic_operation`: Test retry mechanism with a realistic operation that might fail....
- `test_error_statistics_tracking`: Test that error statistics are properly tracked....
- `test_graceful_degradation_scenario`: Test graceful degradation when multiple systems fail....
- `test_logging_integration`: Test that errors are properly logged for monitoring....

**Test Functions:**

##### test_document_processing_pipeline_with_errors

Test error handling in a realistic document processing pipeline.

**Parameters:** self, error_handler
**Decorators:** 

##### test_retry_mechanism_with_realistic_operation

Test retry mechanism with a realistic operation that might fail.

**Parameters:** self, error_handler
**Decorators:** 

##### test_error_statistics_tracking

Test that error statistics are properly tracked.

**Parameters:** self, error_handler
**Decorators:** 

##### test_graceful_degradation_scenario

Test graceful degradation when multiple systems fail.

**Parameters:** self, error_handler
**Decorators:** 

##### test_logging_integration

Test that errors are properly logged for monitoring.

**Parameters:** self, error_handler
**Decorators:** 

### test_frontend.py

Integration tests for the Streamlit frontend interface.

**Statistics:**
- Tests: 28
- Classes: 2
- Documented: 28
- Undocumented: 0

**Fixtures:**
- `app` (scope: function): Create a test app instance....
- `mock_uploaded_file` (scope: function): Create a mock uploaded file....
- `sample_summary_result` (scope: function): Create a sample summary result for testing....

**Test Classes:**

#### TestStreamlitFrontend

Test suite for Streamlit frontend components.

**Methods:**
- `test_app_initialization`: Test that the app initializes correctly....
- `test_session_state_initialization`: Test that session state is initialized correctly....
- `test_render_upload_interface`: Test the file upload interface rendering....
- `test_render_customization_controls`: Test the summary customization controls....
- `test_display_processing_status`: Test processing status display....
- `test_render_summary_output`: Test summary output rendering....
- `test_copy_to_clipboard_functionality`: Test copy to clipboard functionality....
- `test_handle_download_request`: Test PDF download request handling....
- `test_display_error_message`: Test error message display....
- `test_load_model_if_needed`: Test model loading functionality....
- `test_process_document_validation_failure`: Test document processing with validation failure....
- `test_process_document_success`: Test successful document processing....

#### TestFrontendIntegration

Integration tests for frontend components working together.

**Methods:**
- `test_main_app_layout`: Test the main application layout and structure....
- `test_end_to_end_workflow_simulation`: Test a simulated end-to-end workflow....

**Test Functions:**

##### test_app_initialization

Test that the app initializes correctly.

**Parameters:** self, app
**Decorators:** 

##### test_session_state_initialization

Test that session state is initialized correctly.

**Parameters:** self, app
**Decorators:** patch

##### test_render_upload_interface

Test the file upload interface rendering.

**Parameters:** self, mock_expander, mock_subheader, mock_file_uploader, app, mock_uploaded_file
**Decorators:** patch, patch, patch

##### test_render_customization_controls

Test the summary customization controls.

**Parameters:** self, mock_expander, mock_subheader, mock_columns, mock_slider, mock_selectbox, app
**Decorators:** patch, patch, patch, patch, patch

##### test_display_processing_status

Test processing status display.

**Parameters:** self, mock_sleep, mock_info, mock_progress, mock_spinner, app
**Decorators:** patch, patch, patch, patch

##### test_render_summary_output

Test summary output rendering.

**Parameters:** self, mock_expander, mock_button, mock_container, mock_markdown, mock_metric, mock_columns, mock_subheader, app, sample_summary_result
**Decorators:** patch, patch, patch, patch, patch, patch, patch

##### test_copy_to_clipboard_functionality

Test copy to clipboard functionality.

**Parameters:** self, mock_button, mock_code, mock_success, app, sample_summary_result
**Decorators:** patch, patch, patch

##### test_handle_download_request

Test PDF download request handling.

**Parameters:** self, mock_download_button, app, sample_summary_result
**Decorators:** patch

##### test_display_error_message

Test error message display.

**Parameters:** self, mock_columns, mock_button, mock_expander, mock_info, mock_warning, mock_error, app
**Decorators:** patch, patch, patch, patch, patch, patch

##### test_load_model_if_needed

Test model loading functionality.

**Parameters:** self, mock_success, mock_spinner, app
**Decorators:** patch, patch, patch

##### test_process_document_validation_failure

Test document processing with validation failure.

**Parameters:** self, app, mock_uploaded_file
**Decorators:** patch

##### test_process_document_success

Test successful document processing.

**Parameters:** self, app, mock_uploaded_file, sample_summary_result
**Decorators:** patch

##### test_main_app_layout

Test the main application layout and structure.

**Parameters:** self, mock_button, mock_columns, mock_sidebar, mock_markdown, mock_title, mock_set_page_config
**Decorators:** patch, patch, patch, patch, patch, patch

##### test_end_to_end_workflow_simulation

Test a simulated end-to-end workflow.

**Parameters:** self
**Decorators:** 

### test_output_export.py

Integration tests for output and export functionality.
Tests the complete workflow of summary output, copy-to-clipboard formatting,
PDF export generation, and additional export options.

**Statistics:**
- Tests: 20
- Classes: 2
- Documented: 20
- Undocumented: 0

**Fixtures:**
- `output_handler` (scope: function): Create an OutputHandler instance for testing....
- `sample_summary_result` (scope: function): Create a sample SummaryResult for testing....
- `mock_streamlit` (scope: function): Mock Streamlit components for testing....
- `sample_summary_result` (scope: function): Create a sample SummaryResult for testing....

**Test Classes:**

#### TestOutputExportIntegration

Integration tests for output and export functionality.

**Methods:**
- `test_clipboard_formatting_workflow`: Test the complete clipboard formatting workflow....
- `test_pdf_export_generation_workflow`: Test the complete PDF export generation workflow....
- `test_filename_generation_workflow`: Test filename generation for different export types....
- `test_json_export_workflow`: Test JSON export generation workflow....
- `test_multiple_export_formats_workflow`: Test generating multiple export formats from the same summary....
- `test_error_handling_in_export_workflow`: Test error handling during export operations....
- `test_large_summary_export_workflow`: Test export workflow with large summary content....
- `test_special_characters_in_export_workflow`: Test export workflow with special characters and unicode....

#### TestOutputExportStreamlitIntegration

Integration tests for Streamlit app output and export features.

**Methods:**
- `test_streamlit_copy_functionality_integration`: Test integration of copy functionality with Streamlit interface....
- `test_streamlit_pdf_download_integration`: Test integration of PDF download with Streamlit interface....

**Test Functions:**

##### test_clipboard_formatting_workflow

Test the complete clipboard formatting workflow.

**Parameters:** self, output_handler, sample_summary_result
**Decorators:** 

##### test_pdf_export_generation_workflow

Test the complete PDF export generation workflow.

**Parameters:** self, output_handler, sample_summary_result
**Decorators:** 

##### test_filename_generation_workflow

Test filename generation for different export types.

**Parameters:** self, output_handler, sample_summary_result
**Decorators:** 

##### test_json_export_workflow

Test JSON export generation workflow.

**Parameters:** self, output_handler, sample_summary_result
**Decorators:** 

##### test_multiple_export_formats_workflow

Test generating multiple export formats from the same summary.

**Parameters:** self, output_handler, sample_summary_result
**Decorators:** 

##### test_error_handling_in_export_workflow

Test error handling during export operations.

**Parameters:** self, output_handler
**Decorators:** 

##### test_large_summary_export_workflow

Test export workflow with large summary content.

**Parameters:** self, output_handler
**Decorators:** 

##### test_special_characters_in_export_workflow

Test export workflow with special characters and unicode.

**Parameters:** self, output_handler
**Decorators:** 

##### test_streamlit_copy_functionality_integration

Test integration of copy functionality with Streamlit interface.

**Parameters:** self, mock_streamlit, sample_summary_result
**Decorators:** 

##### test_streamlit_pdf_download_integration

Test integration of PDF download with Streamlit interface.

**Parameters:** self, mock_streamlit, sample_summary_result
**Decorators:** 

### test_performance.py

**Error**: Failed to analyze: unterminated triple-quoted string literal (detected at line 1) (<unknown>, line 1)

### test_streamlit_app.py

Simplified integration tests for the Streamlit frontend interface.
These tests focus on testing the core functionality without complex Streamlit mocking.

**Statistics:**
- Tests: 26
- Classes: 4
- Documented: 26
- Undocumented: 0

**Fixtures:**
- `mock_services` (scope: function): Create mock services for testing....

**Test Classes:**

#### TestStreamlitAppCore

Test core functionality of the Streamlit app without complex UI mocking.

**Methods:**
- `test_summary_params_creation`: Test that SummaryParams can be created correctly....
- `test_summary_result_creation`: Test that SummaryResult can be created correctly....
- `test_processing_state_enum`: Test ProcessingState enum values....
- `test_validation_result_creation`: Test ValidationResult creation....

#### TestAppLogic

Test the core application logic without Streamlit dependencies.

**Methods:**
- `test_file_upload_validation_logic`: Test file upload validation logic....
- `test_text_extraction_logic`: Test text extraction logic....
- `test_summarization_logic`: Test summarization logic....
- `test_error_handling_logic`: Test error handling logic....

#### TestAppIntegration

Integration tests for app components working together.

**Methods:**
- `test_complete_workflow_simulation`: Test a complete workflow simulation with mocked components....
- `test_error_workflow_simulation`: Test error handling workflow....

#### TestUIComponents

Test UI component logic without Streamlit rendering.

**Methods:**
- `test_summary_customization_options`: Test summary customization options....
- `test_file_format_support`: Test supported file formats....
- `test_processing_status_messages`: Test processing status messages....

**Test Functions:**

##### test_summary_params_creation

Test that SummaryParams can be created correctly.

**Parameters:** self
**Decorators:** 

##### test_summary_result_creation

Test that SummaryResult can be created correctly.

**Parameters:** self
**Decorators:** 

##### test_processing_state_enum

Test ProcessingState enum values.

**Parameters:** self
**Decorators:** 

##### test_validation_result_creation

Test ValidationResult creation.

**Parameters:** self
**Decorators:** 

##### test_file_upload_validation_logic

Test file upload validation logic.

**Parameters:** self, mock_services
**Decorators:** 

##### test_text_extraction_logic

Test text extraction logic.

**Parameters:** self, mock_services
**Decorators:** 

##### test_summarization_logic

Test summarization logic.

**Parameters:** self, mock_services
**Decorators:** 

##### test_error_handling_logic

Test error handling logic.

**Parameters:** self, mock_services
**Decorators:** 

##### test_complete_workflow_simulation

Test a complete workflow simulation with mocked components.

**Parameters:** self
**Decorators:** 

##### test_error_workflow_simulation

Test error handling workflow.

**Parameters:** self
**Decorators:** 

##### test_summary_customization_options

Test summary customization options.

**Parameters:** self
**Decorators:** 

##### test_file_format_support

Test supported file formats.

**Parameters:** self
**Decorators:** 

##### test_processing_status_messages

Test processing status messages.

**Parameters:** self
**Decorators:** 

### test_streamlit_frontend.py

Integration tests for the Streamlit frontend interface.

**Statistics:**
- Tests: 28
- Classes: 3
- Documented: 28
- Undocumented: 0

**Fixtures:**
- `app` (scope: function): Create app instance for testing....
- `mock_uploaded_file` (scope: function): Create mock uploaded file for testing....
- `sample_summary_result` (scope: function): Create sample summary result for testing....
- `app_with_real_components` (scope: function): Create app with real components for integration testing....

**Test Classes:**

#### MockSessionState

Mock class for Streamlit session state.

**Methods:**

#### TestStreamlitFrontend

Test suite for Streamlit frontend components.

**Methods:**
- `test_initialize_session_state`: Test session state initialization....
- `test_render_upload_interface`: Test file upload interface rendering....
- `test_render_customization_controls`: Test summary customization controls rendering....
- `test_display_processing_status`: Test processing status display....
- `test_render_summary_output`: Test summary output rendering....
- `test_handle_download_request`: Test download request handling....
- `test_display_error_message`: Test error message display....
- `test_load_model_if_needed_success`: Test successful model loading....
- `test_load_model_if_needed_failure`: Test model loading failure....
- `test_process_document_success`: Test successful document processing....
- `test_process_document_validation_failure`: Test document processing with validation failure....
- `test_process_document_extraction_failure`: Test document processing with text extraction failure....
- `test_run_method`: Test main run method....

#### TestStreamlitIntegration

Integration tests for complete Streamlit workflows.

**Methods:**
- `test_complete_workflow_integration`: Test complete document processing workflow....

**Test Functions:**

##### test_initialize_session_state

Test session state initialization.

**Parameters:** self, app
**Decorators:** 

##### test_render_upload_interface

Test file upload interface rendering.

**Parameters:** self, mock_subheader, mock_file_uploader, app, mock_uploaded_file
**Decorators:** patch, patch

##### test_render_customization_controls

Test summary customization controls rendering.

**Parameters:** self, mock_subheader, mock_columns, mock_slider, mock_selectbox, mock_expander, app
**Decorators:** patch, patch, patch, patch, patch

##### test_display_processing_status

Test processing status display.

**Parameters:** self, mock_info, mock_progress, mock_spinner, app
**Decorators:** patch, patch, patch

##### test_render_summary_output

Test summary output rendering.

**Parameters:** self, mock_button, mock_markdown, mock_metric, mock_columns, mock_subheader, mock_container, mock_expander, app, sample_summary_result
**Decorators:** patch, patch, patch, patch, patch, patch, patch

##### test_handle_download_request

Test download request handling.

**Parameters:** self, mock_button, mock_code, mock_success, app, sample_summary_result
**Decorators:** patch, patch, patch

##### test_display_error_message

Test error message display.

**Parameters:** self, mock_expander, mock_error, mock_warning, mock_info, app
**Decorators:** patch, patch, patch, patch

##### test_load_model_if_needed_success

Test successful model loading.

**Parameters:** self, app
**Decorators:** 

##### test_load_model_if_needed_failure

Test model loading failure.

**Parameters:** self, app
**Decorators:** 

##### test_process_document_success

Test successful document processing.

**Parameters:** self, app, mock_uploaded_file
**Decorators:** 

##### test_process_document_validation_failure

Test document processing with validation failure.

**Parameters:** self, app, mock_uploaded_file
**Decorators:** 

##### test_process_document_extraction_failure

Test document processing with text extraction failure.

**Parameters:** self, app, mock_uploaded_file
**Decorators:** 

##### test_run_method

Test main run method.

**Parameters:** self, mock_columns, mock_sidebar, mock_markdown, mock_title, mock_set_page_config, mock_button, mock_warning, mock_success, mock_header, app
**Decorators:** patch, patch, patch, patch, patch, patch, patch, patch, patch

##### test_complete_workflow_integration

Test complete document processing workflow.

**Parameters:** self, app_with_real_components
**Decorators:** 

