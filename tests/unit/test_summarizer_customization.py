"""
Unit tests for LegalSummarizer customization features.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.services.summarizer import LegalSummarizer
from src.models.data_models import SummaryParams, SummaryResult


class TestLegalSummarizerCustomization:
    """Test cases for LegalSummarizer customization features."""
    
    @pytest.fixture
    def summarizer(self):
        """Create a LegalSummarizer instance for testing."""
        return LegalSummarizer()
    
    @pytest.fixture
    def mock_tokenizer(self):
        """Mock tokenizer for testing."""
        tokenizer = Mock()
        tokenizer.encode.return_value = [1, 2, 3, 4, 5]  # 5 tokens
        return tokenizer
    
    @pytest.fixture
    def mock_pipeline(self):
        """Mock summarization pipeline for testing."""
        pipeline = Mock()
        pipeline.return_value = [{"summary_text": "This is a test summary."}]
        return pipeline
    
    def test_get_focus_adjustments_general(self, summarizer):
        """Test focus adjustments for general focus."""
        adjustments = summarizer._get_focus_adjustments("general")
        
        assert adjustments["length_penalty"] == 1.0
        assert adjustments["repetition_penalty"] == 1.1
    
    def test_get_focus_adjustments_obligations(self, summarizer):
        """Test focus adjustments for obligations focus."""
        adjustments = summarizer._get_focus_adjustments("obligations")
        
        assert adjustments["length_penalty"] == 1.2
        assert adjustments["repetition_penalty"] == 1.0
        assert adjustments["no_repeat_ngram_size"] == 2
    
    def test_get_focus_adjustments_parties(self, summarizer):
        """Test focus adjustments for parties focus."""
        adjustments = summarizer._get_focus_adjustments("parties")
        
        assert adjustments["length_penalty"] == 0.8
        assert adjustments["repetition_penalty"] == 1.2
        assert adjustments["no_repeat_ngram_size"] == 3
    
    def test_get_focus_adjustments_dates(self, summarizer):
        """Test focus adjustments for dates focus."""
        adjustments = summarizer._get_focus_adjustments("dates")
        
        assert adjustments["length_penalty"] == 0.9
        assert adjustments["repetition_penalty"] == 1.1
        assert adjustments["no_repeat_ngram_size"] == 2
    
    def test_get_focus_adjustments_invalid(self, summarizer):
        """Test focus adjustments for invalid focus (should default to general)."""
        adjustments = summarizer._get_focus_adjustments("invalid_focus")
        
        assert adjustments["length_penalty"] == 1.0
        assert adjustments["repetition_penalty"] == 1.1
    
    def test_create_focus_prompt_general(self, summarizer):
        """Test focus prompt creation for general focus."""
        text = "This is a legal document."
        prompt = summarizer._create_focus_prompt(text, "general")
        
        assert "Summarize the following legal document, highlighting the main points" in prompt
        assert text in prompt
    
    def test_create_focus_prompt_obligations(self, summarizer):
        """Test focus prompt creation for obligations focus."""
        text = "This is a legal document."
        prompt = summarizer._create_focus_prompt(text, "obligations")
        
        assert "focusing specifically on obligations, duties, responsibilities" in prompt
        assert text in prompt
    
    def test_create_focus_prompt_parties(self, summarizer):
        """Test focus prompt creation for parties focus."""
        text = "This is a legal document."
        prompt = summarizer._create_focus_prompt(text, "parties")
        
        assert "focusing specifically on the parties involved, their roles" in prompt
        assert text in prompt
    
    def test_create_focus_prompt_dates(self, summarizer):
        """Test focus prompt creation for dates focus."""
        text = "This is a legal document."
        prompt = summarizer._create_focus_prompt(text, "dates")
        
        assert "focusing specifically on important dates, deadlines" in prompt
        assert text in prompt
    
    def test_apply_focus_specific_processing_obligations(self, summarizer):
        """Test focus-specific processing for obligations."""
        text = "The contractor shall complete the work and must deliver by the deadline."
        processed = summarizer._apply_focus_specific_processing(text, "obligations")
        
        assert "**shall**" in processed
        assert "**must**" in processed
    
    def test_apply_focus_specific_processing_parties(self, summarizer):
        """Test focus-specific processing for parties."""
        text = "The client and contractor agree to the terms. The vendor will supply materials."
        processed = summarizer._apply_focus_specific_processing(text, "parties")
        
        assert "**client**" in processed
        assert "**contractor**" in processed
        assert "**vendor**" in processed
    
    def test_apply_focus_specific_processing_dates(self, summarizer):
        """Test focus-specific processing for dates."""
        text = "The deadline is next month. The term expires after two years."
        processed = summarizer._apply_focus_specific_processing(text, "dates")
        
        assert "**deadline**" in processed
        assert "**term**" in processed
        assert "**expires**" in processed
    
    def test_apply_focus_specific_processing_general(self, summarizer):
        """Test focus-specific processing for general (no changes)."""
        text = "This is a general legal document."
        processed = summarizer._apply_focus_specific_processing(text, "general")
        
        assert processed == text  # No changes for general focus
    
    def test_emphasize_keywords(self, summarizer):
        """Test keyword emphasis functionality."""
        text = "The party shall complete the obligation within the deadline."
        keywords = ["party", "shall", "obligation"]
        emphasized = summarizer._emphasize_keywords(text, keywords)
        
        assert "**party**" in emphasized
        assert "**shall**" in emphasized
        assert "**obligation**" in emphasized
        assert "within" in emphasized  # Non-keyword should remain unchanged
    
    def test_emphasize_keywords_case_insensitive(self, summarizer):
        """Test keyword emphasis is case insensitive."""
        text = "The PARTY shall complete the Obligation."
        keywords = ["party", "obligation"]
        emphasized = summarizer._emphasize_keywords(text, keywords)
        
        assert "**PARTY**" in emphasized
        assert "**Obligation**" in emphasized
    
    def test_emphasize_keywords_word_boundaries(self, summarizer):
        """Test keyword emphasis respects word boundaries."""
        text = "The party and counterparty have obligations."
        keywords = ["party"]
        emphasized = summarizer._emphasize_keywords(text, keywords)
        
        # Should emphasize "party" but not "counterparty"
        assert "**party**" in emphasized
        assert "counter**party**" not in emphasized
        assert "counterparty" in emphasized
    
    def test_get_summary_length_params_with_focus(self, summarizer):
        """Test that length params include focus adjustments."""
        params = summarizer._get_summary_length_params("standard", "obligations")
        
        # Should have standard length params
        assert params["max_length"] == 200
        assert params["min_length"] == 80
        
        # Should have obligations focus adjustments
        assert params["length_penalty"] == 1.2
        assert params["repetition_penalty"] == 1.0
        assert params["no_repeat_ngram_size"] == 2
        
        # Should have base model params
        assert params["do_sample"] is False
        assert params["num_beams"] == 4
    
    def test_post_process_summary_obligations(self, summarizer):
        """Test post-processing for obligations focus."""
        summary = "The **contractor** **shall** complete the work."
        processed = summarizer._post_process_summary(summary, "obligations")
        
        assert processed.startswith("Key Obligations:")
        assert "contractor" in processed  # Emphasis markers removed
        assert "shall" in processed
        assert "**" not in processed  # No emphasis markers
    
    def test_post_process_summary_parties(self, summarizer):
        """Test post-processing for parties focus."""
        summary = "The **client** and **contractor** are the main parties."
        processed = summarizer._post_process_summary(summary, "parties")
        
        assert processed.startswith("Parties Involved:")
        assert "client" in processed
        assert "contractor" in processed
        assert "**" not in processed
    
    def test_post_process_summary_dates(self, summarizer):
        """Test post-processing for dates focus."""
        summary = "The **deadline** is next month and the **term** is two years."
        processed = summarizer._post_process_summary(summary, "dates")
        
        assert processed.startswith("Important Dates:")
        assert "deadline" in processed
        assert "term" in processed
        assert "**" not in processed
    
    def test_post_process_summary_general(self, summarizer):
        """Test post-processing for general focus (minimal changes)."""
        summary = "This is a **general** summary."
        processed = summarizer._post_process_summary(summary, "general")
        
        assert processed == "This is a general summary."  # Only emphasis markers removed
        assert "**" not in processed   
 
    def test_validate_and_sanitize_params_valid(self, summarizer):
        """Test parameter validation with valid parameters."""
        params = SummaryParams(length="standard", focus="obligations", max_words=250)
        validated = summarizer.validate_and_sanitize_params(params)
        
        assert validated.length == "standard"
        assert validated.focus == "obligations"
        assert validated.max_words == 250
    
    def test_validate_and_sanitize_params_invalid_length(self, summarizer):
        """Test parameter validation with invalid length."""
        params = SummaryParams(length="invalid", focus="general", max_words=200)
        validated = summarizer.validate_and_sanitize_params(params)
        
        assert validated.length == "standard"  # Default
        assert validated.focus == "general"
        assert validated.max_words == 200
    
    def test_validate_and_sanitize_params_invalid_focus(self, summarizer):
        """Test parameter validation with invalid focus."""
        params = SummaryParams(length="brief", focus="invalid", max_words=200)
        validated = summarizer.validate_and_sanitize_params(params)
        
        assert validated.length == "brief"
        assert validated.focus == "general"  # Default
        assert validated.max_words == 200
    
    def test_validate_and_sanitize_params_invalid_max_words_too_low(self, summarizer):
        """Test parameter validation with max_words too low."""
        params = SummaryParams(length="standard", focus="general", max_words=10)
        validated = summarizer.validate_and_sanitize_params(params)
        
        assert validated.length == "standard"
        assert validated.focus == "general"
        assert validated.max_words == 50  # Minimum
    
    def test_validate_and_sanitize_params_invalid_max_words_too_high(self, summarizer):
        """Test parameter validation with max_words too high."""
        params = SummaryParams(length="standard", focus="general", max_words=2000)
        validated = summarizer.validate_and_sanitize_params(params)
        
        assert validated.length == "standard"
        assert validated.focus == "general"
        assert validated.max_words == 1000  # Maximum
    
    def test_get_available_customization_options(self, summarizer):
        """Test getting available customization options."""
        options = summarizer.get_available_customization_options()
        
        # Check structure
        assert "lengths" in options
        assert "focuses" in options
        assert "word_limits" in options
        
        # Check length options
        assert "brief" in options["lengths"]
        assert "standard" in options["lengths"]
        assert "detailed" in options["lengths"]
        
        # Check focus options
        assert "general" in options["focuses"]
        assert "obligations" in options["focuses"]
        assert "parties" in options["focuses"]
        assert "dates" in options["focuses"]
        
        # Check word limits
        assert options["word_limits"]["min"] == 50
        assert options["word_limits"]["max"] == 1000
        assert options["word_limits"]["default"] == 300
    
    def test_get_default_fallback_params(self, summarizer):
        """Test getting default fallback parameters."""
        params = summarizer._get_default_fallback_params()
        
        assert params["max_length"] == 150
        assert params["min_length"] == 50
        assert params["do_sample"] is False
        assert params["num_beams"] == 2  # Reduced for stability
        assert params["early_stopping"] is True
        assert params["length_penalty"] == 1.0
        assert params["repetition_penalty"] == 1.1
    
    def test_create_emergency_fallback_summary_brief(self, summarizer):
        """Test emergency fallback summary creation for brief length."""
        text = "First sentence. Second sentence. Third sentence. Fourth sentence. Fifth sentence."
        params = SummaryParams(length="brief", focus="general", max_words=100)
        
        result = summarizer._create_emergency_fallback_summary(text, params, "test.pdf", 0.0)
        
        assert isinstance(result, SummaryResult)
        assert result.original_filename == "test.pdf"
        assert result.summary_text.startswith("[Extractive Summary]")
        assert result.confidence_score == 0.3  # Low confidence
        assert "First sentence" in result.summary_text
        assert "Second sentence" in result.summary_text
        # Should only have 2 sentences for brief
        assert "Fourth sentence" not in result.summary_text
    
    def test_create_emergency_fallback_summary_detailed(self, summarizer):
        """Test emergency fallback summary creation for detailed length."""
        text = "First. Second. Third. Fourth. Fifth. Sixth. Seventh."
        params = SummaryParams(length="detailed", focus="general", max_words=100)
        
        result = summarizer._create_emergency_fallback_summary(text, params, "test.pdf", 0.0)
        
        # Should have 6 sentences for detailed
        assert "First" in result.summary_text
        assert "Sixth" in result.summary_text
        assert "Seventh" not in result.summary_text  # Only 6 sentences
    
    def test_create_emergency_fallback_summary_word_limit(self, summarizer):
        """Test emergency fallback summary respects word limit."""
        long_text = " ".join(["Word"] * 200) + "."  # 200 words
        params = SummaryParams(length="standard", focus="general", max_words=50)
        
        result = summarizer._create_emergency_fallback_summary(long_text, params, "test.pdf", 0.0)
        
        # Should be truncated to 50 words
        assert result.word_count <= 50
        assert result.summary_text.endswith("...")
    
    @patch('src.services.summarizer.time.time')
    def test_summarize_with_parameter_validation(self, mock_time, summarizer, mock_tokenizer, mock_pipeline):
        """Test that summarize method validates parameters."""
        mock_time.side_effect = [0.0, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5]
        summarizer.tokenizer = mock_tokenizer
        summarizer.summarizer_pipeline = mock_pipeline
        
        mock_tokenizer.encode.return_value = [1, 2, 3, 4, 5]
        mock_pipeline.return_value = [{"summary_text": "Test summary with obligations."}]
        
        # Use invalid parameters
        invalid_params = SummaryParams(length="invalid", focus="invalid", max_words=10)
        
        result = summarizer.summarize("Test text with obligations.", invalid_params, "test.pdf")
        
        # Should still work with sanitized parameters
        assert isinstance(result, SummaryResult)
        assert result.summary_text is not None
    
    @patch('src.services.summarizer.time.time')
    def test_summarize_with_focus_processing(self, mock_time, summarizer, mock_tokenizer, mock_pipeline):
        """Test that summarize method applies focus-specific processing."""
        mock_time.side_effect = [0.0, 2.0, 2.1, 2.2]
        summarizer.tokenizer = mock_tokenizer
        summarizer.summarizer_pipeline = mock_pipeline
        
        mock_tokenizer.encode.return_value = [1, 2, 3, 4, 5]
        mock_pipeline.return_value = [{"summary_text": "The contractor shall complete obligations."}]
        
        params = SummaryParams(length="standard", focus="obligations", max_words=200)
        text = "The contractor shall complete the work."
        
        result = summarizer.summarize(text, params, "test.pdf")
        
        # Should have focus-specific post-processing
        assert "Key Obligations:" in result.summary_text
        assert isinstance(result, SummaryResult)
    
    @patch('src.services.summarizer.time.time')
    def test_summarize_with_fallback_mechanism(self, mock_time, summarizer, mock_tokenizer, mock_pipeline):
        """Test summarize method fallback mechanism."""
        mock_time.side_effect = [0.0, 2.0, 2.1, 2.2, 2.3, 2.4]
        summarizer.tokenizer = mock_tokenizer
        summarizer.summarizer_pipeline = mock_pipeline
        
        mock_tokenizer.encode.return_value = [1, 2, 3, 4, 5]
        
        # First call fails, second call (fallback) succeeds
        mock_pipeline.side_effect = [
            Exception("Custom params failed"),
            [{"summary_text": "Fallback summary."}]
        ]
        
        params = SummaryParams(length="standard", focus="general", max_words=200)
        
        result = summarizer.summarize("Test text.", params, "test.pdf")
        
        # Should succeed with fallback
        assert isinstance(result, SummaryResult)
        assert result.confidence_score < 1.0  # Reduced confidence due to fallback
        assert "Fallback summary" in result.summary_text


class TestLegalSummarizerIntegrationCustomization:
    """Integration tests for LegalSummarizer customization features."""
    
    @pytest.fixture
    def summarizer_with_mocks(self):
        """Create summarizer with necessary mocks for integration testing."""
        summarizer = LegalSummarizer()
        summarizer.tokenizer = Mock()
        summarizer.model = Mock()
        summarizer.summarizer_pipeline = Mock()
        return summarizer
    
    def test_end_to_end_customization_workflow(self, summarizer_with_mocks):
        """Test complete customization workflow."""
        summarizer = summarizer_with_mocks
        
        # Setup mocks
        summarizer.tokenizer.encode.return_value = [1] * 300
        summarizer.summarizer_pipeline.return_value = [
            {"summary_text": "The parties shall fulfill their obligations by the specified dates."}
        ]
        
        # Test different focus areas
        legal_text = """
        This agreement between Client Corp and Contractor LLC establishes obligations.
        The contractor shall complete all work by December 31, 2024.
        Both parties agree to the terms and conditions specified herein.
        """
        
        # Test obligations focus
        obligations_params = SummaryParams(length="detailed", focus="obligations", max_words=300)
        result = summarizer.summarize(legal_text, obligations_params, "contract.pdf")
        
        assert isinstance(result, SummaryResult)
        assert "Key Obligations:" in result.summary_text
        assert result.confidence_score > 0
        
        # Test parties focus
        parties_params = SummaryParams(length="brief", focus="parties", max_words=150)
        result = summarizer.summarize(legal_text, parties_params, "contract.pdf")
        
        assert isinstance(result, SummaryResult)
        assert "Parties Involved:" in result.summary_text
    
    def test_parameter_validation_integration(self, summarizer_with_mocks):
        """Test parameter validation in integration scenario."""
        summarizer = summarizer_with_mocks
        
        summarizer.tokenizer.encode.return_value = [1] * 100
        summarizer.summarizer_pipeline.return_value = [
            {"summary_text": "Valid summary text."}
        ]
        
        # Test with completely invalid parameters
        invalid_params = SummaryParams(length="super_long", focus="random_focus", max_words=5000)
        
        result = summarizer.summarize("Test legal document.", invalid_params, "test.pdf")
        
        # Should still work with sanitized parameters
        assert isinstance(result, SummaryResult)
        assert result.summary_text is not None
        assert len(result.summary_text.split()) <= 1000  # Max word limit applied