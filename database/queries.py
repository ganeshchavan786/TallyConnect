"""
Database Queries for Reports
=============================

SQL queries for generating reports from SQLite database.
"""


class ReportQueries:
    """Collection of SQL queries for report generation."""
    
    # Company Information
    COMPANY_INFO = """
        SELECT 
            name,
            guid,
            alterid,
            dsn,
            status,
            total_records,
            last_sync,
            created_at
        FROM companies
        WHERE guid = ? AND alterid = ?
    """
    
    # Outstanding Report - Party-wise summary
    OUTSTANDING_SUMMARY = """
        SELECT 
            party_name,
            SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) as debit,
            SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END) as credit,
            SUM(amount) as balance,
            COUNT(*) as transaction_count,
            MIN(date) as first_transaction,
            MAX(date) as last_transaction
        FROM vouchers
        WHERE company_guid = ? 
            AND company_alterid = ?
            AND party_name IS NOT NULL
            AND party_name != ''
        GROUP BY party_name
        HAVING ABS(SUM(amount)) > 0.01
        ORDER BY ABS(SUM(amount)) DESC
    """
    
    # Outstanding Report - Detailed transactions for a party
    OUTSTANDING_DETAILS = """
        SELECT 
            date,
            voucher_type,
            voucher_number,
            party_name,
            amount,
            narration
        FROM vouchers
        WHERE company_guid = ?
            AND company_alterid = ?
            AND party_name = ?
        ORDER BY date, voucher_number
    """
    
    # Ledger Report - All transactions for a party/ledger
    LEDGER_TRANSACTIONS = """
        SELECT 
            date,
            voucher_type,
            voucher_number,
            party_name,
            amount,
            narration
        FROM vouchers
        WHERE company_guid = ?
            AND company_alterid = ?
            AND party_name = ?
            AND date BETWEEN ? AND ?
        ORDER BY date, voucher_number
    """
    
    # Dashboard - Summary statistics
    DASHBOARD_STATS = """
        SELECT 
            COUNT(DISTINCT party_name) as total_parties,
            COUNT(*) as total_transactions,
            SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) as total_debit,
            SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END) as total_credit,
            SUM(amount) as net_balance,
            MIN(date) as first_transaction_date,
            MAX(date) as last_transaction_date
        FROM vouchers
        WHERE company_guid = ?
            AND company_alterid = ?
    """
    
    # Dashboard - Top 10 Debtors (Outstanding Receivables)
    TOP_DEBTORS = """
        SELECT 
            party_name,
            SUM(amount) as balance,
            COUNT(*) as transaction_count
        FROM vouchers
        WHERE company_guid = ?
            AND company_alterid = ?
            AND party_name IS NOT NULL
            AND party_name != ''
        GROUP BY party_name
        HAVING SUM(amount) > 0.01
        ORDER BY SUM(amount) DESC
        LIMIT 10
    """
    
    # Dashboard - Top 10 Creditors (Outstanding Payables)
    TOP_CREDITORS = """
        SELECT 
            party_name,
            ABS(SUM(amount)) as balance,
            COUNT(*) as transaction_count
        FROM vouchers
        WHERE company_guid = ?
            AND company_alterid = ?
            AND party_name IS NOT NULL
            AND party_name != ''
        GROUP BY party_name
        HAVING SUM(amount) < -0.01
        ORDER BY SUM(amount) ASC
        LIMIT 10
    """
    
    # Dashboard - Voucher type wise summary
    VOUCHER_TYPE_SUMMARY = """
        SELECT 
            voucher_type,
            COUNT(*) as count,
            SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) as total_debit,
            SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END) as total_credit
        FROM vouchers
        WHERE company_guid = ?
            AND company_alterid = ?
        GROUP BY voucher_type
        ORDER BY count DESC
    """
    
    # Dashboard - Month-wise transaction trend
    MONTHLY_TREND = """
        SELECT 
            strftime('%Y-%m', date) as month,
            COUNT(*) as transaction_count,
            SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) as total_debit,
            SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END) as total_credit
        FROM vouchers
        WHERE company_guid = ?
            AND company_alterid = ?
        GROUP BY strftime('%Y-%m', date)
        ORDER BY month
    """
    
    # Get all unique parties (for dropdowns/filters)
    GET_ALL_PARTIES = """
        SELECT DISTINCT party_name
        FROM vouchers
        WHERE company_guid = ?
            AND company_alterid = ?
            AND party_name IS NOT NULL
            AND party_name != ''
        ORDER BY party_name
    """
    
    # Get all voucher types (for filters)
    GET_VOUCHER_TYPES = """
        SELECT DISTINCT voucher_type
        FROM vouchers
        WHERE company_guid = ?
            AND company_alterid = ?
        ORDER BY voucher_type
    """

