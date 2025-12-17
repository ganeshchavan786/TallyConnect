"""
Database Backup Utility
=======================

Handles database backup operations for TallyConnect.
Part of Phase 1: Critical Fixes implementation.
"""

import shutil
import os
from datetime import datetime
from pathlib import Path
from typing import Tuple, Optional


def backup_database(db_path: str, backup_dir: str = None, max_backups: int = None) -> Tuple[bool, str]:
    """
    Create database backup.
    
    Args:
        db_path: Path to database file
        backup_dir: Directory to store backups (relative to project root)
        max_backups: Maximum number of backups to keep
    
    Returns:
        Tuple (success: bool, message: str)
    """
    try:
        # Phase 2: Use environment variables for configuration
        from backend.config.settings import BACKUP_DIR, MAX_BACKUPS
        
        if backup_dir is None:
            backup_dir = BACKUP_DIR
        if max_backups is None:
            max_backups = MAX_BACKUPS
        
        # Resolve paths
        if not os.path.isabs(db_path):
            # Get project root
            current_file = os.path.abspath(__file__)
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
            db_path = os.path.join(project_root, db_path)
            db_path = os.path.abspath(db_path)
        
        if not os.path.exists(db_path):
            return False, f"Database file not found: {db_path}"
        
        # Create backup directory if not exists
        if not os.path.isabs(backup_dir):
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            backup_dir = os.path.join(project_root, backup_dir)
        
        backup_path = Path(backup_dir)
        backup_path.mkdir(parents=True, exist_ok=True)
        
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        db_name = Path(db_path).stem
        backup_file = backup_path / f"{db_name}_{timestamp}.db"
        
        # Copy database file
        shutil.copy2(db_path, backup_file)
        
        # Get file sizes for reporting
        db_size = os.path.getsize(db_path)
        backup_size = os.path.getsize(backup_file)
        
        # Clean old backups (keep only max_backups)
        backups = sorted(backup_path.glob(f"{db_name}_*.db"), reverse=True)
        deleted_count = 0
        for old_backup in backups[max_backups:]:
            try:
                old_backup.unlink()
                deleted_count += 1
            except Exception as e:
                pass  # Continue even if deletion fails
        
        message = f"Backup created: {backup_file.name} ({backup_size / (1024*1024):.2f} MB)"
        if deleted_count > 0:
            message += f" (Deleted {deleted_count} old backup(s))"
        
        return True, message
        
    except Exception as e:
        return False, f"Backup failed: {str(e)}"


def restore_database(backup_path: str, db_path: str) -> Tuple[bool, str]:
    """
    Restore database from backup.
    
    Args:
        backup_path: Path to backup file
        db_path: Path to restore to
    
    Returns:
        Tuple (success: bool, message: str)
    """
    try:
        # Resolve paths
        if not os.path.isabs(backup_path):
            current_file = os.path.abspath(__file__)
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
            backup_path = os.path.join(project_root, backup_path)
            backup_path = os.path.abspath(backup_path)
        
        if not os.path.exists(backup_path):
            return False, f"Backup file not found: {backup_path}"
        
        if not os.path.isabs(db_path):
            current_file = os.path.abspath(__file__)
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
            db_path = os.path.join(project_root, db_path)
            db_path = os.path.abspath(db_path)
        
        # Create backup of current database before restore
        if os.path.exists(db_path):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pre_restore_backup = f"{db_path}.pre_restore_{timestamp}"
            shutil.copy2(db_path, pre_restore_backup)
        
        # Restore from backup
        shutil.copy2(backup_path, db_path)
        
        return True, f"Database restored from: {Path(backup_path).name}"
        
    except Exception as e:
        return False, f"Restore failed: {str(e)}"


def list_backups(backup_dir: str = "backups") -> list:
    """
    List all available backups.
    
    Args:
        backup_dir: Directory containing backups
    
    Returns:
        List of backup file paths sorted by date (newest first)
    """
    try:
        if not os.path.isabs(backup_dir):
            current_file = os.path.abspath(__file__)
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
            backup_dir = os.path.join(project_root, backup_dir)
        
        backup_path = Path(backup_dir)
        if not backup_path.exists():
            return []
        
        backups = sorted(backup_path.glob("*.db"), key=os.path.getmtime, reverse=True)
        return [str(b) for b in backups]
        
    except Exception as e:
        return []

