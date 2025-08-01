"""
AI-powered legal document summarization service using transformer models.
"""

import logging
import time
from datetime import datetime
from typing import List, Optional
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from ..models.data_models import SummaryParams, SummaryResult


class LegalSummarizer:
    """
    AI summarization engine for legal documents using transformer models.
    
    This class handles model loading, text chunking for long documents,
    and summary generation with customizable parameters.
    """
    
    def __init__(self, model_name: str = "facebook/bart-large-cnn"):
        """
        Initialize the LegalSummarizer with specified model.
        
        Args:
            model_name: Hugging Face model identifier for summarization
        """
        self.model_name = model_name
        self.tokenizer: Optional[AutoTokenizer] = None
        self.model: Optional[AutoModelForSeq2SeqLM] = None
        self.summarizer_pipeline = None
        self.max_chunk_size = 1024  # Maximum tokens per chunk
        self.logger = logging.getLogger(__name__)
        
    def load_model(self) -> None:
        """
        Load and cache the transformer model and tokenizer.
        
        Raises:
            Exception: If model loading fails
        """
        try:
            self.logger.info(f"Loading model: {self.model_name}")
            
            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
            
            # Create summarization pipeline for easier inference
            self.summarizer_pipeline = pipeline(
                "summarization",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if torch.cuda.is_available() else -1
            )
            
            self.logger.info("Model loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load model {self.model_name}: {str(e)}")
            raise Exception(f"Model loading failed: {str(e)}")
    
    def chunk_text(self, text: str, max_length: int = None) -> List[str]:
        """
        Split long text into chunks that fit within model context limits.
        
        Args:
            text: Input text to chunk
            max_length: Maximum tokens per chunk (uses default if None)
            
        Returns:
            List of text chunks
        """
        if max_length is None:
            max_length = self.max_chunk_size
            
        if not self.tokenizer:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        # Tokenize the full text to get accurate token count
        tokens = self.tokenizer.encode(text, add_special_tokens=False)
        
        # If text fits in one chunk, return as-is
        if len(tokens) <= max_length:
            return [text]
        
        chunks = []
        sentences = text.split('. ')
        current_chunk = ""
        current_tokens = 0
        
        for sentence in sentences:
            sentence_tokens = self.tokenizer.encode(sentence, add_special_tokens=False)
            sentence_token_count = len(sentence_tokens)
            
            # If adding this sentence would exceed limit, save current chunk
            if current_tokens + sentence_token_count > max_length and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
                current_tokens = sentence_token_count
            else:
                current_chunk += sentence + ". "
                current_tokens += sentence_token_count
        
        # Add the last chunk if it has content
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks    

    def merge_chunk_summaries(self, summaries: List[str]) -> str:
        """
        Merge summaries from multiple chunks into a coherent final summary.
        
        Args:
            summaries: List of individual chunk summaries
            
        Returns:
            Merged final summary
        """
        if not summaries:
            return ""
        
        if len(summaries) == 1:
            return summaries[0]
        
        # Combine all summaries and summarize again for coherence
        combined_text = " ".join(summaries)
        
        # If combined text is still too long, chunk it again
        if len(self.tokenizer.encode(combined_text)) > self.max_chunk_size:
            chunks = self.chunk_text(combined_text, self.max_chunk_size // 2)
            chunk_summaries = []
            
            for chunk in chunks:
                try:
                    result = self.summarizer_pipeline(
                        chunk,
                        max_length=150,
                        min_length=50,
                        do_sample=False
                    )
                    chunk_summaries.append(result[0]['summary_text'])
                except Exception as e:
                    self.logger.warning(f"Failed to summarize chunk during merge: {str(e)}")
                    chunk_summaries.append(chunk[:200] + "...")
            
            return " ".join(chunk_summaries)
        else:
            # Summarize the combined text directly
            try:
                result = self.summarizer_pipeline(
                    combined_text,
                    max_length=200,
                    min_length=100,
                    do_sample=False
                )
                return result[0]['summary_text']
            except Exception as e:
                self.logger.warning(f"Failed to merge summaries: {str(e)}")
                return " ".join(summaries)
    
    def _get_summary_length_params(self, length: str, focus: str) -> dict:
        """
        Get model parameters based on summary length and focus preferences.
        
        Args:
            length: Summary length preference ("brief", "standard", "detailed")
            focus: Summary focus area ("general", "obligations", "parties", "dates")
            
        Returns:
            Dictionary of model parameters
        """
        # Base parameters for different lengths
        length_params = {
            "brief": {"max_length": 100, "min_length": 30},
            "standard": {"max_length": 200, "min_length": 80},
            "detailed": {"max_length": 400, "min_length": 150}
        }
        
        params = length_params.get(length, length_params["standard"])
        
        # Adjust parameters based on focus area
        focus_adjustments = self._get_focus_adjustments(focus)
        params.update(focus_adjustments)
        
        # Base model parameters
        params.update({
            "do_sample": False,
            "num_beams": 4,
            "early_stopping": True
        })
        
        return params
    
    def _get_focus_adjustments(self, focus: str) -> dict:
        """
        Get focus-specific adjustments for summarization parameters.
        
        Args:
            focus: Summary focus area ("general", "obligations", "parties", "dates")
            
        Returns:
            Dictionary of focus-specific parameter adjustments
        """
        focus_configs = {
            "general": {
                "length_penalty": 1.0,
                "repetition_penalty": 1.1
            },
            "obligations": {
                "length_penalty": 1.2,  # Encourage longer, more detailed summaries for obligations
                "repetition_penalty": 1.0,
                "no_repeat_ngram_size": 2
            },
            "parties": {
                "length_penalty": 0.8,  # Shorter summaries focusing on key parties
                "repetition_penalty": 1.2,
                "no_repeat_ngram_size": 3
            },
            "dates": {
                "length_penalty": 0.9,  # Concise summaries focusing on dates and deadlines
                "repetition_penalty": 1.1,
                "no_repeat_ngram_size": 2
            }
        }
        
        return focus_configs.get(focus, focus_configs["general"])
    
    def _create_focus_prompt(self, text: str, focus: str) -> str:
        """
        Create a focus-specific prompt to guide the summarization.
        
        Args:
            text: Original text to summarize
            focus: Summary focus area
            
        Returns:
            Text with focus-specific prompt prepended
        """
        focus_prompts = {
            "general": "Summarize the following legal document, highlighting the main points and key information:",
            "obligations": "Summarize the following legal document, focusing specifically on obligations, duties, responsibilities, and requirements of each party:",
            "parties": "Summarize the following legal document, focusing specifically on the parties involved, their roles, and relationships:",
            "dates": "Summarize the following legal document, focusing specifically on important dates, deadlines, time periods, and temporal requirements:"
        }
        
        prompt = focus_prompts.get(focus, focus_prompts["general"])
        return f"{prompt}\n\n{text}"
    
    def _apply_focus_specific_processing(self, text: str, focus: str) -> str:
        """
        Apply focus-specific text preprocessing to emphasize relevant content.
        
        Args:
            text: Input text to process
            focus: Summary focus area
            
        Returns:
            Processed text with focus-specific emphasis
        """
        if focus == "obligations":
            # Emphasize obligation-related keywords
            obligation_keywords = [
                "shall", "must", "required", "obligation", "duty", "responsible",
                "liable", "covenant", "undertake", "agree to", "commit to"
            ]
            processed_text = self._emphasize_keywords(text, obligation_keywords)
            
        elif focus == "parties":
            # Emphasize party-related information
            party_keywords = [
                "party", "parties", "client", "contractor", "vendor", "supplier",
                "buyer", "seller", "lessor", "lessee", "licensor", "licensee",
                "plaintiff", "defendant", "company", "corporation", "individual"
            ]
            processed_text = self._emphasize_keywords(text, party_keywords)
            
        elif focus == "dates":
            # Emphasize date and time-related information
            date_keywords = [
                "date", "deadline", "due", "expire", "expires", "term", "period", "duration",
                "commence", "terminate", "effective", "within", "by", "before", "after"
            ]
            processed_text = self._emphasize_keywords(text, date_keywords)
            
        else:
            # General processing - no specific emphasis
            processed_text = text
            
        return processed_text
    
    def _emphasize_keywords(self, text: str, keywords: list) -> str:
        """
        Emphasize specific keywords in text by adding context markers.
        
        Args:
            text: Input text
            keywords: List of keywords to emphasize
            
        Returns:
            Text with emphasized keywords
        """
        import re
        
        processed_text = text
        for keyword in keywords:
            # Use word boundaries to match whole words only
            pattern = r'\b' + re.escape(keyword) + r'\b'
            # Add emphasis markers around the matched word (preserving original case)
            def replacement_func(match):
                return f"**{match.group()}**"
            processed_text = re.sub(pattern, replacement_func, processed_text, flags=re.IGNORECASE)
        
        return processed_text
    
    def summarize(self, text: str, params: SummaryParams, original_filename: str = "") -> SummaryResult:
        """
        Generate a summary of the input text with customizable parameters.
        
        Args:
            text: Input text to summarize
            params: Summary customization parameters
            original_filename: Name of the original document
            
        Returns:
            SummaryResult containing the generated summary and metadata
            
        Raises:
            RuntimeError: If model is not loaded
            Exception: If summarization fails
        """
        if not self.summarizer_pipeline:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        # Validate and sanitize parameters
        validated_params = self.validate_and_sanitize_params(params)
        
        start_time = time.time()
        fallback_used = False
        
        try:
            # Apply focus-specific text preprocessing
            processed_text = self._apply_focus_specific_processing(text, validated_params.focus)
            
            # Get model parameters based on user preferences
            model_params = self._get_summary_length_params(validated_params.length, validated_params.focus)
            
            # Handle long documents by chunking
            chunks = self.chunk_text(processed_text)
            self.logger.info(f"Processing {len(chunks)} chunks for summarization with focus: {validated_params.focus}")
            
            chunk_summaries = []
            
            for i, chunk in enumerate(chunks):
                try:
                    self.logger.debug(f"Summarizing chunk {i+1}/{len(chunks)} with {validated_params.length} length")
                    
                    # Create focus-specific prompt for this chunk
                    prompted_chunk = self._create_focus_prompt(chunk, validated_params.focus)
                    
                    # Generate summary for this chunk with custom parameters
                    result = self.summarizer_pipeline(
                        prompted_chunk,
                        **model_params
                    )
                    
                    chunk_summaries.append(result[0]['summary_text'])
                    
                except Exception as e:
                    self.logger.warning(f"Failed to summarize chunk {i+1} with custom parameters: {str(e)}")
                    
                    # First fallback: try with default parameters
                    try:
                        default_params = self._get_default_fallback_params()
                        result = self.summarizer_pipeline(
                            chunk,
                            **default_params
                        )
                        chunk_summaries.append(result[0]['summary_text'])
                        fallback_used = True
                        self.logger.info(f"Successfully used fallback parameters for chunk {i+1}")
                        
                    except Exception as fallback_error:
                        self.logger.warning(f"Fallback also failed for chunk {i+1}: {str(fallback_error)}")
                        # Final fallback: use extractive summary (first few sentences)
                        sentences = chunk.split('. ')[:3]
                        fallback_summary = '. '.join(sentences) + '.'
                        chunk_summaries.append(fallback_summary)
                        fallback_used = True
            
            # Merge chunk summaries into final summary
            if len(chunk_summaries) > 1:
                final_summary = self.merge_chunk_summaries(chunk_summaries)
            else:
                final_summary = chunk_summaries[0] if chunk_summaries else "Unable to generate summary."
            
            # Post-process summary based on focus
            final_summary = self._post_process_summary(final_summary, validated_params.focus)
            
            # Calculate processing time and metadata
            processing_time = time.time() - start_time
            word_count = len(final_summary.split())
            
            # Adjust confidence score based on fallback usage and successful processing
            base_confidence = len(chunk_summaries) / len(chunks) if chunks else 0
            confidence_score = min(1.0, base_confidence * (0.8 if fallback_used else 1.0))
            
            # Ensure summary doesn't exceed max_words parameter
            if word_count > validated_params.max_words:
                words = final_summary.split()
                final_summary = ' '.join(words[:validated_params.max_words]) + '...'
                word_count = validated_params.max_words
            
            return SummaryResult(
                original_filename=original_filename,
                summary_text=final_summary,
                processing_time=processing_time,
                word_count=word_count,
                confidence_score=confidence_score,
                generated_at=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Summarization failed: {str(e)}")
            # Ultimate fallback: return a basic extractive summary
            if fallback_used:
                raise Exception(f"Failed to generate summary: {str(e)}")
            else:
                return self._create_emergency_fallback_summary(text, validated_params, original_filename, start_time)
    
    def _get_default_fallback_params(self) -> dict:
        """
        Get safe default parameters for fallback summarization.
        
        Returns:
            Dictionary of safe default parameters
        """
        return {
            "max_length": 150,
            "min_length": 50,
            "do_sample": False,
            "num_beams": 2,  # Reduced for stability
            "early_stopping": True,
            "length_penalty": 1.0,
            "repetition_penalty": 1.1
        }
    
    def _post_process_summary(self, summary: str, focus: str) -> str:
        """
        Apply focus-specific post-processing to the generated summary.
        
        Args:
            summary: Generated summary text
            focus: Summary focus area
            
        Returns:
            Post-processed summary
        """
        # Remove emphasis markers added during preprocessing
        import re
        cleaned_summary = re.sub(r'\*\*(.*?)\*\*', r'\1', summary)
        
        # Add focus-specific formatting or structure
        if focus == "obligations":
            # Ensure obligations are clearly structured
            if "obligation" in cleaned_summary.lower() or "shall" in cleaned_summary.lower():
                cleaned_summary = f"Key Obligations: {cleaned_summary}"
                
        elif focus == "parties":
            # Ensure parties are clearly identified
            if any(word in cleaned_summary.lower() for word in ["party", "parties", "client", "contractor"]):
                cleaned_summary = f"Parties Involved: {cleaned_summary}"
                
        elif focus == "dates":
            # Ensure dates and deadlines are highlighted
            if any(word in cleaned_summary.lower() for word in ["date", "deadline", "due", "term"]):
                cleaned_summary = f"Important Dates: {cleaned_summary}"
        
        return cleaned_summary
    
    def _create_emergency_fallback_summary(self, text: str, params: SummaryParams, 
                                         original_filename: str, start_time: float) -> SummaryResult:
        """
        Create an emergency fallback summary when all AI methods fail.
        
        Args:
            text: Original text
            params: Summary parameters
            original_filename: Original filename
            start_time: Processing start time
            
        Returns:
            Basic extractive summary result
        """
        self.logger.warning("Using emergency fallback - creating extractive summary")
        
        # Simple extractive summary: take first few sentences
        sentences = text.split('. ')
        
        # Determine number of sentences based on length preference
        sentence_counts = {
            "brief": 2,
            "standard": 4,
            "detailed": 6
        }
        
        num_sentences = sentence_counts.get(params.length, 4)
        selected_sentences = sentences[:num_sentences]
        
        fallback_summary = '. '.join(selected_sentences)
        if not fallback_summary.endswith('.'):
            fallback_summary += '.'
        
        # Apply word limit
        words = fallback_summary.split()
        if len(words) > params.max_words:
            fallback_summary = ' '.join(words[:params.max_words]) + '...'
        
        processing_time = time.time() - start_time
        
        return SummaryResult(
            original_filename=original_filename,
            summary_text=f"[Extractive Summary] {fallback_summary}",
            processing_time=processing_time,
            word_count=len(fallback_summary.split()),
            confidence_score=0.3,  # Low confidence for extractive summary
            generated_at=datetime.now()
        )
    
    def validate_and_sanitize_params(self, params: SummaryParams) -> SummaryParams:
        """
        Validate and sanitize summary parameters, applying defaults for invalid values.
        
        Args:
            params: Input summary parameters
            
        Returns:
            Validated and sanitized parameters
        """
        # Valid options
        valid_lengths = ["brief", "standard", "detailed"]
        valid_focuses = ["general", "obligations", "parties", "dates"]
        
        # Sanitize length
        sanitized_length = params.length if params.length in valid_lengths else "standard"
        if sanitized_length != params.length:
            self.logger.warning(f"Invalid length '{params.length}', using 'standard'")
        
        # Sanitize focus
        sanitized_focus = params.focus if params.focus in valid_focuses else "general"
        if sanitized_focus != params.focus:
            self.logger.warning(f"Invalid focus '{params.focus}', using 'general'")
        
        # Sanitize max_words (ensure it's reasonable)
        min_words, max_words = 50, 1000
        sanitized_max_words = max(min_words, min(params.max_words, max_words))
        if sanitized_max_words != params.max_words:
            self.logger.warning(f"Max words {params.max_words} out of range, using {sanitized_max_words}")
        
        return SummaryParams(
            length=sanitized_length,
            focus=sanitized_focus,
            max_words=sanitized_max_words
        )
    
    def get_available_customization_options(self) -> dict:
        """
        Get available customization options for the summarizer.
        
        Returns:
            Dictionary containing available options for each parameter
        """
        return {
            "lengths": {
                "brief": "Short summary (50-100 words)",
                "standard": "Standard summary (100-200 words)", 
                "detailed": "Detailed summary (200-400 words)"
            },
            "focuses": {
                "general": "General overview of the document",
                "obligations": "Focus on duties, responsibilities, and requirements",
                "parties": "Focus on parties involved and their roles",
                "dates": "Focus on important dates, deadlines, and time periods"
            },
            "word_limits": {
                "min": 50,
                "max": 1000,
                "default": 300
            }
        }
    
    def is_model_loaded(self) -> bool:
        """
        Check if the model is loaded and ready for inference.
        
        Returns:
            True if model is loaded, False otherwise
        """
        return self.summarizer_pipeline is not None