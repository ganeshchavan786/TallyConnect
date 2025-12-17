"""
Company Data Model
=================

Phase 6: Code Quality
Data model class for Company entities.
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Company:
    """
    Company data model.
    
    Attributes:
        id: Company ID (primary key)
        name: Company name
        guid: Company GUID (unique identifier)
        alterid: Company AlterID (unique per financial year)
        dsn: Data Source Name (optional)
        status: Company status (new, syncing, synced, failed, incomplete)
        total_records: Total number of vouchers synced
        last_sync: Last sync timestamp (UTC)
        created_at: Creation timestamp (UTC)
    """
    id: Optional[int] = None
    name: str = ""
    guid: str = ""
    alterid: str = ""
    dsn: Optional[str] = None
    status: str = "new"
    total_records: int = 0
    last_sync: Optional[str] = None
    created_at: Optional[str] = None
    
    def to_dict(self) -> dict:
        """
        Convert Company to dictionary.
        
        Returns:
            Dictionary representation of Company
        """
        return {
            'id': self.id,
            'name': self.name,
            'guid': self.guid,
            'alterid': self.alterid,
            'dsn': self.dsn,
            'status': self.status,
            'total_records': self.total_records,
            'last_sync': self.last_sync,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Company':
        """
        Create Company from dictionary.
        
        Args:
            data: Dictionary with company data
            
        Returns:
            Company instance
        """
        return cls(
            id=data.get('id'),
            name=data.get('name', ''),
            guid=data.get('guid', ''),
            alterid=data.get('alterid', ''),
            dsn=data.get('dsn'),
            status=data.get('status', 'new'),
            total_records=data.get('total_records', 0),
            last_sync=data.get('last_sync'),
            created_at=data.get('created_at')
        )
    
    @classmethod
    def from_tuple(cls, row: tuple, columns: list = None) -> 'Company':
        """
        Create Company from database tuple.
        
        Args:
            row: Database row tuple
            columns: Optional list of column names (for mapping)
            
        Returns:
            Company instance
        """
        if columns:
            # Map by column names
            data = dict(zip(columns, row))
            return cls.from_dict(data)
        else:
            # Assume standard order: id, name, guid, alterid, dsn, status, total_records, last_sync, created_at
            return cls(
                id=row[0] if len(row) > 0 else None,
                name=row[1] if len(row) > 1 else "",
                guid=row[2] if len(row) > 2 else "",
                alterid=row[3] if len(row) > 3 else "",
                dsn=row[4] if len(row) > 4 else None,
                status=row[5] if len(row) > 5 else "new",
                total_records=row[6] if len(row) > 6 else 0,
                last_sync=row[7] if len(row) > 7 else None,
                created_at=row[8] if len(row) > 8 else None
            )
    
    def is_synced(self) -> bool:
        """Check if company is synced."""
        return self.status == 'synced'
    
    def is_syncing(self) -> bool:
        """Check if company is currently syncing."""
        return self.status == 'syncing'
    
    def has_records(self) -> bool:
        """Check if company has synced records."""
        return self.total_records > 0
    
    def __str__(self) -> str:
        """String representation."""
        return f"Company(id={self.id}, name='{self.name}', guid='{self.guid}', alterid='{self.alterid}', status='{self.status}')"
    
    def __repr__(self) -> str:
        """Developer representation."""
        return self.__str__()

