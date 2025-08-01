"""
Security middleware for the Legal Document Summarizer.
Provides additional security measures and request/response filtering.
"""

import os
import time
import hashlib
import secrets
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
import threading
from functools import wraps

from src.utils.secure_logging import get_secure_logger


class SecurityMiddleware:
    """
    Security middleware that provides additional protection layers.
    """
    
    def __init__(self):
        """Initialize security middleware."""
        self.logger = get_secure_logger("security_middleware")
        self._rate_limiter = RateLimiter()
        self._session_manager = SessionManager()
        self._request_validator = RequestValidator()
    
    def apply_security_headers(self, response_headers: Dict[str, str]) -> Dict[str, str]:
        """
        Apply security headers to HTTP responses.
        
        Args:
            response_headers: Existing response headers
            
        Returns:
            Updated headers with security additions
        """
        security_headers = {
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
                "geolocation=(), microphone=(), camera=(), payment=(), "
                "usb=(), magnetometer=(), gyroscope=(), speaker=(), "
                "accelerometer=(), ambient-light-sensor=(), autoplay=(), "
                "battery=(), display-capture=(), document-domain=(), "
                "encrypted-media=(), fullscreen=(), gamepad=(), midi=(), "
                "picture-in-picture=(), publickey-credentials-get=(), "
                "screen-wake-lock=(), sync-xhr=(), web-share=()"
            ),
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
        }
        
        # Merge with existing headers
        updated_headers = response_headers.copy()
        updated_headers.update(security_headers)
        
        return updated_headers
    
    def validate_request(self, request_data: Dict[str, Any]) -> bool:
        """
        Validate incoming requests for security threats.
        
        Args:
            request_data: Request data to validate
            
        Returns:
            True if request is valid, False otherwise
        """
        return self._request_validator.validate(request_data)
    
    def check_rate_limit(self, client_id: str) -> bool:
        """
        Check if client has exceeded rate limits.
        
        Args:
            client_id: Client identifier
            
        Returns:
            True if within limits, False if exceeded
        """
        return self._rate_limiter.check_limit(client_id)
    
    def create_secure_session(self) -> str:
        """
        Create a new secure session.
        
        Returns:
            Session ID
        """
        return self._session_manager.create_session()
    
    def validate_session(self, session_id: str) -> bool:
        """
        Validate a session ID.
        
        Args:
            session_id: Session ID to validate
            
        Returns:
            True if valid, False otherwise
        """
        return self._session_manager.validate_session(session_id)
    
    def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions.
        
        Returns:
            Number of sessions cleaned up
        """
        return self._session_manager.cleanup_expired()


class RateLimiter:
    """
    Rate limiter to prevent abuse and DoS attacks.
    """
    
    def __init__(self, max_requests: int = 100, window_minutes: int = 15):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum requests per window
            window_minutes: Time window in minutes
        """
        self.max_requests = max_requests
        self.window_seconds = window_minutes * 60
        self._requests: Dict[str, list] = {}
        self._lock = threading.Lock()
    
    def check_limit(self, client_id: str) -> bool:
        """
        Check if client is within rate limits.
        
        Args:
            client_id: Client identifier
            
        Returns:
            True if within limits, False if exceeded
        """
        current_time = time.time()
        
        with self._lock:
            # Initialize client if not exists
            if client_id not in self._requests:
                self._requests[client_id] = []
            
            # Clean old requests
            cutoff_time = current_time - self.window_seconds
            self._requests[client_id] = [
                req_time for req_time in self._requests[client_id]
                if req_time > cutoff_time
            ]
            
            # Check if limit exceeded
            if len(self._requests[client_id]) >= self.max_requests:
                return False
            
            # Add current request
            self._requests[client_id].append(current_time)
            return True


class SessionManager:
    """
    Secure session management.
    """
    
    def __init__(self, session_timeout_minutes: int = 60):
        """
        Initialize session manager.
        
        Args:
            session_timeout_minutes: Session timeout in minutes
        """
        self.session_timeout = timedelta(minutes=session_timeout_minutes)
        self._sessions: Dict[str, datetime] = {}
        self._lock = threading.Lock()
    
    def create_session(self) -> str:
        """
        Create a new secure session.
        
        Returns:
            Session ID
        """
        session_id = secrets.token_urlsafe(32)
        
        with self._lock:
            self._sessions[session_id] = datetime.now()
        
        return session_id
    
    def validate_session(self, session_id: str) -> bool:
        """
        Validate a session ID.
        
        Args:
            session_id: Session ID to validate
            
        Returns:
            True if valid, False otherwise
        """
        with self._lock:
            if session_id not in self._sessions:
                return False
            
            # Check if expired
            if datetime.now() - self._sessions[session_id] > self.session_timeout:
                del self._sessions[session_id]
                return False
            
            # Update last access time
            self._sessions[session_id] = datetime.now()
            return True
    
    def cleanup_expired(self) -> int:
        """
        Clean up expired sessions.
        
        Returns:
            Number of sessions cleaned up
        """
        current_time = datetime.now()
        expired_sessions = []
        
        with self._lock:
            for session_id, last_access in self._sessions.items():
                if current_time - last_access > self.session_timeout:
                    expired_sessions.append(session_id)
            
            for session_id in expired_sessions:
                del self._sessions[session_id]
        
        return len(expired_sessions)


class RequestValidator:
    """
    Request validation for security threats.
    """
    
    def __init__(self):
        """Initialize request validator."""
        self.logger = get_secure_logger("request_validator")
        
        # Common attack patterns
        self.sql_injection_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER)\b)",
            r"(\b(UNION|OR|AND)\b.*\b(SELECT|INSERT|UPDATE|DELETE)\b)",
            r"('|\"|;|--|\*|\/\*|\*\/)",
        ]
        
        self.xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>.*?</iframe>",
        ]
        
        self.path_traversal_patterns = [
            r"\.\./",
            r"\.\.\\",
            r"%2e%2e%2f",
            r"%2e%2e\\",
        ]
    
    def validate(self, request_data: Dict[str, Any]) -> bool:
        """
        Validate request data for security threats.
        
        Args:
            request_data: Request data to validate
            
        Returns:
            True if valid, False if threat detected
        """
        try:
            # Convert all values to strings for pattern matching
            text_data = self._extract_text_data(request_data)
            
            # Check for SQL injection
            if self._check_sql_injection(text_data):
                self.logger.log_security_event("sql_injection_attempt", {
                    "request_data_keys": list(request_data.keys())
                })
                return False
            
            # Check for XSS
            if self._check_xss(text_data):
                self.logger.log_security_event("xss_attempt", {
                    "request_data_keys": list(request_data.keys())
                })
                return False
            
            # Check for path traversal
            if self._check_path_traversal(text_data):
                self.logger.log_security_event("path_traversal_attempt", {
                    "request_data_keys": list(request_data.keys())
                })
                return False
            
            return True
            
        except Exception as e:
            self.logger.log_error(e, {"operation": "request_validation"})
            # Fail secure - reject request if validation fails
            return False
    
    def _extract_text_data(self, data: Any) -> str:
        """
        Extract text data from request for pattern matching.
        
        Args:
            data: Data to extract text from
            
        Returns:
            Combined text string
        """
        if isinstance(data, str):
            return data
        elif isinstance(data, dict):
            return " ".join(self._extract_text_data(v) for v in data.values())
        elif isinstance(data, (list, tuple)):
            return " ".join(self._extract_text_data(item) for item in data)
        else:
            return str(data)
    
    def _check_sql_injection(self, text: str) -> bool:
        """Check for SQL injection patterns."""
        import re
        text_lower = text.lower()
        
        for pattern in self.sql_injection_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True
        return False
    
    def _check_xss(self, text: str) -> bool:
        """Check for XSS patterns."""
        import re
        text_lower = text.lower()
        
        for pattern in self.xss_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True
        return False
    
    def _check_path_traversal(self, text: str) -> bool:
        """Check for path traversal patterns."""
        import re
        text_lower = text.lower()
        
        for pattern in self.path_traversal_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True
        return False


def security_required(func: Callable) -> Callable:
    """
    Decorator to add security checks to functions.
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function with security checks
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Get security middleware instance
        middleware = SecurityMiddleware()
        
        # Basic security checks
        # In a real implementation, you would extract client info from request
        client_id = "default_client"  # This would come from request context
        
        # Check rate limits
        if not middleware.check_rate_limit(client_id):
            raise SecurityError("Rate limit exceeded")
        
        # Validate request data
        request_data = kwargs.copy()
        if not middleware.validate_request(request_data):
            raise SecurityError("Invalid request detected")
        
        # Execute original function
        return func(*args, **kwargs)
    
    return wrapper


class SecurityError(Exception):
    """Custom exception for security-related errors."""
    pass


# Global security middleware instance
_security_middleware: Optional[SecurityMiddleware] = None
_middleware_lock = threading.Lock()


def get_security_middleware() -> SecurityMiddleware:
    """
    Get the global security middleware instance.
    
    Returns:
        SecurityMiddleware instance
    """
    global _security_middleware
    
    if _security_middleware is None:
        with _middleware_lock:
            if _security_middleware is None:
                _security_middleware = SecurityMiddleware()
    
    return _security_middleware