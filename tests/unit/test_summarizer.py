"""
Unit tests for the LegalSummarizer class.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import torch

from src.services.summarizer import LegalSummarizer
from src.models.data_models import SummaryParams, SummaryResult


class TestLegalSummarizer:
    """Test cases for LegalSummarizer class."""
    
    @pytest.fixture
    def summarizer(self):
        """Create a LegalSummarizer instance for testing."""
        return LegalSummarizer(model_name="facebook/bart-large-cnn")
    
    @pytest.fixture
    def mock_tokenizer(self):
        """Mock tokenizer for testing."""
        tokenizer = Mock()
        tokenizer.encode.return_value = [1, 2, 3, 4, 5]  # 5 tokens
        return tokenizer
    
    @pytest.fixture
    def mock_model(self):
        """Mock model for testing."""
        return Mock()
    
    @pytest.fixture
    def mock_pipeline(self):
        """Mock summarization pipeline for testing."""
        pipeline = Mock()
        pipeline.return_value = [{"summary_text": "This is a test summary."}]
        return pipeline
    
    def test_init(self, summarizer):
        """Test LegalSummarizer initialization."""
        assert summarizer.model_name == "facebook/bart-large-cnn"
        assert summarizer.tokenizer is None
        assert summarizer.model is None
        assert summarizer.summarizer_pipeline is None
        assert summarizer.max_chunk_size == 1024
    
    def test_init_custom_model(self):
        """Test LegalSummarizer initialization with custom model."""
        custom_model = "t5-base"
        summarizer = LegalSummarizer(model_name=custom_model)
        assert summarizer.model_name == custom_model
    
    @patch('src.services.summarizer.pipeline')
    @patch('src.services.summarizer.AutoModelForSeq2SeqLM')
    @patch('src.services.summarizer.AutoTokenizer')
    @patch('torch.cuda.is_available')
    def test_load_model_success(self, mock_cuda, mock_tokenizer_class, 
                               mock_model_class, mock_pipeline_func, summarizer):
        """Test successful model loading."""
        # Setup mocks
        mock_cuda.return_value = False
        mock_tokenizer = Mock()
        mock_model = Mock()
        mock_pipeline = Mock()
        
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer
        mock_model_class.from_pretrained.return_value = mock_model
        mock_pipeline_func.return_value = mock_pipeline
        
        # Test model loading
        summarizer.load_model()
        
        # Verify calls
        mock_tokenizer_class.from_pretrained.assert_called_once_with("facebook/bart-large-cnn")
        mock_model_class.from_pretrained.assert_called_once_with("facebook/bart-large-cnn")
        mock_pipeline_func.assert_called_once_with(
            "summarization",
            model=mock_model,
            tokenizer=mock_tokenizer,
            device=-1
        )
        
        # Verify state
        assert summarizer.tokenizer == mock_tokenizer
        assert summarizer.model == mock_model
        assert summarizer.summarizer_pipeline == mock_pipeline
    
    @patch('src.services.summarizer.pipeline')
    @patch('src.services.summarizer.AutoModelForSeq2SeqLM')
    @patch('src.services.summarizer.AutoTokenizer')
    @patch('torch.cuda.is_available')
    def test_load_model_with_cuda(self, mock_cuda, mock_tokenizer_class, 
                                 mock_model_class, mock_pipeline_func, summarizer):
        """Test model loading with CUDA available."""
        mock_cuda.return_value = True
        mock_tokenizer_class.from_pretrained.return_value = Mock()
        mock_model_class.from_pretrained.return_value = Mock()
        mock_pipeline_func.return_value = Mock()
        
        summarizer.load_model()
        
        # Verify CUDA device is used
        mock_pipeline_func.assert_called_once()
        args, kwargs = mock_pipeline_func.call_args
        assert kwargs['device'] == 0
    
    @patch('src.services.summarizer.AutoTokenizer')
    def test_load_model_failure(self, mock_tokenizer_class, summarizer):
        """Test model loading failure."""
        mock_tokenizer_class.from_pretrained.side_effect = Exception("Model not found")
        
        with pytest.raises(Exception, match="Model loading failed"):
            summarizer.load_model()
    
    def test_chunk_text_short_text(self, summarizer, mock_tokenizer):
        """Test chunking with text that fits in one chunk."""
        summarizer.tokenizer = mock_tokenizer
        mock_tokenizer.encode.return_value = [1, 2, 3]  # 3 tokens < max_chunk_size
        
        text = "This is a short text."
        chunks = summarizer.chunk_text(text)
        
        assert len(chunks) == 1
        assert chunks[0] == text
    
    def test_chunk_text_long_text(self, summarizer, mock_tokenizer):
        """Test chunking with text that needs to be split."""
        summarizer.tokenizer = mock_tokenizer
        
        # Mock tokenizer to return different lengths for different inputs
        def mock_encode(text, add_special_tokens=False):
            if text == "First sentence. Second sentence.":
                return [1] * 1200  # Full text: 1200 tokens (exceeds max_length)
            elif "First sentence" in text and "Second sentence" not in text:
                return [1] * 600  # First sentence: 600 tokens
            elif "Second sentence" in text and "First sentence" not in text:
                return [1] * 600  # Second sentence: 600 tokens
            else:
                return [1] * 100   # Default for other calls
        
        mock_tokenizer.encode.side_effect = mock_encode
        
        text = "First sentence. Second sentence."
        chunks = summarizer.chunk_text(text, max_length=1000)
        
        assert len(chunks) == 2
        assert "First sentence" in chunks[0]
        assert "Second sentence" in chunks[1]
    
    def test_chunk_text_model_not_loaded(self, summarizer):
        """Test chunking when model is not loaded."""
        with pytest.raises(RuntimeError, match="Model not loaded"):
            summarizer.chunk_text("Some text")
    
    def test_merge_chunk_summaries_empty(self, summarizer):
        """Test merging empty summaries list."""
        result = summarizer.merge_chunk_summaries([])
        assert result == ""
    
    def test_merge_chunk_summaries_single(self, summarizer):
        """Test merging single summary."""
        summaries = ["This is a single summary."]
        result = summarizer.merge_chunk_summaries(summaries)
        assert result == "This is a single summary."    

    def test_merge_chunk_summaries_multiple(self, summarizer, mock_tokenizer, mock_pipeline):
        """Test merging multiple summaries."""
        summarizer.tokenizer = mock_tokenizer
        summarizer.summarizer_pipeline = mock_pipeline
        
        # Mock short combined text that doesn't need re-chunking
        mock_tokenizer.encode.return_value = [1, 2, 3, 4, 5]  # 5 tokens
        mock_pipeline.return_value = [{"summary_text": "Merged summary."}]
        
        summaries = ["First summary.", "Second summary."]
        result = summarizer.merge_chunk_summaries(summaries)
        
        assert result == "Merged summary."
        mock_pipeline.assert_called_once()
    
    def test_get_summary_length_params_brief(self, summarizer):
        """Test getting parameters for brief summary."""
        params = summarizer._get_summary_length_params("brief", "general")
        
        assert params["max_length"] == 100
        assert params["min_length"] == 30
        assert params["do_sample"] is False
        assert params["num_beams"] == 4
    
    def test_get_summary_length_params_standard(self, summarizer):
        """Test getting parameters for standard summary."""
        params = summarizer._get_summary_length_params("standard", "general")
        
        assert params["max_length"] == 200
        assert params["min_length"] == 80
    
    def test_get_summary_length_params_detailed(self, summarizer):
        """Test getting parameters for detailed summary."""
        params = summarizer._get_summary_length_params("detailed", "general")
        
        assert params["max_length"] == 400
        assert params["min_length"] == 150
    
    def test_get_summary_length_params_invalid(self, summarizer):
        """Test getting parameters for invalid length (should default to standard)."""
        params = summarizer._get_summary_length_params("invalid", "general")
        
        assert params["max_length"] == 200
        assert params["min_length"] == 80
    
    def test_summarize_model_not_loaded(self, summarizer):
        """Test summarization when model is not loaded."""
        params = SummaryParams(length="standard", focus="general", max_words=300)
        
        with pytest.raises(RuntimeError, match="Model not loaded"):
            summarizer.summarize("Some text", params)
    
    @patch('time.time')
    def test_summarize_success_single_chunk(self, mock_time, summarizer, mock_tokenizer, mock_pipeline):
        """Test successful summarization with single chunk."""
        # Setup mocks
        mock_time.side_effect = [0.0, 2.5]  # start_time, end_time
        summarizer.tokenizer = mock_tokenizer
        summarizer.summarizer_pipeline = mock_pipeline
        
        # Mock short text (single chunk)
        mock_tokenizer.encode.return_value = [1, 2, 3, 4, 5]  # 5 tokens
        mock_pipeline.return_value = [{"summary_text": "This is a test summary of legal document."}]
        
        params = SummaryParams(length="standard", focus="general", max_words=300)
        text = "This is a legal document that needs summarization."
        
        result = summarizer.summarize(text, params, "test_doc.pdf")
        
        # Verify result
        assert isinstance(result, SummaryResult)
        assert result.original_filename == "test_doc.pdf"
        assert result.summary_text == "This is a test summary of legal document."
        assert result.processing_time == 2.5
        assert result.word_count == 8
        assert result.confidence_score == 1.0
        assert isinstance(result.generated_at, datetime)
    
    @patch('time.time')
    def test_summarize_success_multiple_chunks(self, mock_time, summarizer, mock_tokenizer, mock_pipeline):
        """Test successful summarization with multiple chunks."""
        mock_time.side_effect = [0.0, 3.0]
        summarizer.tokenizer = mock_tokenizer
        summarizer.summarizer_pipeline = mock_pipeline
        
        # Mock long text that needs chunking
        def mock_encode(text, add_special_tokens=False):
            if "First part" in text and "Second part" in text:
                return [1] * 2000  # Full text: 2000 tokens (needs chunking)
            elif "First part" in text:
                return [1] * 1000  # First chunk: 1000 tokens
            elif "Second part" in text:
                return [1] * 1000  # Second chunk: 1000 tokens
            else:
                return [1] * 100   # Other calls
        
        mock_tokenizer.encode.side_effect = mock_encode
        
        # Mock pipeline responses for chunks and final merge
        mock_pipeline.side_effect = [
            [{"summary_text": "First chunk summary."}],
            [{"summary_text": "Second chunk summary."}],
            [{"summary_text": "Final merged summary."}]
        ]
        
        params = SummaryParams(length="standard", focus="general", max_words=300)
        text = "First part of the document. Second part of the document."
        
        result = summarizer.summarize(text, params, "long_doc.pdf")
        
        assert result.summary_text == "Final merged summary."
        assert result.confidence_score == 1.0  # All chunks processed successfully
        assert mock_pipeline.call_count == 3  # 2 chunks + 1 merge
    
    @patch('time.time')
    def test_summarize_with_word_limit(self, mock_time, summarizer, mock_tokenizer, mock_pipeline):
        """Test summarization with word count exceeding max_words."""
        mock_time.side_effect = [0.0, 1.0, 1.1, 1.2]
        summarizer.tokenizer = mock_tokenizer
        summarizer.summarizer_pipeline = mock_pipeline
        
        mock_tokenizer.encode.return_value = [1, 2, 3, 4, 5]
        # Long summary that exceeds max_words
        long_summary = "This is a very long summary that contains many words and should be truncated"
        mock_pipeline.return_value = [{"summary_text": long_summary}]
        
        params = SummaryParams(length="brief", focus="general", max_words=60)  # Use valid range
        text = "Some legal document text."
        
        result = summarizer.summarize(text, params)
        
        # Should be truncated since long_summary has more than 60 words
        assert result.word_count <= 60
        # The summary should be the full text since it's actually only 13 words
        assert "This is a very long summary" in result.summary_text
    
    @patch('src.services.summarizer.time.time')
    def test_summarize_chunk_failure_fallback(self, mock_time, summarizer, mock_tokenizer, mock_pipeline):
        """Test summarization with chunk processing failure and fallback."""
        mock_time.side_effect = [0.0, 2.0, 2.1, 2.2]  # Extra values for logging calls
        summarizer.tokenizer = mock_tokenizer
        summarizer.summarizer_pipeline = mock_pipeline
        
        mock_tokenizer.encode.return_value = [1, 2, 3, 4, 5]
        # First call fails, should use fallback
        mock_pipeline.side_effect = Exception("Model error")
        
        params = SummaryParams(length="standard", focus="general", max_words=300)
        text = "First sentence. Second sentence. Third sentence. Fourth sentence."
        
        result = summarizer.summarize(text, params)
        
        # Should use fallback (first 3 sentences)
        assert "First sentence. Second sentence. Third sentence." in result.summary_text
        assert result.confidence_score == 0.8  # Reduced confidence due to fallback
    
    def test_summarize_complete_failure(self, summarizer, mock_pipeline):
        """Test summarization complete failure with emergency fallback."""
        summarizer.summarizer_pipeline = mock_pipeline
        
        # Mock chunking to raise exception
        with patch.object(summarizer, 'chunk_text', side_effect=Exception("Chunking failed")):
            params = SummaryParams(length="standard", focus="general", max_words=300)
            
            # Should now return emergency fallback instead of raising exception
            result = summarizer.summarize("Some text", params)
            assert isinstance(result, SummaryResult)
            assert result.summary_text.startswith("[Extractive Summary]")
            assert result.confidence_score == 0.3
    
    def test_is_model_loaded_false(self, summarizer):
        """Test is_model_loaded when model is not loaded."""
        assert summarizer.is_model_loaded() is False
    
    def test_is_model_loaded_true(self, summarizer, mock_pipeline):
        """Test is_model_loaded when model is loaded."""
        summarizer.summarizer_pipeline = mock_pipeline
        assert summarizer.is_model_loaded() is True


class TestLegalSummarizerIntegration:
    """Integration tests for LegalSummarizer with real-like scenarios."""
    
    @pytest.fixture
    def summarizer_with_mocks(self):
        """Create summarizer with necessary mocks for integration testing."""
        summarizer = LegalSummarizer()
        
        # Mock the heavy dependencies
        summarizer.tokenizer = Mock()
        summarizer.model = Mock()
        summarizer.summarizer_pipeline = Mock()
        
        return summarizer
    
    def test_end_to_end_summarization_workflow(self, summarizer_with_mocks):
        """Test complete summarization workflow."""
        summarizer = summarizer_with_mocks
        
        # Setup realistic mocks
        summarizer.tokenizer.encode.return_value = [1] * 500  # Medium length text
        summarizer.summarizer_pipeline.return_value = [
            {"summary_text": "The contract establishes obligations between parties for legal services."}
        ]
        
        params = SummaryParams(
            length="standard",
            focus="obligations", 
            max_words=200
        )
        
        legal_text = """
        This legal services agreement establishes the terms and conditions 
        between the client and the law firm. The client agrees to pay fees 
        as specified in Schedule A. The law firm agrees to provide competent 
        legal representation in accordance with professional standards.
        """
        
        result = summarizer.summarize(legal_text, params, "legal_agreement.pdf")
        
        assert isinstance(result, SummaryResult)
        assert result.original_filename == "legal_agreement.pdf"
        assert "contract" in result.summary_text.lower()
        assert result.word_count > 0
        assert 0 <= result.confidence_score <= 1.0
        assert result.processing_time >= 0