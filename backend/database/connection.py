"""
Database Connection Management
===============================

Handles SQLite database initialization and connection management.
"""

import sqlite3
import os
from contextlib import contextmanager
from backend.config.settings import DB_FILE


def init_db(db_path=DB_FILE):
    """
    Initialize SQLite database with required tables.
    
    Args:
        db_path: Path to SQLite database file (relative or absolute)
        
    Returns:
        sqlite3.Connection: Database connection object
    """
    # If relative path, resolve from project root (where main.py is)
    if not os.path.isabs(db_path):
        # Get project root: go up from backend/database/connection.py
        current_file = os.path.abspath(__file__)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
        db_path = os.path.join(project_root, db_path)
        db_path = os.path.abspath(db_path)
    
    conn = sqlite3.connect(db_path, check_same_thread=False)
    cur = conn.cursor()
    
    # Create companies table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS companies (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      guid TEXT NOT NULL,
      alterid TEXT NOT NULL,
      dsn TEXT,
      status TEXT DEFAULT 'new',
      total_records INTEGER DEFAULT 0,
      last_sync TEXT,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP,
      UNIQUE(guid, alterid)
    )
    """)
    
    # Create vouchers table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS vouchers (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      company_guid TEXT NOT NULL,
      company_alterid TEXT NOT NULL,
      company_name TEXT,
      vch_date TEXT,
      vch_type TEXT,
      vch_no TEXT,
      vch_mst_id TEXT,
      led_name TEXT,
      led_amount REAL,
      vch_dr_cr TEXT,
      vch_dr_amt REAL,
      vch_cr_amt REAL,
      vch_party_name TEXT,
      vch_led_parent TEXT,
      vch_narration TEXT,
      vch_gstin TEXT,
      vch_led_gstin TEXT,
      vch_led_bill_ref TEXT,
      vch_led_bill_type TEXT,
      vch_led_primary_grp TEXT,
      vch_led_nature TEXT,
      vch_led_bs_grp TEXT,
      vch_led_bs_grp_nature TEXT,
      vch_is_optional TEXT,
      vch_led_bill_count INTEGER,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP,
      UNIQUE(company_guid, company_alterid, vch_mst_id, led_name)
    )
    """)
    
    # Create sync_logs table for maintaining sync operation logs
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sync_logs (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      company_guid TEXT NOT NULL,
      company_alterid TEXT NOT NULL,
      company_name TEXT NOT NULL,
      log_level TEXT NOT NULL DEFAULT 'INFO',
      log_message TEXT NOT NULL,
      log_details TEXT,
      sync_status TEXT,
      records_synced INTEGER DEFAULT 0,
      error_code TEXT,
      error_message TEXT,
      duration_seconds REAL,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (company_guid, company_alterid) REFERENCES companies(guid, alterid)
    )
    """)
    
    # Create index for faster queries
    cur.execute("""
    CREATE INDEX IF NOT EXISTS idx_sync_logs_company 
    ON sync_logs(company_guid, company_alterid)
    """)
    
    cur.execute("""
    CREATE INDEX IF NOT EXISTS idx_sync_logs_created_at 
    ON sync_logs(created_at DESC)
    """)
    
    cur.execute("""
    CREATE INDEX IF NOT EXISTS idx_sync_logs_level 
    ON sync_logs(log_level)
    """)
    
    # Phase 1: Critical Fixes - Add indexes for vouchers table (Performance Critical)
    # These indexes will significantly improve dashboard query performance
    cur.execute("""
    CREATE INDEX IF NOT EXISTS idx_vouchers_company_date 
    ON vouchers(company_guid, company_alterid, vch_date)
    """)
    
    cur.execute("""
    CREATE INDEX IF NOT EXISTS idx_vouchers_date 
    ON vouchers(vch_date)
    """)
    
    cur.execute("""
    CREATE INDEX IF NOT EXISTS idx_vouchers_type 
    ON vouchers(vch_type)
    """)
    
    cur.execute("""
    CREATE INDEX IF NOT EXISTS idx_vouchers_company 
    ON vouchers(company_guid, company_alterid)
    """)
    
    # Phase 1: Critical Fixes - Add indexes for companies table
    # Use IF NOT EXISTS to avoid errors if indexes already exist
    try:
        cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_companies_status 
        ON companies(status)
        """)
    except:
        pass  # Index may already exist
    
    try:
        cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_companies_guid_alterid 
        ON companies(guid, alterid)
        """)
    except:
        pass  # Index may already exist
    
    conn.commit()
    return conn


def get_db_connection(db_path=DB_FILE):
    """
    Get database connection (reuse existing or create new).
    
    Args:
        db_path: Path to SQLite database file (relative or absolute)
        
    Returns:
        sqlite3.Connection: Database connection object
    """
    # If relative path, resolve from project root (where main.py is)
    if not os.path.isabs(db_path):
        # Get project root: go up from backend/database/connection.py
        current_file = os.path.abspath(__file__)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
        db_path = os.path.join(project_root, db_path)
        db_path = os.path.abspath(db_path)
    
    return sqlite3.connect(db_path, check_same_thread=False)


@contextmanager
def get_db_connection_with_context(db_path=DB_FILE):
    """
    Phase 2: Get database connection with context manager.
    Auto-closes connection when done.
    
    Usage:
        with get_db_connection_with_context() as conn:
            cur = conn.cursor()
            # ... operations
        # Connection auto-closes here
    
    Args:
        db_path: Path to SQLite database file (relative or absolute)
        
    Yields:
        sqlite3.Connection: Database connection object
    """
    # If relative path, resolve from project root (where main.py is)
    if not os.path.isabs(db_path):
        # Get project root: go up from backend/database/connection.py
        current_file = os.path.abspath(__file__)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
        db_path = os.path.join(project_root, db_path)
        db_path = os.path.abspath(db_path)
    
    conn = sqlite3.connect(db_path, check_same_thread=False)
    try:
        yield conn
    finally:
        conn.close()

