#!/usr/bin/env python3
"""
TallyConnect - Main Entry Point
================================

Application entry point for TallyConnect.
Starts both the main GUI application and the portal server.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import portal starter utility
from backend.utils.portal_starter import start_portal_in_background, shutdown_portal

if __name__ == "__main__":
    try:
        # Start main GUI application FIRST (non-blocking)
        from backend.app import main as start_main_app
        
        # Start portal server in background thread (non-blocking)
        import threading
        portal_thread = threading.Thread(target=start_portal_in_background, daemon=True)
        portal_thread.start()
        
        # Start GUI (this will block until GUI closes)
        start_main_app()
    finally:
        # Shutdown portal when main app closes
        shutdown_portal()

