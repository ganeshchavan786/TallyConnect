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
import socket
from urllib.parse import urlparse, parse_qs, unquote
from datetime import datetime
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

def is_port_in_use(port):
    """Check if a port is already in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))
            return False
        except OSError:
            return True

def find_available_port(start_port=8000, max_port=8010):
    """Find an available port starting from start_port."""
    for port in range(start_port, max_port + 1):
        if not is_port_in_use(port):
            return port
    return None

class PortalHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler for portal requests."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PORTAL_DIR, **kwargs)
        self.generator = ReportGenerator(DB_FILE)
    
    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Default to index.html if root path
        if path == '/' or path == '':
            path = '/index.html'
        
        # API endpoints
        if path.startswith('/api/'):
            self.handle_api(path, parsed_path)
        else:
            # Serve static files
            # Update path to remove leading slash for file system
            file_path = path.lstrip('/')
            full_path = os.path.join(PORTAL_DIR, file_path)
            
            # Security: ensure file is within PORTAL_DIR
            if not os.path.abspath(full_path).startswith(os.path.abspath(PORTAL_DIR)):
                self.send_error(403, "Forbidden")
                return
            
            # Check if file exists
            if os.path.exists(full_path) and os.path.isfile(full_path):
                # Serve file
                try:
                    with open(full_path, 'rb') as f:
                        content = f.read()
                    
                    # Determine content type
                    if full_path.endswith('.html'):
                        content_type = 'text/html; charset=utf-8'
                    elif full_path.endswith('.css'):
                        content_type = 'text/css'
                    elif full_path.endswith('.js'):
                        content_type = 'application/javascript'
                    elif full_path.endswith('.json'):
                        content_type = 'application/json'
                    else:
                        content_type = 'application/octet-stream'
                    
                    self.send_response(200)
                    self.send_header('Content-type', content_type)
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.send_header('Content-Length', str(len(content)))
                    self.end_headers()
                    self.wfile.write(content)
                except Exception as e:
                    self.send_error(500, f"Error reading file: {str(e)}")
            else:
                # File not found
                self.send_error(404, f"File not found: {path}")
    
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
            
            # NEW: Data API endpoints (JSON responses, no file generation)
            elif path.startswith('/api/ledger-data/'):
                self.send_ledger_data(path, parsed)
            
            elif path.startswith('/api/outstanding-data/'):
                self.send_outstanding_data(path, parsed)
            
            elif path.startswith('/api/dashboard-data/'):
                self.send_dashboard_data(path, parsed)
            
            # OLD: Generate and serve report (for backward compatibility)
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
        # Parse query parameters for original ledger name
        parsed = urlparse(path)
        query_params = parse_qs(parsed.query)
        original_ledger_name = query_params.get('ledger', [None])[0] if query_params.get('ledger') else None
        
        # Extract report info from path
        # Format: /api/reports/{type}_{guid}_{alterid}_{ledger?}.html
        filename = os.path.basename(parsed.path)
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
                # Use original ledger name from query parameter if available
                if original_ledger_name:
                    # Use the original name directly (from query parameter)
                    ledger_name = original_ledger_name
                elif len(parts) > 7:
                    # Fallback: Try to extract from URL path
                    ledger_part = '_'.join(parts[7:])
                    
                    # Query database to find matching ledger by sanitized name
                    db_path = os.path.join(get_base_dir(), "TallyConnectDb.db")
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    
                    # Get all ledgers for this company
                    cursor.execute("""
                        SELECT DISTINCT vch_party_name
                        FROM vouchers
                        WHERE company_guid = ? AND company_alterid = ?
                        AND vch_party_name IS NOT NULL AND vch_party_name != ''
                    """, (guid, alterid))
                    
                    ledgers = [row[0] for row in cursor.fetchall()]
                    conn.close()
                    
                    # Find best match by comparing sanitized names
                    ledger_name = None
                    for ledger in ledgers:
                        safe_ledger = ledger.replace(' ', '_').replace('/', '_').replace('\\', '_')
                        safe_ledger = "".join(c if c.isalnum() or c in ('_', '-') else '_' for c in safe_ledger)
                        safe_ledger = safe_ledger.replace('__', '_').strip('_')
                        if safe_ledger == ledger_part:
                            ledger_name = ledger
                            break
                    
                    if not ledger_name:
                        # Last resort: use sanitized name as-is
                        ledger_name = ledger_part.replace('_', ' ')
                else:
                    self.send_error(400, "Ledger name not provided")
                    return
                
                # Temporarily disable browser opening
                original_open = self.generator._open_in_browser
                self.generator._open_in_browser = lambda x: None
                
                # Generate report with error handling
                try:
                    print(f"[INFO] Generating ledger report for: {company_name} - {ledger_name}")
                    report_path = self.generator.generate_ledger_report(
                        company_name, guid, alterid, ledger_name,
                        "01-04-2024", "31-12-2025"
                    )
                    print(f"[INFO] Report generated: {report_path}")
                    if not report_path or not os.path.exists(report_path):
                        raise FileNotFoundError(f"Report not generated: {report_path}")
                except Exception as e:
                    print(f"[ERROR] Report generation failed: {e}")
                    import traceback
                    traceback.print_exc()
                    self.send_error(500, f"Error generating ledger report: {str(e)}")
                    return
                finally:
                    self.generator._open_in_browser = original_open
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
    
    def send_ledger_data(self, path, parsed):
        """Send ledger transaction data as JSON (no file generation)."""
        try:
            # Extract guid, alterid, and ledger from path
            # Format: /api/ledger-data/{guid}_{alterid}/{ledger}
            parts = path.replace('/api/ledger-data/', '').split('/')
            if len(parts) < 2:
                self.send_error(400, "Invalid ledger data request")
                return
            
            guid_alterid = parts[0]
            ledger_name = '/'.join(parts[1:])  # Handle ledger names with special chars
            ledger_name = ledger_name.replace('%20', ' ').replace('%2F', '/')
            
            # Parse guid and alterid
            guid_parts = guid_alterid.split('_')
            if len(guid_parts) < 7:
                self.send_error(400, "Invalid company identifier")
                return
            
            guid = '-'.join(guid_parts[0:5])  # GUID has 5 parts
            # AlterID may have underscores (e.g., 102209.0 becomes 102209_0)
            # Join all remaining parts with '.' to reconstruct original alterid
            if len(guid_parts) > 5:
                alterid = '.'.join(guid_parts[5:])  # Reconstruct alterid (dots were replaced with underscores)
            else:
                alterid = ''
            
            # Get query parameters for date range
            query_params = parse_qs(parsed.query)
            from_date = query_params.get('from', ['01-04-2024'])[0]
            to_date = query_params.get('to', ['31-12-2025'])[0]
            
            # Query database
            db_path = os.path.join(get_base_dir(), "TallyConnectDb.db")
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get company name
            cursor.execute("SELECT name FROM companies WHERE guid=? AND alterid=?", (guid, alterid))
            company_row = cursor.fetchone()
            if not company_row:
                conn.close()
                self.send_error(404, "Company not found")
                return
            company_name = company_row['name']
            
            # Convert dates for SQL
            from_date_sql = datetime.strptime(from_date, "%d-%m-%Y").strftime("%Y-%m-%d")
            to_date_sql = datetime.strptime(to_date, "%d-%m-%Y").strftime("%Y-%m-%d")
            
            # Query transactions
            from database.queries import ReportQueries
            cursor.execute(ReportQueries.LEDGER_TRANSACTIONS, 
                         (guid, alterid, ledger_name, ledger_name, from_date_sql, to_date_sql))
            transactions = cursor.fetchall()
            
            # Calculate balances
            opening_balance = 0
            running_balance = opening_balance
            total_debit = 0
            total_credit = 0
            
            transaction_list = []
            for trans in transactions:
                debit = float(trans['debit'] or 0)
                credit = float(trans['credit'] or 0)
                running_balance += (debit - credit)
                total_debit += debit
                total_credit += credit
                
                transaction_list.append({
                    'date': trans['date'],
                    'voucher_type': trans['voucher_type'] or '',
                    'voucher_number': trans['voucher_number'] or '',
                    'narration': trans['narration'] or '',
                    'debit': debit,
                    'credit': credit,
                    'balance': running_balance
                })
            
            closing_balance = running_balance
            net_movement = total_debit - total_credit
            
            # Prepare response
            response_data = {
                'company_name': company_name,
                'ledger_name': ledger_name,
                'from_date': from_date,
                'to_date': to_date,
                'opening_balance': opening_balance,
                'closing_balance': closing_balance,
                'total_debit': total_debit,
                'total_credit': total_credit,
                'net_movement': net_movement,
                'total_transactions': len(transactions),
                'transactions': transaction_list
            }
            
            conn.close()
            self.send_json_response(response_data)
            
        except Exception as e:
            print(f"[ERROR] send_ledger_data: {e}")
            import traceback
            traceback.print_exc()
            self.send_error(500, f"Error fetching ledger data: {str(e)}")
    
    def send_outstanding_data(self, path, parsed):
        """Send outstanding report data as JSON (no file generation)."""
        try:
            # Extract guid and alterid from path
            # Format: /api/outstanding-data/{guid}_{alterid}
            filename = path.replace('/api/outstanding-data/', '')
            guid_parts = filename.split('_')
            
            if len(guid_parts) < 7:
                self.send_error(400, "Invalid outstanding data request")
                return
            
            guid = '-'.join(guid_parts[0:5])  # GUID has 5 parts
            # AlterID may have underscores (e.g., 102209.0 becomes 102209_0)
            # Join all remaining parts with '.' to reconstruct original alterid
            if len(guid_parts) > 5:
                alterid = '.'.join(guid_parts[5:])  # Reconstruct alterid (dots were replaced with underscores)
            else:
                alterid = ''
            
            # Query database
            db_path = os.path.join(get_base_dir(), "TallyConnectDb.db")
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get company name
            cursor.execute("SELECT name FROM companies WHERE guid=? AND alterid=?", (guid, alterid))
            company_row = cursor.fetchone()
            if not company_row:
                conn.close()
                self.send_error(404, "Company not found")
                return
            company_name = company_row['name']
            
            # Query outstanding summary
            from database.queries import ReportQueries
            cursor.execute(ReportQueries.OUTSTANDING_SUMMARY, (guid, alterid))
            parties = cursor.fetchall()
            
            party_list = []
            for party in parties:
                party_list.append({
                    'party_name': party['party_name'],
                    'debit': float(party['debit'] or 0),
                    'credit': float(party['credit'] or 0),
                    'balance': float(party['balance'] or 0),
                    'transaction_count': party['transaction_count'],
                    'first_transaction': party['first_transaction'],
                    'last_transaction': party['last_transaction']
                })
            
            # Calculate totals
            total_debit = sum(p['debit'] for p in party_list)
            total_credit = sum(p['credit'] for p in party_list)
            total_outstanding = sum(abs(p['balance']) for p in party_list)
            
            response_data = {
                'company_name': company_name,
                'as_on_date': datetime.now().strftime("%d-%m-%Y"),
                'total_parties': len(party_list),
                'total_debit': total_debit,
                'total_credit': total_credit,
                'total_outstanding': total_outstanding,
                'parties': party_list
            }
            
            conn.close()
            self.send_json_response(response_data)
            
        except Exception as e:
            print(f"[ERROR] send_outstanding_data: {e}")
            import traceback
            traceback.print_exc()
            self.send_error(500, f"Error fetching outstanding data: {str(e)}")
    
    def send_dashboard_data(self, path, parsed):
        """Send dashboard data as JSON (no file generation)."""
        try:
            # Extract guid and alterid from path
            # Format: /api/dashboard-data/{guid}_{alterid}
            filename = path.replace('/api/dashboard-data/', '')
            guid_parts = filename.split('_')
            
            if len(guid_parts) < 7:
                self.send_error(400, "Invalid dashboard data request")
                return
            
            guid = '-'.join(guid_parts[0:5])  # GUID has 5 parts
            # AlterID may have underscores (e.g., 102209.0 becomes 102209_0)
            # Join all remaining parts with '.' to reconstruct original alterid
            if len(guid_parts) > 5:
                alterid = '.'.join(guid_parts[5:])  # Reconstruct alterid (dots were replaced with underscores)
            else:
                alterid = ''
            
            # Query database
            db_path = os.path.join(get_base_dir(), "TallyConnectDb.db")
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get company name
            cursor.execute("SELECT name FROM companies WHERE guid=? AND alterid=?", (guid, alterid))
            company_row = cursor.fetchone()
            if not company_row:
                conn.close()
                self.send_error(404, "Company not found")
                return
            company_name = company_row['name']
            
            from database.queries import ReportQueries
            
            # Get dashboard stats
            cursor.execute(ReportQueries.DASHBOARD_STATS, (guid, alterid))
            stats = cursor.fetchone()
            
            # Get top debtors
            cursor.execute(ReportQueries.TOP_DEBTORS, (guid, alterid))
            debtors = [{'party_name': r['party_name'], 'balance': float(r['balance']), 'count': r['transaction_count']} 
                      for r in cursor.fetchall()]
            
            # Get top creditors
            cursor.execute(ReportQueries.TOP_CREDITORS, (guid, alterid))
            creditors = [{'party_name': r['party_name'], 'balance': float(r['balance']), 'count': r['transaction_count']} 
                        for r in cursor.fetchall()]
            
            # Get voucher type summary
            cursor.execute(ReportQueries.VOUCHER_TYPE_SUMMARY, (guid, alterid))
            voucher_types = [{'type': r['voucher_type'], 'count': r['count'], 
                            'debit': float(r['total_debit']), 'credit': float(r['total_credit'])} 
                           for r in cursor.fetchall()]
            
            # Get monthly trend
            cursor.execute(ReportQueries.MONTHLY_TREND, (guid, alterid))
            monthly_trend = [{'month': r['month'], 'count': r['transaction_count'],
                            'debit': float(r['total_debit']), 'credit': float(r['total_credit'])} 
                           for r in cursor.fetchall()]
            
            response_data = {
                'company_name': company_name,
                'stats': {
                    'total_parties': stats['total_parties'],
                    'total_transactions': stats['total_transactions'],
                    'total_debit': float(stats['total_debit'] or 0),
                    'total_credit': float(stats['total_credit'] or 0),
                    'net_balance': float(stats['net_balance'] or 0),
                    'first_transaction': stats['first_transaction_date'],
                    'last_transaction': stats['last_transaction_date']
                },
                'top_debtors': debtors,
                'top_creditors': creditors,
                'voucher_types': voucher_types,
                'monthly_trend': monthly_trend
            }
            
            conn.close()
            self.send_json_response(response_data)
            
        except Exception as e:
            print(f"[ERROR] send_dashboard_data: {e}")
            import traceback
            traceback.print_exc()
            self.send_error(500, f"Error fetching dashboard data: {str(e)}")
    
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
    
    # Update PORTAL_DIR global variable to the correct path
    global PORTAL_DIR
    if os.path.exists(portal_path):
        PORTAL_DIR = portal_path
        if not startup_mode:
            print(f"[INFO] Portal directory found: {portal_path}")
    else:
        # Try relative to current directory (for development)
        base_dir = get_base_dir()
        dev_portal_path = os.path.join(base_dir, "reports", "portal")
        if os.path.exists(dev_portal_path):
            PORTAL_DIR = dev_portal_path
            if not startup_mode:
                print(f"[INFO] Portal directory found: {dev_portal_path}")
        else:
            # Always show error, even in startup mode
            error_msg = f"[ERROR] Portal directory not found!\nResource directory: {resource_dir}\nLooking for: {portal_path}\nAlso tried: {dev_portal_path}"
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
    
    # Change to portal directory for serving files
    os.chdir(PORTAL_DIR)
    
    # Check if port is available, find alternative if needed
    global PORT
    original_port = PORT
    if is_port_in_use(PORT):
        if not startup_mode:
            print(f"[WARNING] Port {PORT} is already in use.")
        # Try to find an available port
        available_port = find_available_port(PORT, PORT + 10)
        if available_port:
            PORT = available_port
            if not startup_mode:
                print(f"[INFO] Using alternative port: {PORT}")
        else:
            error_msg = f"[ERROR] Ports {original_port}-{original_port+10} are all in use!\nPlease close other applications or restart your computer."
            if startup_mode:
                log_file = os.path.join(get_base_dir(), "portal_error.log")
                with open(log_file, 'w') as f:
                    f.write(error_msg)
            else:
                print(error_msg)
            return
    
    # Create server instance (don't use context manager to keep it alive)
    httpd = socketserver.TCPServer(("", PORT), PortalHandler)
    httpd.allow_reuse_address = True  # Allow port reuse
    
    try:
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
        
        # Start server (this blocks until shutdown)
        httpd.serve_forever()
    
    except KeyboardInterrupt:
        if not startup_mode:
            print("\n\nServer stopped.")
    except Exception as e:
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
    
    finally:
        # Cleanup
        try:
            httpd.shutdown()
        except:
            pass
    
    return httpd

if __name__ == "__main__":
    start_server()

