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
            vch_party_name as party_name,
            SUM(COALESCE(vch_dr_amt, 0)) as debit,
            SUM(COALESCE(vch_cr_amt, 0)) as credit,
            (SUM(COALESCE(vch_dr_amt, 0)) - SUM(COALESCE(vch_cr_amt, 0))) as balance,
            COUNT(*) as transaction_count,
            MIN(vch_date) as first_transaction,
            MAX(vch_date) as last_transaction
        FROM vouchers
        WHERE company_guid = ? 
            AND company_alterid = ?
            AND vch_party_name IS NOT NULL
            AND vch_party_name != ''
        GROUP BY vch_party_name
        HAVING ABS(SUM(COALESCE(vch_dr_amt, 0)) - SUM(COALESCE(vch_cr_amt, 0))) > 0.01
        ORDER BY ABS(SUM(COALESCE(vch_dr_amt, 0)) - SUM(COALESCE(vch_cr_amt, 0))) DESC
    """
    
    # Outstanding Report - Detailed transactions for a party
    OUTSTANDING_DETAILS = """
        SELECT 
            vch_date as date,
            vch_type as voucher_type,
            vch_no as voucher_number,
            vch_party_name as party_name,
            vch_dr_amt as debit,
            vch_cr_amt as credit,
            vch_narration as narration
        FROM vouchers
        WHERE company_guid = ?
            AND company_alterid = ?
            AND vch_party_name = ?
        ORDER BY vch_date, vch_no
    """
    
    # Ledger Report - All transactions for a party/ledger
    LEDGER_TRANSACTIONS = """
        SELECT 
            vch_date as date,
            vch_type as voucher_type,
            vch_no as voucher_number,
            vch_party_name as party_name,
            led_name as ledger_name,
            vch_dr_amt as debit,
            vch_cr_amt as credit,
            vch_narration as narration
        FROM vouchers
        WHERE company_guid = ?
            AND company_alterid = ?
            AND (vch_party_name = ? OR led_name = ?)
            AND vch_date BETWEEN ? AND ?
        ORDER BY vch_date, vch_no
    """
    
    # Dashboard - Summary statistics
    DASHBOARD_STATS = """
        SELECT 
            COUNT(DISTINCT vch_party_name) as total_parties,
            COUNT(*) as total_transactions,
            SUM(COALESCE(vch_dr_amt, 0)) as total_debit,
            SUM(COALESCE(vch_cr_amt, 0)) as total_credit,
            (SUM(COALESCE(vch_dr_amt, 0)) - SUM(COALESCE(vch_cr_amt, 0))) as net_balance,
            MIN(vch_date) as first_transaction_date,
            MAX(vch_date) as last_transaction_date
        FROM vouchers
        WHERE company_guid = ?
            AND company_alterid = ?
    """
    
    # Dashboard - Top 10 Debtors (Outstanding Receivables)
    TOP_DEBTORS = """
        SELECT 
            vch_party_name as party_name,
            (SUM(COALESCE(vch_dr_amt, 0)) - SUM(COALESCE(vch_cr_amt, 0))) as balance,
            COUNT(*) as transaction_count
        FROM vouchers
        WHERE company_guid = ?
            AND company_alterid = ?
            AND vch_party_name IS NOT NULL
            AND vch_party_name != ''
        GROUP BY vch_party_name
        HAVING (SUM(COALESCE(vch_dr_amt, 0)) - SUM(COALESCE(vch_cr_amt, 0))) > 0.01
        ORDER BY (SUM(COALESCE(vch_dr_amt, 0)) - SUM(COALESCE(vch_cr_amt, 0))) DESC
        LIMIT 10
    """
    
    # Dashboard - Top 10 Creditors (Outstanding Payables)
    TOP_CREDITORS = """
        SELECT 
            vch_party_name as party_name,
            ABS(SUM(COALESCE(vch_dr_amt, 0)) - SUM(COALESCE(vch_cr_amt, 0))) as balance,
            COUNT(*) as transaction_count
        FROM vouchers
        WHERE company_guid = ?
            AND company_alterid = ?
            AND vch_party_name IS NOT NULL
            AND vch_party_name != ''
        GROUP BY vch_party_name
        HAVING (SUM(COALESCE(vch_dr_amt, 0)) - SUM(COALESCE(vch_cr_amt, 0))) < -0.01
        ORDER BY (SUM(COALESCE(vch_dr_amt, 0)) - SUM(COALESCE(vch_cr_amt, 0))) ASC
        LIMIT 10
    """
    
    # Dashboard - Voucher type wise summary
    VOUCHER_TYPE_SUMMARY = """
        SELECT 
            vch_type as voucher_type,
            COUNT(*) as count,
            SUM(COALESCE(vch_dr_amt, 0)) as total_debit,
            SUM(COALESCE(vch_cr_amt, 0)) as total_credit
        FROM vouchers
        WHERE company_guid = ?
            AND company_alterid = ?
        GROUP BY vch_type
        ORDER BY count DESC
    """
    
    # Dashboard - Month-wise transaction trend
    MONTHLY_TREND = """
        SELECT 
            strftime('%Y-%m', vch_date) as month,
            COUNT(*) as transaction_count,
            SUM(COALESCE(vch_dr_amt, 0)) as total_debit,
            SUM(COALESCE(vch_cr_amt, 0)) as total_credit
        FROM vouchers
        WHERE company_guid = ?
            AND company_alterid = ?
        GROUP BY strftime('%Y-%m', vch_date)
        ORDER BY month
    """
    
    # Get all unique parties (for dropdowns/filters)
    GET_ALL_PARTIES = """
        SELECT DISTINCT vch_party_name as party_name
        FROM vouchers
        WHERE company_guid = ?
            AND company_alterid = ?
            AND vch_party_name IS NOT NULL
            AND vch_party_name != ''
        ORDER BY vch_party_name
    """
    
    # Get all voucher types (for filters)
    GET_VOUCHER_TYPES = """
        SELECT DISTINCT vch_type as voucher_type
        FROM vouchers
        WHERE company_guid = ?
            AND company_alterid = ?
        ORDER BY vch_type
    """
    
    # Get all ledgers (for filters)
    GET_ALL_LEDGERS = """
        SELECT DISTINCT led_name as ledger_name
        FROM vouchers
        WHERE company_guid = ?
            AND company_alterid = ?
            AND led_name IS NOT NULL
            AND led_name != ''
        ORDER BY led_name
    """

