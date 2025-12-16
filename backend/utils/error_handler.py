"""
Error Handler Utilities
=======================

User-friendly error message conversion for Tally connection errors.
"""


def get_user_friendly_error(error_msg):
    """
    Convert technical ODBC errors to user-friendly messages.
    
    Args:
        error_msg: Technical error message (string or exception)
        
    Returns:
        str: User-friendly error message with actionable steps
        
    Examples:
        >>> get_user_friendly_error("('IM002', 'Data source name not found...')")
        "⚠️ Tally is not working or not connected..."
        
        >>> get_user_friendly_error("Connection timeout")
        "⚠️ Tally connection timeout..."
    """
    if not error_msg:
        return "Tally connection failed. Please check if Tally is running."
    
    error_str = str(error_msg).upper()
    
    # ODBC Data source name not found
    if "IM002" in error_str or "DATA SOURCE NAME NOT FOUND" in error_str:
        return "⚠️ Tally is not working or not connected.\n\nPlease ensure:\n1. Tally is running\n2. Tally ODBC is configured\n3. DSN name is correct"
    
    # Connection timeout
    if "TIMEOUT" in error_str or "TIMED OUT" in error_str:
        return "⚠️ Tally connection timeout.\n\nPlease check:\n1. Tally is running\n2. Network connection is stable"
    
    # Driver not found
    if "DRIVER" in error_str and ("NOT FOUND" in error_str or "NOT SPECIFIED" in error_str):
        return "⚠️ Tally ODBC driver not found.\n\nPlease install Tally ODBC driver."
    
    # Connection refused
    if "CONNECTION REFUSED" in error_str or "CANNOT CONNECT" in error_str:
        return "⚠️ Cannot connect to Tally.\n\nPlease ensure Tally is running and accessible."
    
    # Generic ODBC error
    if "ODBC" in error_str:
        return "⚠️ Tally connection error.\n\nPlease check if Tally is running and ODBC is configured correctly."
    
    # Return original error if no match
    return f"⚠️ Error: {error_msg}"


def is_tally_connection_error(error_msg):
    """
    Check if error is a Tally connection error.
    
    Args:
        error_msg: Error message to check
        
    Returns:
        bool: True if it's a Tally connection error
    """
    if not error_msg:
        return False
    
    error_str = str(error_msg).upper()
    connection_indicators = [
        "IM002",
        "DATA SOURCE NAME NOT FOUND",
        "ODBC",
        "DRIVER",
        "CONNECTION",
        "TIMEOUT",
        "TALLY"
    ]
    
    return any(indicator in error_str for indicator in connection_indicators)

