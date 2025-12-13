#!/usr/bin/env python3
"""
TallyConnect Portal Server
==========================

Simple HTTP server that serves the portal and generates reports on-demand.
No manual generation needed - everything happens automatically!
"""

import os
import sys
import json
import sqlite3
import webbrowser
import http.server
import socketserver
from urllib.parse import urlparse, parse_qs
from reports import ReportGenerator
from database.queries import ReportQueries

# Get absolute path to database (works from any directory and in EXE)
def get_base_dir():
    """Get base directory - works for both script and PyInstaller EXE."""
    if getattr(sys, 'frozen', False):
        # Running as compiled EXE - use executable directory (for database)
        return os.path.dirname(sys.executable)
    else:
        # Running as script - use script directory
        return os.path.dirname(os.path.abspath(__file__))

def get_resource_dir():
    """Get resource directory - for bundled files in EXE."""
    if getattr(sys, 'frozen', False):
        # Running as compiled EXE - PyInstaller bundles files in _MEIPASS
        try:
            return sys._MEIPASS
        except AttributeError:
            # Fallback to executable directory
            return os.path.dirname(sys.executable)
    else:
        # Running as script - use script directory
        return os.path.dirname(os.path.abspath(__file__))

# Don't use SCRIPT_DIR directly - use get_base_dir() function instead
# SCRIPT_DIR = get_base_dir()  # For database (should be with EXE)
RESOURCE_DIR = get_resource_dir()  # For bundled files (reports, etc.)
DB_FILE = os.path.join(get_base_dir(), "TallyConnectDb.db")
PORT = 8000
PORTAL_DIR = os.path.join(RESOURCE_DIR, "reports", "portal")

class PortalHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler for portal requests."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PORTAL_DIR, **kwargs)
        self.generator = ReportGenerator(DB_FILE)
    
    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # API endpoints
        if path.startswith('/api/'):
            self.handle_api(path, parsed_path)
        else:
            # Serve static files
            super().do_GET()
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def handle_api(self, path, parsed):
        """Handle API requests."""
        try:
            # Companies list
            if path == '/api/companies.json' or path == '/api/companies.json/':
                self.send_companies()
            
            # Ledgers for company
            elif path.startswith('/api/ledgers/'):
                self.send_ledgers(path)
            
            # Generate and serve report
            elif path.startswith('/api/reports/'):
                self.generate_and_serve_report(path)
            
            else:
                print(f"[DEBUG] API path not found: {path}")
                self.send_error(404, f"API endpoint not found: {path}")
        
        except Exception as e:
            print(f"[ERROR] handle_api: {e}")
            import traceback
            traceback.print_exc()
            self.send_error(500, f"Server error: {str(e)}")
    
    def send_companies(self):
        """Send companies list."""
        try:
            # Use absolute path to database
            db_path = os.path.join(get_base_dir(), "TallyConnectDb.db")
            if not os.path.exists(db_path):
                print(f"[ERROR] Database not found at: {db_path}")
                self.send_json_response([])
                return
            
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT name, guid, alterid, status, total_records FROM companies WHERE status='synced'")
            companies = []
            for row in cursor.fetchall():
                companies.append({
                    'name': row['name'],
                    'guid': row['guid'],
                    'alterid': str(row['alterid']),
                    'status': row['status'] or 'synced',
                    'total_records': row['total_records'] or 0
                })
            
            conn.close()
            
            # If no companies found, return empty array (not error)
            self.send_json_response(companies)
        except Exception as e:
            print(f"[ERROR] send_companies: {e}")
            print(f"[DEBUG] DB_FILE path: {DB_FILE}")
            print(f"[DEBUG] DB_FILE exists: {os.path.exists(DB_FILE)}")
            import traceback
            traceback.print_exc()
            # Return empty array instead of error (so UI doesn't break)
            self.send_json_response([])
    
    def send_ledgers(self, path):
        """Send ledgers list for a company."""
        # Extract guid and alterid from path
        # Format: /api/ledgers/{guid}_{alterid}.json
        filename = path.replace('/api/ledgers/', '').replace('.json', '')
        
        # Try to find company by matching guid and alterid
        db_path = os.path.join(get_base_dir(), "TallyConnectDb.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all companies and match
        cursor.execute("SELECT guid, alterid FROM companies WHERE status='synced'")
        companies = cursor.fetchall()
        
        guid = None
        alterid = None
        
        for comp_guid, comp_alterid in companies:
            safe_guid = comp_guid.replace('-', '_')
            safe_alterid = str(comp_alterid).replace('.', '_')
            if f"{safe_guid}_{safe_alterid}" == filename:
                guid = comp_guid
                alterid = str(comp_alterid)
                break
        
        conn.close()
        
        if not guid or not alterid:
            self.send_error(404, "Company not found")
            return
        
        db_path = os.path.join(get_base_dir(), "TallyConnectDb.db")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT vch_party_name as name, COUNT(*) as count
            FROM vouchers
            WHERE company_guid = ? AND company_alterid = ?
            AND vch_party_name IS NOT NULL AND vch_party_name != ''
            GROUP BY vch_party_name
            ORDER BY vch_party_name
        """, (guid, alterid))
        
        ledgers = []
        for row in cursor.fetchall():
            ledgers.append({
                'name': row['name'],
                'count': row['count']
            })
        
        conn.close()
        self.send_json_response(ledgers)
    
    def generate_and_serve_report(self, path):
        """Generate report on-demand and serve it."""
        # Extract report info from path
        # Format: /api/reports/{type}_{guid}_{alterid}_{ledger?}.html
        filename = os.path.basename(path)
        parts = filename.replace('.html', '').split('_')
        
        if len(parts) < 3:
            self.send_error(400, "Invalid report request")
            return
        
        report_type = parts[0]
        
        # Reconstruct guid (parts 1-5) - GUID has 5 parts separated by dashes
        if len(parts) >= 7:
            # GUID: parts[1] to parts[5] (5 parts)
            guid_parts = parts[1:6]
            guid = '-'.join(guid_parts)
            alterid = parts[6] if len(parts) > 6 else ''
        else:
            self.send_error(400, "Invalid report format")
            return
        
        # Get company name
        db_path = os.path.join(get_base_dir(), "TallyConnectDb.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM companies WHERE guid=? AND alterid=?", (guid, alterid))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            self.send_error(404, "Company not found")
            return
        
        company_name = row[0]
        
        try:
            # Generate report on-demand (suppress browser opening)
            if report_type == 'outstanding':
                # Temporarily disable browser opening
                original_open = self.generator._open_in_browser
                self.generator._open_in_browser = lambda x: None
                report_path = self.generator.generate_outstanding_report(company_name, guid, alterid)
                self.generator._open_in_browser = original_open
            
            elif report_type == 'dashboard':
                # Temporarily disable browser opening
                original_open = self.generator._open_in_browser
                self.generator._open_in_browser = lambda x: None
                report_path = self.generator.generate_dashboard(company_name, guid, alterid)
                self.generator._open_in_browser = original_open
            
            elif report_type == 'ledger':
                # Extract ledger name (parts after alterid)
                if len(parts) > 7:
                    # Get ledger name from database by matching
                    ledger_part = '_'.join(parts[7:])
                    
                    # Query database to find matching ledger
                    db_path = os.path.join(get_base_dir(), "TallyConnectDb.db")
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT DISTINCT vch_party_name
                        FROM vouchers
                        WHERE company_guid = ? AND company_alterid = ?
                        AND vch_party_name IS NOT NULL AND vch_party_name != ''
                    """, (guid, alterid))
                    
                    ledgers = [row[0] for row in cursor.fetchall()]
                    conn.close()
                    
                    # Find best match
                    ledger_name = None
                    for ledger in ledgers:
                        safe_ledger = ledger.replace(' ', '_').replace('/', '_').replace('\\', '_')
                        safe_ledger = "".join(c if c.isalnum() or c in ('_', '-') else '_' for c in safe_ledger)
                        safe_ledger = safe_ledger.replace('__', '_').strip('_')
                        if safe_ledger == ledger_part:
                            ledger_name = ledger
                            break
                    
                    if not ledger_name:
                        # Try first match or use the part as-is
                        ledger_name = ledger_part.replace('_', ' ')
                    
                    # Temporarily disable browser opening
                    original_open = self.generator._open_in_browser
                    self.generator._open_in_browser = lambda x: None
                    report_path = self.generator.generate_ledger_report(
                        company_name, guid, alterid, ledger_name,
                        "01-04-2024", "31-12-2025"
                    )
                    self.generator._open_in_browser = original_open
                else:
                    self.send_error(400, "Ledger name missing")
                    return
            else:
                self.send_error(400, f"Unknown report type: {report_type}")
                return
            
            # Read and serve the generated report
            try:
                with open(report_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.send_header('Cache-Control', 'no-cache')
                self.end_headers()
                self.wfile.write(content.encode('utf-8'))
            except FileNotFoundError:
                self.send_error(404, f"Report file not found: {report_path}")
            except Exception as e:
                self.send_error(500, f"Error reading report: {str(e)}")
        
        except Exception as e:
            self.send_error(500, f"Error generating report: {str(e)}")
    
    def send_json_response(self, data):
        """Send JSON response with CORS headers."""
        json_data = json.dumps(data, indent=2)
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json_data.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Suppress default logging."""
        pass

def is_startup_launch():
    """Check if portal was launched from Windows startup (minimized mode)."""
    # Check command-line argument (set by launcher)
    if '--startup' in sys.argv or '--minimized' in sys.argv:
        return True
    
    # Check if launched from startup folder
    try:
        startup_folder = os.path.join(os.getenv('APPDATA'), 
                                     'Microsoft', 'Windows', 'Start Menu', 
                                     'Programs', 'Startup')
        current_exe = sys.executable if getattr(sys, 'frozen', False) else __file__
        current_dir = os.path.dirname(os.path.abspath(current_exe))
        
        # If current directory is startup folder, it's a startup launch
        if startup_folder.lower() in current_dir.lower():
            return True
    except:
        pass
    
    return False

def start_server():
    """Start the portal server."""
    # Check if launched from startup (minimized mode)
    startup_mode = is_startup_launch()
    
    # Ensure we're in the right directory (works for both script and EXE)
    # In EXE mode, portal is bundled in sys._MEIPASS
    resource_dir = get_resource_dir()
    portal_path = os.path.join(resource_dir, "reports", "portal")
    
    if os.path.exists(portal_path):
        os.chdir(portal_path)
        if not startup_mode:
            print(f"[INFO] Portal directory found: {portal_path}")
    else:
        # Try relative to current directory (for development)
        if os.path.exists("reports/portal"):
            os.chdir("reports/portal")
            if not startup_mode:
                print(f"[INFO] Portal directory found: reports/portal")
        else:
            # Always show error, even in startup mode
            error_msg = f"[ERROR] Portal directory not found!\nResource directory: {resource_dir}\nLooking for: {portal_path}"
            if startup_mode:
                # Log to file if in startup mode
                log_file = os.path.join(get_base_dir(), "portal_error.log")
                with open(log_file, 'w') as f:
                    f.write(error_msg)
            else:
                print(error_msg)
                print(f"Current directory: {os.getcwd()}")
                if getattr(sys, 'frozen', False):
                    print(f"EXE mode - checking sys._MEIPASS: {sys._MEIPASS if hasattr(sys, '_MEIPASS') else 'N/A'}")
                input("Press Enter to exit...")
            return
    
    try:
        with socketserver.TCPServer(("", PORT), PortalHandler) as httpd:
            if not startup_mode:
                # Show console output only if not in startup mode
                print("="*60)
                print("TallyConnect Portal Server")
                print("="*60)
                print(f"\nServer running at: http://localhost:{PORT}")
                print(f"Portal URL: http://localhost:{PORT}/index.html")
                print("\nPress Ctrl+C to stop the server")
                print("="*60)
                print()
            
            # Open browser only if manually launched (not from startup)
            if not startup_mode:
                url = f"http://localhost:{PORT}/index.html"
                webbrowser.open(url)
            
            # Start server
            httpd.serve_forever()
    
    except KeyboardInterrupt:
        if not startup_mode:
            print("\n\nServer stopped.")
    except OSError as e:
        if "Address already in use" in str(e):
            error_msg = f"\n[ERROR] Port {PORT} is already in use!\nPlease close other applications using port {PORT}"
            if startup_mode:
                log_file = os.path.join(get_base_dir(), "portal_error.log")
                with open(log_file, 'w') as f:
                    f.write(error_msg)
            else:
                print(error_msg)
                print("Or modify PORT in portal_server.py")
        else:
            error_msg = f"\n[ERROR] {e}"
            if startup_mode:
                log_file = os.path.join(get_base_dir(), "portal_error.log")
                with open(log_file, 'w') as f:
                    f.write(error_msg)
            else:
                print(error_msg)
        
        if not startup_mode:
            input("Press Enter to exit...")

if __name__ == "__main__":
    start_server()

