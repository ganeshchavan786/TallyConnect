#!/usr/bin/env python3
"""
Check Sync Logs for a Specific Date Prefix
=========================================

Usage:
  python scripts/check_logs_for_date.py 2025-12-18
"""

import sqlite3
import sys
import os


def main():
    date_prefix = sys.argv[1] if len(sys.argv) > 1 else "2025-12-18"
    like = f"{date_prefix}%"
    db_path = "TallyConnectDb.db"
    if not os.path.exists(db_path):
        print(f"[ERROR] DB not found: {db_path}")
        sys.exit(1)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM sync_logs WHERE created_at LIKE ?", (like,))
    count = cur.fetchone()[0]
    print(f"count {date_prefix}: {count}")
    cur.execute(
        """
        SELECT id, created_at, company_name, log_level, sync_status, log_message
        FROM sync_logs
        WHERE created_at LIKE ?
        ORDER BY created_at DESC, id DESC
        """,
        (like,),
    )
    rows = cur.fetchall()
    for r in rows:
        print(r)
    conn.close()


if __name__ == "__main__":
    main()


