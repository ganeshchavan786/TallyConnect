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
from urllib.parse import urlparse, parse_qs, parse_qsl, unquote
from datetime import datetime
from backend.report_generator import ReportGenerator
from backend.database.queries import ReportQueries

# Get absolute path to database (works from any directory and in EXE)
def get_base_dir():
    """Get base directory - works for both script and PyInstaller EXE."""
    if getattr(sys, 'frozen', False):
        # Running as compiled EXE - use executable directory (for database)
        return os.path.dirname(sys.executable)
    else:
        # Running as script - use project root (parent of backend folder)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # If we're in backend folder, go up one level to project root
        if os.path.basename(script_dir) == 'backend':
            return os.path.dirname(script_dir)
        return script_dir

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
        # Running as script - use project root (parent of backend folder)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # If we're in backend folder, go up one level to project root
        if os.path.basename(script_dir) == 'backend':
            return os.path.dirname(script_dir)
        return script_dir

# Don't use SCRIPT_DIR directly - use get_base_dir() function instead
# SCRIPT_DIR = get_base_dir()  # For database (should be with EXE)
RESOURCE_DIR = get_resource_dir()  # For bundled files (reports, etc.)
DB_FILE = os.path.join(get_base_dir(), "TallyConnectDb.db")
PORT = 8000
PORTAL_DIR = os.path.join(RESOURCE_DIR, "frontend", "portal")

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
        # Get startup_mode from global scope - with fallback
        try:
            self.startup_mode = is_startup_launch()
        except Exception:
            # Default to False if detection fails
            self.startup_mode = False
    
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
            
            elif path.startswith('/api/sales-register-data/'):
                self.send_sales_register_data(path, parsed)
            
            elif path.startswith('/api/sync-logs/'):
                self.send_sync_logs(path, parsed)
            
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
            
            # Show ALL companies (regardless of status or record count)
            # This ensures all companies are visible in the portal, even if not synced yet
            cursor.execute("SELECT name, guid, alterid, status, total_records FROM companies ORDER BY status DESC, name ASC")
            companies = []
            for row in cursor.fetchall():
                companies.append({
                    'name': row['name'],
                    'guid': row['guid'],
                    'alterid': str(row['alterid']),
                    'status': row['status'] or 'unknown',
                    'total_records': row['total_records'] or 0
                })
            
            conn.close()
            
            # Debug logging
            if not getattr(self, 'startup_mode', False):
                print(f"[INFO] Found {len(companies)} companies in database:")
                for comp in companies:
                    print(f"  - {comp['name']} (Status: {comp['status']}, Records: {comp['total_records']})")
            
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
        try:
            # Extract guid and alterid from path
            # Format: /api/ledgers/{guid}_{alterid}.json
            filename = path.replace('/api/ledgers/', '').replace('.json', '')
            
            if not getattr(self, 'startup_mode', False):
                print(f"[DEBUG] send_ledgers: filename={filename}")
            
            # Try to find company by matching guid and alterid
            db_path = os.path.join(get_base_dir(), "TallyConnectDb.db")
            if not os.path.exists(db_path):
                print(f"[ERROR] Database not found at: {db_path}")
                self.send_error(500, "Database not found")
                return
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get all companies with records and match (not just synced)
            cursor.execute("SELECT guid, alterid FROM companies WHERE total_records > 0")
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
                if not getattr(self, 'startup_mode', False):
                    print(f"[ERROR] Company not found for filename: {filename}")
                    print(f"[DEBUG] Available companies:")
                    for comp_guid, comp_alterid in companies:
                        safe_guid = comp_guid.replace('-', '_')
                        safe_alterid = str(comp_alterid).replace('.', '_')
                        print(f"  - {safe_guid}_{safe_alterid}")
                self.send_error(404, f"Company not found: {filename}")
                return
            
            if not getattr(self, 'startup_mode', False):
                print(f"[INFO] Found company: guid={guid}, alterid={alterid}")
            
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
            
            if not getattr(self, 'startup_mode', False):
                print(f"[INFO] Found {len(ledgers)} ledgers for company")
            
            self.send_json_response(ledgers)
        except Exception as e:
            print(f"[ERROR] send_ledgers: {e}")
            import traceback
            traceback.print_exc()
            self.send_error(500, f"Error fetching ledgers: {str(e)}")
    
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
            
            # Debug: Print ledger name
            print(f"[DEBUG] Looking for ledger: '{ledger_name}'")
            
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
            
            # Query transactions using WORKING LOGIC from demo project
            # Uses vch_mst_id to identify unique vouchers (Tally-style)
            from backend.database.queries import ReportQueries
            
            # Debug: Print query parameters
            print(f"[DEBUG] Query params: guid={guid}, alterid={alterid}, ledger={ledger_name}, from={from_date_sql}, to={to_date_sql}")
            
            # STEP 1: Get unique voucher IDs for selected ledger
            cursor.execute(ReportQueries.LEDGER_VOUCHER_IDS,
                         (guid, alterid, ledger_name, ledger_name, from_date_sql, to_date_sql))
            unique_voucher_ids = [row['vch_mst_id'] for row in cursor.fetchall()]
            
            print(f"[DEBUG] Found {len(unique_voucher_ids)} unique vouchers for ledger: {ledger_name}")
            
            # Calculate balances
            opening_balance = 0
            running_balance = opening_balance
            total_debit = 0
            total_credit = 0
            
            transaction_list = []
            
            # STEP 2: Process each unique voucher
            for vch_mst_id in unique_voucher_ids:
                # Get all lines for this voucher
                cursor.execute(ReportQueries.LEDGER_VOUCHER_LINES, (vch_mst_id,))
                lines = cursor.fetchall()
                
                selected_ledger_line = None
                other_ledger_lines = []
                
                # Find selected ledger line and other lines
                for line in lines:
                    line_led_name = (line['led_name'] or '').strip().upper()
                    ledger_name_upper = ledger_name.strip().upper()
                    
                    if line_led_name == ledger_name_upper:
                        selected_ledger_line = line
                    else:
                        other_ledger_lines.append(line)
                
                if selected_ledger_line:
                    # Get amounts safely
                    dr_amt = float(selected_ledger_line['vch_dr_amt'] or 0)
                    cr_amt = float(selected_ledger_line['vch_cr_amt'] or 0)
                    
                    # Find counter ledger (Particulars)
                    counter_ledger_name = None
                    
                    # Try to find counter ledger with matching DR/CR type
                    for other_line in other_ledger_lines:
                        other_dr_amt = float(other_line['vch_dr_amt'] or 0)
                        other_cr_amt = float(other_line['vch_cr_amt'] or 0)
                        
                        if dr_amt > 0 and other_cr_amt > 0:
                            counter_ledger_name = other_line['led_name'] or other_line['vch_party_name']
                            break
                        elif cr_amt > 0 and other_dr_amt > 0:
                            counter_ledger_name = other_line['led_name'] or other_line['vch_party_name']
                            break
                    
                    # Fallback to vch_party_name or first other ledger
                    if not counter_ledger_name:
                        if selected_ledger_line['vch_party_name']:
                            party_name_upper = selected_ledger_line['vch_party_name'].strip().upper()
                            if party_name_upper != ledger_name_upper:
                                counter_ledger_name = selected_ledger_line['vch_party_name']
                    
                    if not counter_ledger_name and other_ledger_lines:
                        counter_ledger_name = other_ledger_lines[0]['led_name'] or other_ledger_lines[0]['vch_party_name']
                    
                    particulars = counter_ledger_name if counter_ledger_name else (selected_ledger_line['vch_narration'] or 'Others')
                    
                    # Update balance
                    running_balance += dr_amt - cr_amt
                    total_debit += dr_amt
                    total_credit += cr_amt
                    
                    # Add transaction row(s) - show debit and credit separately if both exist
                    if dr_amt > 0:
                        transaction_list.append({
                            'date': selected_ledger_line['vch_date'],
                            'voucher_type': selected_ledger_line['vch_type'] or '',
                            'voucher_number': selected_ledger_line['vch_no'] or '',
                            'particulars': particulars,
                            'narration': selected_ledger_line['vch_narration'] or '',
                            'debit': dr_amt,
                            'credit': 0,
                            'balance': running_balance
                        })
                    
                    if cr_amt > 0:
                        transaction_list.append({
                            'date': selected_ledger_line['vch_date'],
                            'voucher_type': selected_ledger_line['vch_type'] or '',
                            'voucher_number': selected_ledger_line['vch_no'] or '',
                            'particulars': particulars,
                            'narration': selected_ledger_line['vch_narration'] or '',
                            'debit': 0,
                            'credit': cr_amt,
                            'balance': running_balance
                        })
            
            print(f"[DEBUG] Processed {len(transaction_list)} transaction rows")
            
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
                'total_transactions': len(unique_voucher_ids),  # Number of unique vouchers
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
            from backend.database.queries import ReportQueries
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
            
            from backend.database.queries import ReportQueries
            
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
            
            # Parse query parameters for date filtering
            from datetime import datetime, timedelta
            from urllib.parse import parse_qs
            
            query_params = {}
            if parsed.query:
                query_params = {k: v[0] if isinstance(v, list) and len(v) > 0 else v 
                               for k, v in parse_qs(parsed.query).items()}
            
            start_date_str = query_params.get('start_date', '')
            end_date_str = query_params.get('end_date', '')
            financial_year_str = query_params.get('financial_year', '')
            
            # Calculate date range based on query parameters
            if start_date_str and end_date_str:
                # Use provided date range
                try:
                    current_fy_start = datetime.strptime(start_date_str, "%Y-%m-%d")
                    current_fy_end = datetime.strptime(end_date_str, "%Y-%m-%d")
                except ValueError:
                    # Invalid date format, fall back to current FY
                    current_fy_start = None
                    current_fy_end = None
            elif financial_year_str:
                # Parse financial year (format: "2024-25")
                try:
                    fy_year = int(financial_year_str.split('-')[0])
                    current_fy_start = datetime(fy_year, 4, 1)
                    current_fy_end = datetime(fy_year + 1, 3, 31)
                except (ValueError, IndexError):
                    current_fy_start = None
                    current_fy_end = None
            else:
                # Default to Current Financial Year (April 1 to March 31)
                current_fy_start = None
                current_fy_end = None
            
            # If dates not provided or invalid, use current financial year
            if not current_fy_start or not current_fy_end:
                today = datetime.now()
                current_year = today.year
                if today.month >= 4:  # April to December
                    current_fy_start = datetime(current_year, 4, 1)
                    current_fy_end = datetime(current_year + 1, 3, 31)
                else:  # January to March
                    current_fy_start = datetime(current_year - 1, 4, 1)
                    current_fy_end = datetime(current_year, 3, 31)
            
            # Calculate previous period for growth comparison
            # Previous period = same duration, one year earlier
            period_duration = (current_fy_end - current_fy_start).days
            prev_fy_start = datetime(current_fy_start.year - 1, current_fy_start.month, current_fy_start.day)
            prev_fy_end = datetime(current_fy_end.year - 1, current_fy_end.month, current_fy_end.day)
            
            # Format dates for SQL (YYYY-MM-DD)
            current_fy_start_str = current_fy_start.strftime("%Y-%m-%d")
            current_fy_end_str = current_fy_end.strftime("%Y-%m-%d")
            prev_fy_start_str = prev_fy_start.strftime("%Y-%m-%d")
            prev_fy_end_str = prev_fy_end.strftime("%Y-%m-%d")
            
            # Financial year label
            financial_year_label = f"{current_fy_start.strftime('%Y')}-{current_fy_end.strftime('%Y')}"
            
            # Get Sales Summary for Current Financial Year
            cursor.execute(ReportQueries.DASHBOARD_SALES_SUMMARY, 
                         (guid, alterid, current_fy_start_str, current_fy_end_str))
            sales_current = cursor.fetchone()
            total_sales_amount = float(sales_current['total_sales_amount'] or 0) if sales_current else 0
            total_sales_count = int(sales_current['total_sales_count'] or 0) if sales_current else 0
            avg_sales_per_transaction = total_sales_amount / total_sales_count if total_sales_count > 0 else 0
            
            # Get Sales Summary for Previous Financial Year (for growth calculation)
            cursor.execute(ReportQueries.DASHBOARD_SALES_SUMMARY_PREVIOUS, 
                         (guid, alterid, prev_fy_start_str, prev_fy_end_str))
            sales_previous = cursor.fetchone()
            prev_sales_amount = float(sales_previous['total_sales_amount'] or 0) if sales_previous else 0
            
            # Calculate Growth %
            sales_growth_percent = 0
            if prev_sales_amount > 0:
                sales_growth_percent = ((total_sales_amount - prev_sales_amount) / prev_sales_amount) * 100
            elif total_sales_amount > 0:
                sales_growth_percent = 100  # New sales (no previous data)
            
            # Get Monthly Sales Trend for Current Financial Year
            cursor.execute(ReportQueries.MONTHLY_SALES_TREND, 
                         (guid, alterid, current_fy_start_str, current_fy_end_str))
            monthly_sales_trend = [{'month_key': r['month_key'], 'month_name': r['month_name'],
                                   'sales_amount': float(r['sales_amount'] or 0), 
                                   'sales_count': int(r['sales_count'] or 0)} 
                                  for r in cursor.fetchall()]
            
            # Get Top Sales Customers for Current Financial Year
            cursor.execute(ReportQueries.TOP_SALES_CUSTOMERS, 
                         (guid, alterid, current_fy_start_str, current_fy_end_str))
            top_sales_customers = [{'customer_name': r['customer_name'], 
                                   'total_sales': float(r['total_sales'] or 0),
                                   'invoice_count': int(r['invoice_count'] or 0),
                                   'avg_invoice_value': float(r['total_sales'] or 0) / int(r['invoice_count'] or 1) if int(r['invoice_count'] or 0) > 0 else 0}
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
                'sales': {
                    'total_sales_amount': total_sales_amount,
                    'total_sales_count': total_sales_count,
                    'avg_sales_per_transaction': avg_sales_per_transaction,
                    'sales_growth_percent': sales_growth_percent,
                    'previous_sales_amount': prev_sales_amount,
                    'financial_year': financial_year_label,
                    'period_start': current_fy_start_str,
                    'period_end': current_fy_end_str
                },
                'top_debtors': debtors,
                'top_creditors': creditors,
                'voucher_types': voucher_types,
                'monthly_trend': monthly_trend,
                'monthly_sales_trend': monthly_sales_trend,
                'top_sales_customers': top_sales_customers
            }
            
            conn.close()
            self.send_json_response(response_data)
            
        except Exception as e:
            print(f"[ERROR] send_dashboard_data: {e}")
            import traceback
            traceback.print_exc()
            self.send_error(500, f"Error fetching dashboard data: {str(e)}")
    
    def send_sales_register_data(self, path, parsed):
        """Send Sales Register data as JSON (Monthly and Voucher List views)."""
        try:
            # Extract guid and alterid from path
            # Format: /api/sales-register-data/{guid}_{alterid}?from_date=YYYY-MM-DD&to_date=YYYY-MM-DD
            filename = path.replace('/api/sales-register-data/', '').split('?')[0]
            guid_parts = filename.split('_')
            
            if len(guid_parts) < 7:
                self.send_error(400, "Invalid sales register data request")
                return
            
            guid = '-'.join(guid_parts[0:5])  # GUID has 5 parts
            if len(guid_parts) > 5:
                alterid = '.'.join(guid_parts[5:])  # Reconstruct alterid
            else:
                alterid = ''
            
            # Get date range from query parameters
            query_params = dict(parse_qsl(parsed.query))
            from_date = query_params.get('from_date', '')
            to_date = query_params.get('to_date', '')
            
            # Default to Financial Year if dates not provided
            if not from_date or not to_date:
                from datetime import datetime
                current_year = datetime.now().year
                # Financial Year: April 1 to March 31
                if datetime.now().month >= 4:
                    from_date = f"{current_year}-04-01"
                    to_date = f"{current_year + 1}-03-31"
                else:
                    from_date = f"{current_year - 1}-04-01"
                    to_date = f"{current_year}-03-31"
            
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
            
            # Query monthly summary - CORRECT LOGIC: Only Sales ledger's Credit amount
            from backend.database.queries import ReportQueries
            
            # Step 1: Get all unique Sales vouchers
            cursor.execute(ReportQueries.SALES_REGISTER_VOUCHER_IDS, (guid, alterid, from_date, to_date))
            unique_vouchers = cursor.fetchall()
            
            # Step 2: For each voucher, find Sales ledger line and extract only its Credit amount
            monthly_totals = {}  # {month_key: {'debit': 0, 'credit': 0, 'voucher_count': 0}}
            
            for vch in unique_vouchers:
                voucher_key = vch['voucher_key']
                vch_date = vch['vch_date']
                vch_no = vch['vch_no']
                
                # Step 3: Find Sales ledger line for this voucher
                # Try with vch_mst_id first, then fallback to vch_date + vch_no
                cursor.execute(ReportQueries.SALES_REGISTER_SALES_LEDGER_LINE, 
                             (guid, alterid, voucher_key, vch_date, vch_no))
                sales_line = cursor.fetchone()
                
                if sales_line:
                    # Extract month from date (handle both DD-MM-YYYY and YYYY-MM-DD formats)
                    date_str = sales_line['vch_date']
                    month_key = None
                    year = None
                    
                    # Try YYYY-MM-DD format first
                    if '-' in date_str and len(date_str) >= 7:
                        parts = date_str.split('-')
                        if len(parts) >= 2 and len(parts[0]) == 4:  # YYYY-MM-DD
                            year = parts[0]
                            month_key = f"{parts[0]}-{parts[1]}"
                        elif len(parts) >= 3 and len(parts[2]) == 4:  # DD-MM-YYYY
                            year = parts[2]
                            month_key = f"{parts[2]}-{parts[1]}"
                    
                    if not month_key:
                        # Fallback: use original date
                        month_key = date_str[:7] if len(date_str) >= 7 else date_str
                        year = date_str[:4] if len(date_str) >= 4 else ''
                    
                    # Initialize month if not exists
                    if month_key not in monthly_totals:
                        monthly_totals[month_key] = {
                            'debit': 0,
                            'credit': 0,
                            'voucher_count': 0,
                            'year': year
                        }
                    
                    # Add ONLY Sales ledger's amounts
                    debit_amt = float(sales_line['debit'] or 0)
                    credit_amt = float(sales_line['credit'] or 0)
                    
                    monthly_totals[month_key]['debit'] += debit_amt
                    monthly_totals[month_key]['credit'] += credit_amt
                    monthly_totals[month_key]['voucher_count'] += 1
            
            # Step 4: Convert to list with month names and calculate running balance
            monthly_list = []
            running_balance = 0
            total_debit = 0
            total_credit = 0
            
            # Month name mapping
            month_names = {
                '01': 'January', '02': 'February', '03': 'March',
                '04': 'April', '05': 'May', '06': 'June',
                '07': 'July', '08': 'August', '09': 'September',
                '10': 'October', '11': 'November', '12': 'December'
            }
            
            # Sort by month_key (YYYY-MM)
            sorted_months = sorted(monthly_totals.keys())
            
            for month_key in sorted_months:
                month_data = monthly_totals[month_key]
                debit = month_data['debit']
                credit = month_data['credit']
                
                running_balance += credit - debit
                total_debit += debit
                total_credit += credit
                
                # Extract month number for name
                month_num = month_key.split('-')[1] if '-' in month_key else '01'
                month_name = month_names.get(month_num, 'Unknown')
                year = month_data['year'] if month_data['year'] else (month_key.split('-')[0] if '-' in month_key else '')
                
                monthly_list.append({
                    'month_key': month_key,
                    'month_name': month_name,
                    'year': year,
                    'debit': debit,
                    'credit': credit,
                    'closing_balance': running_balance,
                    'voucher_count': month_data['voucher_count']
                })
            
            # Query voucher list - CORRECT LOGIC: Only Sales ledger's Credit amount per voucher
            # Use same approach as monthly summary - get unique vouchers, then find Sales ledger line for each
            
            # Step 1: Get all unique Sales vouchers (reuse the same query as monthly summary)
            cursor.execute(ReportQueries.SALES_REGISTER_VOUCHER_IDS, (guid, alterid, from_date, to_date))
            unique_vouchers = cursor.fetchall()
            
            voucher_list = []
            for vch in unique_vouchers:
                voucher_key = vch['voucher_key']
                vch_date = vch['vch_date']
                vch_no = vch['vch_no']
                
                # Step 2: Find Sales ledger line for this voucher
                # Sum ALL credit lines that are NOT GST/TAX (this gives us total Sales amount)
                cursor.execute(ReportQueries.SALES_REGISTER_SALES_LEDGER_LINE, 
                             (guid, alterid, voucher_key, vch_date, vch_no))
                sales_line = cursor.fetchone()
                
                # Debug: Print voucher details if amount seems wrong
                if sales_line:
                    sales_amount = float(sales_line['credit'] or 0)
                    if sales_amount > 0:
                        print(f"[DEBUG] Voucher {vch_no}: Sales amount = {sales_amount}")
                else:
                    print(f"[DEBUG] Voucher {vch_no}: No Sales ledger line found!")
                
                if sales_line and float(sales_line['credit'] or 0) > 0:
                    # Step 3: Get customer/party name (Particulars) - Debit side
                    customer_query = """
                        SELECT DISTINCT COALESCE(vch_party_name, led_name, '-') as customer
                        FROM vouchers
                        WHERE company_guid = ?
                            AND company_alterid = ?
                            AND (
                                (COALESCE(NULLIF(TRIM(vch_mst_id), ''), vch_date || '|' || vch_no) = ?)
                                OR (vch_date = ? AND vch_no = ?)
                            )
                            AND vch_dr_amt > 0
                            AND (vch_party_name IS NOT NULL AND vch_party_name != '')
                            AND UPPER(TRIM(led_name)) NOT LIKE '%SALES%'
                            AND UPPER(TRIM(led_name)) NOT LIKE '%GST%'
                            AND UPPER(TRIM(led_name)) NOT LIKE '%TAX%'
                        LIMIT 1
                    """
                    cursor.execute(customer_query, (guid, alterid, voucher_key, vch_date, vch_no))
                    customer_row = cursor.fetchone()
                    particulars = customer_row['customer'] if customer_row and customer_row['customer'] != '-' else '-'
                    
                    # If still not found, try any party name from the voucher (Debit side)
                    if particulars == '-':
                        fallback_query = """
                            SELECT DISTINCT COALESCE(vch_party_name, led_name, '-') as party
                            FROM vouchers
                            WHERE company_guid = ?
                                AND company_alterid = ?
                                AND (
                                    (COALESCE(NULLIF(TRIM(vch_mst_id), ''), vch_date || '|' || vch_no) = ?)
                                    OR (vch_date = ? AND vch_no = ?)
                                )
                                AND vch_dr_amt > 0
                                AND (vch_party_name IS NOT NULL AND vch_party_name != '' OR led_name IS NOT NULL AND led_name != '')
                            LIMIT 1
                        """
                        cursor.execute(fallback_query, (guid, alterid, voucher_key, vch_date, vch_no))
                        fallback_row = cursor.fetchone()
                        if fallback_row and fallback_row['party'] != '-':
                            particulars = fallback_row['party']
                    
                    # Step 4: Extract ONLY Sales ledger's Credit amount (same as monthly summary)
                    sales_debit = float(sales_line['credit'] or 0)  # Sales amount (credit side in DB)
                    sales_credit = 0  # Credit column empty in Tally
                    
                    # Get narration from the voucher
                    narration_query = """
                        SELECT MAX(vch_narration) as narration
                        FROM vouchers
                        WHERE company_guid = ?
                            AND company_alterid = ?
                            AND (
                                (COALESCE(NULLIF(TRIM(vch_mst_id), ''), vch_date || '|' || vch_no) = ?)
                                OR (vch_date = ? AND vch_no = ?)
                            )
                        LIMIT 1
                    """
                    cursor.execute(narration_query, (guid, alterid, voucher_key, vch_date, vch_no))
                    narration_row = cursor.fetchone()
                    narration = narration_row['narration'] if narration_row else ''
                    
                    voucher_list.append({
                        'date': vch_date,
                        'voucher_type': 'Sales',
                        'voucher_number': vch_no,
                        'particulars': particulars,
                        'debit': sales_debit,  # Sales amount shown in Debit column
                        'credit': sales_credit,  # Always 0 for Sales in Tally
                        'narration': narration or ''
                    })
            
            response_data = {
                'company_name': company_name,
                'from_date': from_date,
                'to_date': to_date,
                'monthly_summary': monthly_list,
                'vouchers': voucher_list,
                'total_debit': total_debit,
                'total_credit': total_credit,
                'grand_total': total_credit,  # Sales = Credit
                'total_vouchers': len(voucher_list)
            }
            
            conn.close()
            self.send_json_response(response_data)
            
        except Exception as e:
            print(f"[ERROR] send_sales_register_data: {e}")
            import traceback
            traceback.print_exc()
            self.send_error(500, f"Error fetching sales register data: {str(e)}")
    
    def send_sync_logs(self, path, parsed):
        """Send sync logs data as JSON."""
        try:
            from backend.database.sync_log_dao import SyncLogDAO
            from urllib.parse import parse_qs
            
            # Parse query parameters
            query_string = parsed.query if parsed.query else ''
            query_params = dict(parse_qs(query_string)) if query_string else {}
            company_guid = query_params.get('company_guid', [None])[0]
            company_alterid = query_params.get('company_alterid', [None])[0]
            log_level = query_params.get('log_level', [None])[0]
            sync_status = query_params.get('sync_status', [None])[0]
            limit = int(query_params.get('limit', ['50'])[0]) if query_params.get('limit') else 50
            offset = int(query_params.get('offset', ['0'])[0]) if query_params.get('offset') else 0
            
            # Connect to database
            db_path = os.path.join(get_base_dir(), "TallyConnectDb.db")
            if not os.path.exists(db_path):
                self.send_error(404, "Database not found")
                return
            
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            dao = SyncLogDAO(conn)
            
            # Get logs based on parameters
            if company_guid and company_alterid:
                # Get logs for specific company
                logs = dao.get_logs_by_company(company_guid, company_alterid, limit, offset)
                total_count = dao.get_log_count(company_guid, company_alterid, log_level, sync_status)
            else:
                # Get all logs with filters
                logs = dao.get_all_logs(limit, offset, log_level, sync_status)
                total_count = dao.get_log_count(None, None, log_level, sync_status)
            
            conn.close()
            
            response_data = {
                'logs': logs,
                'total_count': total_count,
                'limit': limit,
                'offset': offset,
                'has_more': (offset + len(logs)) < total_count
            }
            
            self.send_json_response(response_data)
            
        except Exception as e:
            print(f"[ERROR] send_sync_logs: {e}")
            import traceback
            traceback.print_exc()
            self.send_error(500, f"Error fetching sync logs: {str(e)}")
    
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
    portal_path = os.path.join(resource_dir, "frontend", "portal")
    
    # Update PORTAL_DIR global variable to the correct path
    global PORTAL_DIR
    if os.path.exists(portal_path):
        PORTAL_DIR = portal_path
        if not startup_mode:
            print(f"[INFO] Portal directory found: {portal_path}")
    else:
        # Try relative to current directory (for development)
        base_dir = get_base_dir()
        dev_portal_path = os.path.join(base_dir, "frontend", "portal")
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

