"""
Error Handler Utilities
=======================

User-friendly error message conversion for Tally connection errors.
Phase 5: Enhanced error handling with validation errors and better logging.
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
    
    # Validation errors (Phase 5)
    if "VALIDATION" in error_str or "VALIDATOR" in error_str:
        # Extract validation message if available
        if ":" in error_msg:
            parts = str(error_msg).split(":", 1)
            if len(parts) > 1:
                return f"⚠️ Validation Error: {parts[1].strip()}"
        return f"⚠️ Validation Error: {error_msg}"
    
    # Encryption/Decryption errors (Phase 5)
    if "ENCRYPTION" in error_str or "DECRYPTION" in error_str or "CIPHER" in error_str:
        return "⚠️ Encryption error occurred.\n\nPlease check encryption key configuration."
    
    # Database errors
    if "DATABASE" in error_str or "SQLITE" in error_str or "INTEGRITY" in error_str:
        if "UNIQUE" in error_str or "DUPLICATE" in error_str:
            return "⚠️ Data already exists.\n\nThis record may have been synced previously."
        return "⚠️ Database error occurred.\n\nPlease check database file and permissions."
    
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


def log_error_with_context(error: Exception, context: str = "", logger=None):
    """
    Log error with context information.
    Phase 5: Enhanced error logging.
    
    Args:
        error: Exception object
        context: Context information (e.g., "sync", "validation", "encryption")
        logger: Optional logger instance (if None, prints to console)
    """
    error_type = type(error).__name__
    error_msg = str(error)
    
    log_message = f"[ERROR] {context}: {error_type}: {error_msg}"
    
    if logger:
        try:
            logger.error(log_message)
        except:
            print(log_message)
    else:
        print(log_message)
    
    # Print traceback for debugging (only in development)
    import traceback
    traceback.print_exc()


def handle_validation_error(error: Exception, field: str = None) -> str:
    """
    Handle validation errors and return user-friendly message.
    Phase 5: Validation error handling.
    
    Args:
        error: ValidationError exception
        field: Optional field name
        
    Returns:
        User-friendly error message
    """
    from backend.utils.validators import ValidationError
    
    if isinstance(error, ValidationError):
        if field:
            return f"⚠️ Validation Error ({field}): {error.message}"
        return f"⚠️ Validation Error: {error.message}"
    
    return f"⚠️ Validation Error: {str(error)}"

