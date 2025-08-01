"""
Streamlit Cloud entry point for the AI-Powered Legal Document Summarizer.
This file ensures proper module loading in Streamlit Cloud environment.
"""

import sys
import os

# Ensure the current directory is in the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import and run the main application
from app import main

if __name__ == "__main__":
    main()