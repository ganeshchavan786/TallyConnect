#!/usr/bin/env python3
"""
Debug Script for Sync Logs Commit Issue
========================================

This script helps identify why commits are failing.
Tests the actual commit process step by step.
"""

import sqlite3
import os
import sys
import time
from datetime import datetime, timezone

def get_base_dir():
    """Get base directory."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def debug_commit_process():
    """Debug the commit process step by step."""
    base_dir = get_base_dir()
    db_path = os.path.join(base_dir, "TallyConnectDb.db")
    
    print("=" * 60)
    print("SYNC LOGS COMMIT DEBUGGER")
    print("=" * 60)
    print(f"Database: {db_path}\n")
    
    if not os.path.exists(db_path):
        print(f"[ERROR] Database not found: {db_path}")
        return
    
    # Test 1: Check WAL mode
    print("[TEST 1] Checking WAL mode...")
    try:
        conn1 = sqlite3.connect(db_path, check_same_thread=False, timeout=10.0)
        cur1 = conn1.cursor()
        cur1.execute("PRAGMA journal_mode")
        mode = cur1.fetchone()[0]
        print(f"  Journal mode: {mode}")
        
        cur1.execute("PRAGMA synchronous")
        sync = cur1.fetchone()[0]
        print(f"  Synchronous: {sync}")
        
        cur1.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        checkpoint = cur1.fetchone()
        print(f"  WAL checkpoint: {checkpoint}")
        
        conn1.close()
        print("  [OK] WAL mode check complete\n")
    except Exception as e:
        print(f"  [ERROR] WAL mode check failed: {e}\n")
        return
    
    # Test 2: Insert a test log
    print("[TEST 2] Inserting test log...")
    test_log_id = None
    try:
        conn2 = sqlite3.connect(db_path, check_same_thread=False, timeout=10.0)
        # Enable WAL
        conn2.execute("PRAGMA journal_mode=WAL")
        conn2.commit()
        
        # Insert test log
        created_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        cur2 = conn2.cursor()
        cur2.execute("""
            INSERT INTO sync_logs 
            (company_guid, company_alterid, company_name, log_level, log_message, 
             log_details, sync_status, records_synced, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "debug-guid-001",
            "999",
            "Debug Test Company",
            "INFO",
            "Debug test log",
            "Testing commit process",
            "started",
            0,
            created_at
        ))
        test_log_id = cur2.lastrowid
        print(f"  Log ID returned: {test_log_id}")
        
        # Commit
        conn2.commit()
        print("  [OK] Commit called")
        
        # WAL checkpoint
        checkpoint_cur = conn2.cursor()
        checkpoint_cur.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        checkpoint_result = checkpoint_cur.fetchone()
        checkpoint_cur.close()
        print(f"  WAL checkpoint: {checkpoint_result}")
        
        # Verify immediately with same connection
        verify_cur = conn2.cursor()
        verify_cur.execute("SELECT id FROM sync_logs WHERE id = ?", (test_log_id,))
        verify_result = verify_cur.fetchone()
        verify_cur.close()
        
        if verify_result:
            print(f"  [OK] Log found in SAME connection: ID {verify_result[0]}")
        else:
            print(f"  [ERROR] Log NOT found in SAME connection!")
        
        conn2.close()
        print("  [OK] Connection closed\n")
    except Exception as e:
        print(f"  [ERROR] Insert failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    if not test_log_id:
        print("[ERROR] No log ID returned, cannot continue tests")
        return
    
    # Test 3: Wait and verify with NEW connection
    print("[TEST 3] Verifying with NEW connection (after wait)...")
    time.sleep(0.5)  # Wait for WAL sync
    try:
        conn3 = sqlite3.connect(db_path, check_same_thread=False, timeout=10.0)
        
        # WAL checkpoint in new connection
        checkpoint_cur = conn3.cursor()
        checkpoint_cur.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        checkpoint_result = checkpoint_cur.fetchone()
        checkpoint_cur.close()
        print(f"  WAL checkpoint: {checkpoint_result}")
        
        time.sleep(0.1)
        
        # Verify
        verify_cur = conn3.cursor()
        verify_cur.execute("SELECT id FROM sync_logs WHERE id = ?", (test_log_id,))
        verify_result = verify_cur.fetchone()
        verify_cur.close()
        
        if verify_result:
            print(f"  [OK] Log found in NEW connection: ID {verify_result[0]}")
        else:
            print(f"  [ERROR] Log NOT found in NEW connection!")
            print(f"  [DEBUG] This indicates commit is NOT persisting!")
        
        # Check max ID
        max_cur = conn3.cursor()
        max_cur.execute("SELECT MAX(id) FROM sync_logs")
        max_id = max_cur.fetchone()[0]
        max_cur.close()
        print(f"  Max ID in database: {max_id}")
        print(f"  Test log ID: {test_log_id}")
        
        if max_id and max_id >= test_log_id:
            print(f"  [OK] Max ID includes test log")
        else:
            print(f"  [ERROR] Max ID does NOT include test log!")
        
        conn3.close()
        print("  [OK] Verification complete\n")
    except Exception as e:
        print(f"  [ERROR] Verification failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 4: Check WAL file
    print("[TEST 4] Checking WAL file...")
    wal_path = db_path + "-wal"
    shm_path = db_path + "-shm"
    
    if os.path.exists(wal_path):
        wal_size = os.path.getsize(wal_path)
        print(f"  WAL file exists: {wal_path}")
        print(f"  WAL file size: {wal_size} bytes")
        if wal_size > 0:
            print(f"  [WARNING] WAL file has data - checkpoint may not be working!")
        else:
            print(f"  [OK] WAL file is empty")
    else:
        print(f"  [INFO] WAL file does not exist (normal if not in WAL mode)")
    
    if os.path.exists(shm_path):
        shm_size = os.path.getsize(shm_path)
        print(f"  SHM file exists: {shm_path}")
        print(f"  SHM file size: {shm_size} bytes")
    
    print()
    
    # Test 5: Cleanup test log
    print("[TEST 5] Cleaning up test log...")
    try:
        conn4 = sqlite3.connect(db_path, check_same_thread=False, timeout=10.0)
        cur4 = conn4.cursor()
        cur4.execute("DELETE FROM sync_logs WHERE id = ?", (test_log_id,))
        conn4.commit()
        conn4.close()
        print(f"  [OK] Test log {test_log_id} deleted\n")
    except Exception as e:
        print(f"  [WARNING] Could not delete test log: {e}\n")
    
    # Summary
    print("=" * 60)
    print("DEBUG SUMMARY")
    print("=" * 60)
    print("Check the results above to identify the issue:")
    print("  - If log found in SAME connection but NOT in NEW connection:")
    print("    -> Issue: WAL checkpoint not working or commit not persisting")
    print("  - If log NOT found in SAME connection:")
    print("    -> Issue: Insert/commit failing")
    print("  - If WAL file has data:")
    print("    -> Issue: Checkpoint not forcing writes to main database")
    print("=" * 60)

if __name__ == "__main__":
    debug_commit_process()

