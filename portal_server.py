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

DB_FILE = "TallyConnectDb.db"
PORT = 8000
PORTAL_DIR = os.path.join(os.path.dirname(__file__), "reports", "portal")

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
    
    def handle_api(self, path, parsed):
        """Handle API requests."""
        try:
            # Companies list
            if path == '/api/companies.json':
                self.send_companies()
            
            # Ledgers for company
            elif path.startswith('/api/ledgers/'):
                self.send_ledgers(path)
            
            # Generate and serve report
            elif path.startswith('/api/reports/'):
                self.generate_and_serve_report(path)
            
            else:
                self.send_error(404, "API endpoint not found")
        
        except Exception as e:
            self.send_error(500, f"Server error: {str(e)}")
    
    def send_companies(self):
        """Send companies list."""
        conn = sqlite3.connect(DB_FILE)
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
        
        self.send_json_response(companies)
    
    def send_ledgers(self, path):
        """Send ledgers list for a company."""
        # Extract guid and alterid from path
        # Format: /api/ledgers/{guid}_{alterid}.json
        filename = path.replace('/api/ledgers/', '').replace('.json', '')
        
        # Try to find company by matching guid and alterid
        conn = sqlite3.connect(DB_FILE)
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
        
        conn = sqlite3.connect(DB_FILE)
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
        
        # Reconstruct guid (parts 1-5)
        if len(parts) >= 6:
            guid = '-'.join(parts[1:6])
            alterid = parts[6] if len(parts) > 6 else ''
        else:
            self.send_error(400, "Invalid report format")
            return
        
        # Get company name
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM companies WHERE guid=? AND alterid=?", (guid, alterid))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            self.send_error(404, "Company not found")
            return
        
        company_name = row[0]
        
        try:
            # Generate report on-demand
            if report_type == 'outstanding':
                report_path = self.generator.generate_outstanding_report(company_name, guid, alterid)
            
            elif report_type == 'dashboard':
                report_path = self.generator.generate_dashboard(company_name, guid, alterid)
            
            elif report_type == 'ledger':
                # Extract ledger name (parts after alterid)
                if len(parts) > 7:
                    # Get ledger name from database by matching
                    ledger_part = '_'.join(parts[7:])
                    
                    # Query database to find matching ledger
                    conn = sqlite3.connect(DB_FILE)
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
                    
                    report_path = self.generator.generate_ledger_report(
                        company_name, guid, alterid, ledger_name,
                        "01-04-2024", "31-12-2025"
                    )
                else:
                    self.send_error(400, "Ledger name missing")
                    return
            else:
                self.send_error(400, f"Unknown report type: {report_type}")
                return
            
            # Read and serve the generated report
            with open(report_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        
        except Exception as e:
            self.send_error(500, f"Error generating report: {str(e)}")
    
    def send_json_response(self, data):
        """Send JSON response."""
        json_data = json.dumps(data, indent=2)
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json_data.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Suppress default logging."""
        pass

def start_server():
    """Start the portal server."""
    os.chdir(PORTAL_DIR)
    
    try:
        with socketserver.TCPServer(("", PORT), PortalHandler) as httpd:
            print("="*60)
            print("TallyConnect Portal Server")
            print("="*60)
            print(f"\nServer running at: http://localhost:{PORT}")
            print(f"Portal URL: http://localhost:{PORT}/index.html")
            print("\nPress Ctrl+C to stop the server")
            print("="*60)
            print()
            
            # Open browser automatically
            url = f"http://localhost:{PORT}/index.html"
            webbrowser.open(url)
            
            # Start server
            httpd.serve_forever()
    
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"\n[ERROR] Port {PORT} is already in use!")
            print(f"Please close other applications using port {PORT}")
            print("Or modify PORT in portal_server.py")
        else:
            print(f"\n[ERROR] {e}")

if __name__ == "__main__":
    start_server()

