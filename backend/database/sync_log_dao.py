"""
Sync Log Data Access Object
============================

Handles all database operations related to sync logs.
"""

import sqlite3
from typing import List, Tuple, Optional, Dict
from datetime import datetime


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
                if params:
                    cur.execute(query, params)
                else:
                    cur.execute(query)
                self.db_conn.commit()
                return cur
        else:
            cur = self.db_conn.cursor()
            if params:
                cur.execute(query, params)
            else:
                cur.execute(query)
            self.db_conn.commit()
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
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        params = (company_guid, company_alterid, company_name, log_level, log_message,
                 log_details, sync_status, records_synced, error_code, error_message,
                 duration_seconds, created_at)
        
        cur = self._execute(query, params)
        return cur.lastrowid
    
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
        query = """
        DELETE FROM sync_logs 
        WHERE created_at < datetime('now', '-' || ? || ' days')
        """
        cur = self._execute(query, (days,))
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

