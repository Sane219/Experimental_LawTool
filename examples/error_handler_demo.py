"""
Demo script showing how to use the ErrorHandler in the Legal Document Summarizer.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.error_handler import ErrorHandler, ErrorSeverity
from datetime import datetime


def demo_error_handling():
    """Demonstrate various error handling scenarios."""
    
    print("=== Legal Document Summarizer - Error Handler Demo ===\n")
    
    # Initialize error handler
    error_handler = ErrorHandler("demo_logger")
    
    # Demo 1: File upload error
    print("1. File Upload Error Demo:")
    upload_error = Exception("File size exceeds 10MB limit")
    upload_result = error_handler.handle_upload_error(
        upload_error, 
        {"filename": "large_contract.pdf", "size": 15000000}
    )
    
    print(f"   Title: {upload_result.title}")
    print(f"   Message: {upload_result.message}")
    print(f"   Severity: {upload_result.severity.value}")
    print(f"   Show Retry: {upload_result.show_retry}")
    print(f"   Suggested Actions:")
    for action in upload_result.suggested_actions:
        print(f"     - {action}")
    print()
    
    # Demo 2: Text extraction error
    print("2. Text Extraction Error Demo:")
    extraction_error = Exception("No text found in document")
    extraction_result = error_handler.handle_extraction_error(
        extraction_error,
        {"filename": "scanned_document.pdf"}
    )
    
    print(f"   Title: {extraction_result.title}")
    print(f"   Message: {extraction_result.message}")
    print(f"   Severity: {extraction_result.severity.value}")
    print(f"   Show Retry: {extraction_result.show_retry}")
    print()
    
    # Demo 3: AI Model error
    print("3. AI Model Error Demo:")
    model_error = Exception("Model service unavailable")
    model_result = error_handler.handle_model_error(
        model_error,
        {"document_length": 25000}
    )
    
    print(f"   Title: {model_result.title}")
    print(f"   Message: {model_result.message}")
    print(f"   Severity: {model_result.severity.value}")
    print(f"   Show Contact Support: {model_result.show_contact_support}")
    print()
    
    # Demo 4: Retry mechanism
    print("4. Retry Mechanism Demo:")
    
    def unreliable_operation():
        """Simulate an operation that fails sometimes."""
        import random
        if random.random() < 0.7:  # 70% chance of failure
            raise Exception("Temporary service unavailable")
        return "Operation completed successfully"
    
    try:
        result = error_handler.with_retry(unreliable_operation, "demo_operation")
        print(f"   Success: {result}")
    except Exception as e:
        print(f"   Failed after retries: {e}")
    
    # Demo 5: Error statistics
    print("\n5. Error Statistics Demo:")
    stats = error_handler.get_error_statistics()
    print(f"   Current retry counts: {stats['retry_counts']}")
    print(f"   Timestamp: {stats['timestamp']}")
    
    print("\n=== Demo Complete ===")


def demo_streamlit_integration():
    """Show how error handler would integrate with Streamlit UI."""
    
    print("\n=== Streamlit Integration Example ===\n")
    
    error_handler = ErrorHandler("streamlit_app")
    
    # Simulate a user uploading a file that's too large
    def handle_file_upload_error():
        try:
            # Simulate file upload validation
            raise Exception("File size exceeds limit")
        except Exception as e:
            user_message = error_handler.handle_upload_error(e, {"filename": "contract.pdf"})
            
            # In Streamlit, you would display this to the user
            print("Streamlit Error Display:")
            print(f"st.error('{user_message.title}')")
            print(f"st.write('{user_message.message}')")
            
            if user_message.show_retry:
                print("st.button('Try Again')")
            
            if user_message.suggested_actions:
                print("st.write('Suggestions:')")
                for action in user_message.suggested_actions:
                    print(f"st.write('• {action}')")
    
    handle_file_upload_error()
    
    print("\n=== Streamlit Integration Demo Complete ===")


if __name__ == "__main__":
    demo_error_handling()
    demo_streamlit_integration()