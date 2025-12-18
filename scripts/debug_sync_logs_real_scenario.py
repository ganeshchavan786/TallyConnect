#!/usr/bin/env python3
"""
Debug Script - Real Sync Scenario
===================================

Simulates the actual sync process with multiple connections
to identify connection conflicts.
"""

import sqlite3
import os
import sys
import time
import threading
from datetime import datetime, timezone

def get_base_dir():
    """Get base directory."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def simulate_sync_worker():
    """Simulate sync worker with lock (like actual sync)."""
    base_dir = get_base_dir()
    db_path = os.path.join(base_dir, "TallyConnectDb.db")
    
    print("[SYNC WORKER] Starting...")
    
    # Simulate main sync connection (with lock)
    sync_lock = threading.Lock()
    
    with sync_lock:
        print("[SYNC WORKER] Lock acquired")
        sync_conn = sqlite3.connect(db_path, check_same_thread=False, timeout=10.0)
        sync_conn.execute("PRAGMA journal_mode=WAL")
        sync_conn.commit()
        
        # Simulate long-running sync operation
        print("[SYNC WORKER] Simulating sync operation...")
        time.sleep(0.1)
        
        sync_conn.close()
        print("[SYNC WORKER] Sync connection closed")
    
    print("[SYNC WORKER] Lock released")

def simulate_logger():
    """Simulate logger (like actual logger)."""
    base_dir = get_base_dir()
    db_path = os.path.join(base_dir, "TallyConnectDb.db")
    
    print("[LOGGER] Starting...")
    
    # Simulate logger connection (independent, no lock)
    logger_conn = sqlite3.connect(db_path, check_same_thread=False, timeout=10.0)
    logger_conn.execute("PRAGMA journal_mode=WAL")
    logger_conn.commit()
    
    # Insert log
    created_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    cur = logger_conn.cursor()
    cur.execute("""
        INSERT INTO sync_logs 
        (company_guid, company_alterid, company_name, log_level, log_message, 
         log_details, sync_status, records_synced, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "debug-guid-002",
        "999",
        "Debug Test Company 2",
        "INFO",
        "Debug test log from logger",
        "Testing logger commit",
        "started",
        0,
        created_at
    ))
    log_id = cur.lastrowid
    print(f"[LOGGER] Log ID returned: {log_id}")
    
    # Commit
    logger_conn.commit()
    print("[LOGGER] Commit called")
    
    # WAL checkpoint
    checkpoint_cur = logger_conn.cursor()
    checkpoint_cur.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    checkpoint_result = checkpoint_cur.fetchone()
    checkpoint_cur.close()
    print(f"[LOGGER] WAL checkpoint: {checkpoint_result}")
    
    # Wait
    time.sleep(0.5)
    
    # Close
    logger_conn.close()
    print("[LOGGER] Connection closed")
    
    return log_id

def verify_log(log_id):
    """Verify log with fresh connection."""
    base_dir = get_base_dir()
    db_path = os.path.join(base_dir, "TallyConnectDb.db")
    
    print(f"[VERIFY] Verifying log {log_id}...")
    time.sleep(0.1)
    
    verify_conn = sqlite3.connect(db_path, check_same_thread=False, timeout=10.0)
    
    # WAL checkpoint
    checkpoint_cur = verify_conn.cursor()
    checkpoint_cur.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    checkpoint_result = checkpoint_cur.fetchone()
    checkpoint_cur.close()
    print(f"[VERIFY] WAL checkpoint: {checkpoint_result}")
    
    time.sleep(0.1)
    
    # Verify
    verify_cur = verify_conn.cursor()
    verify_cur.execute("SELECT id FROM sync_logs WHERE id = ?", (log_id,))
    verify_result = verify_cur.fetchone()
    verify_cur.close()
    
    if verify_result:
        print(f"[VERIFY] [OK] Log found: ID {verify_result[0]}")
    else:
        print(f"[VERIFY] [ERROR] Log NOT found!")
    
    # Check max ID
    max_cur = verify_conn.cursor()
    max_cur.execute("SELECT MAX(id) FROM sync_logs")
    max_id = max_cur.fetchone()[0]
    max_cur.close()
    print(f"[VERIFY] Max ID: {max_id}")
    
    verify_conn.close()
    
    return verify_result is not None

def debug_real_scenario():
    """Debug real sync scenario."""
    print("=" * 60)
    print("REAL SYNC SCENARIO DEBUGGER")
    print("=" * 60)
    print()
    
    # Scenario 1: Logger while sync is running
    print("[SCENARIO 1] Logger while sync is running...")
    sync_thread = threading.Thread(target=simulate_sync_worker)
    sync_thread.start()
    
    # Wait a bit, then start logger
    time.sleep(0.05)
    log_id = simulate_logger()
    
    # Wait for sync to finish
    sync_thread.join()
    
    # Verify
    result = verify_log(log_id)
    
    if result:
        print("[SCENARIO 1] [OK] Log persisted correctly")
    else:
        print("[SCENARIO 1] [ERROR] Log did NOT persist!")
    
    print()
    
    # Scenario 2: Multiple rapid logs
    print("[SCENARIO 2] Multiple rapid logs...")
    log_ids = []
    for i in range(3):
        log_id = simulate_logger()
        log_ids.append(log_id)
        time.sleep(0.1)
    
    # Verify all
    all_ok = True
    for log_id in log_ids:
        result = verify_log(log_id)
        if not result:
            all_ok = False
    
    if all_ok:
        print("[SCENARIO 2] [OK] All logs persisted")
    else:
        print("[SCENARIO 2] [ERROR] Some logs did NOT persist!")
    
    print()
    
    # Cleanup
    print("[CLEANUP] Deleting test logs...")
    base_dir = get_base_dir()
    db_path = os.path.join(base_dir, "TallyConnectDb.db")
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

if __name__ == "__main__":
    debug_real_scenario()

