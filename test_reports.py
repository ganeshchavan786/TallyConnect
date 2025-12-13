#!/usr/bin/env python3
"""
Test script for report generation
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from reports import ReportGenerator

DB_FILE = "TallyConnectDb.db"

def test_reports():
    """Test all three report types."""
    
    # Company details from database
    company_name = "Vrushali Infotech Pvt Ltd. 25-26"
    guid = "8fdcfdd1-71cc-4873-99c6-95735225388e"
    alterid = "102209.0"
    
    print("="*60)
    print("TallyConnect - Reports Testing")
    print("="*60)
    print(f"\nCompany: {company_name}")
    print(f"GUID: {guid}")
    print(f"AlterID: {alterid}\n")
    
    generator = ReportGenerator(DB_FILE)
    
    # Test 1: Outstanding Report
    print("\n[1/3] Testing Outstanding Report...")
    try:
        path = generator.generate_outstanding_report(company_name, guid, alterid)
        print(f"[OK] Outstanding report generated: {os.path.basename(path)}")
        print(f"  Location: {path}")
    except Exception as e:
        print(f"[ERROR] Outstanding report failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Ledger Report
    print("\n[2/3] Testing Ledger Report...")
    try:
        # Get first party from database
        import sqlite3
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT vch_party_name 
            FROM vouchers 
            WHERE company_guid=? AND company_alterid=? 
            AND vch_party_name IS NOT NULL AND vch_party_name != ''
            LIMIT 1
        """, (guid, alterid))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            party_name = row[0]
            path = generator.generate_ledger_report(
                company_name, guid, alterid, party_name, 
                "01-04-2024", "31-12-2025"
            )
            print(f"[OK] Ledger report generated for: {party_name}")
            print(f"  Location: {os.path.basename(path)}")
        else:
            print("[WARNING] No parties found in database")
    except Exception as e:
        print(f"[ERROR] Ledger report failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Dashboard
    print("\n[3/3] Testing Dashboard...")
    try:
        path = generator.generate_dashboard(company_name, guid, alterid)
        print(f"[OK] Dashboard generated: {os.path.basename(path)}")
        print(f"  Location: {path}")
    except Exception as e:
        print(f"[ERROR] Dashboard failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)
    print("Testing completed!")
    print("="*60)
    print("\nCheck the 'generated_reports' folder for output files.")
    print("Reports should have opened automatically in your browser.\n")

if __name__ == "__main__":
    test_reports()

