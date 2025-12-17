"""
Check Sync Logs Status
======================

Diagnostic script to check why sync logs are not appearing.
"""

import sqlite3
import os
from pathlib import Path

def get_db_path():
    """Get database path."""
    base_dir = Path(__file__).parent.parent
    return base_dir / "TallyConnectDb.db"

def check_sync_logs():
    """Check sync logs status."""
    db_path = get_db_path()
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return
    
    print(f"Checking sync logs in: {db_path}\n")
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    # Check if table exists
    cur.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='sync_logs'
    """)
    table_exists = cur.fetchone()
    
    if not table_exists:
        print("[ERROR] sync_logs table does not exist!")
        print("   Run the application once to create the table.")
        conn.close()
        return
    
    print("[OK] sync_logs table exists")
    
    # Check table structure
    cur.execute("PRAGMA table_info(sync_logs)")
    columns = cur.fetchall()
    print(f"\nTable structure ({len(columns)} columns):")
    for col in columns:
        print(f"   - {col[1]} ({col[2]})")
    
    # Check log count
    cur.execute("SELECT COUNT(*) FROM sync_logs")
    count = cur.fetchone()[0]
    print(f"\nTotal sync logs: {count}")
    
    if count == 0:
        print("\n[WARNING] No sync logs found!")
        print("\nPossible reasons:")
        print("   1. Companies were synced BEFORE sync logger was implemented")
        print("   2. Sync operations are not calling the logger")
        print("   3. Logger is failing silently (check console for errors)")
        print("\nSolution: Run a new sync operation to generate logs")
    else:
        # Show recent logs
        print(f"\nRecent logs (last 5):")
        cur.execute("""
            SELECT id, company_name, log_level, sync_status, 
                   log_message, records_synced, created_at
            FROM sync_logs
            ORDER BY created_at DESC
            LIMIT 5
        """)
        logs = cur.fetchall()
        for log in logs:
            print(f"\n   ID: {log[0]}")
            print(f"   Company: {log[1]}")
            print(f"   Level: {log[2]} | Status: {log[3]}")
            print(f"   Message: {log[4][:50]}...")
            print(f"   Records: {log[5]}")
            print(f"   Created: {log[6]}")
    
    # Check companies
    cur.execute("SELECT COUNT(*) FROM companies WHERE status = 'synced'")
    synced_companies = cur.fetchone()[0]
    print(f"\nSynced companies: {synced_companies}")
    
    if synced_companies > 0 and count == 0:
        print("\n[WARNING] Companies are synced but no logs exist!")
        print("   This means companies were synced before logger was added.")
        print("   Run a new sync to generate logs.")
    
    conn.close()
    print("\n[OK] Check complete!")

if __name__ == "__main__":
    check_sync_logs()

