# Unit Test Suite

Unit tests for individual components and functions

## Statistics

- **Test Files**: 9
- **Total Tests**: 284
- **Test Classes**: 19

## Test Files

### test_config.py

Unit tests for configuration management.

**Statistics:**
- Tests: 22
- Classes: 1
- Documented: 22
- Undocumented: 0

**Test Classes:**

#### TestConfig

Test Config class.

**Methods:**
- `test_default_values`: Test default configuration values....
- `test_summary_lengths_configuration`: Test summary length configurations....
- `test_summary_focus_options`: Test summary focus options....
- `test_validate_config_valid`: Test config validation with valid settings....
- `test_validate_config_invalid_file_size`: Test config validation with invalid file size....
- `test_validate_config_invalid_chunk_size`: Test config validation with invalid chunk size....
- `test_get_summary_word_limits_valid`: Test getting word limits for valid length....
- `test_get_summary_word_limits_invalid`: Test getting word limits for invalid length returns default....
- `test_is_supported_format_valid`: Test supported format validation....
- `test_is_supported_format_invalid`: Test unsupported format validation....
- `test_environment_variable_override`: Test that environment variables override defaults....

**Test Functions:**

##### test_default_values

Test default configuration values.

**Parameters:** self
**Decorators:** 

##### test_summary_lengths_configuration

Test summary length configurations.

**Parameters:** self
**Decorators:** 

##### test_summary_focus_options

Test summary focus options.

**Parameters:** self
**Decorators:** 

##### test_validate_config_valid

Test config validation with valid settings.

**Parameters:** self
**Decorators:** 

##### test_validate_config_invalid_file_size

Test config validation with invalid file size.

**Parameters:** self
**Decorators:** object

##### test_validate_config_invalid_chunk_size

Test config validation with invalid chunk size.

**Parameters:** self
**Decorators:** object

##### test_get_summary_word_limits_valid

Test getting word limits for valid length.

**Parameters:** self
**Decorators:** 

##### test_get_summary_word_limits_invalid

Test getting word limits for invalid length returns default.

**Parameters:** self
**Decorators:** 

##### test_is_supported_format_valid

Test supported format validation.

**Parameters:** self
**Decorators:** 

##### test_is_supported_format_invalid

Test unsupported format validation.

**Parameters:** self
**Decorators:** 

##### test_environment_variable_override

Test that environment variables override defaults.

**Parameters:** self
**Decorators:** dict

### test_data_models.py

Unit tests for data models.

**Statistics:**
- Tests: 14
- Classes: 5
- Documented: 14
- Undocumented: 0

**Test Classes:**

#### TestDocumentMetadata

Test DocumentMetadata data class.

**Methods:**
- `test_document_metadata_creation`: Test creating DocumentMetadata instance....

#### TestSummaryParams

Test SummaryParams data class.

**Methods:**
- `test_summary_params_creation`: Test creating SummaryParams instance....
- `test_summary_params_default_max_words`: Test default max_words value....

#### TestSummaryResult

Test SummaryResult data class.

**Methods:**
- `test_summary_result_creation`: Test creating SummaryResult instance....

#### TestValidationResult

Test ValidationResult data class.

**Methods:**
- `test_validation_result_valid`: Test creating valid ValidationResult....
- `test_validation_result_invalid`: Test creating invalid ValidationResult....

#### TestProcessingState

Test ProcessingState enum.

**Methods:**
- `test_processing_state_values`: Test ProcessingState enum values....

**Test Functions:**

##### test_document_metadata_creation

Test creating DocumentMetadata instance.

**Parameters:** self
**Decorators:** 

##### test_summary_params_creation

Test creating SummaryParams instance.

**Parameters:** self
**Decorators:** 

##### test_summary_params_default_max_words

Test default max_words value.

**Parameters:** self
**Decorators:** 

##### test_summary_result_creation

Test creating SummaryResult instance.

**Parameters:** self
**Decorators:** 

##### test_validation_result_valid

Test creating valid ValidationResult.

**Parameters:** self
**Decorators:** 

##### test_validation_result_invalid

Test creating invalid ValidationResult.

**Parameters:** self
**Decorators:** 

##### test_processing_state_values

Test ProcessingState enum values.

**Parameters:** self
**Decorators:** 

### test_document_handler.py

Unit tests for document handler service.

**Statistics:**
- Tests: 32
- Classes: 1
- Documented: 32
- Undocumented: 0

**Test Classes:**

#### TestDocumentHandler

Test DocumentHandler class.

**Methods:**
- `test_validate_file_valid_pdf`: Test validation of valid PDF file....
- `test_validate_file_valid_docx`: Test validation of valid DOCX file....
- `test_validate_file_valid_txt`: Test validation of valid TXT file....
- `test_validate_file_unsupported_format`: Test validation of unsupported file format....
- `test_validate_file_too_large`: Test validation of file that's too large....
- `test_validate_file_empty`: Test validation of empty file....
- `test_validate_file_dangerous_filename`: Test validation of file with dangerous filename....
- `test_extract_metadata_valid_file`: Test metadata extraction from valid file....
- `test_extract_metadata_invalid_file`: Test metadata extraction from invalid file....
- `test_save_temp_file_valid`: Test saving valid file to temporary location....
- `test_save_temp_file_invalid`: Test saving invalid file returns None....
- `test_cleanup_temp_files`: Test cleanup of temporary files....
- `test_contains_dangerous_chars`: Test dangerous character detection....
- `test_get_file_info_existing_file`: Test getting file info for existing file....
- `test_get_file_info_nonexistent_file`: Test getting file info for non-existent file....
- `test_save_temp_file_exception_handling`: Test exception handling in save_temp_file....

**Test Functions:**

##### test_validate_file_valid_pdf

Test validation of valid PDF file.

**Parameters:** self
**Decorators:** 

##### test_validate_file_valid_docx

Test validation of valid DOCX file.

**Parameters:** self
**Decorators:** 

##### test_validate_file_valid_txt

Test validation of valid TXT file.

**Parameters:** self
**Decorators:** 

##### test_validate_file_unsupported_format

Test validation of unsupported file format.

**Parameters:** self
**Decorators:** 

##### test_validate_file_too_large

Test validation of file that's too large.

**Parameters:** self
**Decorators:** 

##### test_validate_file_empty

Test validation of empty file.

**Parameters:** self
**Decorators:** 

##### test_validate_file_dangerous_filename

Test validation of file with dangerous filename.

**Parameters:** self
**Decorators:** 

##### test_extract_metadata_valid_file

Test metadata extraction from valid file.

**Parameters:** self
**Decorators:** 

##### test_extract_metadata_invalid_file

Test metadata extraction from invalid file.

**Parameters:** self
**Decorators:** 

##### test_save_temp_file_valid

Test saving valid file to temporary location.

**Parameters:** self
**Decorators:** 

##### test_save_temp_file_invalid

Test saving invalid file returns None.

**Parameters:** self
**Decorators:** 

##### test_cleanup_temp_files

Test cleanup of temporary files.

**Parameters:** self
**Decorators:** 

##### test_contains_dangerous_chars

Test dangerous character detection.

**Parameters:** self
**Decorators:** 

##### test_get_file_info_existing_file

Test getting file info for existing file.

**Parameters:** self
**Decorators:** 

##### test_get_file_info_nonexistent_file

Test getting file info for non-existent file.

**Parameters:** self
**Decorators:** 

##### test_save_temp_file_exception_handling

Test exception handling in save_temp_file.

**Parameters:** self, mock_temp_file
**Decorators:** patch

### test_error_handler.py

Unit tests for the ErrorHandler class.

**Statistics:**
- Tests: 18
- Classes: 3
- Documented: 18
- Undocumented: 0

**Fixtures:**
- `error_handler` (scope: function): Create an ErrorHandler instance for testing....
- `mock_logger` (scope: function): Mock the logger for testing....

**Test Classes:**

#### TestErrorHandler

Test cases for ErrorHandler class.

**Methods:**
- `test_initialization`: Test ErrorHandler initialization....
- `test_handle_upload_error_file_size`: Test handling of file size upload errors....
- `test_handle_model_error_memory`: Test handling of model memory errors....
- `test_with_retry_success_first_attempt`: Test retry mechanism with successful first attempt....
- `test_with_retry_max_retries_exceeded`: Test retry mechanism when max retries are exceeded....
- `test_reset_retry_count`: Test resetting retry count for an operation....
- `test_get_error_statistics`: Test getting error statistics....

#### TestErrorContext

Test cases for ErrorContext dataclass.

**Methods:**
- `test_error_context_creation`: Test creating ErrorContext with all fields....

#### TestUserMessage

Test cases for UserMessage dataclass.

**Methods:**
- `test_user_message_creation`: Test creating UserMessage with all fields....

**Test Functions:**

##### test_initialization

Test ErrorHandler initialization.

**Parameters:** self, error_handler
**Decorators:** 

##### test_handle_upload_error_file_size

Test handling of file size upload errors.

**Parameters:** self, error_handler, mock_logger
**Decorators:** 

##### test_handle_model_error_memory

Test handling of model memory errors.

**Parameters:** self, error_handler, mock_logger
**Decorators:** 

##### test_with_retry_success_first_attempt

Test retry mechanism with successful first attempt.

**Parameters:** self, error_handler
**Decorators:** 

##### test_with_retry_max_retries_exceeded

Test retry mechanism when max retries are exceeded.

**Parameters:** self, error_handler
**Decorators:** 

##### test_reset_retry_count

Test resetting retry count for an operation.

**Parameters:** self, error_handler
**Decorators:** 

##### test_get_error_statistics

Test getting error statistics.

**Parameters:** self, error_handler
**Decorators:** 

##### test_error_context_creation

Test creating ErrorContext with all fields.

**Parameters:** self
**Decorators:** 

##### test_user_message_creation

Test creating UserMessage with all fields.

**Parameters:** self
**Decorators:** 

### test_error_handler_comprehensive.py

Comprehensive tests for the ErrorHandler class.

**Statistics:**
- Tests: 22
- Classes: 3
- Documented: 22
- Undocumented: 0

**Fixtures:**
- `error_handler` (scope: function): Create an ErrorHandler instance for testing....
- `mock_logger` (scope: function): Mock the logger for testing....

**Test Classes:**

#### TestErrorHandlerComprehensive

Test cases for ErrorHandler class.

**Methods:**
- `test_handle_upload_error_file_format`: Test handling of file format upload errors....
- `test_handle_extraction_error_empty_document`: Test handling of empty document extraction errors....
- `test_handle_extraction_error_generic`: Test handling of generic extraction errors....
- `test_handle_model_error_unavailable`: Test handling of model unavailable errors....
- `test_handle_system_error`: Test handling of system errors....
- `test_handle_validation_error`: Test handling of validation errors....
- `test_with_retry_exponential_backoff`: Test that retry delay increases exponentially....
- `test_log_error_different_levels`: Test that different error types log at appropriate levels....
- `test_cleanup_old_retry_counts`: Test cleanup of old retry counts....

#### TestErrorContext

Test cases for ErrorContext dataclass.

**Methods:**
- `test_error_context_creation`: Test creating ErrorContext with all fields....

#### TestUserMessage

Test cases for UserMessage dataclass.

**Methods:**
- `test_user_message_defaults`: Test UserMessage with default values....

**Test Functions:**

##### test_handle_upload_error_file_format

Test handling of file format upload errors.

**Parameters:** self, error_handler, mock_logger
**Decorators:** 

##### test_handle_extraction_error_empty_document

Test handling of empty document extraction errors.

**Parameters:** self, error_handler, mock_logger
**Decorators:** 

##### test_handle_extraction_error_generic

Test handling of generic extraction errors.

**Parameters:** self, error_handler, mock_logger
**Decorators:** 

##### test_handle_model_error_unavailable

Test handling of model unavailable errors.

**Parameters:** self, error_handler, mock_logger
**Decorators:** 

##### test_handle_system_error

Test handling of system errors.

**Parameters:** self, error_handler, mock_logger
**Decorators:** 

##### test_handle_validation_error

Test handling of validation errors.

**Parameters:** self, error_handler, mock_logger
**Decorators:** 

##### test_with_retry_exponential_backoff

Test that retry delay increases exponentially.

**Parameters:** self, error_handler
**Decorators:** 

##### test_log_error_different_levels

Test that different error types log at appropriate levels.

**Parameters:** self, error_handler, mock_logger
**Decorators:** 

##### test_cleanup_old_retry_counts

Test cleanup of old retry counts.

**Parameters:** self, error_handler, mock_logger
**Decorators:** 

##### test_error_context_creation

Test creating ErrorContext with all fields.

**Parameters:** self
**Decorators:** 

##### test_user_message_defaults

Test UserMessage with default values.

**Parameters:** self
**Decorators:** 

### test_error_handler_simple.py

Simple tests for error handling functionality.

**Statistics:**
- Tests: 12
- Classes: 1
- Documented: 0
- Undocumented: 12

**Fixtures:**
- `error_handler` (scope: function): ...

**Test Classes:**

#### TestErrorHandlerSimple



**Methods:**
- `test_handle_upload_error_file_size`: ...
- `test_handle_model_error_memory`: ...
- `test_with_retry_success`: ...
- `test_with_retry_max_retries_exceeded`: ...
- `test_reset_retry_count`: ...
- `test_get_error_statistics`: ...

**Test Functions:**

##### test_handle_upload_error_file_size



**Parameters:** self, error_handler
**Decorators:** 

##### test_handle_model_error_memory



**Parameters:** self, error_handler
**Decorators:** 

##### test_with_retry_success



**Parameters:** self, error_handler
**Decorators:** 

##### test_with_retry_max_retries_exceeded



**Parameters:** self, error_handler
**Decorators:** 

##### test_reset_retry_count



**Parameters:** self, error_handler
**Decorators:** 

##### test_get_error_statistics



**Parameters:** self, error_handler
**Decorators:** 

### test_summarizer.py

Unit tests for the LegalSummarizer class.

**Statistics:**
- Tests: 48
- Classes: 2
- Documented: 48
- Undocumented: 0

**Fixtures:**
- `summarizer` (scope: function): Create a LegalSummarizer instance for testing....
- `mock_tokenizer` (scope: function): Mock tokenizer for testing....
- `mock_model` (scope: function): Mock model for testing....
- `mock_pipeline` (scope: function): Mock summarization pipeline for testing....
- `summarizer_with_mocks` (scope: function): Create summarizer with necessary mocks for integration testing....

**Test Classes:**

#### TestLegalSummarizer

Test cases for LegalSummarizer class.

**Methods:**
- `test_init`: Test LegalSummarizer initialization....
- `test_init_custom_model`: Test LegalSummarizer initialization with custom model....
- `test_load_model_success`: Test successful model loading....
- `test_load_model_with_cuda`: Test model loading with CUDA available....
- `test_load_model_failure`: Test model loading failure....
- `test_chunk_text_short_text`: Test chunking with text that fits in one chunk....
- `test_chunk_text_long_text`: Test chunking with text that needs to be split....
- `test_chunk_text_model_not_loaded`: Test chunking when model is not loaded....
- `test_merge_chunk_summaries_empty`: Test merging empty summaries list....
- `test_merge_chunk_summaries_single`: Test merging single summary....
- `test_merge_chunk_summaries_multiple`: Test merging multiple summaries....
- `test_get_summary_length_params_brief`: Test getting parameters for brief summary....
- `test_get_summary_length_params_standard`: Test getting parameters for standard summary....
- `test_get_summary_length_params_detailed`: Test getting parameters for detailed summary....
- `test_get_summary_length_params_invalid`: Test getting parameters for invalid length (should default to standard)....
- `test_summarize_model_not_loaded`: Test summarization when model is not loaded....
- `test_summarize_success_single_chunk`: Test successful summarization with single chunk....
- `test_summarize_success_multiple_chunks`: Test successful summarization with multiple chunks....
- `test_summarize_with_word_limit`: Test summarization with word count exceeding max_words....
- `test_summarize_chunk_failure_fallback`: Test summarization with chunk processing failure and fallback....
- `test_summarize_complete_failure`: Test summarization complete failure with emergency fallback....
- `test_is_model_loaded_false`: Test is_model_loaded when model is not loaded....
- `test_is_model_loaded_true`: Test is_model_loaded when model is loaded....

#### TestLegalSummarizerIntegration

Integration tests for LegalSummarizer with real-like scenarios.

**Methods:**
- `test_end_to_end_summarization_workflow`: Test complete summarization workflow....

**Test Functions:**

##### test_init

Test LegalSummarizer initialization.

**Parameters:** self, summarizer
**Decorators:** 

##### test_init_custom_model

Test LegalSummarizer initialization with custom model.

**Parameters:** self
**Decorators:** 

##### test_load_model_success

Test successful model loading.

**Parameters:** self, mock_cuda, mock_tokenizer_class, mock_model_class, mock_pipeline_func, summarizer
**Decorators:** patch, patch, patch, patch

##### test_load_model_with_cuda

Test model loading with CUDA available.

**Parameters:** self, mock_cuda, mock_tokenizer_class, mock_model_class, mock_pipeline_func, summarizer
**Decorators:** patch, patch, patch, patch

##### test_load_model_failure

Test model loading failure.

**Parameters:** self, mock_tokenizer_class, summarizer
**Decorators:** patch

##### test_chunk_text_short_text

Test chunking with text that fits in one chunk.

**Parameters:** self, summarizer, mock_tokenizer
**Decorators:** 

##### test_chunk_text_long_text

Test chunking with text that needs to be split.

**Parameters:** self, summarizer, mock_tokenizer
**Decorators:** 

##### test_chunk_text_model_not_loaded

Test chunking when model is not loaded.

**Parameters:** self, summarizer
**Decorators:** 

##### test_merge_chunk_summaries_empty

Test merging empty summaries list.

**Parameters:** self, summarizer
**Decorators:** 

##### test_merge_chunk_summaries_single

Test merging single summary.

**Parameters:** self, summarizer
**Decorators:** 

##### test_merge_chunk_summaries_multiple

Test merging multiple summaries.

**Parameters:** self, summarizer, mock_tokenizer, mock_pipeline
**Decorators:** 

##### test_get_summary_length_params_brief

Test getting parameters for brief summary.

**Parameters:** self, summarizer
**Decorators:** 

##### test_get_summary_length_params_standard

Test getting parameters for standard summary.

**Parameters:** self, summarizer
**Decorators:** 

##### test_get_summary_length_params_detailed

Test getting parameters for detailed summary.

**Parameters:** self, summarizer
**Decorators:** 

##### test_get_summary_length_params_invalid

Test getting parameters for invalid length (should default to standard).

**Parameters:** self, summarizer
**Decorators:** 

##### test_summarize_model_not_loaded

Test summarization when model is not loaded.

**Parameters:** self, summarizer
**Decorators:** 

##### test_summarize_success_single_chunk

Test successful summarization with single chunk.

**Parameters:** self, mock_time, summarizer, mock_tokenizer, mock_pipeline
**Decorators:** patch

##### test_summarize_success_multiple_chunks

Test successful summarization with multiple chunks.

**Parameters:** self, mock_time, summarizer, mock_tokenizer, mock_pipeline
**Decorators:** patch

##### test_summarize_with_word_limit

Test summarization with word count exceeding max_words.

**Parameters:** self, mock_time, summarizer, mock_tokenizer, mock_pipeline
**Decorators:** patch

##### test_summarize_chunk_failure_fallback

Test summarization with chunk processing failure and fallback.

**Parameters:** self, mock_time, summarizer, mock_tokenizer, mock_pipeline
**Decorators:** patch

##### test_summarize_complete_failure

Test summarization complete failure with emergency fallback.

**Parameters:** self, summarizer, mock_pipeline
**Decorators:** 

##### test_is_model_loaded_false

Test is_model_loaded when model is not loaded.

**Parameters:** self, summarizer
**Decorators:** 

##### test_is_model_loaded_true

Test is_model_loaded when model is loaded.

**Parameters:** self, summarizer, mock_pipeline
**Decorators:** 

##### test_end_to_end_summarization_workflow

Test complete summarization workflow.

**Parameters:** self, summarizer_with_mocks
**Decorators:** 

### test_summarizer_customization.py

Unit tests for LegalSummarizer customization features.

**Statistics:**
- Tests: 72
- Classes: 2
- Documented: 72
- Undocumented: 0

**Fixtures:**
- `summarizer` (scope: function): Create a LegalSummarizer instance for testing....
- `mock_tokenizer` (scope: function): Mock tokenizer for testing....
- `mock_pipeline` (scope: function): Mock summarization pipeline for testing....
- `summarizer_with_mocks` (scope: function): Create summarizer with necessary mocks for integration testing....

**Test Classes:**

#### TestLegalSummarizerCustomization

Test cases for LegalSummarizer customization features.

**Methods:**
- `test_get_focus_adjustments_general`: Test focus adjustments for general focus....
- `test_get_focus_adjustments_obligations`: Test focus adjustments for obligations focus....
- `test_get_focus_adjustments_parties`: Test focus adjustments for parties focus....
- `test_get_focus_adjustments_dates`: Test focus adjustments for dates focus....
- `test_get_focus_adjustments_invalid`: Test focus adjustments for invalid focus (should default to general)....
- `test_create_focus_prompt_general`: Test focus prompt creation for general focus....
- `test_create_focus_prompt_obligations`: Test focus prompt creation for obligations focus....
- `test_create_focus_prompt_parties`: Test focus prompt creation for parties focus....
- `test_create_focus_prompt_dates`: Test focus prompt creation for dates focus....
- `test_apply_focus_specific_processing_obligations`: Test focus-specific processing for obligations....
- `test_apply_focus_specific_processing_parties`: Test focus-specific processing for parties....
- `test_apply_focus_specific_processing_dates`: Test focus-specific processing for dates....
- `test_apply_focus_specific_processing_general`: Test focus-specific processing for general (no changes)....
- `test_emphasize_keywords`: Test keyword emphasis functionality....
- `test_emphasize_keywords_case_insensitive`: Test keyword emphasis is case insensitive....
- `test_emphasize_keywords_word_boundaries`: Test keyword emphasis respects word boundaries....
- `test_get_summary_length_params_with_focus`: Test that length params include focus adjustments....
- `test_post_process_summary_obligations`: Test post-processing for obligations focus....
- `test_post_process_summary_parties`: Test post-processing for parties focus....
- `test_post_process_summary_dates`: Test post-processing for dates focus....
- `test_post_process_summary_general`: Test post-processing for general focus (minimal changes)....
- `test_validate_and_sanitize_params_valid`: Test parameter validation with valid parameters....
- `test_validate_and_sanitize_params_invalid_length`: Test parameter validation with invalid length....
- `test_validate_and_sanitize_params_invalid_focus`: Test parameter validation with invalid focus....
- `test_validate_and_sanitize_params_invalid_max_words_too_low`: Test parameter validation with max_words too low....
- `test_validate_and_sanitize_params_invalid_max_words_too_high`: Test parameter validation with max_words too high....
- `test_get_available_customization_options`: Test getting available customization options....
- `test_get_default_fallback_params`: Test getting default fallback parameters....
- `test_create_emergency_fallback_summary_brief`: Test emergency fallback summary creation for brief length....
- `test_create_emergency_fallback_summary_detailed`: Test emergency fallback summary creation for detailed length....
- `test_create_emergency_fallback_summary_word_limit`: Test emergency fallback summary respects word limit....
- `test_summarize_with_parameter_validation`: Test that summarize method validates parameters....
- `test_summarize_with_focus_processing`: Test that summarize method applies focus-specific processing....
- `test_summarize_with_fallback_mechanism`: Test summarize method fallback mechanism....

#### TestLegalSummarizerIntegrationCustomization

Integration tests for LegalSummarizer customization features.

**Methods:**
- `test_end_to_end_customization_workflow`: Test complete customization workflow....
- `test_parameter_validation_integration`: Test parameter validation in integration scenario....

**Test Functions:**

##### test_get_focus_adjustments_general

Test focus adjustments for general focus.

**Parameters:** self, summarizer
**Decorators:** 

##### test_get_focus_adjustments_obligations

Test focus adjustments for obligations focus.

**Parameters:** self, summarizer
**Decorators:** 

##### test_get_focus_adjustments_parties

Test focus adjustments for parties focus.

**Parameters:** self, summarizer
**Decorators:** 

##### test_get_focus_adjustments_dates

Test focus adjustments for dates focus.

**Parameters:** self, summarizer
**Decorators:** 

##### test_get_focus_adjustments_invalid

Test focus adjustments for invalid focus (should default to general).

**Parameters:** self, summarizer
**Decorators:** 

##### test_create_focus_prompt_general

Test focus prompt creation for general focus.

**Parameters:** self, summarizer
**Decorators:** 

##### test_create_focus_prompt_obligations

Test focus prompt creation for obligations focus.

**Parameters:** self, summarizer
**Decorators:** 

##### test_create_focus_prompt_parties

Test focus prompt creation for parties focus.

**Parameters:** self, summarizer
**Decorators:** 

##### test_create_focus_prompt_dates

Test focus prompt creation for dates focus.

**Parameters:** self, summarizer
**Decorators:** 

##### test_apply_focus_specific_processing_obligations

Test focus-specific processing for obligations.

**Parameters:** self, summarizer
**Decorators:** 

##### test_apply_focus_specific_processing_parties

Test focus-specific processing for parties.

**Parameters:** self, summarizer
**Decorators:** 

##### test_apply_focus_specific_processing_dates

Test focus-specific processing for dates.

**Parameters:** self, summarizer
**Decorators:** 

##### test_apply_focus_specific_processing_general

Test focus-specific processing for general (no changes).

**Parameters:** self, summarizer
**Decorators:** 

##### test_emphasize_keywords

Test keyword emphasis functionality.

**Parameters:** self, summarizer
**Decorators:** 

##### test_emphasize_keywords_case_insensitive

Test keyword emphasis is case insensitive.

**Parameters:** self, summarizer
**Decorators:** 

##### test_emphasize_keywords_word_boundaries

Test keyword emphasis respects word boundaries.

**Parameters:** self, summarizer
**Decorators:** 

##### test_get_summary_length_params_with_focus

Test that length params include focus adjustments.

**Parameters:** self, summarizer
**Decorators:** 

##### test_post_process_summary_obligations

Test post-processing for obligations focus.

**Parameters:** self, summarizer
**Decorators:** 

##### test_post_process_summary_parties

Test post-processing for parties focus.

**Parameters:** self, summarizer
**Decorators:** 

##### test_post_process_summary_dates

Test post-processing for dates focus.

**Parameters:** self, summarizer
**Decorators:** 

##### test_post_process_summary_general

Test post-processing for general focus (minimal changes).

**Parameters:** self, summarizer
**Decorators:** 

##### test_validate_and_sanitize_params_valid

Test parameter validation with valid parameters.

**Parameters:** self, summarizer
**Decorators:** 

##### test_validate_and_sanitize_params_invalid_length

Test parameter validation with invalid length.

**Parameters:** self, summarizer
**Decorators:** 

##### test_validate_and_sanitize_params_invalid_focus

Test parameter validation with invalid focus.

**Parameters:** self, summarizer
**Decorators:** 

##### test_validate_and_sanitize_params_invalid_max_words_too_low

Test parameter validation with max_words too low.

**Parameters:** self, summarizer
**Decorators:** 

##### test_validate_and_sanitize_params_invalid_max_words_too_high

Test parameter validation with max_words too high.

**Parameters:** self, summarizer
**Decorators:** 

##### test_get_available_customization_options

Test getting available customization options.

**Parameters:** self, summarizer
**Decorators:** 

##### test_get_default_fallback_params

Test getting default fallback parameters.

**Parameters:** self, summarizer
**Decorators:** 

##### test_create_emergency_fallback_summary_brief

Test emergency fallback summary creation for brief length.

**Parameters:** self, summarizer
**Decorators:** 

##### test_create_emergency_fallback_summary_detailed

Test emergency fallback summary creation for detailed length.

**Parameters:** self, summarizer
**Decorators:** 

##### test_create_emergency_fallback_summary_word_limit

Test emergency fallback summary respects word limit.

**Parameters:** self, summarizer
**Decorators:** 

##### test_summarize_with_parameter_validation

Test that summarize method validates parameters.

**Parameters:** self, mock_time, summarizer, mock_tokenizer, mock_pipeline
**Decorators:** patch

##### test_summarize_with_focus_processing

Test that summarize method applies focus-specific processing.

**Parameters:** self, mock_time, summarizer, mock_tokenizer, mock_pipeline
**Decorators:** patch

##### test_summarize_with_fallback_mechanism

Test summarize method fallback mechanism.

**Parameters:** self, mock_time, summarizer, mock_tokenizer, mock_pipeline
**Decorators:** patch

##### test_end_to_end_customization_workflow

Test complete customization workflow.

**Parameters:** self, summarizer_with_mocks
**Decorators:** 

##### test_parameter_validation_integration

Test parameter validation in integration scenario.

**Parameters:** self, summarizer_with_mocks
**Decorators:** 

### test_text_extractor.py

Unit tests for text extraction service.

**Statistics:**
- Tests: 44
- Classes: 1
- Documented: 44
- Undocumented: 0

**Test Classes:**

#### TestTextExtractor

Test TextExtractor class.

**Methods:**
- `test_clean_text_basic`: Test basic text cleaning functionality....
- `test_clean_text_control_characters`: Test removal of control characters....
- `test_clean_text_line_breaks`: Test normalization of line breaks....
- `test_clean_text_excessive_line_breaks`: Test removal of excessive line breaks....
- `test_clean_text_empty_input`: Test cleaning empty or None input....
- `test_validate_legal_content_valid`: Test validation of valid legal content....
- `test_validate_legal_content_with_patterns`: Test validation with legal patterns....
- `test_validate_legal_content_invalid_short`: Test validation of too short text....
- `test_validate_legal_content_invalid_no_keywords`: Test validation of text without legal keywords....
- `test_validate_legal_content_empty`: Test validation of empty content....
- `test_extract_from_txt_success`: Test successful text extraction from TXT file....
- `test_extract_from_txt_different_encodings`: Test TXT extraction with different encodings....
- `test_extract_from_txt_file_not_found`: Test TXT extraction with non-existent file....
- `test_extract_from_docx_success`: Test successful DOCX extraction....
- `test_extract_from_docx_with_tables`: Test DOCX extraction with tables....
- `test_extract_from_docx_file_not_found`: Test DOCX extraction with non-existent file....
- `test_extract_from_docx_library_not_available`: Test DOCX extraction when library is not available....
- `test_extract_from_pdf_with_pdfplumber`: Test PDF extraction using pdfplumber....
- `test_extract_from_pdf_with_pypdf2_fallback`: Test PDF extraction fallback to PyPDF2....
- `test_extract_from_pdf_file_not_found`: Test PDF extraction with non-existent file....
- `test_extract_text_dispatcher`: Test the main extract_text method dispatcher....
- `test_extract_text_unsupported_format`: Test extract_text with unsupported file format....

**Test Functions:**

##### test_clean_text_basic

Test basic text cleaning functionality.

**Parameters:** self
**Decorators:** 

##### test_clean_text_control_characters

Test removal of control characters.

**Parameters:** self
**Decorators:** 

##### test_clean_text_line_breaks

Test normalization of line breaks.

**Parameters:** self
**Decorators:** 

##### test_clean_text_excessive_line_breaks

Test removal of excessive line breaks.

**Parameters:** self
**Decorators:** 

##### test_clean_text_empty_input

Test cleaning empty or None input.

**Parameters:** self
**Decorators:** 

##### test_validate_legal_content_valid

Test validation of valid legal content.

**Parameters:** self
**Decorators:** 

##### test_validate_legal_content_with_patterns

Test validation with legal patterns.

**Parameters:** self
**Decorators:** 

##### test_validate_legal_content_invalid_short

Test validation of too short text.

**Parameters:** self
**Decorators:** 

##### test_validate_legal_content_invalid_no_keywords

Test validation of text without legal keywords.

**Parameters:** self
**Decorators:** 

##### test_validate_legal_content_empty

Test validation of empty content.

**Parameters:** self
**Decorators:** 

##### test_extract_from_txt_success

Test successful text extraction from TXT file.

**Parameters:** self
**Decorators:** 

##### test_extract_from_txt_different_encodings

Test TXT extraction with different encodings.

**Parameters:** self
**Decorators:** 

##### test_extract_from_txt_file_not_found

Test TXT extraction with non-existent file.

**Parameters:** self
**Decorators:** 

##### test_extract_from_docx_success

Test successful DOCX extraction.

**Parameters:** self, mock_document_class
**Decorators:** patch

##### test_extract_from_docx_with_tables

Test DOCX extraction with tables.

**Parameters:** self, mock_document_class
**Decorators:** patch

##### test_extract_from_docx_file_not_found

Test DOCX extraction with non-existent file.

**Parameters:** self
**Decorators:** 

##### test_extract_from_docx_library_not_available

Test DOCX extraction when library is not available.

**Parameters:** self
**Decorators:** patch

##### test_extract_from_pdf_with_pdfplumber

Test PDF extraction using pdfplumber.

**Parameters:** self, mock_pdfplumber
**Decorators:** patch

##### test_extract_from_pdf_with_pypdf2_fallback

Test PDF extraction fallback to PyPDF2.

**Parameters:** self, mock_pypdf2
**Decorators:** patch, patch

##### test_extract_from_pdf_file_not_found

Test PDF extraction with non-existent file.

**Parameters:** self
**Decorators:** 

##### test_extract_text_dispatcher

Test the main extract_text method dispatcher.

**Parameters:** self
**Decorators:** 

##### test_extract_text_unsupported_format

Test extract_text with unsupported file format.

**Parameters:** self
**Decorators:** 

