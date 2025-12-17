"""
Data Validators
===============

Phase 5: Security & Validation
Provides comprehensive data validation for user inputs and business logic.

Features:
- Input validation (GUID, AlterID, dates, amounts)
- Type validation
- Range validation
- Format validation
- Business rule validation
"""

import re
from datetime import datetime
from typing import Tuple, Optional, Any


class ValidationError(Exception):
    """Custom exception for validation errors."""
    def __init__(self, message: str, field: str = None):
        self.message = message
        self.field = field
        super().__init__(self.message)


class CompanyValidator:
    """Validators for company-related data."""
    
    # GUID format: 8-4-4-4-12 (e.g., 12345678-1234-1234-1234-123456789012)
    GUID_PATTERN = re.compile(r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')
    
    @staticmethod
    def validate_guid(guid: str) -> Tuple[bool, str]:
        """
        Validate GUID format.
        
        Args:
            guid: Company GUID string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not guid:
            return False, "GUID cannot be empty"
        
        if not isinstance(guid, str):
            return False, "GUID must be a string"
        
        guid = guid.strip()
        
        if len(guid) < 10:
            return False, "GUID is too short (minimum 10 characters)"
        
        if len(guid) > 50:
            return False, "GUID is too long (maximum 50 characters)"
        
        # Check GUID format (8-4-4-4-12)
        if not CompanyValidator.GUID_PATTERN.match(guid):
            return False, "GUID format is invalid (expected: 8-4-4-4-12 format)"
        
        return True, ""
    
    @staticmethod
    def validate_alterid(alterid: Any) -> Tuple[bool, str]:
        """
        Validate AlterID format.
        
        Args:
            alterid: Company AlterID (can be string, int, or float)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if alterid is None:
            return False, "AlterID cannot be None"
        
        # Convert to string for validation
        alterid_str = str(alterid).strip()
        
        if not alterid_str:
            return False, "AlterID cannot be empty"
        
        # Try to convert to float (AlterID can be numeric like 95278.0)
        try:
            alterid_float = float(alterid_str)
            if alterid_float < 0:
                return False, "AlterID cannot be negative"
            if alterid_float > 999999999:
                return False, "AlterID is too large (maximum 999999999)"
        except ValueError:
            return False, "AlterID must be numeric"
        
        return True, ""
    
    @staticmethod
    def validate_company_name(name: str) -> Tuple[bool, str]:
        """
        Validate company name.
        
        Args:
            name: Company name string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not name:
            return False, "Company name cannot be empty"
        
        if not isinstance(name, str):
            return False, "Company name must be a string"
        
        name = name.strip()
        
        if len(name) < 1:
            return False, "Company name cannot be empty"
        
        if len(name) > 200:
            return False, "Company name is too long (maximum 200 characters)"
        
        # Check for potentially dangerous characters (SQL injection prevention)
        dangerous_chars = [';', '--', '/*', '*/', 'xp_', 'sp_']
        for char in dangerous_chars:
            if char.lower() in name.lower():
                return False, f"Company name contains invalid characters"
        
        return True, ""
    
    @staticmethod
    def validate_dsn(dsn: str) -> Tuple[bool, str]:
        """
        Validate DSN (Data Source Name).
        
        Args:
            dsn: DSN string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not dsn:
            return False, "DSN cannot be empty"
        
        if not isinstance(dsn, str):
            return False, "DSN must be a string"
        
        dsn = dsn.strip()
        
        if len(dsn) < 1:
            return False, "DSN cannot be empty"
        
        if len(dsn) > 100:
            return False, "DSN is too long (maximum 100 characters)"
        
        # Check for potentially dangerous characters
        dangerous_chars = [';', '--', '/*', '*/']
        for char in dangerous_chars:
            if char in dsn:
                return False, "DSN contains invalid characters"
        
        return True, ""


class DateValidator:
    """Validators for date-related data."""
    
    @staticmethod
    def validate_date_format(date_str: str, format: str = "%d-%m-%Y") -> Tuple[bool, str]:
        """
        Validate date format.
        
        Args:
            date_str: Date string to validate
            format: Expected date format (default: DD-MM-YYYY)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not date_str:
            return False, "Date cannot be empty"
        
        if not isinstance(date_str, str):
            return False, "Date must be a string"
        
        date_str = date_str.strip()
        
        try:
            datetime.strptime(date_str, format)
            return True, ""
        except ValueError:
            return False, f"Date format is invalid (expected: {format})"
    
    @staticmethod
    def validate_date_range(from_date: str, to_date: str, format: str = "%d-%m-%Y") -> Tuple[bool, str]:
        """
        Validate date range (from_date <= to_date).
        
        Args:
            from_date: Start date string
            to_date: End date string
            format: Date format (default: DD-MM-YYYY)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate individual dates
        is_valid, error = DateValidator.validate_date_format(from_date, format)
        if not is_valid:
            return False, f"From date: {error}"
        
        is_valid, error = DateValidator.validate_date_format(to_date, format)
        if not is_valid:
            return False, f"To date: {error}"
        
        # Parse dates
        try:
            from_dt = datetime.strptime(from_date.strip(), format)
            to_dt = datetime.strptime(to_date.strip(), format)
            
            if from_dt > to_dt:
                return False, "From date cannot be after to date"
            
            # Check if date range is too large (e.g., more than 10 years)
            days_diff = (to_dt - from_dt).days
            if days_diff > 3650:  # 10 years
                return False, "Date range is too large (maximum 10 years)"
            
            return True, ""
        except ValueError:
            return False, "Date parsing error"
    
    @staticmethod
    def validate_financial_year(fy_str: str) -> Tuple[bool, str]:
        """
        Validate financial year format (e.g., "2024-25").
        
        Args:
            fy_str: Financial year string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not fy_str:
            return False, "Financial year cannot be empty"
        
        if not isinstance(fy_str, str):
            return False, "Financial year must be a string"
        
        fy_str = fy_str.strip()
        
        # Pattern: YYYY-YY (e.g., 2024-25)
        pattern = re.compile(r'^\d{4}-\d{2}$')
        if not pattern.match(fy_str):
            return False, "Financial year format is invalid (expected: YYYY-YY, e.g., 2024-25)"
        
        # Validate year range
        try:
            start_year = int(fy_str.split('-')[0])
            end_year_short = int(fy_str.split('-')[1])
            end_year = 2000 + end_year_short
            
            if start_year < 1900 or start_year > 2100:
                return False, "Financial year start year is out of range (1900-2100)"
            
            if end_year != start_year + 1:
                return False, "Financial year end year must be start year + 1"
        except (ValueError, IndexError):
            return False, "Financial year parsing error"
        
        return True, ""


class AmountValidator:
    """Validators for amount-related data."""
    
    @staticmethod
    def validate_amount(amount: Any) -> Tuple[bool, str]:
        """
        Validate amount (must be non-negative number).
        
        Args:
            amount: Amount value (can be int, float, or string)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if amount is None:
            return False, "Amount cannot be None"
        
        # Convert to float
        try:
            amount_float = float(amount)
        except (ValueError, TypeError):
            return False, "Amount must be a number"
        
        if amount_float < 0:
            return False, "Amount cannot be negative"
        
        # Check for extremely large values (potential data corruption)
        if abs(amount_float) > 1e15:  # 1 quadrillion
            return False, "Amount is too large (maximum 1,000,000,000,000,000)"
        
        return True, ""
    
    @staticmethod
    def validate_percentage(percentage: Any) -> Tuple[bool, str]:
        """
        Validate percentage (0-100).
        
        Args:
            percentage: Percentage value
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        is_valid, error = AmountValidator.validate_amount(percentage)
        if not is_valid:
            return False, error
        
        try:
            percentage_float = float(percentage)
            if percentage_float > 100:
                return False, "Percentage cannot exceed 100"
            return True, ""
        except (ValueError, TypeError):
            return False, "Percentage must be a number"


class VoucherValidator:
    """Validators for voucher-related data."""
    
    @staticmethod
    def validate_voucher_type(vch_type: str) -> Tuple[bool, str]:
        """
        Validate voucher type.
        
        Args:
            vch_type: Voucher type string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not vch_type:
            return False, "Voucher type cannot be empty"
        
        if not isinstance(vch_type, str):
            return False, "Voucher type must be a string"
        
        vch_type = vch_type.strip()
        
        if len(vch_type) > 50:
            return False, "Voucher type is too long (maximum 50 characters)"
        
        return True, ""
    
    @staticmethod
    def validate_voucher_number(vch_no: str) -> Tuple[bool, str]:
        """
        Validate voucher number.
        
        Args:
            vch_no: Voucher number string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not vch_no:
            return False, "Voucher number cannot be empty"
        
        if not isinstance(vch_no, str):
            return False, "Voucher number must be a string"
        
        vch_no = vch_no.strip()
        
        if len(vch_no) > 100:
            return False, "Voucher number is too long (maximum 100 characters)"
        
        return True, ""


class InputSanitizer:
    """Utilities for sanitizing user inputs."""
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 1000) -> str:
        """
        Sanitize string input.
        
        Args:
            value: Input string
            max_length: Maximum allowed length
            
        Returns:
            Sanitized string
        """
        if not value:
            return ""
        
        if not isinstance(value, str):
            value = str(value)
        
        # Strip whitespace
        value = value.strip()
        
        # Truncate if too long
        if len(value) > max_length:
            value = value[:max_length]
        
        # Remove null bytes
        value = value.replace('\x00', '')
        
        return value
    
    @staticmethod
    def sanitize_sql_input(value: str) -> str:
        """
        Sanitize input for SQL queries (additional safety layer).
        Note: This is a secondary safety measure. Primary protection is parameterized queries.
        
        Args:
            value: Input string
            
        Returns:
            Sanitized string
        """
        if not value:
            return ""
        
        value = InputSanitizer.sanitize_string(value)
        
        # Remove SQL injection patterns (secondary safety)
        dangerous_patterns = [';', '--', '/*', '*/', 'xp_', 'sp_', 'exec', 'execute']
        for pattern in dangerous_patterns:
            if pattern.lower() in value.lower():
                # Replace with safe alternative
                value = value.replace(pattern, '')
        
        return value


# Convenience functions for common validations
def validate_company_data(name: str, guid: str, alterid: Any) -> Tuple[bool, str]:
    """
    Validate complete company data.
    
    Args:
        name: Company name
        guid: Company GUID
        alterid: Company AlterID
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Validate name
    is_valid, error = CompanyValidator.validate_company_name(name)
    if not is_valid:
        return False, error
    
    # Validate GUID
    is_valid, error = CompanyValidator.validate_guid(guid)
    if not is_valid:
        return False, error
    
    # Validate AlterID
    is_valid, error = CompanyValidator.validate_alterid(alterid)
    if not is_valid:
        return False, error
    
    return True, ""


def validate_sync_params(guid: str, alterid: Any, from_date: str, to_date: str) -> Tuple[bool, str]:
    """
    Validate sync parameters.
    
    Args:
        guid: Company GUID
        alterid: Company AlterID
        from_date: Start date (DD-MM-YYYY)
        to_date: End date (DD-MM-YYYY)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Validate GUID
    is_valid, error = CompanyValidator.validate_guid(guid)
    if not is_valid:
        return False, f"GUID validation failed: {error}"
    
    # Validate AlterID
    is_valid, error = CompanyValidator.validate_alterid(alterid)
    if not is_valid:
        return False, f"AlterID validation failed: {error}"
    
    # Validate date range
    is_valid, error = DateValidator.validate_date_range(from_date, to_date)
    if not is_valid:
        return False, f"Date range validation failed: {error}"
    
    return True, ""

