"""
Streamlit Cloud entry point for the AI-Powered Legal Document Summarizer.
This file ensures proper module loading in Streamlit Cloud environment.
"""

import sys
import os
import streamlit as st

# Enhanced path configuration for Streamlit Cloud
def setup_streamlit_environment():
    """Set up the environment for Streamlit Cloud deployment."""
    # Get current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Add multiple path strategies
    paths_to_add = [
        current_dir,
        os.path.dirname(current_dir),
        os.path.join(current_dir, 'src'),
        os.path.join(current_dir, '..'),
    ]
    
    for path in paths_to_add:
        if os.path.exists(path) and path not in sys.path:
            sys.path.insert(0, path)
    
    # Set environment variables
    os.environ['PYTHONPATH'] = ':'.join(sys.path)
    
    # Debug information (only show if there are issues)
    if 'debug_imports' in st.query_params:
        st.write("**Debug Information:**")
        st.write(f"Current Directory: {current_dir}")
        st.write(f"Python Path: {sys.path[:5]}...")  # Show first 5 paths
        st.write(f"Files in current dir: {os.listdir(current_dir)[:10]}...")

# Set up environment
setup_streamlit_environment()

try:
    # Import and run the main application
    from app import main
    
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    st.error(f"❌ **Streamlit App Import Error**: {e}")
    st.error("**Fallback**: Trying to load standalone version...")
    
    try:
        # Fallback to standalone app
        from standalone_app import main as standalone_main
        st.warning("⚠️ **Using Standalone Version**: Some advanced features may be limited.")
        standalone_main()
    except ImportError as e2:
        st.error(f"❌ **Standalone App Import Error**: {e2}")
        st.error("**Please use one of the following main files:**")
        st.write("1. `app.py` - Full featured version")
        st.write("2. `standalone_app.py` - Simplified but reliable version")
        st.write("3. `simple_app.py` - Basic testing version")
        st.stop()