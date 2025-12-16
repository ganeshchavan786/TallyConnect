"""
Company Data Access Object
==========================

Handles all database operations related to companies.
"""

import sqlite3
from typing import List, Tuple, Optional, Dict
from datetime import datetime


class CompanyDAO:
    """Data Access Object for Company operations."""
    
    def __init__(self, db_conn: sqlite3.Connection, db_lock=None):
        """
        Initialize CompanyDAO.
        
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
    
    def get_all_synced(self) -> List[Tuple]:
        """
        Get all synced companies.
        
        Returns:
            List of tuples: (name, alterid, status, total_records, guid)
        """
        query = "SELECT name, alterid, status, total_records, guid FROM companies WHERE status='synced' ORDER BY name"
        cur = self._execute(query)
        return cur.fetchall()
    
    def get_by_guid_alterid(self, guid: str, alterid: str) -> Optional[Tuple]:
        """
        Get company by GUID and AlterID.
        
        Args:
            guid: Company GUID
            alterid: Company AlterID
            
        Returns:
            Tuple of company data or None
        """
        query = "SELECT * FROM companies WHERE guid=? AND alterid=?"
        cur = self._execute(query, (guid, alterid))
        return cur.fetchone()
    
    def get_guid_by_name_alterid(self, name: str, alterid: str) -> Optional[str]:
        """
        Get GUID by company name and AlterID.
        
        Args:
            name: Company name
            alterid: Company AlterID
            
        Returns:
            GUID string or None
        """
        query = "SELECT guid FROM companies WHERE name=? AND alterid=?"
        cur = self._execute(query, (name, alterid))
        row = cur.fetchone()
        return row[0] if row else None
    
    def get_all_status(self) -> Dict[Tuple, str]:
        """
        Get status for all companies.
        
        Returns:
            Dict with (guid, alterid) as key and status as value
        """
        query = "SELECT guid, alterid, status FROM companies"
        cur = self._execute(query)
        result = {}
        for row in cur.fetchall():
            guid, alterid, status = row
            key = (str(guid) if guid is not None else None, 
                   str(alterid) if alterid is not None else 'None')
            result[key] = status
        return result
    
    def get_syncing_companies(self) -> List[Tuple]:
        """
        Get all companies with 'syncing' status.
        
        Returns:
            List of tuples: (name, guid, alterid)
        """
        query = "SELECT name, guid, alterid FROM companies WHERE status='syncing'"
        cur = self._execute(query)
        return cur.fetchall()
    
    def insert_or_update(self, name: str, guid: str, alterid: str, dsn: str = None, 
                         status: str = 'syncing') -> bool:
        """
        Insert or update company.
        
        Args:
            name: Company name
            guid: Company GUID
            alterid: Company AlterID
            dsn: DSN name (optional)
            status: Company status (default: 'syncing')
            
        Returns:
            True if successful
        """
        # Check if exists
        existing = self.get_by_guid_alterid(guid, alterid)
        
        if existing:
            # Update existing
            query = "UPDATE companies SET name=?, dsn=?, status=? WHERE guid=? AND alterid=?"
            self._execute(query, (name, dsn, status, guid, alterid))
        else:
            # Insert new
            query = "INSERT OR IGNORE INTO companies (name, guid, alterid, dsn, status) VALUES (?, ?, ?, ?, ?)"
            self._execute(query, (name, guid, alterid, dsn, status))
        
        return True
    
    def update_status(self, guid: str, alterid: str, status: str) -> bool:
        """
        Update company status.
        
        Args:
            guid: Company GUID
            alterid: Company AlterID
            status: New status
            
        Returns:
            True if successful
        """
        query = "UPDATE companies SET status=? WHERE guid=? AND alterid=?"
        self._execute(query, (status, guid, alterid))
        return True
    
    def update_sync_complete(self, guid: str, alterid: str, total_records: int) -> bool:
        """
        Update company after sync completion.
        
        Args:
            guid: Company GUID
            alterid: Company AlterID
            total_records: Total number of records synced
            
        Returns:
            True if successful
        """
        query = """
        UPDATE companies 
        SET total_records=?, last_sync=?, status='synced' 
        WHERE guid=? AND alterid=?
        """
        last_sync = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._execute(query, (total_records, last_sync, guid, alterid))
        return True
    
    def mark_interrupted_syncs(self) -> int:
        """
        Mark all 'syncing' companies as 'incomplete'.
        
        Returns:
            Number of companies marked
        """
        companies = self.get_syncing_companies()
        count = 0
        for name, guid, alterid in companies:
            self.update_status(guid, alterid, 'incomplete')
            count += 1
        return count
    
    def delete_company(self, guid: str, alterid: str) -> bool:
        """
        Delete company and all its vouchers.
        
        Args:
            guid: Company GUID
            alterid: Company AlterID
            
        Returns:
            True if successful
        """
        # Delete vouchers first
        query_vouchers = "DELETE FROM vouchers WHERE company_guid=? AND company_alterid=?"
        self._execute(query_vouchers, (guid, alterid))
        
        # Delete company
        query_company = "DELETE FROM companies WHERE guid=? AND alterid=?"
        self._execute(query_company, (guid, alterid))
        
        return True
    
    def get_company_info(self, guid: str, alterid: str) -> Optional[Dict]:
        """
        Get complete company information.
        
        Args:
            guid: Company GUID
            alterid: Company AlterID
            
        Returns:
            Dict with company info or None
        """
        row = self.get_by_guid_alterid(guid, alterid)
        if not row:
            return None
        
        return {
            'id': row[0],
            'name': row[1],
            'guid': row[2],
            'alterid': row[3],
            'dsn': row[4],
            'status': row[5],
            'total_records': row[6],
            'last_sync': row[7],
            'created_at': row[8]
        }

