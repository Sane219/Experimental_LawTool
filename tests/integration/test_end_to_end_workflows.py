"""
End-to-end integration tests for complete document processing workflows.
Tests the entire application pipeline from file upload to summary export.
"""

import pytest
import io
import tempfile
import os
from unittest.mock import patch, MagicMock
from datetime import datetime

from src.models.data_models import SummaryParams, SummaryResult, ProcessingState
from src.services.document_handler import DocumentHandler
from src.services.text_extractor import TextExtractor
from src.services.summarizer import LegalSummarizer
from src.services.output_handler import OutputHandler
from src.services.security_service import get_security_service
from src.utils.error_handler import ErrorHandler
from src.utils.config import Config


class TestEndToEndWorkflows:
    """Test complete end-to-end document processing workflows."""
    
    @pytest.fixture
    def app_services(self):
        """Set up all application services for end-to-end testing."""
        return {
            'document_handler': DocumentHandler(),
            'text_extractor': TextExtractor(),
            'summarizer': LegalSummarizer(),
            'output_handler': OutputHandler(),
            'error_handler': ErrorHandler(),
            'security_service': get_security_service()
        }
    
    @pytest.fixture
    def sample_legal_documents(self):
        """Sample legal documents for comprehensive testing."""
        return {
            'contract': """
                SOFTWARE LICENSE AGREEMENT
                
                This Software License Agreement ("Agreement") is entered into on March 1, 2024,
                between TechCorp Inc. ("Licensor") and BusinessCorp LLC ("Licensee").
                
                GRANT OF LICENSE:
                Subject to the terms and conditions of this Agreement, Licensor hereby grants
                to Licensee a non-exclusive, non-transferable license to use the Software.
                
                OBLIGATIONS:
                1. Licensee shall not reverse engineer, decompile, or disassemble the Software
                2. Licensor shall provide technical support for 12 months from the effective date
                3. Licensee shall pay license fees within 30 days of invoice
                4. Licensor shall deliver the Software within 10 business days
                
                IMPORTANT DATES:
                - Agreement effective: March 1, 2024
                - Support period ends: March 1, 2025
                - Payment due: March 31, 2024
                
                PARTIES:
                Licensor: TechCorp Inc., represented by John Smith, CEO
                Licensee: BusinessCorp LLC, represented by Jane Doe, CTO
                
                This Agreement shall be governed by the laws of Delaware.
                """
        }
    
    def test_complete_pdf_processing_workflow(self, app_services, sample_legal_documents):
        """Test complete PDF processing from upload to export."""
        services = app_services
        
        # Create mock PDF file
        pdf_content = sample_legal_documents['contract'].encode('utf-8')
        pdf_file = io.BytesIO(pdf_content)
        
        with patch.object(services['text_extractor'], 'extract_from_pdf', 
                         return_value=sample_legal_documents['contract']):
            with patch.object(services['summarizer'], 'load_model'):
                with patch.object(services['summarizer'], 'summarize') as mock_summarize:
                    # Setup expected summary result
                    expected_summary = SummaryResult(
                        original_filename="software_license.pdf",
                        summary_text="Software License Agreement between TechCorp Inc. and BusinessCorp LLC granting non-exclusive license with support obligations and payment terms.",
                        processing_time=3.2,
                        word_count=28,
                        confidence_score=0.88,
                        generated_at=datetime.now()
                    )
                    mock_summarize.return_value = expected_summary
                    
                    # Step 1: File validation
                    validation_result = services['document_handler'].validate_file(
                        pdf_file, "software_license.pdf"
                    )
                    assert validation_result.is_valid
                    assert validation_result.file_info.file_type == '.pdf'
                    
                    # Step 2: Text extraction
                    extracted_text = services['text_extractor'].extract_from_pdf("dummy_path")
                    assert "SOFTWARE LICENSE AGREEMENT" in extracted_text
                    assert "TechCorp Inc." in extracted_text
                    
                    # Step 3: AI summarization
                    summary_params = SummaryParams(
                        length="standard",
                        focus="general",
                        max_words=300
                    )
                    
                    summary_result = servic
                       "
               )
                    
                    # S
e
                  8
                    assert "license"ower()
                    assert summary_res0
                    
                    # Step 5: Test export functionality
                    with patch.object(services['output_handler'], 'generate_pdf_export')ck_pdf:
                        mo
    
                        assert pdf_export
                        mock_pdf.assert_calsult)h(summary_re_once_witled