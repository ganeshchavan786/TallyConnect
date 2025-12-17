"""
Company Data Access Object
==========================

Handles all database operations related to companies.
"""

import sqlite3
from typing import List, Tuple, Optional, Dict
from datetime import datetime
import sqlite3


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
            alterid: Company AlterID (will be converted to string)
            
        Returns:
            Tuple of company data or None
        """
        # CRITICAL: Convert alterid to string for proper matching
        # Database stores alterid as TEXT, so we need string comparison
        alterid_str = str(alterid) if alterid is not None else ""
        
        # Use explicit CAST to ensure type matching
        query = "SELECT * FROM companies WHERE guid=? AND CAST(alterid AS TEXT)=?"
        cur = self._execute(query, (guid, alterid_str))
        result = cur.fetchone()
        
        # Additional verification: Check if result actually matches
        if result:
            result_alterid = str(result[3]) if len(result) > 3 else ""
            result_guid = result[2] if len(result) > 2 else ""
            
            # Verify exact match
            if result_guid != guid or result_alterid != alterid_str:
                print(f"[WARNING] get_by_guid_alterid: Query returned wrong company!")
                print(f"  Expected: GUID={guid}, AlterID={alterid_str}")
                print(f"  Got: GUID={result_guid}, AlterID={result_alterid}")
                return None
            
            print(f"[DEBUG] get_by_guid_alterid: Found company - Name: {result[1] if len(result) > 1 else 'Unknown'}, AlterID in DB: {result_alterid}, Searched AlterID: {alterid_str}")
        else:
            print(f"[DEBUG] get_by_guid_alterid: No company found - GUID: {guid}, AlterID: {alterid_str}")
        
        return result
    
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
    
    def update_sync_complete(self, guid: str, alterid: str, total_records: int, company_name: str = None, logger=None) -> bool:
        """
        Update company after sync completion.
        If company doesn't exist, insert it.
        
        IMPORTANT: AlterID is unique per company in Tally.
        - AlterID is the primary identifier for fetching data from Tally
        - If company is altered in Tally, AlterID increments (101, 102, 103...)
        - Same GUID + Different AlterID = New version of company (should insert new record)
        - UNIQUE(guid, alterid) constraint allows same GUID with different AlterIDs
        
        Args:
            guid: Company GUID
            alterid: Company AlterID (unique identifier, increments when company altered)
            total_records: Total number of records synced
            company_name: Company name (optional, used if company doesn't exist)
            logger: Optional SyncLogger instance for logging
            
        Returns:
            True if successful
        """
        # CRITICAL: Ensure alterid is string for proper matching
        alterid_str = str(alterid) if alterid is not None else ""
        last_sync = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Check if company with this exact GUID+AlterID exists
        existing = self.get_by_guid_alterid(guid, alterid_str)
        
        # CRITICAL: Double-verify the existing company matches
        if existing:
            existing_alterid_check = str(existing[3]) if len(existing) > 3 else ""
            existing_guid_check = existing[2] if len(existing) > 2 else ""
            if existing_guid_check != guid or existing_alterid_check != alterid_str:
                print(f"[WARNING] get_by_guid_alterid returned wrong company! Expected GUID={guid}, AlterID={alterid_str}, Got GUID={existing_guid_check}, AlterID={existing_alterid_check}")
                existing = None  # Force insert
        
        # Debug logging
        print(f"[DEBUG] update_sync_complete: GUID={guid}, AlterID={alterid_str}, Existing={existing is not None}")
        
        if existing:
            # Company with this exact GUID+AlterID exists - UPDATE it
            existing_name = existing[1] if len(existing) > 1 else 'Unknown'
            existing_records = existing[5] if len(existing) > 5 else 0
            existing_alterid = str(existing[3]) if len(existing) > 3 else ""
            
            # Double-check AlterID matches
            if existing_alterid != alterid_str:
                print(f"[WARNING] AlterID mismatch! Existing: {existing_alterid}, New: {alterid_str}. Forcing insert.")
                existing = None  # Force insert
            else:
                # UPDATE existing company
                query = """
                UPDATE companies 
                SET total_records=?, last_sync=?, status='synced', name=?
                WHERE guid=? AND alterid=?
                """
                try:
                    cur = self._execute(query, (total_records, last_sync, company_name or existing_name, guid, alterid_str))
                    rows_affected = cur.rowcount
                    print(f"[DEBUG] UPDATE executed: rows_affected={rows_affected}")
                    
                    # CRITICAL: Force commit and verify
                    self.db_conn.commit()
                    
                    # Verify update worked by querying again
                    verify = self.get_by_guid_alterid(guid, alterid_str)
                    if verify:
                        verify_alterid = str(verify[3]) if len(verify) > 3 else ""
                        if verify_alterid == alterid_str:
                            print(f"[DEBUG] Company update verified: {verify[1] if len(verify) > 1 else 'Unknown'}")
                            
                            # Log the update
                            if logger:
                                try:
                                    logger.info(
                                        guid, alterid_str, company_name or existing_name,
                                        f"Company updated in database: total_records={total_records}, status=synced",
                                        details=f"Previous records: {existing_records}, New records: {total_records}",
                                        sync_status='completed'
                                    )
                                except Exception as log_err:
                                    print(f"[WARNING] Failed to log company update: {log_err}")
                            return True
                        else:
                            print(f"[ERROR] Verification failed: AlterID mismatch! DB has {verify_alterid}, expected {alterid_str}")
                            existing = None  # Force insert
                    else:
                        print(f"[ERROR] Company update FAILED - not found after update!")
                        print(f"[DEBUG] GUID={guid}, AlterID={alterid_str}, Name={company_name or existing_name}")
                        existing = None  # Force insert if update failed
                except Exception as update_err:
                    print(f"[ERROR] UPDATE query failed: {update_err}")
                    import traceback
                    traceback.print_exc()
                    existing = None  # Force insert on error
        else:
            # Company with this GUID+AlterID doesn't exist - INSERT new record
            # This handles:
            # 1. New company (never synced before)
            # 2. Company altered in Tally (new AlterID, same GUID)
            name = company_name or f"Company {guid[:8]}"
            
            print(f"[DEBUG] Inserting new company: Name={name}, GUID={guid}, AlterID={alterid_str}, Records={total_records}")
            
            # Use INSERT (not INSERT OR REPLACE) because UNIQUE(guid, alterid) allows same GUID with different AlterID
            query = """
            INSERT INTO companies (name, guid, alterid, status, total_records, last_sync)
            VALUES (?, ?, ?, 'synced', ?, ?)
            """
            try:
                self._execute(query, (name, guid, alterid_str, total_records, last_sync))
                
                # Verify the insert worked
                verify = self.get_by_guid_alterid(guid, alterid_str)
                if verify:
                    print(f"[DEBUG] ✅ Company insert verified: {verify[1] if len(verify) > 1 else 'Unknown'}")
                else:
                    print(f"[ERROR] ❌ Company insert failed - not found after insert!")
                    print(f"[DEBUG] GUID={guid}, AlterID={alterid_str}, Name={name}")
                    # Check if there's a constraint violation or other issue
                    try:
                        # Try to find by GUID only to see if there's a conflict
                        query_check = "SELECT * FROM companies WHERE guid=?"
                        cur = self._execute(query_check, (guid,))
                        all_with_guid = cur.fetchall()
                        if all_with_guid:
                            print(f"[DEBUG] Found {len(all_with_guid)} companies with same GUID but different AlterIDs:")
                            for comp in all_with_guid:
                                print(f"  - {comp[1] if len(comp) > 1 else 'Unknown'} | AlterID: {comp[3] if len(comp) > 3 else 'Unknown'}")
                    except Exception as check_err:
                        print(f"[DEBUG] Error checking existing companies: {check_err}")
                    raise Exception(f"Company insert failed - record not found after insert")
                    
            except sqlite3.IntegrityError as e:
                # UNIQUE constraint violation - company already exists (shouldn't happen, but handle gracefully)
                print(f"[WARNING] Company already exists (UNIQUE constraint): {e}")
                # Try to update instead
                query_update = """
                UPDATE companies 
                SET total_records=?, last_sync=?, status='synced', name=?
                WHERE guid=? AND alterid=?
                """
                self._execute(query_update, (total_records, last_sync, name, guid, alterid_str))
                print(f"[DEBUG] Updated existing company instead")
            except Exception as e:
                print(f"[ERROR] Failed to insert company: {e}")
                print(f"[DEBUG] GUID={guid}, AlterID={alterid_str}, Name={name}")
                import traceback
                traceback.print_exc()
                raise
            
            # Log the insert
            if logger:
                logger.info(
                    guid, alterid_str, name,
                    f"Company added to database: total_records={total_records}, status=synced",
                    details=f"New company inserted: {name} (AlterID: {alterid_str})",
                    sync_status='completed'
                )
        
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

