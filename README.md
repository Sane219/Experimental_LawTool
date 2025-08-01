# AI-Powered Legal Document Summarizer

A secure, intelligent web application that uses transformer models to automatically generate concise summaries of legal documents. Built with Streamlit and designed for legal professionals who need quick, accurate document analysis.

## 🚀 Features

### Core Functionality
- **Multi-format Support**: Upload PDF, DOCX, and TXT legal documents
- **AI-Powered Summarization**: Uses state-of-the-art transformer models (BART/T5)
- **Customizable Output**: Adjust summary length (brief, standard, detailed) and focus areas
- **Smart Processing**: Automatic text chunking for large documents
- **Export Options**: Download summaries as formatted PDF files

### Security & Privacy
- **Zero Persistence**: No document storage - all processing in memory
- **Automatic Cleanup**: Temporary files deleted immediately after processing
- **Secure Communication**: HTTPS support for all data transmission
- **Privacy First**: No logging or caching of sensitive document content

### User Experience
- **Intuitive Interface**: Clean, professional Streamlit web interface
- **Real-time Processing**: Live progress indicators and status updates
- **Error Handling**: Graceful error recovery with user-friendly messages
- **Copy to Clipboard**: Quick summary sharing functionality

## 📋 Requirements

- Python 3.8 or higher
- 4GB+ RAM recommended for large documents
- Modern web browser with JavaScript enabled

## 🛠️ Installation

### Quick Start
```bash
# Clone the repository
git clone <repository-url>
cd legal-document-summarizer

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

### Development Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov pytest-mock pytest-timeout

# Run tests
pytest tests/
```

## 🏗️ Project Structure

```
legal-document-summarizer/
├── 📁 src/                          # Source code
│   ├── 📁 models/                   # Data models and schemas
│   │   └── data_models.py           # Core data structures
│   ├── 📁 services/                 # Business logic services
│   │   ├── document_handler.py      # File upload and validation
│   │   ├── text_extractor.py        # PDF/DOCX text extraction
│   │   ├── summarizer.py            # AI summarization engine
│   │   ├── output_handler.py        # Export and formatting
│   │   └── security_service.py      # Security utilities
│   └── 📁 utils/                    # Utility functions
│       ├── config.py                # Configuration management
│       └── error_handler.py         # Error handling
├── 📁 tests/                        # Comprehensive test suite
│   ├── 📁 unit/                     # Unit tests (9 files)
│   ├── 📁 integration/              # Integration tests (10 files)
│   ├── 📁 performance/              # Performance tests (2 files)
│   ├── 📁 edge_cases/               # Edge case tests (2 files)
│   ├── 📁 security/                 # Security tests (1 file)
│   └── conftest.py                  # Shared test fixtures
├── 📁 scripts/                      # Utility scripts
│   ├── run_comprehensive_tests.py   # Test runner
│   ├── test_quality_analyzer.py     # Quality analysis
│   └── generate_test_docs.py        # Documentation generator
├── 📁 docs/                         # Documentation
│   ├── testing-guide.md             # Testing guidelines
│   └── 📁 tests/                    # Auto-generated test docs
├── 📁 .github/workflows/            # CI/CD pipeline
│   └── comprehensive-testing.yml    # GitHub Actions workflow
├── app.py                           # Main Streamlit application
├── run_secure.py                    # Secure application launcher
├── requirements.txt                 # Python dependencies
├── pytest.ini                      # Test configuration
└── SECURITY.md                      # Security guidelines
```

## 🧪 Testing

### Run All Tests
```bash
# Comprehensive test suite
python scripts/run_comprehensive_tests.py

# Quick tests (unit + integration)
python scripts/run_comprehensive_tests.py --quick

# Specific test categories
pytest tests/unit/          # Unit tests only
pytest tests/integration/   # Integration tests only
pytest tests/performance/   # Performance tests only
```

### Test Coverage
```bash
# Generate coverage report
pytest tests/ --cov=src --cov-report=html

# View coverage in browser
open htmlcov/index.html
```

### Quality Analysis
```bash
# Analyze test quality and coverage
python scripts/test_quality_analyzer.py

# Generate test documentation
python scripts/generate_test_docs.py
```

## 🚀 Usage

### Basic Usage
1. Start the application: `streamlit run app.py`
2. Open your browser to `http://localhost:8501`
3. Upload a legal document (PDF, DOCX, or TXT)
4. Select summary preferences (length and focus)
5. Click "Generate Summary"
6. Copy or download the generated summary

### Advanced Configuration
Create a `.env` file from `.env.example` to customize:
- Model selection and parameters
- File size limits
- Processing timeouts
- Security settings

### Secure Deployment
```bash
# Run with enhanced security
python run_secure.py

# Or with custom configuration
HTTPS_ENABLED=true MAX_FILE_SIZE=20MB python run_secure.py
```

## 🔒 Security

This application is designed with security-first principles for handling sensitive legal documents:

### Data Protection
- **No Persistent Storage**: Documents are processed entirely in memory
- **Automatic Cleanup**: All temporary files and data are immediately deleted
- **Session Isolation**: Each user session is completely isolated
- **Memory Management**: Efficient memory usage with automatic garbage collection

### Communication Security
- **HTTPS Support**: Encrypted communication for all data transmission
- **Input Validation**: Comprehensive validation of all user inputs
- **File Type Verification**: Strict file type checking and validation
- **Size Limits**: Configurable file size limits to prevent abuse

### Privacy Compliance
- **No Logging**: Document content is never logged or cached
- **No Analytics**: No tracking or analytics on document content
- **Local Processing**: All AI processing happens locally (no external API calls)
- **Audit Trail**: Security events are logged (without document content)

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes and add tests
4. Run the test suite: `python scripts/run_comprehensive_tests.py`
5. Commit your changes: `git commit -am 'Add your feature'`
6. Push to the branch: `git push origin feature/your-feature`
7. Submit a pull request

### Code Quality Standards
- **Test Coverage**: Minimum 85% overall, 95% for critical components
- **Documentation**: All functions and classes must have docstrings
- **Code Style**: Follow PEP 8 with black formatting
- **Type Hints**: Use type hints for all function signatures
- **Security**: Follow security guidelines in `SECURITY.md`

## 📊 Performance

### Benchmarks
- **Processing Speed**: < 30 seconds for documents up to 50 pages
- **Memory Usage**: < 2GB peak memory consumption
- **File Support**: Up to 10MB file size (configurable)
- **Concurrent Users**: Supports multiple simultaneous users

### Optimization Features
- **Smart Chunking**: Automatic text chunking for large documents
- **Model Caching**: Efficient model loading and caching
- **Memory Management**: Proactive memory cleanup and optimization
- **Progress Tracking**: Real-time processing progress indicators

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Documentation
- **Testing Guide**: `docs/testing-guide.md`
- **Security Guidelines**: `SECURITY.md`
- **API Documentation**: Auto-generated in `docs/tests/`

### Getting Help
- Check the documentation in the `docs/` directory
- Review existing issues and discussions
- Create a new issue with detailed information about your problem

### Troubleshooting
- **Memory Issues**: Reduce file size or increase available RAM
- **Processing Timeout**: Check document complexity and system resources
- **Import Errors**: Ensure all dependencies are installed correctly
- **Model Loading**: Verify internet connection for initial model download

---

**Built with ❤️ for legal professionals who value efficiency and security.**