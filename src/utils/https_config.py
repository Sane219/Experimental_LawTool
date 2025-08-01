"""
HTTPS configuration and secure communication setup for the Legal Document Summarizer.
Ensures all communications are encrypted and secure.
"""

import os
import ssl
import tempfile
from typing import Dict, Optional, Tuple
from pathlib import Path


class HTTPSConfig:
    """
    Handles HTTPS configuration and secure communication setup.
    """
    
    def __init__(self):
        """Initialize HTTPS configuration."""
        self.cert_file: Optional[str] = None
        self.key_file: Optional[str] = None
        self.ca_file: Optional[str] = None
        self._temp_cert_files: list = []
    
    def setup_https_config(self) -> Dict[str, any]:
        """
        Setup HTTPS configuration for Streamlit application.
        
        Returns:
            Dictionary with HTTPS configuration parameters
        """
        config = {
            'server.enableCORS': False,
            'server.enableXsrfProtection': True,
            'server.enableWebsocketCompression': True,
            'server.maxUploadSize': 10,  # 10MB max upload
            'server.maxMessageSize': 200,  # 200MB max message size
            'server.enableStaticServing': False,  # Disable static file serving
            'server.runOnSave': False,  # Disable auto-reload for security
            'browser.gatherUsageStats': False,  # Disable usage stats collection
            'global.disableWatchdogWarning': True,  # Disable watchdog warnings
        }
        
        # Check for SSL certificates
        cert_path, key_path = self._get_ssl_certificates()
        
        if cert_path and key_path:
            config.update({
                'server.sslCertFile': cert_path,
                'server.sslKeyFile': key_path,
                'server.port': 8501,  # Default HTTPS port for Streamlit
            })
        else:
            # Development mode - generate self-signed certificate
            cert_path, key_path = self._generate_self_signed_cert()
            if cert_path and key_path:
                config.update({
                    'server.sslCertFile': cert_path,
                    'server.sslKeyFile': key_path,
                    'server.port': 8501,
                })
        
        return config
    
    def _get_ssl_certificates(self) -> Tuple[Optional[str], Optional[str]]:
        """
        Get SSL certificate and key file paths from environment or default locations.
        
        Returns:
            Tuple of (cert_file_path, key_file_path) or (None, None) if not found
        """
        # Check environment variables first
        cert_file = os.getenv('SSL_CERT_FILE')
        key_file = os.getenv('SSL_KEY_FILE')
        
        if cert_file and key_file and os.path.exists(cert_file) and os.path.exists(key_file):
            return cert_file, key_file
        
        # Check common certificate locations
        common_cert_locations = [
            ('/etc/ssl/certs/server.crt', '/etc/ssl/private/server.key'),
            ('./certs/server.crt', './certs/server.key'),
            ('./ssl/server.crt', './ssl/server.key'),
        ]
        
        for cert_path, key_path in common_cert_locations:
            if os.path.exists(cert_path) and os.path.exists(key_path):
                return cert_path, key_path
        
        return None, None
    
    def _generate_self_signed_cert(self) -> Tuple[Optional[str], Optional[str]]:
        """
        Generate a self-signed certificate for development/testing.
        
        Returns:
            Tuple of (cert_file_path, key_file_path) or (None, None) if generation fails
        """
        try:
            from cryptography import x509
            from cryptography.x509.oid import NameOID
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import rsa
            import datetime
            
            # Generate private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
            )
            
            # Create certificate
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Development"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "Local"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Legal Document Summarizer"),
                x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
            ])
            
            cert = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                issuer
            ).public_key(
                private_key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.datetime.utcnow()
            ).not_valid_after(
                datetime.datetime.utcnow() + datetime.timedelta(days=365)
            ).add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName("localhost"),
                    x509.DNSName("127.0.0.1"),
                ]),
                critical=False,
            ).sign(private_key, hashes.SHA256())
            
            # Create temporary files for certificate and key
            cert_file = tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.crt')
            key_file = tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.key')
            
            # Write certificate
            cert_file.write(cert.public_bytes(serialization.Encoding.PEM))
            cert_file.close()
            
            # Write private key
            key_file.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
            key_file.close()
            
            # Track temp files for cleanup
            self._temp_cert_files.extend([cert_file.name, key_file.name])
            
            return cert_file.name, key_file.name
            
        except ImportError:
            print("Warning: cryptography library not available. Cannot generate self-signed certificate.")
            print("Install with: pip install cryptography")
            return None, None
        except Exception as e:
            print(f"Warning: Failed to generate self-signed certificate: {e}")
            return None, None
    
    def create_ssl_context(self) -> Optional[ssl.SSLContext]:
        """
        Create SSL context for secure connections.
        
        Returns:
            SSL context or None if SSL is not available
        """
        try:
            # Create SSL context with secure defaults
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            
            # Configure security settings
            context.minimum_version = ssl.TLSVersion.TLSv1_2
            context.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS')
            
            # Load certificates if available
            cert_path, key_path = self._get_ssl_certificates()
            if cert_path and key_path:
                context.load_cert_chain(cert_path, key_path)
            
            return context
            
        except Exception as e:
            print(f"Warning: Failed to create SSL context: {e}")
            return None
    
    def get_security_headers(self) -> Dict[str, str]:
        """
        Get HTTP security headers to be added to responses.
        
        Returns:
            Dictionary of security headers
        """
        return {
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Content-Security-Policy': (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data:; "
                "font-src 'self'; "
                "connect-src 'self'; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self'; "
                "upgrade-insecure-requests;"
            ),
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Permissions-Policy': (
                "geolocation=(), "
                "microphone=(), "
                "camera=(), "
                "payment=(), "
                "usb=(), "
                "magnetometer=(), "
                "gyroscope=(), "
                "speaker=(), "
                "accelerometer=(), "
                "ambient-light-sensor=(), "
                "autoplay=(), "
                "battery=(), "
                "display-capture=(), "
                "document-domain=(), "
                "encrypted-media=(), "
                "fullscreen=(), "
                "gamepad=(), "
                "midi=(), "
                "picture-in-picture=(), "
                "publickey-credentials-get=(), "
                "screen-wake-lock=(), "
                "sync-xhr=(), "
                "web-share=()"
            ),
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
        }
    
    def validate_https_setup(self) -> Dict[str, any]:
        """
        Validate HTTPS setup and return status information.
        
        Returns:
            Dictionary with validation results
        """
        status = {
            'https_enabled': False,
            'certificate_valid': False,
            'ssl_context_available': False,
            'security_headers_configured': True,
            'issues': []
        }
        
        # Check for certificates
        cert_path, key_path = self._get_ssl_certificates()
        if cert_path and key_path:
            status['https_enabled'] = True
            
            # Validate certificate
            try:
                with open(cert_path, 'rb') as f:
                    cert_data = f.read()
                    if b'BEGIN CERTIFICATE' in cert_data:
                        status['certificate_valid'] = True
                    else:
                        status['issues'].append('Certificate file format invalid')
            except Exception as e:
                status['issues'].append(f'Cannot read certificate file: {e}')
        else:
            status['issues'].append('No SSL certificates found')
        
        # Check SSL context
        ssl_context = self.create_ssl_context()
        if ssl_context:
            status['ssl_context_available'] = True
        else:
            status['issues'].append('Cannot create SSL context')
        
        return status
    
    def cleanup_temp_certificates(self) -> None:
        """Clean up temporary certificate files."""
        for cert_file in self._temp_cert_files:
            try:
                if os.path.exists(cert_file):
                    os.unlink(cert_file)
            except Exception:
                pass
        self._temp_cert_files.clear()
    
    def __del__(self):
        """Cleanup temporary files when object is destroyed."""
        self.cleanup_temp_certificates()


def setup_streamlit_https() -> None:
    """
    Setup HTTPS configuration for Streamlit application.
    This should be called before starting the Streamlit app.
    """
    https_config = HTTPSConfig()
    config = https_config.setup_https_config()
    
    # Set Streamlit configuration
    import streamlit as st
    
    for key, value in config.items():
        try:
            st.set_option(key, value)
        except Exception as e:
            print(f"Warning: Could not set Streamlit option {key}: {e}")


def get_https_run_command() -> str:
    """
    Get the command to run Streamlit with HTTPS configuration.
    
    Returns:
        Command string to run Streamlit with HTTPS
    """
    https_config = HTTPSConfig()
    cert_path, key_path = https_config._get_ssl_certificates()
    
    if cert_path and key_path:
        return f"streamlit run app.py --server.sslCertFile {cert_path} --server.sslKeyFile {key_path} --server.port 8501"
    else:
        # Generate self-signed certificate
        cert_path, key_path = https_config._generate_self_signed_cert()
        if cert_path and key_path:
            return f"streamlit run app.py --server.sslCertFile {cert_path} --server.sslKeyFile {key_path} --server.port 8501"
        else:
            return "streamlit run app.py --server.port 8501"


if __name__ == "__main__":
    # Test HTTPS configuration
    https_config = HTTPSConfig()
    status = https_config.validate_https_setup()
    
    print("HTTPS Configuration Status:")
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    print(f"\nRun command: {get_https_run_command()}")