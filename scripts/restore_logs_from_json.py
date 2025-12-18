#!/usr/bin/env python3
"""
Restore Sync Logs from JSON Backup
===================================

Restores sync logs from sync_logs_backup.jsonl to database.
Use this if database commits fail but JSON backup has logs.
"""

import sqlite3
import json
import os
import sys
from datetime import datetime

def get_base_dir():
    """Get base directory of the application."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def restore_logs_from_json():
    """Restore logs from JSON backup to database."""
    base_dir = get_base_dir()
    json_path = os.path.join(base_dir, "sync_logs_backup.jsonl")
    db_path = os.path.join(base_dir, "TallyConnectDb.db")
    
    print(f"Restoring logs from: {json_path}")
    print(f"Database: {db_path}\n")
    
    if not os.path.exists(json_path):
        print(f"[ERROR] JSON backup file not found: {json_path}")
        return
    
    if not os.path.exists(db_path):
        print(f"[ERROR] Database file not found: {db_path}")
        return
    
    # Read JSON logs
    logs = []
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        log = json.loads(line)
                        logs.append(log)
                    except json.JSONDecodeError as e:
                        print(f"[WARNING] Skipping invalid JSON line: {e}")
    except Exception as e:
        print(f"[ERROR] Failed to read JSON file: {e}")
        return
    
    print(f"Found {len(logs)} logs in JSON backup\n")
    
    if not logs:
        print("[INFO] No logs to restore")
        return
    
    # Connect to database
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        # Enable WAL mode
        try:
            cur.execute("PRAGMA journal_mode=WAL")
            conn.commit()
        except:
            pass
        
        # Basic stats (avoid loading all IDs into memory)
        cur.execute("SELECT COUNT(*) FROM sync_logs")
        existing_count = cur.fetchone()[0]
        cur.execute("SELECT MAX(id) FROM sync_logs")
        max_existing_id = cur.fetchone()[0]
        print(f"Existing logs in database: {existing_count}")
        print(f"Max existing ID: {max_existing_id}")
        
        # Restore logs
        restored_with_id = 0
        restored_new_id = 0
        skipped = 0
        errors = 0
        
        for log in logs:
            try:
                log_id = log.get("log_id")

                company_guid = log.get("company_guid")
                company_alterid = log.get("company_alterid")
                company_name = log.get("company_name")
                log_level = (log.get("log_level") or "").upper()
                log_message = log.get("log_message")
                if not (company_guid and company_alterid and company_name and log_level and log_message):
                    print(f"[WARNING] Log missing required fields, skipping (log_id={log_id})")
                    errors += 1
                    continue

                # Use timestamp from JSON or current time
                created_at = log.get("timestamp") or log.get("created_at")
                if created_at:
                    # Convert ISO format to SQLite format
                    try:
                        dt = datetime.fromisoformat(str(created_at).replace('Z', '+00:00'))
                        created_at = dt.strftime("%Y-%m-%d %H:%M:%S")
                    except:
                        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                else:
                    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # De-duplicate by stable signature (NOT by log_id)
                signature_params = (
                    str(company_guid),
                    str(company_alterid),
                    str(company_name),
                    str(log_level),
                    str(log_message),
                    str(created_at),
                )
                cur.execute(
                    """
                    SELECT 1
                    FROM sync_logs
                    WHERE company_guid = ?
                      AND company_alterid = ?
                      AND company_name = ?
                      AND log_level = ?
                      AND log_message = ?
                      AND created_at = ?
                    """,
                    signature_params,
                )
                if cur.fetchone():
                    skipped += 1
                    continue

                # If log_id is free, try to insert with ID (nice-to-have); otherwise insert without ID.
                id_is_free = False
                if log_id:
                    cur.execute("SELECT 1 FROM sync_logs WHERE id = ?", (log_id,))
                    id_is_free = cur.fetchone() is None

                if log_id and id_is_free:
                    query = """
                    INSERT INTO sync_logs
                    (id, company_guid, company_alterid, company_name, log_level, log_message,
                     log_details, sync_status, records_synced, error_code, error_message,
                     duration_seconds, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    params = (
                        int(log_id),
                        str(company_guid),
                        str(company_alterid),
                        str(company_name),
                        str(log_level),
                        str(log_message),
                        log.get("log_details"),
                        log.get("sync_status"),
                        log.get("records_synced", 0),
                        log.get("error_code"),
                        log.get("error_message"),
                        log.get("duration_seconds"),
                        created_at,
                    )
                    cur.execute(query, params)
                    conn.commit()
                    restored_with_id += 1
                    print(f"[OK] Restored (kept ID {log_id}): {company_name} - {log_level}")
                else:
                    query = """
                    INSERT INTO sync_logs
                    (company_guid, company_alterid, company_name, log_level, log_message,
                     log_details, sync_status, records_synced, error_code, error_message,
                     duration_seconds, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    params = (
                        str(company_guid),
                        str(company_alterid),
                        str(company_name),
                        str(log_level),
                        str(log_message),
                        log.get("log_details"),
                        log.get("sync_status"),
                        log.get("records_synced", 0),
                        log.get("error_code"),
                        log.get("error_message"),
                        log.get("duration_seconds"),
                        created_at,
                    )
                    cur.execute(query, params)
                    conn.commit()
                    restored_new_id += 1
                    print(f"[OK] Restored (new ID): {company_name} - {log_level} @ {created_at}")

            except sqlite3.IntegrityError as e:
                print(f"[ERROR] Integrity error restoring log_id={log.get('log_id')}: {e}")
                errors += 1
            except Exception as e:
                print(f"[ERROR] Failed to restore log_id={log.get('log_id')}: {e}")
                errors += 1
        
        conn.close()
        
        print(f"\n{'='*50}")
        print(f"Restore Summary:")
        print(f"  Total logs in JSON: {len(logs)}")
        print(f"  Restored (kept ID): {restored_with_id}")
        print(f"  Restored (new ID): {restored_new_id}")
        print(f"  Skipped (already exist): {skipped}")
        print(f"  Errors: {errors}")
        print(f"{'='*50}")
        
    except Exception as e:
        print(f"[ERROR] Database error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    restore_logs_from_json()

