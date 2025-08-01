"""
Security configuration for the Legal Document Summarizer.
Centralizes all security-related settings and policies.
"""

import os
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum


class SecurityLevel(Enum):
    """Security levels for different deployment environments."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


@dataclass
class SecurityConfig:
    """Security configuration settings."""
    
    # General security settings
    security_level: SecurityLevel = SecurityLevel.PRODUCTION
    enable_https: bool = True
    require_https: bool = True
    
    # Session management
    session_timeout_minutes: int = 60
    session_cleanup_interval_minutes: int = 15
    max_concurrent_sessions: int = 100
    
    # Rate limiting
    rate_limit_requests_per_window: int = 100
    rate_limit_window_minutes: int = 15
    rate_limit_enabled: bool = True
    
    # File upload security
    max_file_size_mb: int = 10
    allowed_file_extensions: List[str] = None
    scan_uploads_for_malware: bool = True
    quarantine_suspicious_files: bool = True
    
    # Memory management
    memory_cleanup_interval_minutes: int = 5
    memory_pressure_threshold_percent: float = 80.0
    force_gc_on_cleanup: bool = True
    track_sensitive_objects: bool = True
    
    # Logging and monitoring
    log_security_events: bool = True
    log_level: str = "INFO"
    sanitize_logs: bool = True
    log_retention_days: int = 30
    
    # Data protection
    encrypt_temp_files: bool = True
    secure_delete_files: bool = True
    clear_memory_on_exit: bool = True
    disable_swap_for_sensitive_data: bool = True
    
    # Network security
    allowed_hosts: List[str] = None
    cors_enabled: bool = False
    xsrf_protection: bool = True
    
    # Content security
    content_security_policy: str = None
    x_frame_options: str = "DENY"
    x_content_type_options: str = "nosniff"
    
    def __post_init__(self):
        """Initialize default values after dataclass creation."""
        if self.allowed_file_extensions is None:
            self.allowed_file_extensions = ['.pdf', '.docx', '.txt']
        
        if self.allowed_hosts is None:
            self.allowed_hosts = ['localhost', '127.0.0.1']
        
        if self.content_security_policy is None:
            self.content_security_policy = (
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
            )
    
    @classmethod
    def from_environment(cls) -> 'SecurityConfig':
        """
        Create security configuration from environment variables.
        
        Returns:
            SecurityConfig instance with values from environment
        """
        return cls(
            security_level=SecurityLevel(os.getenv('SECURITY_LEVEL', 'production')),
            enable_https=os.getenv('ENABLE_HTTPS', 'true').lower() == 'true',
            require_https=os.getenv('REQUIRE_HTTPS', 'true').lower() == 'true',
            session_timeout_minutes=int(os.getenv('SESSION_TIMEOUT_MINUTES', '60')),
            max_concurrent_sessions=int(os.getenv('MAX_CONCURRENT_SESSIONS', '100')),
            rate_limit_requests_per_window=int(os.getenv('RATE_LIMIT_REQUESTS', '100')),
            rate_limit_window_minutes=int(os.getenv('RATE_LIMIT_WINDOW_MINUTES', '15')),
            max_file_size_mb=int(os.getenv('MAX_FILE_SIZE_MB', '10')),
            memory_pressure_threshold_percent=float(os.getenv('MEMORY_PRESSURE_THRESHOLD', '80.0')),
            log_level=os.getenv('LOG_LEVEL', 'INFO'),
            log_retention_days=int(os.getenv('LOG_RETENTION_DAYS', '30')),
        )
    
    def get_streamlit_config(self) -> Dict[str, Any]:
        """
        Get Streamlit-specific configuration.
        
        Returns:
            Dictionary with Streamlit configuration options
        """
        config = {
            'server.enableCORS': self.cors_enabled,
            'server.enableXsrfProtection': self.xsrf_protection,
            'server.maxUploadSize': self.max_file_size_mb,
            'server.enableStaticServing': False,
            'server.runOnSave': False,
            'browser.gatherUsageStats': False,
            'global.disableWatchdogWarning': True,
        }
        
        if self.enable_https:
            config.update({
                'server.port': 8501,
                'server.enableWebsocketCompression': True,
            })
        
        return config
    
    def get_security_headers(self) -> Dict[str, str]:
        """
        Get HTTP security headers configuration.
        
        Returns:
            Dictionary with security headers
        """
        headers = {
            'X-Content-Type-Options': self.x_content_type_options,
            'X-Frame-Options': self.x_frame_options,
            'Content-Security-Policy': self.content_security_policy,
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
        }
        
        if self.enable_https:
            headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
            headers['X-XSS-Protection'] = '1; mode=block'
        
        # Comprehensive permissions policy
        headers['Permissions-Policy'] = (
            "geolocation=(), microphone=(), camera=(), payment=(), "
            "usb=(), magnetometer=(), gyroscope=(), speaker=(), "
            "accelerometer=(), ambient-light-sensor=(), autoplay=(), "
            "battery=(), display-capture=(), document-domain=(), "
            "encrypted-media=(), fullscreen=(), gamepad=(), midi=(), "
            "picture-in-picture=(), publickey-credentials-get=(), "
            "screen-wake-lock=(), sync-xhr=(), web-share=()"
        )
        
        return headers
    
    def validate(self) -> List[str]:
        """
        Validate security configuration.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Validate file size limits
        if self.max_file_size_mb <= 0 or self.max_file_size_mb > 100:
            errors.append("max_file_size_mb must be between 1 and 100")
        
        # Validate session timeout
        if self.session_timeout_minutes <= 0:
            errors.append("session_timeout_minutes must be positive")
        
        # Validate rate limiting
        if self.rate_limit_enabled:
            if self.rate_limit_requests_per_window <= 0:
                errors.append("rate_limit_requests_per_window must be positive")
            if self.rate_limit_window_minutes <= 0:
                errors.append("rate_limit_window_minutes must be positive")
        
        # Validate memory settings
        if not (0 < self.memory_pressure_threshold_percent <= 100):
            errors.append("memory_pressure_threshold_percent must be between 0 and 100")
        
        # Validate file extensions
        if not self.allowed_file_extensions:
            errors.append("allowed_file_extensions cannot be empty")
        
        # Validate hosts
        if not self.allowed_hosts:
            errors.append("allowed_hosts cannot be empty")
        
        # Production-specific validations
        if self.security_level == SecurityLevel.PRODUCTION:
            if not self.require_https:
                errors.append("HTTPS is required in production")
            if self.cors_enabled:
                errors.append("CORS should be disabled in production")
            if not self.xsrf_protection:
                errors.append("XSRF protection is required in production")
        
        return errors
    
    def is_development_mode(self) -> bool:
        """Check if running in development mode."""
        return self.security_level == SecurityLevel.DEVELOPMENT
    
    def is_production_mode(self) -> bool:
        """Check if running in production mode."""
        return self.security_level == SecurityLevel.PRODUCTION


# Global security configuration instance
_security_config: SecurityConfig = None


def get_security_config() -> SecurityConfig:
    """
    Get the global security configuration instance.
    
    Returns:
        SecurityConfig instance
    """
    global _security_config
    
    if _security_config is None:
        _security_config = SecurityConfig.from_environment()
        
        # Validate configuration
        errors = _security_config.validate()
        if errors:
            raise ValueError(f"Security configuration errors: {', '.join(errors)}")
    
    return _security_config


def update_security_config(**kwargs) -> None:
    """
    Update security configuration with new values.
    
    Args:
        **kwargs: Configuration values to update
    """
    global _security_config
    
    if _security_config is None:
        _security_config = SecurityConfig.from_environment()
    
    # Update configuration
    for key, value in kwargs.items():
        if hasattr(_security_config, key):
            setattr(_security_config, key, value)
        else:
            raise ValueError(f"Unknown security configuration option: {key}")
    
    # Validate updated configuration
    errors = _security_config.validate()
    if errors:
        raise ValueError(f"Security configuration errors: {', '.join(errors)}")


def reset_security_config() -> None:
    """Reset security configuration to defaults."""
    global _security_config
    _security_config = None