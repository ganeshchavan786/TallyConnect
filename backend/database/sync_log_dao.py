"""
Sync Log Data Access Object
============================

Handles all database operations related to sync logs.
"""

import sqlite3
from typing import List, Tuple, Optional, Dict
from datetime import datetime, timedelta


class SyncLogDAO:
    """Data Access Object for Sync Log operations."""
    
    def __init__(self, db_conn: sqlite3.Connection, db_lock=None):
        """
        Initialize SyncLogDAO.
        
        Args:
            db_conn: SQLite database connection
            db_lock: Optional threading lock for thread-safe operations
        """
        self.db_conn = db_conn
        self.db_lock = db_lock
    
    def _execute(self, query: str, params: tuple = None):
        """Execute query with optional lock."""
        if self.db_lock:
            with self.db_lock:
                cur = self.db_conn.cursor()
                try:
                    if params:
                        cur.execute(query, params)
                    else:
                        cur.execute(query)
                    # Force immediate commit with verification
                    self.db_conn.commit()
                    # Verify commit by checking if still in transaction
                    if hasattr(self.db_conn, 'in_transaction') and self.db_conn.in_transaction:
                        # Still in transaction - commit may have failed, retry
                        self.db_conn.commit()
                except Exception as e:
                    # Rollback on error
                    try:
                        self.db_conn.rollback()
                    except:
                        pass
                    raise
                return cur
        else:
            # No lock - direct execution (for independent logger connection)
            cur = self.db_conn.cursor()
            try:
                # Check if connection is in autocommit mode
                is_autocommit = getattr(self.db_conn, 'isolation_level', None) is None
                
                if params:
                    cur.execute(query, params)
                else:
                    cur.execute(query)
                
                # Always commit explicitly (don't rely on autocommit)
                self.db_conn.commit()
                
                # CRITICAL: Force SQLite to flush changes to disk
                # This ensures the commit is actually written, not just buffered
                try:
                    # Execute a simple query to force SQLite to sync
                    flush_cur = self.db_conn.cursor()
                    flush_cur.execute("SELECT changes()")
                    flush_cur.close()
                except:
                    pass
                
                # Verify connection is still open and valid
                try:
                    test_cur = self.db_conn.cursor()
                    test_cur.execute("SELECT 1")
                    test_cur.close()
                except Exception as conn_err:
                    print(f"[ERROR] Database connection is invalid: {conn_err}")
                    raise Exception(f"Database connection error: {conn_err}")
                    
            except Exception as e:
                if not is_autocommit:
                    try:
                        self.db_conn.rollback()
                    except:
                        pass
                print(f"[ERROR] Failed to execute query: {e}")
                import traceback
                traceback.print_exc()
                raise
            return cur
    
    def add_log(self, company_guid: str, company_alterid: str, company_name: str,
                log_level: str, log_message: str, log_details: str = None,
                sync_status: str = None, records_synced: int = 0,
                error_code: str = None, error_message: str = None,
                duration_seconds: float = None) -> int:
        """
        Add a sync log entry.
        
        Args:
            company_guid: Company GUID
            company_alterid: Company AlterID
            company_name: Company name
            log_level: Log level (INFO, WARNING, ERROR, SUCCESS)
            log_message: Log message
            log_details: Additional details (optional)
            sync_status: Sync status (started, in_progress, completed, failed)
            records_synced: Number of records synced
            error_code: Error code if any
            error_message: Error message if any
            duration_seconds: Duration in seconds
            
        Returns:
            Log entry ID
        """
        query = """
        INSERT INTO sync_logs 
        (company_guid, company_alterid, company_name, log_level, log_message, 
         log_details, sync_status, records_synced, error_code, error_message, 
         duration_seconds, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        # Use local timestamps to match UI expectations and date-based filters
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        params = (company_guid, company_alterid, company_name, log_level, log_message,
                 log_details, sync_status, records_synced, error_code, error_message,
                 duration_seconds, created_at)
        
        try:
            # Execute query and get log ID
            cur = self._execute(query, params)
            log_id = cur.lastrowid
            
            # CRITICAL: Ensure commit happened (explicit commit)
            # Commit is already done in _execute, but we do it again to be sure
            self.db_conn.commit()
            
            # CRITICAL: Force SQLite to write to disk (checkpoint WAL if in WAL mode)
            try:
                # This ensures WAL changes are written to main database file
                # TRUNCATE mode forces immediate write to main database
                checkpoint_cur = self.db_conn.cursor()
                checkpoint_cur.execute("PRAGMA wal_checkpoint(TRUNCATE)")
                checkpoint_result = checkpoint_cur.fetchone()
                checkpoint_cur.close()
                # Checkpoint returns: (busy, log, checkpointed)
                # If checkpointed > 0, some pages were written
                if checkpoint_result and len(checkpoint_result) >= 3:
                    if checkpoint_result[2] > 0:
                        print(f"[DEBUG] WAL checkpoint: {checkpoint_result[2]} pages written to main database")
                    elif checkpoint_result[0] == 1:
                        print(f"[WARNING] WAL checkpoint busy - database may be locked")
            except Exception as checkpoint_err:
                # WAL checkpoint might fail if not in WAL mode, that's OK
                print(f"[WARNING] WAL checkpoint error: {checkpoint_err}")
            
            # CRITICAL: Force connection to flush any pending operations
            try:
                # Execute a simple query to ensure connection is active and flushed
                flush_cur = self.db_conn.cursor()
                flush_cur.execute("SELECT changes()")
                flush_cur.close()
            except:
                pass
            
            # Verify log was inserted by querying it back
            if log_id is None or log_id == 0:
                # Try to get the last inserted ID manually
                try:
                    verify_cur = self.db_conn.cursor()
                    verify_cur.execute("SELECT last_insert_rowid()")
                    result = verify_cur.fetchone()
                    if result and result[0]:
                        log_id = result[0]
                    verify_cur.close()
                except:
                    pass
            
            # CRITICAL: Verify log was actually inserted (with retry mechanism)
            if log_id:
                import time
                max_retries = 5
                found = False
                for retry in range(max_retries):
                    try:
                        # CRITICAL: Use same connection for verification
                        # WAL mode allows concurrent reads, but we need to ensure we're reading from same connection
                        verify_cur = self.db_conn.cursor()
                        verify_cur.execute("SELECT id FROM sync_logs WHERE id = ?", (log_id,))
                        verify_result = verify_cur.fetchone()
                        verify_cur.close()
                        
                        if verify_result:
                            # Log found - commit was successful
                            found = True
                            if retry > 0:
                                print(f"[INFO] Log ID {log_id} verified after {retry} retries")
                            break
                        else:
                            # Log not found - commit may have failed
                            if retry < max_retries - 1:
                                time.sleep(0.2)  # Wait 200ms for WAL to sync
                                # Force commit again
                                self.db_conn.commit()
                                # Check if connection is still valid
                                try:
                                    test_cur = self.db_conn.cursor()
                                    test_cur.execute("SELECT 1")
                                    test_cur.close()
                                except Exception as conn_test_err:
                                    print(f"[ERROR] Connection invalid during retry: {conn_test_err}")
                                    break
                                print(f"[WARNING] Log ID {log_id} not found, retrying commit (attempt {retry + 1}/{max_retries})")
                            else:
                                print(f"[ERROR] Log ID {log_id} returned but NOT found in database after {max_retries} retries!")
                                print(f"[ERROR] Commit is failing - connection may be closed or database locked")
                                print(f"[ERROR] Connection state: isolation_level={getattr(self.db_conn, 'isolation_level', 'unknown')}")
                                # Try to verify with a fresh query
                                try:
                                    fresh_cur = self.db_conn.cursor()
                                    fresh_cur.execute("SELECT MAX(id) FROM sync_logs")
                                    max_id = fresh_cur.fetchone()[0]
                                    fresh_cur.close()
                                    print(f"[DEBUG] Current max ID in database: {max_id}, Expected: {log_id}")
                                    if max_id and max_id < log_id:
                                        print(f"[ERROR] Database max ID ({max_id}) is less than returned log ID ({log_id})!")
                                        print(f"[ERROR] This confirms commit failed - log was not persisted!")
                                except Exception as fresh_err:
                                    print(f"[ERROR] Could not check max ID: {fresh_err}")
                    except Exception as verify_err:
                        if retry < max_retries - 1:
                            time.sleep(0.2)
                        else:
                            print(f"[ERROR] Could not verify log insertion: {verify_err}")
                            import traceback
                            traceback.print_exc()
                
                if not found and log_id:
                    print(f"[CRITICAL] Log ID {log_id} was returned but log is NOT in database!")
                    print(f"[CRITICAL] This indicates a serious commit failure!")
                    print(f"[CRITICAL] Check: 1) Connection is open, 2) WAL mode is enabled, 3) No other process has database locked")
            
            return log_id
        except Exception as e:
            print(f"[SYNC LOG DAO ERROR] Failed to insert log: {e}")
            import traceback
            traceback.print_exc()
            # Try to rollback if possible
            try:
                self.db_conn.rollback()
            except:
                pass
            return None
    
    def get_logs_by_company(self, company_guid: str, company_alterid: str,
                            limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        Get sync logs for a specific company.
        
        Args:
            company_guid: Company GUID
            company_alterid: Company AlterID
            limit: Maximum number of logs to return
            offset: Offset for pagination
            
        Returns:
            List of log dictionaries
        """
        query = """
        SELECT id, company_guid, company_alterid, company_name, log_level, 
               log_message, log_details, sync_status, records_synced, 
               error_code, error_message, duration_seconds, created_at
        FROM sync_logs
        WHERE company_guid = ? AND company_alterid = ?
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?
        """
        cur = self._execute(query, (company_guid, company_alterid, limit, offset))
        
        logs = []
        for row in cur.fetchall():
            logs.append({
                'id': row[0],
                'company_guid': row[1],
                'company_alterid': row[2],
                'company_name': row[3],
                'log_level': row[4],
                'log_message': row[5],
                'log_details': row[6],
                'sync_status': row[7],
                'records_synced': row[8] or 0,
                'error_code': row[9],
                'error_message': row[10],
                'duration_seconds': row[11],
                'created_at': row[12]
            })
        return logs
    
    def get_all_logs(self, limit: int = 100, offset: int = 0,
                    log_level: str = None, sync_status: str = None) -> List[Dict]:
        """
        Get all sync logs with optional filters.
        
        Args:
            limit: Maximum number of logs to return
            offset: Offset for pagination
            log_level: Filter by log level (optional)
            sync_status: Filter by sync status (optional)
            
        Returns:
            List of log dictionaries
        """
        query = """
        SELECT id, company_guid, company_alterid, company_name, log_level, 
               log_message, log_details, sync_status, records_synced, 
               error_code, error_message, duration_seconds, created_at
        FROM sync_logs
        WHERE 1=1
        """
        params = []
        
        if log_level:
            query += " AND log_level = ?"
            params.append(log_level)
        
        if sync_status:
            query += " AND sync_status = ?"
            params.append(sync_status)
        
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cur = self._execute(query, tuple(params))
        
        logs = []
        for row in cur.fetchall():
            logs.append({
                'id': row[0],
                'company_guid': row[1],
                'company_alterid': row[2],
                'company_name': row[3],
                'log_level': row[4],
                'log_message': row[5],
                'log_details': row[6],
                'sync_status': row[7],
                'records_synced': row[8] or 0,
                'error_code': row[9],
                'error_message': row[10],
                'duration_seconds': row[11],
                'created_at': row[12]
            })
        return logs
    
    def get_log_count(self, company_guid: str = None, company_alterid: str = None,
                      log_level: str = None, sync_status: str = None) -> int:
        """
        Get total count of logs with optional filters.
        
        Args:
            company_guid: Company GUID (optional)
            company_alterid: Company AlterID (optional)
            log_level: Filter by log level (optional)
            sync_status: Filter by sync status (optional)
            
        Returns:
            Total count
        """
        query = "SELECT COUNT(*) FROM sync_logs WHERE 1=1"
        params = []
        
        if company_guid and company_alterid:
            query += " AND company_guid = ? AND company_alterid = ?"
            params.extend([company_guid, company_alterid])
        
        if log_level:
            query += " AND log_level = ?"
            params.append(log_level)
        
        if sync_status:
            query += " AND sync_status = ?"
            params.append(sync_status)
        
        cur = self._execute(query, tuple(params) if params else None)
        return cur.fetchone()[0]
    
    def get_latest_sync_log(self, company_guid: str, company_alterid: str) -> Optional[Dict]:
        """
        Get the latest sync log for a company.
        
        Args:
            company_guid: Company GUID
            company_alterid: Company AlterID
            
        Returns:
            Latest log dictionary or None
        """
        query = """
        SELECT id, company_guid, company_alterid, company_name, log_level, 
               log_message, log_details, sync_status, records_synced, 
               error_code, error_message, duration_seconds, created_at
        FROM sync_logs
        WHERE company_guid = ? AND company_alterid = ?
        ORDER BY created_at DESC
        LIMIT 1
        """
        cur = self._execute(query, (company_guid, company_alterid))
        row = cur.fetchone()
        
        if not row:
            return None
        
        return {
            'id': row[0],
            'company_guid': row[1],
            'company_alterid': row[2],
            'company_name': row[3],
            'log_level': row[4],
            'log_message': row[5],
            'log_details': row[6],
            'sync_status': row[7],
            'records_synced': row[8] or 0,
            'error_code': row[9],
            'error_message': row[10],
            'duration_seconds': row[11],
            'created_at': row[12]
        }
    
    def delete_old_logs(self, days: int = 90) -> int:
        """
        Delete logs older than specified days.
        
        Args:
            days: Number of days to keep logs
            
        Returns:
            Number of logs deleted
        """
        cutoff_dt = datetime.now() - timedelta(days=days)
        cutoff_str = cutoff_dt.strftime("%Y-%m-%d %H:%M:%S")
        query = "DELETE FROM sync_logs WHERE created_at < ?"
        cur = self._execute(query, (cutoff_str,))
        return cur.rowcount
    
    def delete_logs_by_company(self, company_guid: str, company_alterid: str) -> int:
        """
        Delete all logs for a specific company.
        
        Args:
            company_guid: Company GUID
            company_alterid: Company AlterID
            
        Returns:
            Number of logs deleted
        """
        query = "DELETE FROM sync_logs WHERE company_guid = ? AND company_alterid = ?"
        cur = self._execute(query, (company_guid, company_alterid))
        return cur.rowcount

