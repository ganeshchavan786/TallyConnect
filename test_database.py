#!/usr/bin/env python3
"""
Test Database Connection and Queries
=====================================
Quick script to test database and check ledger data
"""

import sqlite3
import os

DB_FILE = "TallyConnectDb.db"

def test_database():
    """Test database connection and queries."""
    
    print("="*60)
    print("TallyConnect Database Test")
    print("="*60)
    print()
    
    # Check if database exists
    if not os.path.exists(DB_FILE):
        print(f"[ERROR] Database not found: {DB_FILE}")
        print(f"Current directory: {os.getcwd()}")
        return
    
    print(f"[OK] Database found: {DB_FILE}")
    print(f"Size: {os.path.getsize(DB_FILE) / 1024:.2f} KB")
    print()
    
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Test 1: Check companies
        print("="*60)
        print("TEST 1: Companies")
        print("="*60)
        cursor.execute("SELECT name, guid, alterid, status, total_records FROM companies")
        companies = cursor.fetchall()
        print(f"Total companies: {len(companies)}")
        for row in companies:
            print(f"  - {row['name']} (Status: {row['status']}, Records: {row['total_records']})")
            print(f"    GUID: {row['guid']}")
            print(f"    AlterID: {row['alterid']}")
        print()
        
        if not companies:
            print("[WARNING] No companies found!")
            conn.close()
            return
        
        # Get first company for testing
        test_company = companies[0]
        test_guid = test_company['guid']
        test_alterid = test_company['alterid']
        test_name = test_company['name']
        
        print(f"Using company for testing: {test_name}")
        print()
        
        # Test 2: Check vouchers count
        print("="*60)
        print("TEST 2: Vouchers Count")
        print("="*60)
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM vouchers
            WHERE company_guid = ? AND company_alterid = ?
        """, (test_guid, test_alterid))
        voucher_count = cursor.fetchone()['total']
        print(f"Total vouchers for {test_name}: {voucher_count}")
        print()
        
        # Test 3: Check ledgers (distinct party names)
        print("="*60)
        print("TEST 3: Ledgers (Distinct Party Names)")
        print("="*60)
        cursor.execute("""
            SELECT DISTINCT vch_party_name as name, COUNT(*) as count
            FROM vouchers
            WHERE company_guid = ? AND company_alterid = ?
            AND vch_party_name IS NOT NULL AND vch_party_name != ''
            GROUP BY vch_party_name
            ORDER BY vch_party_name
        """, (test_guid, test_alterid))
        ledgers = cursor.fetchall()
        print(f"Total ledgers: {len(ledgers)}")
        print()
        print("First 10 ledgers:")
        for i, row in enumerate(ledgers[:10], 1):
            print(f"  {i}. {row['name']} (Transactions: {row['count']})")
        if len(ledgers) > 10:
            print(f"  ... and {len(ledgers) - 10} more")
        print()
        
        # Test 4: Test specific ledger (first one)
        if ledgers:
            test_ledger = ledgers[0]['name']
            print("="*60)
            print(f"TEST 4: Test Ledger - '{test_ledger}'")
            print("="*60)
            
            # Check vouchers for this ledger
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM vouchers
                WHERE company_guid = ? AND company_alterid = ?
                AND vch_party_name = ?
            """, (test_guid, test_alterid, test_ledger))
            ledger_voucher_count = cursor.fetchone()['count']
            print(f"Vouchers for '{test_ledger}': {ledger_voucher_count}")
            
            # Check date range
            cursor.execute("""
                SELECT 
                    MIN(vch_date) as min_date,
                    MAX(vch_date) as max_date
                FROM vouchers
                WHERE company_guid = ? AND company_alterid = ?
                AND vch_party_name = ?
            """, (test_guid, test_alterid, test_ledger))
            date_range = cursor.fetchone()
            print(f"Date range: {date_range['min_date']} to {date_range['max_date']}")
            print()
            
            # Test 5: Check if report can be generated
            print("="*60)
            print("TEST 5: Report Generation Test")
            print("="*60)
            try:
                from reports import ReportGenerator
                generator = ReportGenerator(DB_FILE)
                
                print(f"Generating ledger report for: {test_name} - {test_ledger}")
                report_path = generator.generate_ledger_report(
                    test_name,
                    test_guid,
                    test_alterid,
                    test_ledger,
                    "01-04-2024",
                    "31-12-2025"
                )
                
                if report_path and os.path.exists(report_path):
                    print(f"[SUCCESS] Report generated: {report_path}")
                    print(f"File size: {os.path.getsize(report_path) / 1024:.2f} KB")
                else:
                    print(f"[ERROR] Report not generated or file not found")
                    print(f"Report path: {report_path}")
            except Exception as e:
                print(f"[ERROR] Report generation failed: {e}")
                import traceback
                traceback.print_exc()
        
        # Test 6: Check voucher dates
        print()
        print("="*60)
        print("TEST 6: Voucher Date Range")
        print("="*60)
        cursor.execute("""
            SELECT 
                MIN(vch_date) as min_date,
                MAX(vch_date) as max_date,
                COUNT(DISTINCT DATE(vch_date)) as unique_dates
            FROM vouchers
            WHERE company_guid = ? AND company_alterid = ?
        """, (test_guid, test_alterid))
        date_info = cursor.fetchone()
        print(f"Min date: {date_info['min_date']}")
        print(f"Max date: {date_info['max_date']}")
        print(f"Unique dates: {date_info['unique_dates']}")
        print()
        
        conn.close()
        
        print("="*60)
        print("TEST COMPLETE")
        print("="*60)
        
    except Exception as e:
        print(f"[ERROR] Database test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_database()
    input("\nPress Enter to exit...")

