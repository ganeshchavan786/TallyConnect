#!/usr/bin/env python3
"""
TallyConnect Portal Launcher
=============================

Launches portal server - can be bundled with EXE or run standalone.
"""

import os
import sys
import subprocess

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, relative_path)

def main():
    """Launch portal server."""
    # Get script directory
    if getattr(sys, 'frozen', False):
        # Running as compiled EXE
        script_dir = os.path.dirname(sys.executable)
    else:
        # Running as script
        script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Change to script directory
    os.chdir(script_dir)
    
    # Try to import and run portal_server
    try:
        # Add current directory to path
        sys.path.insert(0, script_dir)
        import portal_server
        portal_server.start_server()
    except ImportError as e:
        print(f"Error importing portal_server: {e}")
        print(f"Current directory: {os.getcwd()}")
        print(f"Script directory: {script_dir}")
        input("Press Enter to exit...")
    except Exception as e:
        print(f"Error starting portal: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()

