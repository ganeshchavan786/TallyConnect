"""
Sync Logger
===========

Professional logging module for sync operations.
Stores logs in database for persistence and retrieval.
"""

import sqlite3
import os
import sys
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
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._dao = SyncLogDAO(conn, self.db_lock)
        return self._dao
    
    def log(self, company_guid: str, company_alterid: str, company_name: str,
            log_level: str, message: str, details: str = None,
            sync_status: str = None, records_synced: int = 0,
            error_code: str = None, error_message: str = None,
            duration_seconds: float = None):
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
        """
        try:
            self.dao.add_log(
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
        except Exception as e:
            # Fallback to console if database logging fails
            print(f"[SYNC LOGGER ERROR] Failed to log to database: {e}")
            print(f"[SYNC LOG] {log_level}: {message}")
    
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
                     details: str = None):
        """Log sync start."""
        self.log(company_guid, company_alterid, company_name, 'INFO',
                f"Sync started for {company_name}", details, 'started')
    
    def sync_progress(self, company_guid: str, company_alterid: str, company_name: str,
                      records_synced: int, message: str = None, details: str = None):
        """Log sync progress."""
        msg = message or f"Synced {records_synced} records"
        self.log(company_guid, company_alterid, company_name, 'INFO', msg,
                details, 'in_progress', records_synced=records_synced)
    
    def sync_completed(self, company_guid: str, company_alterid: str, company_name: str,
                       records_synced: int, duration_seconds: float, details: str = None):
        """Log sync completion."""
        self.log(company_guid, company_alterid, company_name, 'SUCCESS',
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

