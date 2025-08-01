"""
Memory management utilities for the Legal Document Summarizer.
Ensures sensitive data is properly cleared from memory and prevents memory leaks.
"""

import gc
import os
import sys
import psutil
import threading
import weakref
from typing import Any, Dict, List, Optional, Set
from datetime import datetime, timedelta
import tracemalloc

from src.utils.secure_logging import get_secure_logger


class MemoryManager:
    """
    Advanced memory management for secure document processing.
    """
    
    def __init__(self):
        """Initialize memory manager."""
        self.logger = get_secure_logger("memory_manager")
        self._tracked_objects: Set[weakref.ref] = set()
        self._sensitive_data_refs: List[weakref.ref] = []
        self._cleanup_thread: Optional[threading.Thread] = None
        self._shutdown_event = threading.Event()
        self._lock = threading.Lock()
        
        # Start memory monitoring
        self._start_memory_monitoring()
    
    def track_sensitive_object(self, obj: Any) -> None:
        """
        Track a sensitive object for automatic cleanup.
        
        Args:
            obj: Object containing sensitive data to track
        """
        try:
            # Create weak reference with cleanup callback
            weak_ref = weakref.ref(obj, self._cleanup_callback)
            
            with self._lock:
                self._tracked_objects.add(weak_ref)
                self._sensitive_data_refs.append(weak_ref)
                
        except TypeError:
            # Object doesn't support weak references
            self.logger.log_security_event("weak_ref_failed", {
                "object_type": type(obj).__name__
            })
    
    def clear_sensitive_data(self, obj: Any) -> None:
        """
        Clear sensitive data from an object.
        
        Args:
            obj: Object to clear sensitive data from
        """
        try:
            if hasattr(obj, '__dict__'):
                # Clear dictionary attributes
                for key, value in list(obj.__dict__.items()):
                    if self._is_sensitive_attribute(key):
                        # Overwrite with random data first
                        if isinstance(value, str):
                            obj.__dict__[key] = os.urandom(len(value.encode())).decode('latin-1', errors='ignore')
                        elif isinstance(value, bytes):
                            obj.__dict__[key] = os.urandom(len(value))
                        
                        # Then delete
                        del obj.__dict__[key]
            
            # Clear if it's a container type
            if isinstance(obj, dict):
                self._clear_dict(obj)
            elif isinstance(obj, list):
                self._clear_list(obj)
            elif isinstance(obj, str) and len(obj) > 100:
                # For large strings, overwrite memory location if possible
                self._secure_string_clear(obj)
                
        except Exception as e:
            self.logger.log_error(e, {"operation": "clear_sensitive_data"})
    
    def force_garbage_collection(self, generations: int = 3) -> Dict[str, int]:
        """
        Force garbage collection with multiple passes.
        
        Args:
            generations: Number of GC generations to collect
            
        Returns:
            Dictionary with collection statistics
        """
        stats = {
            'objects_before': len(gc.get_objects()),
            'collected': 0,
            'unreachable': 0
        }
        
        try:
            # Multiple collection passes
            for generation in range(generations):
                collected = gc.collect(generation)
                stats['collected'] += collected
            
            # Get final object count
            stats['objects_after'] = len(gc.get_objects())
            stats['unreachable'] = stats['objects_before'] - stats['objects_after']
            
            self.logger.log_cleanup_operation("garbage_collection", stats['collected'])
            
        except Exception as e:
            self.logger.log_error(e, {"operation": "force_garbage_collection"})
        
        return stats
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """
        Get current memory usage statistics.
        
        Returns:
            Dictionary with memory usage information
        """
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            
            return {
                'rss_mb': memory_info.rss / 1024 / 1024,  # Resident Set Size
                'vms_mb': memory_info.vms / 1024 / 1024,  # Virtual Memory Size
                'percent': process.memory_percent(),
                'available_mb': psutil.virtual_memory().available / 1024 / 1024,
                'gc_objects': len(gc.get_objects()),
                'tracked_objects': len(self._tracked_objects)
            }
        except Exception as e:
            self.logger.log_error(e, {"operation": "get_memory_usage"})
            return {}
    
    def check_memory_pressure(self, threshold_percent: float = 80.0) -> bool:
        """
        Check if system is under memory pressure.
        
        Args:
            threshold_percent: Memory usage threshold percentage
            
        Returns:
            True if under memory pressure
        """
        try:
            memory_usage = self.get_memory_usage()
            return memory_usage.get('percent', 0) > threshold_percent
        except Exception:
            return False
    
    def emergency_cleanup(self) -> Dict[str, int]:
        """
        Perform emergency memory cleanup.
        
        Returns:
            Cleanup statistics
        """
        stats = {
            'objects_cleared': 0,
            'references_cleared': 0,
            'gc_collected': 0
        }
        
        try:
            # Clear all tracked sensitive objects
            with self._lock:
                for weak_ref in list(self._sensitive_data_refs):
                    obj = weak_ref()
                    if obj is not None:
                        self.clear_sensitive_data(obj)
                        stats['objects_cleared'] += 1
                
                # Clear reference lists
                stats['references_cleared'] = len(self._sensitive_data_refs)
                self._sensitive_data_refs.clear()
            
            # Force aggressive garbage collection
            gc_stats = self.force_garbage_collection()
            stats['gc_collected'] = gc_stats['collected']
            
            self.logger.log_cleanup_operation("emergency_cleanup", stats['objects_cleared'])
            
        except Exception as e:
            self.logger.log_error(e, {"operation": "emergency_cleanup"})
        
        return stats
    
    def _is_sensitive_attribute(self, attr_name: str) -> bool:
        """
        Check if an attribute name suggests sensitive data.
        
        Args:
            attr_name: Attribute name to check
            
        Returns:
            True if attribute is likely sensitive
        """
        sensitive_keywords = [
            'content', 'text', 'document', 'summary', 'data',
            'password', 'token', 'key', 'secret', 'private',
            'confidential', 'legal', 'client', 'case'
        ]
        
        attr_lower = attr_name.lower()
        return any(keyword in attr_lower for keyword in sensitive_keywords)
    
    def _clear_dict(self, d: dict) -> None:
        """Clear sensitive data from dictionary."""
        for key in list(d.keys()):
            if self._is_sensitive_attribute(str(key)):
                # Overwrite then delete
                if isinstance(d[key], str):
                    d[key] = "CLEARED"
                del d[key]
    
    def _clear_list(self, lst: list) -> None:
        """Clear sensitive data from list."""
        for i in range(len(lst)):
            if isinstance(lst[i], str) and len(lst[i]) > 50:
                lst[i] = "CLEARED"
            elif isinstance(lst[i], dict):
                self._clear_dict(lst[i])
    
    def _secure_string_clear(self, s: str) -> None:
        """
        Attempt to securely clear a string from memory.
        Note: This is limited in Python due to string immutability.
        
        Args:
            s: String to clear
        """
        try:
            # This is a best-effort approach in Python
            # Python strings are immutable, so we can't truly overwrite them
            # But we can try to encourage garbage collection
            del s
        except Exception:
            pass
    
    def _cleanup_callback(self, weak_ref: weakref.ref) -> None:
        """
        Callback for when tracked objects are garbage collected.
        
        Args:
            weak_ref: Weak reference that was collected
        """
        with self._lock:
            self._tracked_objects.discard(weak_ref)
            if weak_ref in self._sensitive_data_refs:
                self._sensitive_data_refs.remove(weak_ref)
    
    def _start_memory_monitoring(self) -> None:
        """Start background memory monitoring thread."""
        if self._cleanup_thread is None or not self._cleanup_thread.is_alive():
            self._cleanup_thread = threading.Thread(
                target=self._memory_monitor_worker,
                daemon=True,
                name="MemoryMonitorThread"
            )
            self._cleanup_thread.start()
    
    def _memory_monitor_worker(self) -> None:
        """Background worker for memory monitoring and cleanup."""
        while not self._shutdown_event.is_set():
            try:
                # Check memory pressure every 30 seconds
                if self.check_memory_pressure():
                    self.logger.log_security_event("memory_pressure_detected", 
                                                 self.get_memory_usage())
                    
                    # Perform cleanup if under pressure
                    self.force_garbage_collection()
                
                # Clean up dead references
                with self._lock:
                    dead_refs = [ref for ref in self._tracked_objects if ref() is None]
                    for ref in dead_refs:
                        self._tracked_objects.discard(ref)
                
                # Wait before next check
                if self._shutdown_event.wait(30):  # 30 seconds
                    break
                    
            except Exception as e:
                self.logger.log_error(e, {"operation": "memory_monitor"})
                # Continue monitoring even if there's an error
                self._shutdown_event.wait(60)  # Wait 1 minute before retrying
    
    def shutdown(self) -> None:
        """Shutdown memory manager and cleanup resources."""
        self._shutdown_event.set()
        
        if self._cleanup_thread and self._cleanup_thread.is_alive():
            self._cleanup_thread.join(timeout=10)
        
        # Final cleanup
        self.emergency_cleanup()


class SecureBuffer:
    """
    A secure buffer that automatically clears its contents.
    """
    
    def __init__(self, initial_data: Any = None):
        """
        Initialize secure buffer.
        
        Args:
            initial_data: Initial data to store
        """
        self._data = initial_data
        self._memory_manager = get_memory_manager()
        self._memory_manager.track_sensitive_object(self)
    
    def get_data(self) -> Any:
        """Get the stored data."""
        return self._data
    
    def set_data(self, data: Any) -> None:
        """Set new data, clearing old data first."""
        if self._data is not None:
            self._memory_manager.clear_sensitive_data(self._data)
        self._data = data
    
    def clear(self) -> None:
        """Clear the buffer contents."""
        if self._data is not None:
            self._memory_manager.clear_sensitive_data(self._data)
            self._data = None
    
    def __del__(self):
        """Clear data when buffer is destroyed."""
        try:
            self.clear()
        except Exception:
            pass


# Global memory manager instance
_memory_manager: Optional[MemoryManager] = None
_manager_lock = threading.Lock()


def get_memory_manager() -> MemoryManager:
    """
    Get the global memory manager instance.
    
    Returns:
        MemoryManager instance
    """
    global _memory_manager
    
    if _memory_manager is None:
        with _manager_lock:
            if _memory_manager is None:
                _memory_manager = MemoryManager()
    
    return _memory_manager


def secure_delete(obj: Any) -> None:
    """
    Securely delete an object from memory.
    
    Args:
        obj: Object to securely delete
    """
    memory_manager = get_memory_manager()
    memory_manager.clear_sensitive_data(obj)


def track_sensitive_data(obj: Any) -> None:
    """
    Track an object containing sensitive data.
    
    Args:
        obj: Object to track
    """
    memory_manager = get_memory_manager()
    memory_manager.track_sensitive_object(obj)


def emergency_memory_cleanup() -> Dict[str, int]:
    """
    Perform emergency memory cleanup.
    
    Returns:
        Cleanup statistics
    """
    memory_manager = get_memory_manager()
    return memory_manager.emergency_cleanup()


def cleanup_on_exit():
    """Cleanup function to be called on application exit."""
    global _memory_manager
    
    if _memory_manager:
        _memory_manager.shutdown()
        _memory_manager = None


# Register cleanup function for application exit
import atexit
atexit.register(cleanup_on_exit)