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
    
    # Ledger Report - All transactions for a party/ledger (Tally Style)
    # Shows each entry separately with other party as Particulars
    # Ledger Report - Get unique voucher IDs for selected ledger
    # This query gets distinct vch_mst_id values (one per voucher)
    LEDGER_VOUCHER_IDS = """
        SELECT DISTINCT vch_mst_id
        FROM vouchers
        WHERE company_guid = ?
            AND company_alterid = ?
            AND (TRIM(UPPER(led_name)) = TRIM(UPPER(?)) OR TRIM(UPPER(vch_party_name)) = TRIM(UPPER(?)))
            AND vch_date BETWEEN ? AND ?
            AND vch_mst_id IS NOT NULL AND TRIM(vch_mst_id) != ''
        ORDER BY vch_date, vch_no
    """
    
    # Ledger Report - Get all lines for a specific voucher
    LEDGER_VOUCHER_LINES = """
        SELECT
            vch_date, vch_type, vch_no, vch_party_name,
            led_name, vch_dr_amt, vch_cr_amt, vch_narration
        FROM vouchers
        WHERE vch_mst_id = ?
        ORDER BY id
    """
    
    # Legacy query (kept for backward compatibility, but not used in new logic)
    LEDGER_TRANSACTIONS = """
        WITH ledger_vouchers AS (
            SELECT 
                vch_date,
                vch_type,
                vch_no,
                company_guid,
                company_alterid,
                SUM(COALESCE(vch_dr_amt, 0)) as total_debit,
                SUM(COALESCE(vch_cr_amt, 0)) as total_credit,
                MAX(vch_narration) as narration
            FROM vouchers
            WHERE company_guid = ?
                AND company_alterid = ?
                AND (vch_party_name LIKE ? OR led_name LIKE ?)
                AND vch_date BETWEEN ? AND ?
            GROUP BY vch_date, vch_no, vch_type, company_guid, company_alterid
        )
        SELECT 
            lv.vch_date as date,
            lv.vch_type as voucher_type,
            lv.vch_no as voucher_number,
            COALESCE(
                (SELECT GROUP_CONCAT(
                    CASE 
                        WHEN v.led_name IS NOT NULL AND v.led_name != '' AND v.led_name != ?
                        THEN v.led_name
                        WHEN v.vch_party_name IS NOT NULL AND v.vch_party_name != '' AND v.vch_party_name != ?
                        THEN v.vch_party_name
                        ELSE NULL
                    END,
                    ', '
                )
                FROM vouchers v
                WHERE v.company_guid = lv.company_guid
                    AND v.company_alterid = lv.company_alterid
                    AND v.vch_date = lv.vch_date
                    AND v.vch_no = lv.vch_no
                    AND (v.led_name != ? OR v.led_name IS NULL)
                    AND (v.vch_party_name != ? OR v.vch_party_name IS NULL)
                LIMIT 1),
                lv.narration,
                '-'
            ) as particulars,
            lv.total_debit as debit,
            lv.total_credit as credit,
            lv.narration as narration
        FROM ledger_vouchers lv
        ORDER BY lv.vch_date, lv.vch_no
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
    
    # Dashboard - Sales Summary (Current Financial Year)
    # Uses same logic as Sales Register: Sum all credit lines for Sales vouchers
    # Handles both "SALES" and "GST SALES" voucher types
    DASHBOARD_SALES_SUMMARY = """
        SELECT 
            COUNT(DISTINCT COALESCE(NULLIF(TRIM(vch_mst_id), ''), vch_date || '|' || vch_no)) as total_sales_count,
            SUM(vch_cr_amt) as total_sales_amount
        FROM vouchers
        WHERE company_guid = ?
            AND company_alterid = ?
            AND (UPPER(TRIM(vch_type)) = 'SALES' OR UPPER(TRIM(vch_type)) LIKE '%SALES%')
            AND vch_cr_amt > 0
            AND vch_date BETWEEN ? AND ?
    """
    
    # Dashboard - Sales Summary (Previous Period for Growth Calculation)
    # Handles both "SALES" and "GST SALES" voucher types
    DASHBOARD_SALES_SUMMARY_PREVIOUS = """
        SELECT 
            COUNT(DISTINCT COALESCE(NULLIF(TRIM(vch_mst_id), ''), vch_date || '|' || vch_no)) as total_sales_count,
            SUM(vch_cr_amt) as total_sales_amount
        FROM vouchers
        WHERE company_guid = ?
            AND company_alterid = ?
            AND (UPPER(TRIM(vch_type)) = 'SALES' OR UPPER(TRIM(vch_type)) LIKE '%SALES%')
            AND vch_cr_amt > 0
            AND vch_date BETWEEN ? AND ?
    """
    
    # Dashboard - Monthly Sales Trend
    # Handles both "SALES" and "GST SALES" voucher types
    MONTHLY_SALES_TREND = """
        SELECT 
            strftime('%Y-%m', vch_date) as month_key,
            strftime('%b %Y', vch_date) as month_name,
            SUM(vch_cr_amt) as sales_amount,
            COUNT(DISTINCT COALESCE(NULLIF(TRIM(vch_mst_id), ''), vch_date || '|' || vch_no)) as sales_count
        FROM vouchers
        WHERE company_guid = ?
            AND company_alterid = ?
            AND (UPPER(TRIM(vch_type)) = 'SALES' OR UPPER(TRIM(vch_type)) LIKE '%SALES%')
            AND vch_cr_amt > 0
            AND vch_date BETWEEN ? AND ?
        GROUP BY month_key
        ORDER BY month_key
    """
    
    # Dashboard - Top Sales Customers
    # Groups sales by customer (vch_party_name) and sums total sales amount
    # Uses same logic as Sales Register: sum all credit lines for Sales vouchers
    # Handles both "SALES" and "GST SALES" voucher types
    TOP_SALES_CUSTOMERS = """
        SELECT 
            vch_party_name as customer_name,
            SUM(vch_cr_amt) as total_sales,
            COUNT(DISTINCT COALESCE(NULLIF(TRIM(vch_mst_id), ''), vch_date || '|' || vch_no)) as invoice_count
        FROM vouchers
        WHERE company_guid = ?
            AND company_alterid = ?
            AND (UPPER(TRIM(vch_type)) = 'SALES' OR UPPER(TRIM(vch_type)) LIKE '%SALES%')
            AND vch_party_name IS NOT NULL
            AND vch_party_name != ''
            AND vch_cr_amt > 0
            AND vch_date BETWEEN ? AND ?
        GROUP BY vch_party_name
        ORDER BY SUM(vch_cr_amt) DESC
        LIMIT 10
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
    
    # Sales Register - Monthly Summary (Group by month)
    # Sales Register - Get unique Sales vouchers (by vch_mst_id or vch_date+vch_no)
    # Handles both "SALES" and "GST SALES" voucher types
    SALES_REGISTER_VOUCHER_IDS = """
        SELECT DISTINCT 
            COALESCE(NULLIF(TRIM(vch_mst_id), ''), vch_date || '|' || vch_no) as voucher_key,
            vch_date,
            vch_no
        FROM vouchers
        WHERE company_guid = ?
            AND company_alterid = ?
            AND (UPPER(TRIM(vch_type)) = 'SALES' OR UPPER(TRIM(vch_type)) LIKE '%SALES%')
            AND vch_date BETWEEN ? AND ?
        ORDER BY vch_date, vch_no
    """
    
    # Sales Register - Get Sales ledger line for a specific voucher
    # IMPORTANT: Tally Sales Register shows TOTAL invoice amount (Sales + GST + TAX)
    # So we need to sum ALL credit lines, not just Sales ledger
    SALES_REGISTER_SALES_LEDGER_LINE = """
        SELECT 
            vch_date,
            SUM(vch_cr_amt) as credit,
            SUM(vch_dr_amt) as debit
        FROM vouchers
        WHERE company_guid = ?
            AND company_alterid = ?
            AND (
                (COALESCE(NULLIF(TRIM(vch_mst_id), ''), vch_date || '|' || vch_no) = ?)
                OR (vch_date = ? AND vch_no = ?)
            )
            AND vch_cr_amt > 0
    """
    
    # Sales Register - Voucher List (Grouped by voucher - Tally Style)
    # Shows one line per voucher with ONLY Sales ledger's amount
    # Filter: Only include lines where led_name contains "Sales" OR exclude GST/TAX lines
    # Handles both "SALES" and "GST SALES" voucher types
    SALES_REGISTER_VOUCHERS = """
        SELECT 
            MAX(vch_date) as date,
            MAX(vch_type) as voucher_type,
            MAX(vch_no) as voucher_number,
            SUM(vch_dr_amt) as debit,
            SUM(vch_cr_amt) as credit,
            MAX(vch_narration) as narration,
            COALESCE(NULLIF(TRIM(vch_mst_id), ''), vch_date || '|' || vch_no) as voucher_key
        FROM vouchers
        WHERE company_guid = ?
            AND company_alterid = ?
            AND (UPPER(TRIM(vch_type)) = 'SALES' OR UPPER(TRIM(vch_type)) LIKE '%SALES%')
            AND vch_date BETWEEN ? AND ?
            AND vch_cr_amt > 0
            AND (
                UPPER(TRIM(led_name)) LIKE '%SALES%'
                OR (UPPER(TRIM(led_name)) NOT LIKE '%GST%' 
                    AND UPPER(TRIM(led_name)) NOT LIKE '%TAX%'
                    AND (vch_party_name IS NULL OR (
                        UPPER(TRIM(vch_party_name)) NOT LIKE '%GST%'
                        AND UPPER(TRIM(vch_party_name)) NOT LIKE '%TAX%'
                    ))
                )
            )
        GROUP BY voucher_key
        ORDER BY MAX(vch_date), MAX(vch_no)
    """

