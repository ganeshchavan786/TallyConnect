#!/usr/bin/env python3
"""
Portal Starter Utility
======================

Handles portal server startup, error handling, and verification.
Keeps main.py clean and focused.
"""

import os
import sys
import threading
import time
import socket

# Global variable to store portal server instance
_portal_server_instance = None
_portal_thread = None


def start_portal_in_background():
    """Start portal server in background thread with proper error handling."""
    global _portal_server_instance, _portal_thread
    
    try:
        # Import portal_server
        from backend import portal_server
        
        # Check if portal directory exists before starting
        project_root = _get_project_root()
        portal_dir = os.path.join(project_root, "frontend", "portal")
        
        if not os.path.exists(portal_dir):
            _log_warning(f"Portal directory not found: {portal_dir}")
            _log_info("Portal will not start. Main app will continue.")
            return False
        
        # Start server in a daemon thread (will stop when main app closes)
        def run_portal():
            global _portal_server_instance
            try:
                # Start server and store instance
                _portal_server_instance = portal_server.start_server()
                if _portal_server_instance:
                    port = getattr(portal_server, 'PORT', 8000)
                    _log_success(f"Portal server started on port {port}")
            except Exception as e:
                # Log error but don't crash main app
                _log_error(f"Portal server failed to start: {e}")
                _write_error_log(e)
        
        _portal_thread = threading.Thread(target=run_portal, daemon=True)
        _portal_thread.start()
        
        # Verify server in background (non-blocking)
        def verify_in_background():
            time.sleep(2)  # Wait for server to start
            _verify_and_open_portal()
        
        verify_thread = threading.Thread(target=verify_in_background, daemon=True)
        verify_thread.start()
        
        # Return immediately (non-blocking)
        return True
            
    except ImportError as e:
        _log_error(f"Could not import portal_server: {e}")
        _log_info("Portal will not start. Main app will continue.")
        return False
    except Exception as e:
        _log_error(f"Portal startup error: {e}")
        _write_error_log(e)
        return False


def _verify_and_open_portal():
    """Verify portal server is running and open browser."""
    try:
        from backend import portal_server
        import webbrowser
        
        port = getattr(portal_server, 'PORT', 8000)
        
        # Check if server is actually running
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result == 0:
            # Server is running, open browser
            try:
                webbrowser.open(f'http://localhost:{port}')
                _log_info(f"Portal opened in browser: http://localhost:{port}")
                return True
            except Exception as e:
                _log_warning(f"Could not open browser: {e}")
                return True  # Server is running, just browser failed
        else:
            _log_warning(f"Portal server may not have started. Port {port} is not responding.")
            return False
    except Exception as e:
        _log_warning(f"Could not verify portal server status: {e}")
        return False


def shutdown_portal():
    """Shutdown portal server gracefully."""
    global _portal_server_instance
    if _portal_server_instance:
        try:
            _portal_server_instance.shutdown()
            _log_info("Portal server shut down gracefully")
        except Exception as e:
            _log_warning(f"Error shutting down portal: {e}")


def _get_project_root():
    """Get project root directory."""
    # Get the directory where this file is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up two levels: utils -> backend -> project root
    backend_dir = os.path.dirname(script_dir)
    project_root = os.path.dirname(backend_dir)
    return project_root


def _log_info(message):
    """Log info message."""
    print(f"[INFO] {message}")


def _log_success(message):
    """Log success message."""
    print(f"[SUCCESS] {message}")


def _log_warning(message):
    """Log warning message."""
    print(f"[WARNING] {message}")


def _log_error(message):
    """Log error message."""
    print(f"[ERROR] {message}")


def _write_error_log(error):
    """Write error to log file."""
    try:
        project_root = _get_project_root()
        log_file = os.path.join(project_root, "portal_startup_error.log")
        with open(log_file, 'w') as f:
            f.write(f"Portal startup error: {error}\n")
            import traceback
            f.write(traceback.format_exc())
    except:
        pass

