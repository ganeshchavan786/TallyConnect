"""
Backend Utilities
=================

Utility functions and helpers for TallyConnect backend.
"""

import os
from datetime import datetime
from typing import Optional

# Import from submodules
from .error_handler import get_user_friendly_error, is_tally_connection_error
from .portal_starter import start_portal_in_background, shutdown_portal

# Report utilities (moved from backend/utils.py)
def format_currency(amount: float, currency: str = "₹") -> str:
    """
    Format number as currency with Indian numbering system.
    
    Args:
        amount: Amount to format
        currency: Currency symbol (default: ₹)
        
    Returns:
        Formatted currency string
        
    Example:
        >>> format_currency(1234567.89)
        '₹ 12,34,567.89'
    """
    if amount < 0:
        return f"-{currency} {abs(amount):,.2f}"
    return f"{currency} {amount:,.2f}"


def calculate_age(date_str: str, as_on_date: Optional[str] = None) -> int:
    """
    Calculate age of transaction in days.
    
    Args:
        date_str: Transaction date (DD-MM-YYYY or YYYY-MM-DD)
        as_on_date: Date to calculate age from (default: today)
        
    Returns:
        Age in days
    """
    try:
        # Try DD-MM-YYYY format first
        try:
            trans_date = datetime.strptime(date_str, "%d-%m-%Y")
        except ValueError:
            # Try YYYY-MM-DD format
            trans_date = datetime.strptime(date_str, "%Y-%m-%d")
        
        if as_on_date:
            try:
                reference_date = datetime.strptime(as_on_date, "%d-%m-%Y")
            except ValueError:
                reference_date = datetime.strptime(as_on_date, "%Y-%m-%d")
        else:
            reference_date = datetime.now()
        
        delta = reference_date - trans_date
        return delta.days
    except Exception:
        return 0


def get_age_bucket(days: int) -> str:
    """
    Get age bucket for outstanding analysis.
    
    Args:
        days: Age in days
        
    Returns:
        Age bucket string
        
    Example:
        >>> get_age_bucket(45)
        '30-60 days'
    """
    if days <= 0:
        return "Not Due"
    elif days <= 30:
        return "0-30 days"
    elif days <= 60:
        return "30-60 days"
    elif days <= 90:
        return "60-90 days"
    else:
        return ">90 days"


def get_report_path(report_type: str, company_name: str) -> str:
    """
    Generate report file path.
    
    Args:
        report_type: Type of report ('outstanding', 'ledger', 'dashboard')
        company_name: Name of company
        
    Returns:
        Full path to report HTML file
    """
    # Get project root (parent of backend folder)
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    project_root = os.path.dirname(backend_dir)
    reports_dir = os.path.join(project_root, "generated_reports")
    os.makedirs(reports_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = "".join(c if c.isalnum() else "_" for c in company_name)
    filename = f"{report_type}_{safe_name}_{timestamp}.html"
    
    return os.path.join(reports_dir, filename)


def format_date(date_str: str, output_format: str = "%d-%m-%Y") -> str:
    """
    Format date string to desired format.
    
    Args:
        date_str: Input date string
        output_format: Desired output format (strftime format)
        
    Returns:
        Formatted date string
    """
    try:
        # Try multiple input formats
        for fmt in ["%d-%m-%Y", "%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"]:
            try:
                date_obj = datetime.strptime(date_str, fmt)
                return date_obj.strftime(output_format)
            except ValueError:
                continue
        return date_str  # Return as-is if parsing fails
    except Exception:
        return date_str


def sanitize_html(text: str) -> str:
    """
    Sanitize text for HTML output.
    
    Args:
        text: Input text
        
    Returns:
        HTML-safe text
    """
    if not text:
        return ""
    
    replacements = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;'
    }
    
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    
    return text

__all__ = [
    # Error handling
    'get_user_friendly_error',
    'is_tally_connection_error',
    # Portal management
    'start_portal_in_background',
    'shutdown_portal',
    # Report utilities
    'format_currency',
    'calculate_age',
    'get_age_bucket',
    'get_report_path',
    'format_date',
    'sanitize_html',
]

