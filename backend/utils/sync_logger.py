"""
Sync Logger
===========

Professional logging module for sync operations.
Stores logs in database for persistence and retrieval.
"""

import sqlite3
import os
import sys
import json
from datetime import datetime
from typing import Optional
from backend.database.sync_log_dao import SyncLogDAO


def get_base_dir():
    """Get base directory of the application."""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        return os.path.dirname(sys.executable)
    else:
        # Running as script
        return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class SyncLogger:
    """
    Professional logger for sync operations.
    Stores logs in database for persistence and retrieval.
    """
    
    def __init__(self, db_path: str = None, db_lock=None):
        """
        Initialize SyncLogger.
        
        Args:
            db_path: Path to database file (default: TallyConnectDb.db in base dir)
            db_lock: Optional threading lock for thread-safe operations
        """
        if db_path is None:
            db_path = os.path.join(get_base_dir(), "TallyConnectDb.db")
        self.db_path = db_path
        self.db_lock = db_lock
        self._dao = None
    
    @property
    def dao(self) -> SyncLogDAO:
        """Get or create SyncLogDAO instance."""
        if self._dao is None:
            # Use timeout to prevent lock issues during sync
            # Use separate connection for logging to avoid lock conflicts
            conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=30.0)
            # Enable WAL mode for better concurrency (allows reads during writes)
            try:
                conn.execute("PRAGMA journal_mode=WAL")
                conn.commit()
                # Verify WAL mode is enabled
                wal_check = conn.execute("PRAGMA journal_mode").fetchone()
                if wal_check and wal_check[0] != 'wal':
                    print(f"[WARNING] WAL mode not enabled, current mode: {wal_check[0]}")
            except Exception as wal_err:
                print(f"[WARNING] Could not enable WAL mode: {wal_err}")
            # DO NOT use autocommit mode - explicit commits are more reliable
            # Keep default isolation level (requires explicit commit())
            # This ensures we have control over when commits happen
            # Set synchronous mode to NORMAL for better performance (WAL mode allows this)
            try:
                conn.execute("PRAGMA synchronous=NORMAL")
            except:
                pass
            # Use separate lock for logging to avoid blocking on main sync lock
            # If db_lock is provided, use it; otherwise create a new one
            log_lock = self.db_lock if self.db_lock else None
            self._dao = SyncLogDAO(conn, log_lock)
            # Store connection reference to keep it alive
            self._conn = conn
        return self._dao
    
    def log(self, company_guid: str, company_alterid: str, company_name: str,
            log_level: str, message: str, details: str = None,
            sync_status: str = None, records_synced: int = 0,
            error_code: str = None, error_message: str = None,
            duration_seconds: float = None) -> int:
        """
        Log a sync operation event.
        
        Args:
            company_guid: Company GUID
            company_alterid: Company AlterID
            company_name: Company name
            log_level: Log level (INFO, WARNING, ERROR, SUCCESS)
            message: Log message
            details: Additional details (optional)
            sync_status: Sync status (started, in_progress, completed, failed)
            records_synced: Number of records synced
            error_code: Error code if any
            error_message: Error message if any
            duration_seconds: Duration in seconds
            
        Returns:
            Log entry ID, or None if logging failed
        """
        try:
            # Create log data for JSON backup
            log_data = {
                "company_guid": company_guid,
                "company_alterid": company_alterid,
                "company_name": company_name,
                "log_level": log_level.upper(),
                "log_message": message,
                "log_details": details,
                "sync_status": sync_status,
                "records_synced": records_synced,
                "error_code": error_code,
                "error_message": error_message,
                "duration_seconds": duration_seconds,
                "timestamp": datetime.now().isoformat()
            }
            
            # Try to save to database
            log_id = self.dao.add_log(
                company_guid=company_guid,
                company_alterid=company_alterid,
                company_name=company_name,
                log_level=log_level.upper(),
                log_message=message,
                log_details=details,
                sync_status=sync_status,
                records_synced=records_synced,
                error_code=error_code,
                error_message=error_message,
                duration_seconds=duration_seconds
            )
            
            # Save to JSON file as backup
            try:
                json_log_path = os.path.join(get_base_dir(), "sync_logs_backup.jsonl")
                log_data["log_id"] = log_id
                with open(json_log_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(log_data, ensure_ascii=False) + "\n")
            except Exception as json_err:
                print(f"[WARNING] Failed to save log to JSON: {json_err}")
            
            # CRITICAL: Verify log was actually saved to database
            if log_id:
                # CRITICAL: Ensure commit is flushed before verification
                # Force commit and WAL checkpoint on the insert connection
                try:
                    if hasattr(self, '_dao') and self._dao:
                        if hasattr(self._dao, 'db_conn'):
                            # Final commit to ensure everything is written
                            try:
                                self._dao.db_conn.commit()
                                # Force WAL checkpoint on the insert connection BEFORE closing
                                checkpoint_cur = self._dao.db_conn.cursor()
                                checkpoint_cur.execute("PRAGMA wal_checkpoint(TRUNCATE)")
                                checkpoint_result = checkpoint_cur.fetchone()
                                checkpoint_cur.close()
                                if checkpoint_result and len(checkpoint_result) >= 3:
                                    if checkpoint_result[2] > 0:
                                        print(f"[DEBUG] Insert connection WAL checkpoint: {checkpoint_result[2]} pages written")
                                    elif checkpoint_result[0] == 1:
                                        print(f"[WARNING] WAL checkpoint busy on insert connection")
                            except Exception as checkpoint_err:
                                print(f"[WARNING] Insert connection checkpoint error: {checkpoint_err}")
                except:
                    pass
                
                # Wait for WAL to sync and commit to complete
                import time
                time.sleep(0.5)  # Increased delay for WAL sync (0.5s for reliability)
                
                # NOW close the insert connection after checkpoint
                try:
                    if hasattr(self, '_dao') and self._dao:
                        if hasattr(self._dao, 'db_conn'):
                            try:
                                self._dao.db_conn.close()
                            except:
                                pass
                            # Reset DAO so it creates new connection next time
                            self._dao = None
                except:
                    pass
                
                # Verify with completely fresh connection (ensures we see committed data)
                try:
                    verify_conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=5.0)
                    # Force WAL checkpoint FIRST to ensure changes are written to main database
                    try:
                        checkpoint_cur = verify_conn.cursor()
                        checkpoint_cur.execute("PRAGMA wal_checkpoint(TRUNCATE)")
                        checkpoint_result = checkpoint_cur.fetchone()
                        checkpoint_cur.close()
                        # Checkpoint returns: (busy, log, checkpointed)
                        if checkpoint_result and len(checkpoint_result) >= 3:
                            if checkpoint_result[2] > 0:
                                print(f"[DEBUG] WAL checkpoint: {checkpoint_result[2]} pages written")
                            # Wait a bit more after checkpoint
                            time.sleep(0.1)
                    except Exception as checkpoint_err:
                        print(f"[WARNING] WAL checkpoint failed: {checkpoint_err}")
                    
                    # Now verify with the fresh connection
                    # IMPORTANT: verify more than just ID to avoid false positives if IDs ever get reused
                    verify_cur = verify_conn.cursor()
                    verify_cur.execute(
                        """
                        SELECT id
                        FROM sync_logs
                        WHERE id = ?
                          AND company_guid = ?
                          AND company_alterid = ?
                          AND company_name = ?
                          AND log_level = ?
                          AND log_message = ?
                        """,
                        (
                            log_id,
                            company_guid,
                            str(company_alterid),
                            company_name,
                            log_level.upper(),
                            message,
                        ),
                    )
                    verify_result = verify_cur.fetchone()
                    verify_cur.close()
                    verify_conn.close()
                    
                    if verify_result:
                        print(f"[DEBUG] Log saved and verified - ID: {log_id}, Company: {company_name}, Level: {log_level}, Status: {sync_status}")
                    else:
                        print(f"[ERROR] Log ID {log_id} returned but NOT found in database!")
                        print(f"[ERROR] Commit failed - attempting automatic restore from JSON...")
                        # Use same logic as restore_logs_from_json.py
                        restore_success = self._restore_log_from_json(log_data, log_id)
                        if not restore_success:
                            print(f"[WARNING] Automatic restore failed - log saved to JSON backup")
                            print(f"[INFO] Run 'python scripts/restore_logs_from_json.py' to restore manually")
                except Exception as verify_err:
                    print(f"[WARNING] Could not verify log {log_id}: {verify_err}")
                    import traceback
                    traceback.print_exc()
                    # If verification fails, try auto-restore anyway
                    print(f"[INFO] Attempting auto-restore due to verification error...")
                    restore_success = self._restore_log_from_json(log_data, log_id)
                    if not restore_success:
                        print(f"[WARNING] Auto-restore also failed - log saved to JSON backup")
            else:
                print(f"[ERROR] Log ID is None - commit may have failed!")
                print(f"[ERROR] Log data: {json.dumps(log_data, ensure_ascii=False)}")
            
            return log_id
        except Exception as e:
            # Fallback to console if database logging fails
            print(f"[SYNC LOGGER ERROR] Failed to log to database: {e}")
            print(f"[SYNC LOG] {log_level}: {message}")
            import traceback
            traceback.print_exc()
            return None
    
    def info(self, company_guid: str, company_alterid: str, company_name: str,
             message: str, details: str = None, sync_status: str = None):
        """Log info message."""
        self.log(company_guid, company_alterid, company_name, 'INFO', message,
                details, sync_status)
    
    def warning(self, company_guid: str, company_alterid: str, company_name: str,
                message: str, details: str = None, sync_status: str = None):
        """Log warning message."""
        self.log(company_guid, company_alterid, company_name, 'WARNING', message,
                details, sync_status)
    
    def error(self, company_guid: str, company_alterid: str, company_name: str,
              message: str, error_code: str = None, error_message: str = None,
              details: str = None, sync_status: str = None):
        """Log error message."""
        self.log(company_guid, company_alterid, company_name, 'ERROR', message,
                details, sync_status, error_code=error_code, error_message=error_message)
    
    def success(self, company_guid: str, company_alterid: str, company_name: str,
                message: str, records_synced: int = 0, duration_seconds: float = None,
                details: str = None):
        """Log success message."""
        self.log(company_guid, company_alterid, company_name, 'SUCCESS', message,
                details, 'completed', records_synced=records_synced,
                duration_seconds=duration_seconds)
    
    def sync_started(self, company_guid: str, company_alterid: str, company_name: str,
                     details: str = None) -> int:
        """Log sync start. Returns log ID."""
        return self.log(company_guid, company_alterid, company_name, 'INFO',
                f"Sync started for {company_name}", details, 'started')
    
    def sync_progress(self, company_guid: str, company_alterid: str, company_name: str,
                      records_synced: int, message: str = None, details: str = None):
        """Log sync progress."""
        msg = message or f"Synced {records_synced} records"
        self.log(company_guid, company_alterid, company_name, 'INFO', msg,
                details, 'in_progress', records_synced=records_synced)
    
    def sync_completed(self, company_guid: str, company_alterid: str, company_name: str,
                       records_synced: int, duration_seconds: float, details: str = None) -> int:
        """Log sync completion. Returns log ID."""
        return self.log(company_guid, company_alterid, company_name, 'SUCCESS',
                f"Sync completed successfully: {records_synced} records synced in {duration_seconds:.2f} seconds",
                details, 'completed', records_synced=records_synced,
                duration_seconds=duration_seconds)
    
    def sync_failed(self, company_guid: str, company_alterid: str, company_name: str,
                    error_message: str, error_code: str = None, details: str = None,
                    records_synced: int = 0):
        """Log sync failure."""
        self.log(company_guid, company_alterid, company_name, 'ERROR',
                f"Sync failed: {error_message}", details, 'failed',
                records_synced=records_synced, error_code=error_code,
                error_message=error_message)
    
    def _restore_log_from_json(self, log_data: dict, log_id: int) -> bool:
        """
        Restore log from JSON data to database.
        Uses same logic as restore_logs_from_json.py
        
        Args:
            log_data: Log data dictionary (from JSON)
            log_id: Log ID to restore
            
        Returns:
            True if restore successful, False otherwise
        """
        try:
            restore_conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=10.0)
            restore_cur = restore_conn.cursor()
            
            # Enable WAL mode (same as restore script)
            try:
                restore_conn.execute("PRAGMA journal_mode=WAL")
                restore_conn.commit()
            except:
                pass
            
            # Validate required fields before attempting restore
            required_fields = ["company_guid", "company_alterid", "company_name", "log_level", "log_message"]
            missing_fields = [field for field in required_fields if not log_data.get(field)]
            if missing_fields:
                print(f"[ERROR] Missing required fields for log {log_id}: {missing_fields}")
                restore_cur.close()
                restore_conn.close()
                return False
            
            # Convert timestamp from JSON to SQLite format (same as restore script)
            created_at = log_data.get("timestamp")
            if created_at:
                try:
                    # Convert ISO format to SQLite format
                    dt = datetime.fromisoformat(str(created_at).replace('Z', '+00:00'))
                    created_at = dt.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    from datetime import timezone
                    created_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            else:
                from datetime import timezone
                created_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

            # If an identical log already exists (signature match), restore not needed
            signature_params = (
                str(log_data.get("company_guid")),
                str(log_data.get("company_alterid")),
                str(log_data.get("company_name")),
                str(log_data.get("log_level")).upper(),
                str(log_data.get("log_message")),
                created_at,
            )
            restore_cur.execute(
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
            if restore_cur.fetchone():
                print(f"[INFO] Matching log already exists in database - restore not needed")
                restore_cur.close()
                restore_conn.close()
                return True
            
            # If the provided ID is already occupied, insert without ID (IDs can be reused/occupied due to tests/restores)
            id_free = True
            try:
                restore_cur.execute("SELECT 1 FROM sync_logs WHERE id = ?", (log_id,))
                id_free = restore_cur.fetchone() is None
            except Exception:
                id_free = False

            if log_id and id_free:
                restore_query = """
                INSERT INTO sync_logs 
                (id, company_guid, company_alterid, company_name, log_level, log_message, 
                 log_details, sync_status, records_synced, error_code, error_message, 
                 duration_seconds, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                restore_params = (
                    int(log_id),
                    log_data.get("company_guid"),
                    log_data.get("company_alterid"),
                    log_data.get("company_name"),
                    str(log_data.get("log_level")).upper(),
                    log_data.get("log_message"),
                    log_data.get("log_details"),
                    log_data.get("sync_status"),
                    log_data.get("records_synced", 0),
                    log_data.get("error_code"),
                    log_data.get("error_message"),
                    log_data.get("duration_seconds"),
                    created_at
                )
                restore_cur.execute(restore_query, restore_params)
            else:
                restore_query = """
                INSERT INTO sync_logs 
                (company_guid, company_alterid, company_name, log_level, log_message, 
                 log_details, sync_status, records_synced, error_code, error_message, 
                 duration_seconds, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                restore_params = (
                    log_data.get("company_guid"),
                    log_data.get("company_alterid"),
                    log_data.get("company_name"),
                    str(log_data.get("log_level")).upper(),
                    log_data.get("log_message"),
                    log_data.get("log_details"),
                    log_data.get("sync_status"),
                    log_data.get("records_synced", 0),
                    log_data.get("error_code"),
                    log_data.get("error_message"),
                    log_data.get("duration_seconds"),
                    created_at
                )
                restore_cur.execute(restore_query, restore_params)

            restore_conn.commit()
            
            # Force WAL checkpoint to ensure data is written
            try:
                restore_conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
            except:
                pass
            
            # Verify restore with a small delay for WAL sync
            import time
            time.sleep(0.1)
            
            # Verify by signature (more reliable than ID)
            restore_cur.execute(
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
            if restore_cur.fetchone():
                print(f"[SUCCESS] Log restored successfully from JSON!")
                restore_cur.close()
                restore_conn.close()
                return True
            else:
                print(f"[ERROR] Restore failed - log still not in database after insert")
                restore_cur.close()
                restore_conn.close()
                return False
                
        except sqlite3.IntegrityError as e:
            # Log already exists - that's OK (might have been inserted by another process)
            print(f"[INFO] Log {log_id} already exists (IntegrityError) - restore successful")
            try:
                if restore_conn:
                    restore_cur.close()
                    restore_conn.close()
            except:
                pass
            return True
        except sqlite3.OperationalError as e:
            # Database locked or other operational error
            print(f"[ERROR] Database operational error during restore: {e}")
            try:
                if restore_conn:
                    restore_cur.close()
                    restore_conn.close()
            except:
                pass
            return False
        except Exception as restore_err:
            print(f"[ERROR] Automatic restore failed: {restore_err}")
            import traceback
            traceback.print_exc()
            try:
                if restore_conn:
                    restore_cur.close()
                    restore_conn.close()
            except:
                pass
            return False


# Global logger instance (can be initialized with specific db_path and lock)
_global_logger = None

def get_sync_logger(db_path: str = None, db_lock=None) -> SyncLogger:
    """
    Get sync logger instance.
    Creates a new instance each time to ensure fresh database connection.
    
    Args:
        db_path: Path to database file (optional)
        db_lock: Optional threading lock (optional)
        
    Returns:
        SyncLogger instance
    """
    # Always create a new instance to ensure fresh database connection
    # This prevents stale connections and ensures proper logging
    return SyncLogger(db_path, db_lock)

