"""
Database Connection Management
===============================

Handles SQLite database initialization and connection management.
"""

import sqlite3
from backend.config.settings import DB_FILE


def init_db(db_path=DB_FILE):
    """
    Initialize SQLite database with required tables.
    
    Args:
        db_path: Path to SQLite database file
        
    Returns:
        sqlite3.Connection: Database connection object
    """
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
    
    conn.commit()
    return conn


def get_db_connection(db_path=DB_FILE):
    """
    Get database connection (reuse existing or create new).
    
    Args:
        db_path: Path to SQLite database file
        
    Returns:
        sqlite3.Connection: Database connection object
    """
    return sqlite3.connect(db_path, check_same_thread=False)

