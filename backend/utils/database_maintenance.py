"""
Database Maintenance Utilities
================================

Handles database maintenance operations for TallyConnect.
Part of Phase 3: Maintenance & Optimization implementation.

Includes:
- Database vacuuming
- Health checks
- Maintenance scheduling
"""

import sqlite3
import os
from typing import Dict, Tuple, Optional
from backend.config.settings import DB_FILE
from backend.database.connection import get_db_connection_with_context


def vacuum_database(db_path: str = DB_FILE) -> Tuple[bool, str]:
    """
    Vacuum database to reclaim space and optimize.
    
    Phase 3: Vacuuming removes deleted data and optimizes database structure.
    
    Args:
        db_path: Path to database file
    
    Returns:
        Tuple (success: bool, message: str)
    """
    try:
        # Resolve path
        if not os.path.isabs(db_path):
            current_file = os.path.abspath(__file__)
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
            db_path = os.path.join(project_root, db_path)
            db_path = os.path.abspath(db_path)
        
        if not os.path.exists(db_path):
            return False, f"Database file not found: {db_path}"
        
        # Get size before vacuum
        size_before = os.path.getsize(db_path)
        
        # Vacuum database
        with get_db_connection_with_context(db_path) as conn:
            cur = conn.cursor()
            
            # Get page count before
            cur.execute("PRAGMA page_count")
            page_count_before = cur.fetchone()[0]
            
            cur.execute("PRAGMA page_size")
            page_size = cur.fetchone()[0]
            
            # Perform vacuum
            cur.execute("VACUUM")
            conn.commit()
            
            # Get page count after
            cur.execute("PRAGMA page_count")
            page_count_after = cur.fetchone()[0]
        
        # Get size after vacuum
        size_after = os.path.getsize(db_path)
        
        # Calculate savings
        size_saved = size_before - size_after
        size_saved_mb = size_saved / (1024 * 1024)
        size_before_mb = size_before / (1024 * 1024)
        size_after_mb = size_after / (1024 * 1024)
        
        # Calculate percentage reduction
        if size_before > 0:
            reduction_pct = (size_saved / size_before) * 100
        else:
            reduction_pct = 0
        
        message = (
            f"Vacuum completed successfully. "
            f"Size: {size_before_mb:.2f} MB → {size_after_mb:.2f} MB "
            f"(Saved {size_saved_mb:.2f} MB, {reduction_pct:.1f}% reduction)"
        )
        
        return True, message
        
    except Exception as e:
        return False, f"Vacuum failed: {str(e)}"


def check_database_health(db_path: str = DB_FILE) -> Dict:
    """
    Check database health and return status.
    
    Phase 3: Health monitoring for proactive maintenance.
    
    Args:
        db_path: Path to database file
    
    Returns:
        Dict with health metrics:
        {
            'status': 'healthy' | 'unhealthy' | 'error',
            'size_mb': float,
            'company_count': int,
            'voucher_count': int,
            'log_count': int,
            'integrity': str,
            'page_count': int,
            'page_size': int,
            'errors': list
        }
    """
    result = {
        'status': 'unknown',
        'size_mb': 0.0,
        'company_count': 0,
        'voucher_count': 0,
        'log_count': 0,
        'integrity': 'unknown',
        'page_count': 0,
        'page_size': 0,
        'errors': []
    }
    
    try:
        # Resolve path
        if not os.path.isabs(db_path):
            current_file = os.path.abspath(__file__)
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
            db_path = os.path.join(project_root, db_path)
            db_path = os.path.abspath(db_path)
        
        if not os.path.exists(db_path):
            result['status'] = 'error'
            result['errors'].append(f"Database file not found: {db_path}")
            return result
        
        # Get database size
        result['size_mb'] = os.path.getsize(db_path) / (1024 * 1024)
        
        # Check integrity and get metrics
        with get_db_connection_with_context(db_path) as conn:
            cur = conn.cursor()
            
            # Integrity check
            try:
                cur.execute("PRAGMA integrity_check")
                integrity_result = cur.fetchone()[0]
                result['integrity'] = integrity_result
                
                if integrity_result == 'ok':
                    result['status'] = 'healthy'
                else:
                    result['status'] = 'unhealthy'
                    result['errors'].append(f"Integrity check failed: {integrity_result}")
            except Exception as e:
                result['status'] = 'error'
                result['errors'].append(f"Integrity check error: {str(e)}")
            
            # Get page information
            try:
                cur.execute("PRAGMA page_count")
                result['page_count'] = cur.fetchone()[0]
                
                cur.execute("PRAGMA page_size")
                result['page_size'] = cur.fetchone()[0]
            except Exception as e:
                result['errors'].append(f"Page info error: {str(e)}")
            
            # Get table counts
            try:
                cur.execute("SELECT COUNT(*) FROM companies")
                result['company_count'] = cur.fetchone()[0]
            except Exception as e:
                result['errors'].append(f"Company count error: {str(e)}")
            
            try:
                cur.execute("SELECT COUNT(*) FROM vouchers")
                result['voucher_count'] = cur.fetchone()[0]
            except Exception as e:
                result['errors'].append(f"Voucher count error: {str(e)}")
            
            try:
                cur.execute("SELECT COUNT(*) FROM sync_logs")
                result['log_count'] = cur.fetchone()[0]
            except Exception as e:
                result['errors'].append(f"Log count error: {str(e)}")
        
        # Final status determination
        if result['status'] == 'unknown':
            if result['errors']:
                result['status'] = 'error'
            else:
                result['status'] = 'healthy'
        
        return result
        
    except Exception as e:
        result['status'] = 'error'
        result['errors'].append(f"Health check failed: {str(e)}")
        return result


def get_database_statistics(db_path: str = DB_FILE) -> Dict:
    """
    Get detailed database statistics.
    
    Args:
        db_path: Path to database file
    
    Returns:
        Dict with statistics
    """
    stats = {
        'size_mb': 0.0,
        'tables': {},
        'indexes': [],
        'page_count': 0,
        'page_size': 0
    }
    
    try:
        # Resolve path
        if not os.path.isabs(db_path):
            current_file = os.path.abspath(__file__)
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
            db_path = os.path.join(project_root, db_path)
            db_path = os.path.abspath(db_path)
        
        if not os.path.exists(db_path):
            return stats
        
        stats['size_mb'] = os.path.getsize(db_path) / (1024 * 1024)
        
        with get_db_connection_with_context(db_path) as conn:
            cur = conn.cursor()
            
            # Get page info
            cur.execute("PRAGMA page_count")
            stats['page_count'] = cur.fetchone()[0]
            
            cur.execute("PRAGMA page_size")
            stats['page_size'] = cur.fetchone()[0]
            
            # Get table info
            cur.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """)
            tables = [row[0] for row in cur.fetchall()]
            
            for table in tables:
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                count = cur.fetchone()[0]
                stats['tables'][table] = count
            
            # Get index info
            cur.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='index' AND name NOT LIKE 'sqlite_%'
            """)
            stats['indexes'] = [row[0] for row in cur.fetchall()]
        
        return stats
        
    except Exception as e:
        return stats

