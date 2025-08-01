@echo off
REM GitHub Repository Setup Script for Windows
REM This script initializes Git, adds files, and pushes to GitHub

echo 🚀 Setting up GitHub repository for Legal Document Summarizer
echo ==================================================

REM Check if git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Git is not installed. Please install Git first.
    pause
    exit /b 1
)

REM Initialize Git repository if not already initialized
if not exist ".git" (
    echo 📁 Initializing Git repository...
    git init
) else (
    echo 📁 Git repository already exists
)

REM Configure Git user
echo 👤 Configuring Git user...
git config user.name "Sane219"
git config user.email "sanketchauhan0987@gmail.com"

REM Add remote origin
echo 🔗 Adding remote origin...
git remote remove origin 2>nul
git remote add origin https://github.com/Sane219/Experimental_LawTool.git

REM Add all files except those in .gitignore
echo 📦 Adding files to Git...
git add .

REM Check what files are being added
echo 📋 Files to be committed:
git status --porcelain

REM Create initial commit
echo 💾 Creating initial commit...
git commit -m "Initial commit: AI-Powered Legal Document Summarizer

✨ Features:
- Streamlit web application for legal document summarization
- AI-powered text summarization using transformer models
- Support for PDF, DOCX, and TXT files
- Secure processing with no persistent storage
- Comprehensive testing suite
- CI/CD pipeline with GitHub Actions
- Ready for Streamlit Cloud deployment

🛠️ Tech Stack:
- Python 3.8+
- Streamlit
- Transformers (Hugging Face)
- PyTorch
- PyPDF2/pdfplumber for document processing

🚀 Deployment:
- Configured for Streamlit Cloud
- GitHub Actions for CI/CD
- Comprehensive documentation"

REM Push to GitHub
echo 🚀 Pushing to GitHub...
git branch -M main
git push -u origin main

echo.
echo ✅ Repository setup complete!
echo 🌐 Repository URL: https://github.com/Sane219/Experimental_LawTool
echo.
echo 📋 Next steps:
echo 1. Go to https://share.streamlit.io
echo 2. Connect your GitHub account
echo 3. Create new app with repository: Sane219/Experimental_LawTool
echo 4. Set main file: app.py
echo 5. Deploy!
echo.
echo 📚 Documentation:
echo - README.md - Complete project documentation
echo - DEPLOYMENT.md - Streamlit deployment guide
echo - SECURITY.md - Security guidelines

pause