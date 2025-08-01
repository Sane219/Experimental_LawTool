"""
Security service for the Legal Document Summarizer.
Implements security and data protection measures to ensure client confidentiality.
"""

import os
import gc
import tempfile
import threading
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import streamlit as st
import weakref
import hashlib
import secrets


class SecurityService:
    """
    Handles security and data protection measures for the application.
    Ensures sensitive legal documents are processed securely without persistent storage.
    """
    
    def __init__(self):
        """Initialize the security service."""
        self._temp_files: List[str] = []
        self._temp_files_lock = threading.Lock()
        self._session_data: Dict[str, Any] = {}
        self._session_data_lock = threading.Lock()
        self._cleanup_thread: Optional[threading.Thread] = None
        self._shutdown_event = threading.Event()
        self._start_cleanup_thread()
    
    def generate_session_id(self) -> str:
        """
        Generate a secure session ID for tracking session data.
        
        Returns:
            Secure random session ID
        """
        return secrets.token_urlsafe(32)
    
    def register_temp_file(self, file_path: str) -> None:
        """
        Register a temporary file for automatic cleanup.
        
        Args:
            file_path: Path to temporary file
        """
        with self._temp_files_lock:
            if file_path not in self._temp_files:
                self._temp_files.append(file_path)
    
    def create_secure_temp_file(self, suffix: str = "", prefix: str = "legal_doc_") -> str:
        """
        Create a secure temporary file with automatic cleanup registration.
        
        Args:
            suffix: File suffix/extension
            prefix: File prefix
            
        Returns:
            Path to created temporary file
        """
        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix,
            prefix=prefix,
            mode='wb'
        )
        temp_file.close()
        
        # Register for cleanup
        self.register_temp_file(temp_file.name)
        
        return temp_file.name
    
    def cleanup_temp_files(self, specific_files: Optional[List[str]] = None) -> int:
        """
        Clean up temporary files immediately.
        
        Args:
            specific_files: List of specific files to clean up, or None for all
            
        Returns:
            Number of files successfully cleaned up
        """
        cleaned_count = 0
        
        with self._temp_files_lock:
            files_to_clean = specific_files if specific_files else self._temp_files.copy()
            
            for file_path in files_to_clean:
                try:
                    if os.path.exists(file_path):
                        # Securely overwrite file before deletion
                        self._secure_delete_file(file_path)
                        cleaned_count += 1
                    
                    # Remove from tracking list
                    if file_path in self._temp_files:
                        self._temp_files.remove(file_path)
                        
                except Exception as e:
                    # Log error but continue cleanup
                    print(f"Warning: Failed to clean up temp file {file_path}: {e}")
        
        return cleaned_count
    
    def _secure_delete_file(self, file_path: str) -> None:
        """
        Securely delete a file by overwriting it before removal.
        
        Args:
            file_path: Path to file to securely delete
        """
        try:
            if not os.path.exists(file_path):
                return
            
            # Get file size
            file_size = os.path.getsize(file_path)
            
            # Overwrite with random data multiple times
            with open(file_path, 'r+b') as f:
                for _ in range(3):  # 3 passes of random data
                    f.seek(0)
                    f.write(os.urandom(file_size))
                    f.flush()
                    os.fsync(f.fileno())
            
            # Finally delete the file
            os.unlink(file_path)
            
        except Exception as e:
            # If secure deletion fails, try regular deletion
            try:
                os.unlink(file_path)
            except Exception:
                pass
    
    def store_session_data(self, session_id: str, key: str, value: Any, ttl_minutes: int = 60) -> None:
        """
        Store data for a session with automatic expiration.
        
        Args:
            session_id: Session identifier
            key: Data key
            value: Data value
            ttl_minutes: Time to live in minutes
        """
        expiry_time = datetime.now() + timedelta(minutes=ttl_minutes)
        
        with self._session_data_lock:
            if session_id not in self._session_data:
                self._session_data[session_id] = {}
            
            self._session_data[session_id][key] = {
                'value': value,
                'expires_at': expiry_time
            }
    
    def get_session_data(self, session_id: str, key: str) -> Optional[Any]:
        """
        Retrieve session data if not expired.
        
        Args:
            session_id: Session identifier
            key: Data key
            
        Returns:
            Data value if exists and not expired, None otherwise
        """
        with self._session_data_lock:
            if session_id not in self._session_data:
                return None
            
            session = self._session_data[session_id]
            if key not in session:
                return None
            
            data_entry = session[key]
            if datetime.now() > data_entry['expires_at']:
                # Data expired, remove it
                del session[key]
                return None
            
            return data_entry['value']
    
    def clear_session_data(self, session_id: Optional[str] = None) -> int:
        """
        Clear session data for a specific session or all sessions.
        
        Args:
            session_id: Specific session to clear, or None for all sessions
            
        Returns:
            Number of sessions cleared
        """
        cleared_count = 0
        
        with self._session_data_lock:
            if session_id:
                if session_id in self._session_data:
                    # Clear specific session data
                    self._session_data[session_id].clear()
                    del self._session_data[session_id]
                    cleared_count = 1
            else:
                # Clear all session data
                cleared_count = len(self._session_data)
                self._session_data.clear()
        
        # Force garbage collection to clear memory
        gc.collect()
        
        return cleared_count
    
    def clear_streamlit_session(self) -> None:
        """
        Clear sensitive data from Streamlit session state.
        """
        try:
            # Check if we're in a Streamlit context
            import streamlit as st
            from streamlit.runtime.scriptrunner_utils.script_run_context import get_script_run_ctx
            
            # Only clear if we have a valid Streamlit context
            if get_script_run_ctx() is not None:
                sensitive_keys = [
                    'uploaded_file_info',
                    'summary_result',
                    'extracted_text',
                    'document_content',
                    'file_data',
                    'temp_file_path'
                ]
                
                for key in sensitive_keys:
                    if key in st.session_state:
                        del st.session_state[key]
        except Exception:
            # If we can't access Streamlit session state, that's okay
            # This can happen during testing or when not in a Streamlit context
            pass
        
        # Force garbage collection
        gc.collect()
    
    def _start_cleanup_thread(self) -> None:
        """Start the background cleanup thread."""
        if self._cleanup_thread is None or not self._cleanup_thread.is_alive():
            self._cleanup_thread = threading.Thread(
                target=self._cleanup_worker,
                daemon=True,
                name="SecurityCleanupThread"
            )
            self._cleanup_thread.start()
    
    def _cleanup_worker(self) -> None:
        """
        Background worker that periodically cleans up expired data and temp files.
        """
        while not self._shutdown_event.is_set():
            try:
                # Clean up expired session data
                self._cleanup_expired_sessions()
                
                # Clean up any orphaned temp files
                self._cleanup_orphaned_temp_files()
                
                # Wait for next cleanup cycle (every 5 minutes)
                if self._shutdown_event.wait(300):  # 300 seconds = 5 minutes
                    break
                    
            except Exception as e:
                print(f"Warning: Cleanup worker error: {e}")
                # Continue running even if there's an error
                time.sleep(60)  # Wait 1 minute before retrying
    
    def _cleanup_expired_sessions(self) -> None:
        """Clean up expired session data."""
        current_time = datetime.now()
        expired_sessions = []
        
        with self._session_data_lock:
            for session_id, session_data in self._session_data.items():
                expired_keys = []
                
                for key, data_entry in session_data.items():
                    if current_time > data_entry['expires_at']:
                        expired_keys.append(key)
                
                # Remove expired keys
                for key in expired_keys:
                    del session_data[key]
                
                # Mark session for removal if empty
                if not session_data:
                    expired_sessions.append(session_id)
            
            # Remove empty sessions
            for session_id in expired_sessions:
                del self._session_data[session_id]
    
    def _cleanup_orphaned_temp_files(self) -> None:
        """Clean up any orphaned temporary files."""
        with self._temp_files_lock:
            orphaned_files = []
            
            for file_path in self._temp_files:
                try:
                    if os.path.exists(file_path):
                        # Check if file is older than 1 hour
                        file_age = time.time() - os.path.getctime(file_path)
                        if file_age > 3600:  # 1 hour in seconds
                            orphaned_files.append(file_path)
                    else:
                        # File doesn't exist, remove from tracking
                        orphaned_files.append(file_path)
                except Exception:
                    # If we can't check the file, consider it orphaned
                    orphaned_files.append(file_path)
            
            # Clean up orphaned files
            for file_path in orphaned_files:
                try:
                    if os.path.exists(file_path):
                        self._secure_delete_file(file_path)
                    self._temp_files.remove(file_path)
                except Exception:
                    pass
    
    def get_security_status(self) -> Dict[str, Any]:
        """
        Get current security status and statistics.
        
        Returns:
            Dictionary with security status information
        """
        with self._temp_files_lock:
            temp_files_count = len(self._temp_files)
        
        with self._session_data_lock:
            session_count = len(self._session_data)
            total_session_keys = sum(len(session) for session in self._session_data.values())
        
        return {
            'temp_files_tracked': temp_files_count,
            'active_sessions': session_count,
            'total_session_keys': total_session_keys,
            'cleanup_thread_active': self._cleanup_thread.is_alive() if self._cleanup_thread else False,
            'last_cleanup': datetime.now().isoformat()
        }
    
    def force_memory_cleanup(self) -> None:
        """
        Force immediate memory cleanup and garbage collection.
        """
        # Clear all session data
        self.clear_session_data()
        
        # Clean up all temp files
        self.cleanup_temp_files()
        
        # Clear Streamlit session
        self.clear_streamlit_session()
        
        # Force multiple garbage collection passes
        for _ in range(3):
            gc.collect()
    
    def shutdown(self) -> None:
        """
        Shutdown the security service and clean up all resources.
        """
        # Signal shutdown to cleanup thread
        self._shutdown_event.set()
        
        # Wait for cleanup thread to finish
        if self._cleanup_thread and self._cleanup_thread.is_alive():
            self._cleanup_thread.join(timeout=10)
        
        # Final cleanup
        self.force_memory_cleanup()
    
    def __del__(self):
        """Cleanup when service is destroyed."""
        try:
            self.shutdown()
        except Exception:
            pass


# Global security service instance
_security_service: Optional[SecurityService] = None
_security_service_lock = threading.Lock()


def get_security_service() -> SecurityService:
    """
    Get the global security service instance (singleton pattern).
    
    Returns:
        SecurityService instance
    """
    global _security_service
    
    if _security_service is None:
        with _security_service_lock:
            if _security_service is None:
                _security_service = SecurityService()
    
    return _security_service


def cleanup_on_exit():
    """
    Cleanup function to be called on application exit.
    """
    global _security_service
    
    if _security_service:
        _security_service.shutdown()
        _security_service = None


# Register cleanup function for application exit
import atexit
atexit.register(cleanup_on_exit)