#!/usr/bin/env python3
"""
TallyConnect Portal Launcher
=============================

Launches portal server - can be bundled with EXE or run standalone.
Runs in background with system tray icon.
"""

import os
import sys
import subprocess
import threading

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
    # Check if launched from startup folder
    import os
    is_startup = '--startup' in sys.argv
    
    # Try to detect startup launch
    if not is_startup:
        try:
            # Check if parent is explorer (Windows startup)
            import psutil
            parent = psutil.Process().parent()
            if parent.name().lower() in ['explorer.exe']:
                # Check if we were launched from startup folder
                # This is a heuristic - startup items are usually launched by explorer
                is_startup = True
        except ImportError:
            # psutil not available, use alternative method
            pass
        except Exception:
            pass
    
    # Add --startup flag if detected
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
        # Get the directory where this file is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Get project root (parent of backend folder)
        project_root = os.path.dirname(script_dir)
        # Add project root to path so backend module can be imported
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        script_dir = project_root
    
    # Change to script directory (where EXE is or script is)
    os.chdir(script_dir)
    
    # Try to import and run portal_server
    try:
        # Add script directory to path (already done above, but ensure it's there)
        if script_dir not in sys.path:
            sys.path.insert(0, script_dir)
        
        # Try importing portal_server from backend
        from backend import portal_server
        
        # Suppress console output if running as EXE or in startup mode
        if getattr(sys, 'frozen', False) or is_startup:
            # Redirect stdout/stderr to null to hide console
            try:
                sys.stdout = open(os.devnull, 'w')
                sys.stderr = open(os.devnull, 'w')
            except:
                pass
        
        # Store server instance for graceful shutdown (use list for nested function access)
        server_instance = [None]
        
        def start_server_thread():
            """Start server in a thread."""
            server_instance[0] = portal_server.start_server()
        
        # Start server in background thread (NOT daemon - keep running even if main thread exits)
        # This ensures server continues even if tray icon is stopped
        server_thread = threading.Thread(target=start_server_thread, daemon=False)
        server_thread.start()
        
        # Wait a moment for server to start
        import time
        time.sleep(2)
        
        # Get current port (might have changed if 8000 was in use)
        current_port = portal_server.PORT
        
        # Create system tray icon
        try:
            import pystray
            from PIL import Image, ImageDraw
            
            # Create a simple icon
            def create_icon():
                # Create a 64x64 image with blue background
                image = Image.new('RGB', (64, 64), color='#3498db')
                draw = ImageDraw.Draw(image)
                # Draw a simple "P" for Portal
                draw.text((32, 32), "P", fill='white', anchor="mm")
                return image
            
            # Menu items
            def open_portal(icon=None, item=None):
                """Open portal in browser."""
                os.system(f'start http://localhost:{current_port}/index.html')
            
            def stop_server(icon=None, item=None):
                """Stop server gracefully and exit."""
                # Shutdown server if running
                if server_instance[0]:
                    try:
                        server_instance[0].shutdown()
                    except:
                        pass
                # Stop the tray icon (this will exit the main thread)
                # But server thread (non-daemon) will keep process alive until it finishes
                icon.stop()
            
            menu = pystray.Menu(
                pystray.MenuItem("Open Portal", open_portal),
                pystray.MenuItem("Stop Server", stop_server),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Exit", stop_server)
            )
            
            # Create and run icon
            icon = pystray.Icon("TallyConnect Portal", create_icon(), f"TallyConnect Portal\nRunning on http://localhost:{current_port}", menu)
            
            # Run icon (blocks until stopped) - this keeps the app running
            # IMPORTANT: Even if icon stops, server thread (non-daemon) will keep process alive
            icon.run()
            
            # After icon stops (user clicked Exit), gracefully shutdown server
            if server_instance[0]:
                try:
                    server_instance[0].shutdown()
                except:
                    pass
            # Wait for server thread to finish (max 2 seconds)
            server_thread.join(timeout=2)
            
        except ImportError:
            # pystray not available, run server normally (with console)
            if not is_startup:
                print("System tray not available. Running in console mode.")
                print("Install: pip install pystray Pillow")
            portal_server.start_server()
        except Exception as e:
            # Tray icon failed, run server normally (with console)
            if not is_startup:
                print(f"System tray error: {e}")
                import traceback
                traceback.print_exc()
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

