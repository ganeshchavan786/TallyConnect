#!/usr/bin/env python3
"""
Portal Diagnostic Tool
======================

Comprehensive diagnostic tool to identify issues with the portal UI.
Checks database, API endpoints, and data availability.
"""

import os
import sys
import sqlite3
import json
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_section(title):
    """Print a section header."""
    print(f"\n{'-' * 70}")
    print(f"  {title}")
    print(f"{'-' * 70}")


def check_database():
    """Check database file and connection."""
    print_header("DATABASE CHECK")
    
    # Get database path
    if getattr(sys, 'frozen', False):
        db_path = os.path.join(os.path.dirname(sys.executable), "TallyConnectDb.db")
    else:
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "TallyConnectDb.db")
    
    print(f"Database Path: {db_path}")
    print(f"Exists: {'YES' if os.path.exists(db_path) else 'NO'}")
    
    if not os.path.exists(db_path):
        print("\n[WARNING] ISSUE: Database file not found!")
        print("   Solution: Run TallyConnect app and sync at least one company.")
        return None
    
    # Check file size
    size = os.path.getsize(db_path)
    print(f"Size: {size:,} bytes ({size / 1024:.2f} KB)")
    
    if size == 0:
        print("\n[WARNING] ISSUE: Database file is empty!")
        return None
    
    # Try to connect
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print("Connection: SUCCESS")
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Tables: {', '.join(tables) if tables else 'None'}")
        
        required_tables = ['companies', 'vouchers']
        missing_tables = [t for t in required_tables if t not in tables]
        if missing_tables:
            print(f"\n[WARNING] ISSUE: Missing tables: {', '.join(missing_tables)}")
            conn.close()
            return None
        
        conn.close()
        return db_path
        
    except Exception as e:
        print(f"Connection: FAILED")
        print(f"Error: {e}")
        return None


def check_companies(db_path):
    """Check companies in database."""
    print_section("COMPANIES CHECK")
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Total companies
        cursor.execute("SELECT COUNT(*) FROM companies")
        total = cursor.fetchone()[0]
        print(f"Total Companies: {total}")
        
        # Synced companies
        cursor.execute("SELECT COUNT(*) FROM companies WHERE status='synced'")
        synced = cursor.fetchone()[0]
        print(f"Synced Companies: {synced}")
        
        if synced == 0:
            print("\n[WARNING] ISSUE: No synced companies found!")
            print("   Solution: Open TallyConnect app and sync at least one company.")
            conn.close()
            return []
        
        # Get synced companies details
        cursor.execute("""
            SELECT name, guid, alterid, status, total_records 
            FROM companies 
            WHERE status='synced'
            ORDER BY name
        """)
        
        companies = []
        print(f"\n📋 Synced Companies ({synced}):")
        for idx, row in enumerate(cursor.fetchall(), 1):
            company = {
                'name': row['name'],
                'guid': row['guid'],
                'alterid': str(row['alterid']),
                'status': row['status'],
                'total_records': row['total_records'] or 0
            }
            companies.append(company)
            print(f"  {idx}. {company['name']}")
            print(f"     GUID: {company['guid']}")
            print(f"     AlterID: {company['alterid']}")
            print(f"     Records: {company['total_records']}")
        
        conn.close()
        return companies
        
    except Exception as e:
        print(f"[ERROR] Error checking companies: {e}")
        return []


def check_vouchers(db_path, companies):
    """Check vouchers for each company."""
    print_section("VOUCHERS CHECK")
    
    if not companies:
        print("[WARNING] No companies to check vouchers for.")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        for company in companies:
            guid = company['guid']
            alterid = company['alterid']
            
            # Count vouchers
            cursor.execute("""
                SELECT COUNT(*) FROM vouchers 
                WHERE company_guid = ? AND company_alterid = ?
            """, (guid, alterid))
            count = cursor.fetchone()[0]
            
            print(f"\n{company['name']}:")
            print(f"  Total Vouchers: {count}")
            
            if count == 0:
                print(f"  [WARNING] ISSUE: No vouchers found for this company!")
                print(f"     Solution: Re-sync this company in TallyConnect app.")
            else:
                # Count distinct ledgers
                cursor.execute("""
                    SELECT COUNT(DISTINCT vch_party_name) 
                    FROM vouchers 
                    WHERE company_guid = ? AND company_alterid = ?
                    AND vch_party_name IS NOT NULL AND vch_party_name != ''
                """, (guid, alterid))
                ledger_count = cursor.fetchone()[0]
                print(f"  Distinct Ledgers: {ledger_count}")
                
                if ledger_count == 0:
                    print(f"  [WARNING] ISSUE: No ledgers found (all vouchers have null/empty party names)!")
        
        conn.close()
        
    except Exception as e:
        print(f"[ERROR] Error checking vouchers: {e}")


def check_api_endpoints():
    """Check if API endpoints would work."""
    print_section("API ENDPOINTS CHECK")
    
    print("Testing API endpoint logic...")
    
    # Check if portal_server can be imported
    try:
        from backend.portal_server import get_base_dir, DB_FILE
        print("Portal server module: OK")
        
        base_dir = get_base_dir()
        print(f"   Base directory: {base_dir}")
        
        db_file = DB_FILE
        print(f"   DB file path: {db_file}")
        print(f"   DB file exists: {'YES' if os.path.exists(db_file) else 'NO'}")
        
    except Exception as e:
        print(f"Portal server module: FAILED")
        print(f"   Error: {e}")


def check_portal_files():
    """Check if portal frontend files exist."""
    print_section("PORTAL FILES CHECK")
    
    # Get portal directory
    if getattr(sys, 'frozen', False):
        try:
            portal_dir = os.path.join(sys._MEIPASS, "frontend", "portal")
        except:
            portal_dir = os.path.join(os.path.dirname(sys.executable), "frontend", "portal")
    else:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        portal_dir = os.path.join(project_root, "frontend", "portal")
    
    print(f"Portal Directory: {portal_dir}")
    print(f"Exists: {'YES' if os.path.exists(portal_dir) else 'NO'}")
    
    if not os.path.exists(portal_dir):
        print("\n[WARNING] ISSUE: Portal directory not found!")
        return
    
    # Check index.html
    index_file = os.path.join(portal_dir, "index.html")
    print(f"\nindex.html: {'EXISTS' if os.path.exists(index_file) else 'MISSING'}")
    
    if os.path.exists(index_file):
        size = os.path.getsize(index_file)
        print(f"   Size: {size:,} bytes")


def generate_test_data(db_path, companies):
    """Generate test API response data."""
    print_section("TEST API RESPONSES")
    
    if not companies:
        print("[WARNING] No companies to generate test data for.")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        for company in companies:
            guid = company['guid']
            alterid = company['alterid']
            
            print(f"\n{company['name']}:")
            
            # Test companies.json response
            print("  Companies API response:")
            company_data = {
                'name': company['name'],
                'guid': company['guid'],
                'alterid': company['alterid'],
                'status': company['status'],
                'total_records': company['total_records']
            }
            print(f"    {json.dumps(company_data, indent=6)}")
            
            # Test ledgers API response
            cursor.execute("""
                SELECT DISTINCT vch_party_name as name, COUNT(*) as count
                FROM vouchers
                WHERE company_guid = ? AND company_alterid = ?
                AND vch_party_name IS NOT NULL AND vch_party_name != ''
                GROUP BY vch_party_name
                ORDER BY vch_party_name
                LIMIT 5
            """, (guid, alterid))
            
            ledgers = []
            for row in cursor.fetchall():
                ledgers.append({
                    'name': row['name'],
                    'count': row['count']
                })
            
            print(f"  Ledgers API response ({len(ledgers)} ledgers):")
            if ledgers:
                for ledger in ledgers[:3]:  # Show first 3
                    print(f"    - {ledger['name']}: {ledger['count']} transactions")
                if len(ledgers) > 3:
                    print(f"    ... and {len(ledgers) - 3} more")
            else:
                    print("    [WARNING] No ledgers found!")
        
        conn.close()
        
    except Exception as e:
        print(f"[ERROR] Error generating test data: {e}")


def print_recommendations():
    """Print troubleshooting recommendations."""
    print_header("TROUBLESHOOTING RECOMMENDATIONS")
    
    print("""
If data is not showing in the portal UI, check:

1. [OK] Database exists and has data
   - Run this diagnostic tool to verify
   - If database is empty, sync companies in TallyConnect app

2. [OK] Portal server is running
   - Check if server is running on localhost:8000
   - Open browser console (F12) and check Network tab
   - Look for API calls to /api/companies.json

3. [OK] Browser console errors
   - Press F12 in browser
   - Check Console tab for JavaScript errors
   - Check Network tab for failed API requests

4. [OK] Company status is 'synced'
   - Only companies with status='synced' are shown
   - Check in TallyConnect app if company sync completed

5. [OK] Vouchers exist for company
   - Each company must have vouchers in database
   - Ledgers are generated from voucher party names

6. [OK] API endpoints are accessible
   - Try: http://localhost:8000/api/companies.json
   - Should return JSON array of companies
   - If 404, check server is running
   - If 500, check server console for errors

7. [OK] CORS and headers
   - API responses should have CORS headers
   - Check browser Network tab for response headers

Common Issues:
- Database not found → Run TallyConnect app first
- No synced companies → Sync at least one company
- No vouchers → Re-sync the company
- Server not running → Start portal server
- Port conflict → Check if port 8000 is available
""")


def main():
    """Run all diagnostic checks."""
    print("\n" + "=" * 70)
    print("  TALLYCONNECT PORTAL DIAGNOSTIC TOOL")
    print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 70)
    
    # Check database
    db_path = check_database()
    if not db_path:
        print_recommendations()
        return
    
    # Check companies
    companies = check_companies(db_path)
    
    # Check vouchers
    check_vouchers(db_path, companies)
    
    # Check API endpoints
    check_api_endpoints()
    
    # Check portal files
    check_portal_files()
    
    # Generate test data
    generate_test_data(db_path, companies)
    
    # Print recommendations
    print_recommendations()
    
    print("\n" + "=" * 70)
    print("  DIAGNOSTIC COMPLETE")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()

