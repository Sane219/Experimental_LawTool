"""
Simplified Streamlit application for testing deployment.
This version has minimal dependencies to ensure it works on Streamlit Cloud.
"""

import streamlit as st
import sys
import os
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from typing import Optional

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Simple data models (inline for testing)
class ProcessingState(Enum):
    IDLE = "idle"
    UPLOADING = "uploading"
    EXTRACTING = "extracting_text"
    SUMMARIZING = "generating_summary"
    COMPLETE = "complete"
    ERROR = "error"

@dataclass
class SummaryParams:
    length: str = "standard"
    focus: str = "general"
    max_words: int = 300

def main():
    """Simple main application for testing."""
    st.set_page_config(
        page_title="Legal Document Summarizer",
        page_icon="⚖️",
        layout="wide"
    )
    
    st.title("⚖️ AI-Powered Legal Document Summarizer")
    st.markdown("**Status**: Testing deployment on Streamlit Cloud")
    
    # Test basic functionality
    st.subheader("📄 Upload Legal Document")
    
    uploaded_file = st.file_uploader(
        "Choose a legal document",
        type=['pdf', 'docx', 'txt'],
        help="Supported formats: PDF, DOCX, TXT. Maximum size: 10MB"
    )
    
    if uploaded_file is not None:
        st.success(f"File uploaded: {uploaded_file.name}")
        st.info("Full AI processing will be available once all modules are properly loaded.")
        
        # Show file details
        st.write(f"**Filename**: {uploaded_file.name}")
        st.write(f"**Size**: {uploaded_file.size / 1024:.1f} KB")
        st.write(f"**Type**: {uploaded_file.type}")
    
    # Test summary customization
    st.subheader("⚙️ Summary Customization")
    
    col1, col2 = st.columns(2)
    
    with col1:
        length = st.selectbox(
            "Summary Length",
            ["brief", "standard", "detailed"],
            index=1
        )
    
    with col2:
        focus = st.selectbox(
            "Summary Focus", 
            ["general", "obligations", "parties", "dates"],
            index=0
        )
    
    # Create summary params
    params = SummaryParams(length=length, focus=focus)
    
    st.write(f"**Selected Parameters**: {params.length} summary with {params.focus} focus")
    
    # Test import status
    st.subheader("🔧 System Status")
    
    try:
        from src.models.data_models import SummaryParams as ImportedSummaryParams
        st.success("✅ Data models imported successfully")
    except ImportError as e:
        st.error(f"❌ Data models import failed: {e}")
    
    try:
        from src.utils.config import Config
        st.success("✅ Configuration module imported successfully")
    except ImportError as e:
        st.error(f"❌ Configuration import failed: {e}")
    
    # Show Python path info
    with st.expander("🐍 Python Environment Info"):
        st.write("**Python Path:**")
        for i, path in enumerate(sys.path[:10]):  # Show first 10 paths
            st.write(f"{i+1}. {path}")
        
        st.write(f"**Current Directory**: {current_dir}")
        st.write(f"**Working Directory**: {os.getcwd()}")
    
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; color: #666; font-size: 0.8em;">
            🚀 Testing deployment on Streamlit Cloud<br>
            Full functionality will be available once all modules load properly.
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()