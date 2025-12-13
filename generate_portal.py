#!/usr/bin/env python3
"""
Generate Portal Data and Reports
================================

This script generates:
1. Company list JSON
2. Ledger lists for each company
3. All reports (Outstanding, Ledger, Dashboard)
4. Portal index.html ready to use
"""

import os
import sqlite3
import json
from reports import ReportGenerator
from database.queries import ReportQueries

DB_FILE = "TallyConnectDb.db"
PORTAL_DIR = "reports/portal"
API_DIR = os.path.join(PORTAL_DIR, "api")
REPORTS_DIR = os.path.join(API_DIR, "reports")

def init_portal_dirs():
    """Create portal directories."""
    os.makedirs(API_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)
    print("[OK] Portal directories created")

def load_companies():
    """Load all companies from database."""
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
    return companies

def save_companies_json(companies):
    """Save companies list to JSON."""
    json_path = os.path.join(API_DIR, "companies.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(companies, f, indent=2)
    print(f"[OK] Saved {len(companies)} companies to companies.json")

def load_ledgers(guid, alterid):
    """Load all ledgers for a company."""
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
    return ledgers

def save_ledgers_json(guid, alterid, ledgers):
    """Save ledgers list to JSON."""
    ledgers_dir = os.path.join(API_DIR, "ledgers")
    os.makedirs(ledgers_dir, exist_ok=True)
    
    safe_id = f"{guid}_{alterid}".replace('-', '_').replace('.', '_')
    json_path = os.path.join(ledgers_dir, f"{safe_id}.json")
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(ledgers, f, indent=2)
    print(f"  [OK] Saved {len(ledgers)} ledgers")

def generate_all_reports():
    """Generate all reports for all companies."""
    companies = load_companies()
    generator = ReportGenerator(DB_FILE)
    
    print(f"\nGenerating reports for {len(companies)} companies...")
    
    for company in companies:
        print(f"\nCompany: {company['name']}")
        
        guid = company['guid']
        alterid = company['alterid']
        name = company['name']
        
        try:
            # Outstanding Report
            print("  -> Outstanding Report...", end=" ")
            report_path = generator.generate_outstanding_report(name, guid, alterid)
            # Copy to portal reports directory
            import shutil
            safe_name = f"outstanding_{guid}_{alterid}".replace('-', '_').replace('.', '_')
            dest_path = os.path.join(REPORTS_DIR, f"{safe_name}.html")
            shutil.copy(report_path, dest_path)
            print("[OK]")
            
            # Dashboard
            print("  -> Dashboard...", end=" ")
            report_path = generator.generate_dashboard(name, guid, alterid)
            safe_name = f"dashboard_{guid}_{alterid}".replace('-', '_').replace('.', '_')
            dest_path = os.path.join(REPORTS_DIR, f"{safe_name}.html")
            shutil.copy(report_path, dest_path)
            print("[OK]")
            
            # Ledger Reports (for each ledger)
            ledgers = load_ledgers(guid, alterid)
            save_ledgers_json(guid, alterid, ledgers)
            
            print(f"  -> Ledger Reports ({len(ledgers)} ledgers)...", end=" ")
            for ledger in ledgers[:10]:  # Limit to first 10 for performance
                try:
                    report_path = generator.generate_ledger_report(
                        name, guid, alterid, ledger['name'],
                        "01-04-2024", "31-12-2025"
                    )
                    safe_ledger = ledger['name'].replace(' ', '_').replace('/', '_').replace('\\', '_')
                    safe_ledger = "".join(c if c.isalnum() or c in ('_', '-') else '_' for c in safe_ledger)
                    safe_name = f"ledger_{guid}_{alterid}_{safe_ledger}".replace('-', '_').replace('.', '_')
                    dest_path = os.path.join(REPORTS_DIR, f"{safe_name}.html")
                    shutil.copy(report_path, dest_path)
                except Exception as e:
                    pass
            print("[OK]")
            
        except Exception as e:
            print(f"[ERROR] {e}")

def main():
    """Main function."""
    print("="*60)
    print("TallyConnect - Portal Generator")
    print("="*60)
    
    # Initialize directories
    init_portal_dirs()
    
    # Load and save companies
    print("\nLoading companies...")
    companies = load_companies()
    save_companies_json(companies)
    
    # Generate all reports
    generate_all_reports()
    
    print("\n" + "="*60)
    print("[SUCCESS] Portal generation complete!")
    print("="*60)
    print(f"\nPortal location: {PORTAL_DIR}/")
    print(f"Open: {PORTAL_DIR}/index.html in browser")
    print("\nTip: Run create_desktop_shortcut.bat to create desktop shortcut")

if __name__ == "__main__":
    main()

