"""
Voucher Data Model
==================

Phase 6: Code Quality
Data model class for Voucher entities.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Voucher:
    """
    Voucher data model.
    
    Attributes:
        id: Voucher ID (primary key)
        company_guid: Company GUID
        company_alterid: Company AlterID
        company_name: Company name
        vch_date: Voucher date
        vch_type: Voucher type
        vch_no: Voucher number
        vch_mst_id: Voucher master ID
        led_name: Ledger name
        led_amount: Ledger amount
        vch_dr_cr: Debit/Credit indicator
        vch_dr_amt: Debit amount
        vch_cr_amt: Credit amount
        vch_party_name: Party name
        vch_led_parent: Ledger parent
        vch_narration: Narration
        vch_gstin: GSTIN
        vch_led_gstin: Ledger GSTIN
        vch_led_bill_ref: Bill reference
        vch_led_bill_type: Bill type
        vch_led_primary_grp: Primary group
        vch_led_nature: Ledger nature
        vch_led_bs_grp: Balance sheet group
        vch_led_bs_grp_nature: BS group nature
        vch_is_optional: Is optional
        vch_led_bill_count: Bill count
        created_at: Creation timestamp
    """
    id: Optional[int] = None
    company_guid: str = ""
    company_alterid: str = ""
    company_name: Optional[str] = None
    vch_date: Optional[str] = None
    vch_type: Optional[str] = None
    vch_no: Optional[str] = None
    vch_mst_id: Optional[str] = None
    led_name: Optional[str] = None
    led_amount: Optional[float] = None
    vch_dr_cr: Optional[str] = None
    vch_dr_amt: Optional[float] = None
    vch_cr_amt: Optional[float] = None
    vch_party_name: Optional[str] = None
    vch_led_parent: Optional[str] = None
    vch_narration: Optional[str] = None
    vch_gstin: Optional[str] = None
    vch_led_gstin: Optional[str] = None
    vch_led_bill_ref: Optional[str] = None
    vch_led_bill_type: Optional[str] = None
    vch_led_primary_grp: Optional[str] = None
    vch_led_nature: Optional[str] = None
    vch_led_bs_grp: Optional[str] = None
    vch_led_bs_grp_nature: Optional[str] = None
    vch_is_optional: Optional[str] = None
    vch_led_bill_count: Optional[int] = None
    created_at: Optional[str] = None
    
    def to_dict(self) -> dict:
        """
        Convert Voucher to dictionary.
        
        Returns:
            Dictionary representation of Voucher
        """
        return {
            'id': self.id,
            'company_guid': self.company_guid,
            'company_alterid': self.company_alterid,
            'company_name': self.company_name,
            'vch_date': self.vch_date,
            'vch_type': self.vch_type,
            'vch_no': self.vch_no,
            'vch_mst_id': self.vch_mst_id,
            'led_name': self.led_name,
            'led_amount': self.led_amount,
            'vch_dr_cr': self.vch_dr_cr,
            'vch_dr_amt': self.vch_dr_amt,
            'vch_cr_amt': self.vch_cr_amt,
            'vch_party_name': self.vch_party_name,
            'vch_led_parent': self.vch_led_parent,
            'vch_narration': self.vch_narration,
            'vch_gstin': self.vch_gstin,
            'vch_led_gstin': self.vch_led_gstin,
            'vch_led_bill_ref': self.vch_led_bill_ref,
            'vch_led_bill_type': self.vch_led_bill_type,
            'vch_led_primary_grp': self.vch_led_primary_grp,
            'vch_led_nature': self.vch_led_nature,
            'vch_led_bs_grp': self.vch_led_bs_grp,
            'vch_led_bs_grp_nature': self.vch_led_bs_grp_nature,
            'vch_is_optional': self.vch_is_optional,
            'vch_led_bill_count': self.vch_led_bill_count,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Voucher':
        """
        Create Voucher from dictionary.
        
        Args:
            data: Dictionary with voucher data
            
        Returns:
            Voucher instance
        """
        return cls(**{k: v for k, v in data.items() if hasattr(cls, k)})
    
    def is_debit(self) -> bool:
        """Check if voucher is debit."""
        return self.vch_dr_cr == 'Dr' or (self.vch_dr_amt and self.vch_dr_amt > 0)
    
    def is_credit(self) -> bool:
        """Check if voucher is credit."""
        return self.vch_dr_cr == 'Cr' or (self.vch_cr_amt and self.vch_cr_amt > 0)
    
    def get_amount(self) -> float:
        """Get voucher amount (debit or credit)."""
        if self.vch_dr_amt:
            return self.vch_dr_amt
        if self.vch_cr_amt:
            return self.vch_cr_amt
        return self.led_amount or 0.0
    
    def __str__(self) -> str:
        """String representation."""
        return f"Voucher(id={self.id}, company='{self.company_name}', type='{self.vch_type}', date='{self.vch_date}', amount={self.get_amount()})"
    
    def __repr__(self) -> str:
        """Developer representation."""
        return self.__str__()

