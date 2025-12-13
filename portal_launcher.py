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
    # Check if launched from startup (add --startup flag)
    import os
    startup_folder = os.path.join(os.getenv('APPDATA'), 
                                   'Microsoft', 'Windows', 'Start Menu', 
                                   'Programs', 'Startup')
    current_exe = sys.executable if getattr(sys, 'frozen', False) else __file__
    is_startup = os.path.dirname(os.path.abspath(current_exe)).lower() in startup_folder.lower() or \
                 '--startup' in sys.argv
    
    # Add --startup flag if launched from startup
    if is_startup and '--startup' not in sys.argv:
        sys.argv.append('--startup')
    
    # Get script directory
    if getattr(sys, 'frozen', False):
        # Running as compiled EXE
        script_dir = os.path.dirname(sys.executable)
        # PyInstaller bundles files in _MEIPASS
        if hasattr(sys, '_MEIPASS'):
            sys.path.insert(0, sys._MEIPASS)
    else:
        # Running as script
        script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Change to script directory (where EXE is or script is)
    os.chdir(script_dir)
    
    # Try to import and run portal_server
    try:
        # Add script directory to path
        sys.path.insert(0, script_dir)
        
        # Try importing portal_server
        import portal_server
        portal_server.start_server()
    except ImportError as e:
        if not is_startup:
            print(f"Error importing portal_server: {e}")
            print(f"Current directory: {os.getcwd()}")
            print(f"Script directory: {script_dir}")
            if hasattr(sys, '_MEIPASS'):
                print(f"MEIPASS: {sys._MEIPASS}")
            input("Press Enter to exit...")
    except Exception as e:
        if not is_startup:
            print(f"Error starting portal: {e}")
            import traceback
            traceback.print_exc()
            input("Press Enter to exit...")

if __name__ == "__main__":
    main()

