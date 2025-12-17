"""
Sync Log Data Model
===================

Phase 6: Code Quality
Data model class for SyncLog entities.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class SyncLog:
    """
    Sync log data model.
    
    Attributes:
        id: Log ID (primary key)
        company_guid: Company GUID
        company_alterid: Company AlterID
        company_name: Company name
        log_level: Log level (INFO, WARNING, ERROR, SUCCESS)
        log_message: Log message
        log_details: Additional details
        sync_status: Sync status (started, in_progress, completed, failed)
        records_synced: Number of records synced
        error_code: Error code (if any)
        error_message: Error message (if any)
        duration_seconds: Duration in seconds
        created_at: Creation timestamp (UTC)
    """
    id: Optional[int] = None
    company_guid: str = ""
    company_alterid: str = ""
    company_name: str = ""
    log_level: str = "INFO"
    log_message: str = ""
    log_details: Optional[str] = None
    sync_status: Optional[str] = None
    records_synced: int = 0
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    duration_seconds: Optional[float] = None
    created_at: Optional[str] = None
    
    def to_dict(self) -> dict:
        """
        Convert SyncLog to dictionary.
        
        Returns:
            Dictionary representation of SyncLog
        """
        return {
            'id': self.id,
            'company_guid': self.company_guid,
            'company_alterid': self.company_alterid,
            'company_name': self.company_name,
            'log_level': self.log_level,
            'log_message': self.log_message,
            'log_details': self.log_details,
            'sync_status': self.sync_status,
            'records_synced': self.records_synced,
            'error_code': self.error_code,
            'error_message': self.error_message,
            'duration_seconds': self.duration_seconds,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'SyncLog':
        """
        Create SyncLog from dictionary.
        
        Args:
            data: Dictionary with sync log data
            
        Returns:
            SyncLog instance
        """
        return cls(**{k: v for k, v in data.items() if hasattr(cls, k)})
    
    def is_error(self) -> bool:
        """Check if log is an error."""
        return self.log_level == 'ERROR'
    
    def is_success(self) -> bool:
        """Check if log is a success."""
        return self.log_level == 'SUCCESS'
    
    def is_warning(self) -> bool:
        """Check if log is a warning."""
        return self.log_level == 'WARNING'
    
    def is_info(self) -> bool:
        """Check if log is info."""
        return self.log_level == 'INFO'
    
    def is_completed(self) -> bool:
        """Check if sync is completed."""
        return self.sync_status == 'completed'
    
    def is_failed(self) -> bool:
        """Check if sync failed."""
        return self.sync_status == 'failed'
    
    def __str__(self) -> str:
        """String representation."""
        return f"SyncLog(id={self.id}, company='{self.company_name}', level='{self.log_level}', status='{self.sync_status}', message='{self.log_message[:50]}...')"
    
    def __repr__(self) -> str:
        """Developer representation."""
        return self.__str__()

