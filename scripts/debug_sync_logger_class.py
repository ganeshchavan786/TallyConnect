#!/usr/bin/env python3
"""
Debug Script - Using Actual SyncLogger Class
=============================================

Tests the actual SyncLogger class to identify issues.
"""

import os
import sys
import time

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.utils.sync_logger import SyncLogger, get_sync_logger

def debug_sync_logger():
    """Debug using actual SyncLogger class."""
    print("=" * 60)
    print("SYNC LOGGER CLASS DEBUGGER")
    print("=" * 60)
    print()
    
    # Test 1: Create logger
    print("[TEST 1] Creating SyncLogger...")
    logger = get_sync_logger(db_lock=None)
    print(f"  Logger created: {logger}")
    print(f"  DB path: {logger.db_path}")
    print()
    
    # Test 2: Log a message
    print("[TEST 2] Logging message...")
    log_id = logger.log(
        company_guid="debug-guid-003",
        company_alterid="999",
        company_name="Debug Test Company 3",
        log_level="INFO",
        message="Debug test from SyncLogger class",
        details="Testing actual SyncLogger",
        sync_status="started",
        records_synced=0
    )
    print(f"  Log ID returned: {log_id}")
    print()
    
    # Test 3: Wait and verify
    print("[TEST 3] Waiting and verifying...")
    time.sleep(1.0)  # Wait longer
    
    import sqlite3
    db_path = logger.db_path
    verify_conn = sqlite3.connect(db_path, check_same_thread=False, timeout=10.0)
    verify_cur = verify_conn.cursor()
    verify_cur.execute("SELECT id FROM sync_logs WHERE id = ?", (log_id,))
    verify_result = verify_cur.fetchone()
    verify_cur.close()
    
    # Check max ID
    max_cur = verify_conn.cursor()
    max_cur.execute("SELECT MAX(id) FROM sync_logs")
    max_id = max_cur.fetchone()[0]
    max_cur.close()
    verify_conn.close()
    
    if verify_result:
        print(f"  [OK] Log found: ID {verify_result[0]}")
    else:
        print(f"  [ERROR] Log NOT found!")
    
    print(f"  Max ID: {max_id}")
    print(f"  Test log ID: {log_id}")
    
    if max_id and max_id >= log_id:
        print(f"  [OK] Max ID includes test log")
    else:
        print(f"  [ERROR] Max ID does NOT include test log!")
    
    print()
    
    # Test 4: Multiple logs
    print("[TEST 4] Multiple logs...")
    log_ids = []
    for i in range(3):
        log_id = logger.log(
            company_guid="debug-guid-004",
            company_alterid="999",
            company_name="Debug Test Company 4",
            log_level="INFO",
            message=f"Debug test {i+1}",
            details=f"Testing multiple logs {i+1}",
            sync_status="started",
            records_synced=0
        )
        log_ids.append(log_id)
        print(f"  Log {i+1} ID: {log_id}")
        time.sleep(0.2)
    
    print()
    
    # Verify all
    print("[TEST 5] Verifying all logs...")
    time.sleep(1.0)
    
    verify_conn = sqlite3.connect(db_path, check_same_thread=False, timeout=10.0)
    all_ok = True
    for log_id in log_ids:
        verify_cur = verify_conn.cursor()
        verify_cur.execute("SELECT id FROM sync_logs WHERE id = ?", (log_id,))
        verify_result = verify_cur.fetchone()
        verify_cur.close()
        
        if verify_result:
            print(f"  [OK] Log {log_id} found")
        else:
            print(f"  [ERROR] Log {log_id} NOT found!")
            all_ok = False
    
    # Check max ID
    max_cur = verify_conn.cursor()
    max_cur.execute("SELECT MAX(id) FROM sync_logs")
    max_id = max_cur.fetchone()[0]
    max_cur.close()
    verify_conn.close()
    
    print(f"  Max ID: {max_id}")
    
    if all_ok:
        print("  [OK] All logs persisted")
    else:
        print("  [ERROR] Some logs did NOT persist!")
    
    print()
    
    # Cleanup
    print("[CLEANUP] Deleting test logs...")
    cleanup_conn = sqlite3.connect(db_path, check_same_thread=False, timeout=10.0)
    cleanup_cur = cleanup_conn.cursor()
    for log_id in log_ids + [log_id]:
        cleanup_cur.execute("DELETE FROM sync_logs WHERE id = ?", (log_id,))
    cleanup_conn.commit()
    cleanup_conn.close()
    print("[CLEANUP] [OK] Test logs deleted")
    
    print()
    print("=" * 60)
    print("DEBUG COMPLETE")
    print("=" * 60)
    print()
    print("ANALYSIS:")
    print("  If all tests pass, SyncLogger is working correctly.")
    print("  If tests fail, check:")
    print("    1. Connection lifecycle in sync_logger.py")
    print("    2. WAL checkpoint timing")
    print("    3. Verification logic")

if __name__ == "__main__":
    debug_sync_logger()

