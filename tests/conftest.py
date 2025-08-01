"""
Pytest configuration and shared fixtures for comprehensive testing.
Provides common test utilities, fixtures, and configuration for all test modules.
"""

import pytest
import tempfile
import os
import shutil
from unittest.mock import Mock, patch
from datetime import datetime
import io

from src.models.data_models import SummaryParams, SummaryResult, DocumentMetadata, ValidationResult
from src.services.document_handler import DocumentHandler
from src.services.text_extractor import TextExtractor
from src.services.summarizer import LegalSummarizer
from src.services.output_handler import OutputHandler
from src.services.security_service import get_security_service
from src.utils.error_handler import ErrorHandler
from src.utils.config import Config


# Test configuration
pytest_plugins = ["pytest_mock"]


@pytest.fixture(scope="session")
def test_config():
    """Test configuration settings."""
    return {
        'max_file_size': 1024 * 1024,  # 1MB for testing
        'supported_formats': ['.pdf', '.docx', '.txt'],
        'test_timeout': 30,
        'mock_processing_time': 2.5,
        'mock_confidence_score': 0.85
    }


@pytest.fixture(scope="session")
def temp_directory():
    """Create a temporary directory for test files."""
    temp_dir = tempfile.mkdtemp(prefix="legal_summarizer_test_")
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_legal_documents():
    """Comprehensive collection of sample legal documents for testing."""
    return {
        'simple_contract': """
            SIMPLE SERVICE AGREEMENT
            
            This agreement is between Company A and Company B.
            Services will be provided for 12 months.
            Payment is due within 30 days.
            """,
        
        'complex_contract': """
            COMPREHENSIVE SOFTWARE LICENSE AGREEMENT
            
            This Software License Agreement ("Agreement") is entered into on March 1, 2024,
            between TechCorp Inc., a Delaware corporation ("Licensor") and BusinessCorp LLC,
            a California limited liability company ("Licensee").
            
            RECITALS
            WHEREAS, Licensor has developed proprietary software technology;
            WHEREAS, Licensee desires to obtain a license to use such technology;
            
            NOW, THEREFORE, in consideration of the mutual covenants contained herein,
            the parties agree as follows:
            
            1. GRANT OF LICENSE
            Subject to the terms and conditions of this Agreement, Licensor hereby grants
            to Licensee a non-exclusive, non-transferable, revocable license to use the
            Software solely for Licensee's internal business purposes.
            
            2. OBLIGATIONS OF LICENSEE
            2.1 Licensee shall not reverse engineer, decompile, or disassemble the Software.
            2.2 Licensee shall not distribute, sublicense, or transfer the Software.
            2.3 Licensee shall pay all license fees within thirty (30) days of invoice.
            2.4 Licensee shall maintain the confidentiality of the Software.
            
            3. OBLIGATIONS OF LICENSOR
            3.1 Licensor shall provide technical support for twelve (12) months.
            3.2 Licensor shall deliver the Software within ten (10) business days.
            3.3 Licensor warrants that it has the right to grant this license.
            
            4. IMPORTANT DATES
            - Agreement Effective Date: March 1, 2024
            - Software Delivery Deadline: March 15, 2024
            - Support Period Ends: March 1, 2025
            - First Payment Due: March 31, 2024
            
            5. PARTIES
            Licensor: TechCorp Inc.
            Address: 123 Tech Street, Silicon Valley, CA 94000
            Representative: John Smith, Chief Executive Officer
            
            Licensee: BusinessCorp LLC
            Address: 456 Business Ave, Los Angeles, CA 90000
            Representative: Jane Doe, Chief Technology Officer
            
            6. GOVERNING LAW
            This Agreement shall be governed by and construed in accordance with the
            laws of the State of Delaware, without regard to its conflict of laws principles.
            
            IN WITNESS WHEREOF, the parties have executed this Agreement as of the date
            first written above.
            """,
        
        'lease_agreement': """
            COMMERCIAL LEASE AGREEMENT
            
            This Commercial Lease Agreement ("Lease") is made on February 15, 2024,
            between Property Holdings LLC ("Landlord") and Retail Store Inc. ("Tenant").
            
            1. PREMISES
            The leased premises consist of approximately 2,500 square feet of retail space
            located at 123 Main Street, Downtown City, State 12345 ("Premises").
            
            2. LEASE TERM
            The lease term shall be five (5) years, commencing on April 1, 2024,
            and expiring on March 31, 2029, unless sooner terminated.
            
            3. RENT
            Base monthly rent: $8,500.00, due on the first day of each month.
            Security deposit: $25,500.00 (three months' rent).
            
            4. PERMITTED USE
            The Premises may be used solely for retail clothing store operations.
            
            5. TENANT OBLIGATIONS
            5.1 Pay rent and additional charges when due
            5.2 Maintain the Premises in good condition
            5.3 Obtain and maintain required business licenses
            5.4 Carry commercial general liability insurance of at least $1,000,000
            
            6. LANDLORD OBLIGATIONS
            6.1 Provide quiet enjoyment of the Premises
            6.2 Maintain the structural integrity of the building
            6.3 Handle major repairs and maintenance of common areas
            
            7. IMPORTANT DATES
            - Lease Commencement: April 1, 2024
            - Lease Expiration: March 31, 2029
            - Rent Due Date: 1st of each month
            - Security Deposit Due: March 1, 2024
            """,
        
        'employment_agreement': """
            EMPLOYMENT AGREEMENT
            
            This Employment Agreement ("Agreement") is entered into on January 10, 2024,
            between Innovation Corp, a Delaware corporation ("Company") and Sarah Johnson
            ("Employee").
            
            1. POSITION AND DUTIES
            Employee is hired as Senior Software Engineer and shall perform duties including
            software development, code review, technical leadership, and mentoring.
            
            2. COMPENSATION
            2.1 Annual Base Salary: $120,000.00
            2.2 Performance Bonus: Up to 20% of annual salary based on performance metrics
            2.3 Stock Options: 5,000 shares vesting over four (4) years
            2.4 Benefits: Health, dental, vision insurance, 401(k) with company matching
            
            3. EMPLOYMENT TERMS
            3.1 Start Date: February 1, 2024
            3.2 Employment at-will
            3.3 Standard work week: 40 hours
            3.4 Flexible schedule permitted
            3.5 Remote work allowed up to three (3) days per week
            
            4. CONFIDENTIALITY
            Employee agrees to maintain strict confidentiality of all proprietary information,
            trade secrets, and confidential business information during and after employment.
            
            5. NON-COMPETE
            Employee agrees not to work for direct competitors for twelve (12) months
            after termination within a fifty (50) mile radius of Company's headquarters.
            
            6. TERMINATION
            Either party may terminate this Agreement with thirty (30) days written notice.
            Company may terminate immediately for cause.
            """
    }


@pytest.fixture
def mock_services():
    """Create mock services for testing."""
    return {
        'document_handler': Mock(spec=DocumentHandler),
        'text_extractor': Mock(spec=TextExtractor),
        'summarizer': Mock(spec=LegalSummarizer),
        'output_handler': Mock(spec=OutputHandler),
        'error_handler': Mock(spec=ErrorHandler),
        'security_service': Mock()
    }


@pytest.fixture
def sample_validation_result():
    """Sample validation result for testing."""
    return ValidationResult(
        is_valid=True,
        error_message=None,
        file_info=DocumentMetadata(
            filename="test_document.pdf",
            file_size=1024,
            file_type=".pdf",
            upload_timestamp=datetime.now()
        )
    )


@pytest.fixture
def sample_summary_result():
    """Sample summary result for testing."""
    return SummaryResult(
        original_filename="test_document.pdf",
        summary_text="This is a comprehensive test summary of a legal document containing key provisions and obligations.",
        processing_time=2.5,
        word_count=18,
        confidence_score=0.85,
        generated_at=datetime.now()
    )


@pytest.fixture
def sample_summary_params():
    """Sample summary parameters for testing."""
    return SummaryParams(
        length="standard",
        focus="general",
        max_words=300
    )


@pytest.fixture
def test_files(temp_directory):
    """Create test files for various scenarios."""
    files = {}
    
    # Create a simple text file
    text_file_path = os.path.join(temp_directory, "test.txt")
    with open(text_file_path, 'w', encoding='utf-8') as f:
        f.write("Simple legal document content for testing.")
    files['text'] = text_file_path
    
    # Create a large text file
    large_file_path = os.path.join(temp_directory, "large.txt")
    with open(large_file_path, 'w', encoding='utf-8') as f:
        content = "Large legal document content. " * 1000
        f.write(content)
    files['large'] = large_file_path
    
    # Create an empty file
    empty_file_path = os.path.join(temp_directory, "empty.txt")
    with open(empty_file_path, 'w', encoding='utf-8') as f:
        pass
    files['empty'] = empty_file_path
    
    # Create a binary file
    binary_file_path = os.path.join(temp_directory, "binary.bin")
    with open(binary_file_path, 'wb') as f:
        f.write(bytes(range(256)))
    files['binary'] = binary_file_path
    
    return files


@pytest.fixture
def corrupted_files(temp_directory):
    """Create corrupted files for edge case testing."""
    files = {}
    
    # Corrupted PDF
    corrupted_pdf_path = os.path.join(temp_directory, "corrupted.pdf")
    with open(corrupted_pdf_path, 'wb') as f:
        f.write(b"%PDF-1.4\nCorrupted content")
    files['pdf'] = corrupted_pdf_path
    
    # File with null bytes
    null_bytes_path = os.path.join(temp_directory, "null_bytes.txt")
    with open(null_bytes_path, 'wb') as f:
        f.write(b"Content with\x00null\x00bytes")
    files['null_bytes'] = null_bytes_path
    
    return files


@pytest.fixture
def performance_test_data():
    """Generate data for performance testing."""
    return {
        'small_doc': "Legal content " * 100,  # ~1KB
        'medium_doc': "Legal content " * 1000,  # ~10KB
        'large_doc': "Legal content " * 10000,  # ~100KB
        'xlarge_doc': "Legal content " * 50000  # ~500KB
    }


class TestUtilities:
    """Utility class for common test operations."""
    
    @staticmethod
    def create_mock_file(content: str, filename: str = "test.txt") -> io.BytesIO:
        """Create a mock file object for testing."""
        file_obj = io.BytesIO(content.encode('utf-8'))
        file_obj.name = filename
        return file_obj
    
    @staticmethod
    def create_mock_summary_result(filename: str, confidence: float = 0.85) -> SummaryResult:
        """Create a mock summary result for testing."""
        return SummaryResult(
            original_filename=filename,
            summary_text=f"Mock summary for {filename}",
            processing_time=2.5,
            word_count=10,
            confidence_score=confidence,
            generated_at=datetime.now()
        )
    
    @staticmethod
    def assert_summary_quality(summary_result: SummaryResult, min_confidence: float = 0.7):
        """Assert that a summary result meets quality standards."""
        assert summary_result is not None
        assert summary_result.confidence_score >= min_confidence
        assert summary_result.processing_time < 30.0  # Design requirement
        assert summary_result.word_count > 0
        assert len(summary_result.summary_text.strip()) > 0
    
    @staticmethod
    def assert_validation_result(validation_result: ValidationResult, should_be_valid: bool = True):
        """Assert that a validation result meets expectations."""
        assert validation_result is not None
        assert validation_result.is_valid == should_be_valid
        
        if should_be_valid:
            assert validation_result.file_info is not None
            assert validation_result.error_message is None
        else:
            assert validation_result.error_message is not None


@pytest.fixture
def test_utilities():
    """Provide test utilities for all tests."""
    return TestUtilities


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers and settings."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    )
    config.addinivalue_line(
        "markers", "security: marks tests as security tests"
    )
    config.addinivalue_line(
        "markers", "edge_case: marks tests as edge case tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test location."""
    for item in items:
        # Add markers based on test file location
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)
            item.add_marker(pytest.mark.slow)
        elif "security" in str(item.fspath):
            item.add_marker(pytest.mark.security)
        elif "edge_cases" in str(item.fspath):
            item.add_marker(pytest.mark.edge_case)


# Custom pytest fixtures for specific test scenarios
@pytest.fixture
def mock_ai_model():
    """Mock AI model for testing without actual model loading."""
    with patch('src.services.summarizer.LegalSummarizer.load_model') as mock_load:
        with patch('src.services.summarizer.LegalSummarizer.summarize') as mock_summarize:
            mock_load.return_value = True
            mock_summarize.return_value = SummaryResult(
                original_filename="mock_test.pdf",
                summary_text="Mock AI-generated summary for testing purposes.",
                processing_time=2.5,
                word_count=8,
                confidence_score=0.85,
                generated_at=datetime.now()
            )
            yield {
                'load_model': mock_load,
                'summarize': mock_summarize
            }


@pytest.fixture
def performance_monitor():
    """Monitor performance metrics during tests."""
    import psutil
    import time
    
    process = psutil.Process()
    start_time = time.time()
    start_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    yield {
        'start_time': start_time,
        'start_memory': start_memory,
        'process': process
    }
    
    end_time = time.time()
    end_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # Log performance metrics
    duration = end_time - start_time
    memory_delta = end_memory - start_memory
    
    print(f"\nPerformance Metrics:")
    print(f"  Duration: {duration:.2f}s")
    print(f"  Memory Delta: {memory_delta:.2f}MB")
    print(f"  Peak Memory: {end_memory:.2f}MB")