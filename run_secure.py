#!/usr/bin/env python3
"""
Secure startup script for the Legal Document Summarizer.
Configures HTTPS and security settings before starting the application.
"""

import os
import sys
import subprocess
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.utils.https_config import HTTPSConfig, get_https_run_command
from src.utils.secure_logging import get_secure_logger


def main():
    """Main startup function with security configuration."""
    logger = get_secure_logger("startup")
    
    print("🔒 Legal Document Summarizer - Secure Startup")
    print("=" * 50)
    
    # Initialize HTTPS configuration
    https_config = HTTPSConfig()
    
    # Validate HTTPS setup
    print("🔍 Validating HTTPS configuration...")
    status = https_config.validate_https_setup()
    
    print(f"HTTPS Enabled: {'✅' if status['https_enabled'] else '❌'}")
    print(f"Certificate Valid: {'✅' if status['certificate_valid'] else '❌'}")
    print(f"SSL Context Available: {'✅' if status['ssl_context_available'] else '❌'}")
    
    if status['issues']:
        print("\n⚠️  Issues found:")
        for issue in status['issues']:
            print(f"  - {issue}")
    
    # Set security environment variables
    os.environ['STREAMLIT_SERVER_ENABLE_CORS'] = 'false'
    os.environ['STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION'] = 'true'
    os.environ['STREAMLIT_SERVER_MAX_UPLOAD_SIZE'] = '10'
    os.environ['STREAMLIT_SERVER_MAX_MESSAGE_SIZE'] = '200'
    
    # Get the secure run command
    run_command = get_https_run_command()
    
    print(f"\n🚀 Starting application with command:")
    print(f"   {run_command}")
    print("\n📝 Security features enabled:")
    print("   - HTTPS encryption")
    print("   - XSRF protection")
    print("   - CORS disabled")
    print("   - File size limits")
    print("   - Secure logging")
    print("   - In-memory processing")
    print("   - Automatic cleanup")
    
    # Log startup
    logger.log_security_event("application_startup", {
        "https_enabled": status['https_enabled'],
        "certificate_valid": status['certificate_valid'],
        "ssl_context_available": status['ssl_context_available']
    })
    
    print("\n" + "=" * 50)
    print("🌐 Application will be available at:")
    if status['https_enabled']:
        print("   https://localhost:8501")
        print("   https://127.0.0.1:8501")
    else:
        print("   http://localhost:8501 (WARNING: Not using HTTPS)")
        print("   http://127.0.0.1:8501 (WARNING: Not using HTTPS)")
    
    print("\n⚠️  IMPORTANT SECURITY NOTES:")
    print("   - Documents are processed in memory only")
    print("   - No persistent storage of document content")
    print("   - Temporary files are automatically cleaned up")
    print("   - Session data expires automatically")
    print("   - All communications should use HTTPS")
    print("\n" + "=" * 50)
    
    try:
        # Start the application
        subprocess.run(run_command.split(), check=True)
    except KeyboardInterrupt:
        print("\n\n🛑 Application stopped by user")
        logger.log_security_event("application_shutdown", {"reason": "user_interrupt"})
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Failed to start application: {e}")
        logger.log_error(e, {"operation": "application_startup"})
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        logger.log_error(e, {"operation": "application_startup"})
        sys.exit(1)
    finally:
        # Cleanup on exit
        print("\n🧹 Performing security cleanup...")
        try:
            from src.services.security_service import cleanup_on_exit
            cleanup_on_exit()
            https_config.cleanup_temp_certificates()
            print("✅ Cleanup completed")
        except Exception as e:
            print(f"⚠️  Cleanup warning: {e}")


if __name__ == "__main__":
    main()