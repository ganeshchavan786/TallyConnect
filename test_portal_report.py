#!/usr/bin/env python3
"""
Test Portal Report Generation
==============================
Simulates what portal server does when generating ledger report
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from reports import ReportGenerator
from reports.utils import get_report_path

DB_FILE = "TallyConnectDb.db"

def test_portal_report():
    """Test report generation as portal server does."""
    
    print("="*60)
    print("Portal Report Generation Test")
    print("="*60)
    print()
    
    # Simulate portal server directory change
    original_dir = os.getcwd()
    portal_dir = os.path.join(original_dir, "reports", "portal")
    
    print(f"Original directory: {original_dir}")
    print(f"Portal directory: {portal_dir}")
    print()
    
    # Test company and ledger (from database test)
    company_name = "Vrushali Infotech Pvt Ltd. 25-26"
    guid = "8fdcfdd1-71cc-4873-99c6-95735225388e"
    alterid = "102209.0"
    ledger_name = "A P HOLDINGS PVT.LTD"
    
    print(f"Company: {company_name}")
    print(f"Ledger: {ledger_name}")
    print()
    
    # Test 1: Generate report from project root
    print("="*60)
    print("TEST 1: Generate from project root")
    print("="*60)
    os.chdir(original_dir)
    print(f"Current directory: {os.getcwd()}")
    
    generator = ReportGenerator(DB_FILE)
    report_path = generator.generate_ledger_report(
        company_name, guid, alterid, ledger_name,
        "01-04-2024", "31-12-2025"
    )
    
    print(f"Report path: {report_path}")
    print(f"Absolute path: {os.path.abspath(report_path)}")
    print(f"File exists: {os.path.exists(report_path)}")
    if os.path.exists(report_path):
        print(f"File size: {os.path.getsize(report_path) / 1024:.2f} KB")
    print()
    
    # Test 2: Try to read from portal directory
    print("="*60)
    print("TEST 2: Read from portal directory")
    print("="*60)
    if os.path.exists(portal_dir):
        os.chdir(portal_dir)
        print(f"Changed to: {os.getcwd()}")
        
        # Try to read the report
        abs_report_path = os.path.abspath(report_path)
        print(f"Trying to read: {abs_report_path}")
        print(f"File exists: {os.path.exists(abs_report_path)}")
        
        if os.path.exists(abs_report_path):
            try:
                with open(abs_report_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                print(f"[SUCCESS] File readable! Content length: {len(content)} bytes")
            except Exception as e:
                print(f"[ERROR] Cannot read file: {e}")
        else:
            print("[ERROR] File not found from portal directory!")
            print(f"Looking for: {abs_report_path}")
            
            # Try relative path
            rel_path = os.path.relpath(abs_report_path, portal_dir)
            print(f"Relative path: {rel_path}")
            print(f"Relative exists: {os.path.exists(rel_path)}")
    else:
        print(f"[WARNING] Portal directory not found: {portal_dir}")
    
    print()
    
    # Test 3: Check get_report_path
    print("="*60)
    print("TEST 3: Check get_report_path function")
    print("="*60)
    os.chdir(original_dir)
    test_path = get_report_path('ledger', f"{company_name}_{ledger_name}")
    print(f"Generated path: {test_path}")
    print(f"Absolute: {os.path.abspath(test_path)}")
    print(f"Is absolute: {os.path.isabs(test_path)}")
    print()
    
    # Test 4: Check if portal server can access
    print("="*60)
    print("TEST 4: Portal Server Access Simulation")
    print("="*60)
    if os.path.exists(portal_dir):
        os.chdir(portal_dir)
        print(f"Portal server directory: {os.getcwd()}")
        
        # Try to access report using absolute path
        abs_path = os.path.abspath(report_path)
        print(f"Report absolute path: {abs_path}")
        print(f"Can access: {os.path.exists(abs_path)}")
        
        if os.path.exists(abs_path):
            print("[SUCCESS] Portal server can access report!")
        else:
            print("[ERROR] Portal server cannot access report!")
            print("This is the problem!")
    
    # Restore directory
    os.chdir(original_dir)
    
    print()
    print("="*60)
    print("TEST COMPLETE")
    print("="*60)

if __name__ == "__main__":
    test_portal_report()
    input("\nPress Enter to exit...")

