# -*- coding: utf-8 -*-
"""
Standalone Ledger Report Application
====================================
This is a complete, self-contained Flask application for Ledger Report functionality.
Includes: HTML, CSS, JavaScript, Python backend, and database connection.

Requirements:
    pip install flask flask-cors

Usage:
    python ledger_report_standalone.py

Database:
    Ensure TallyConnectDb.db is in the same directory as this file.
    Modify DB_PATH below if your database is in a different location.
"""

from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime

# ============================================
# DATABASE CONFIGURATION
# ============================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "TallyConnectDb.db")

# ============================================
# FLASK APP SETUP
# ============================================
app = Flask(__name__)

# Enable CORS
try:
    CORS(app)
    print("✅ CORS enabled")
except ImportError:
    print("⚠️  flask-cors not installed, using manual CORS headers")
    @app.after_request
    def add_cors_headers(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

print(f"🔍 Looking for DB at: {DB_PATH}")
print(f"📁 DB exists: {os.path.exists(DB_PATH)}")

# ============================================
# HTML CONTENT (with embedded CSS)
# ============================================
LEDGER_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ledger Report</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
            padding: 30px;
        }

        h1 {
            color: #333;
            margin-bottom: 30px;
            font-size: 28px;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }

        .controls {
            display: flex;
            gap: 20px;
            margin-bottom: 30px;
            flex-wrap: wrap;
            align-items: end;
        }

        .form-group {
            flex: 1;
            min-width: 200px;
        }

        label {
            display: block;
            margin-bottom: 8px;
            color: #555;
            font-weight: 600;
        }

        select, input[type="date"] {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 6px;
            font-size: 14px;
            transition: border-color 0.3s;
        }

        select:focus, input[type="date"]:focus {
            outline: none;
            border-color: #667eea;
        }

        .info-section {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            border-left: 4px solid #667eea;
        }

        .info-section h2 {
            color: #333;
            margin-bottom: 15px;
            font-size: 20px;
        }

        .info-row {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 10px;
        }

        .info-item {
            display: flex;
            flex-direction: column;
        }

        .info-label {
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 5px;
        }

        .info-value {
            font-size: 18px;
            font-weight: 600;
            color: #333;
        }

        .info-value.positive {
            color: #28a745;
        }

        .info-value.negative {
            color: #dc3545;
        }

        .table-container {
            overflow-x: auto;
            margin-top: 20px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            background: white;
        }

        thead {
            background: #667eea;
            color: white;
        }

        th {
            padding: 15px;
            text-align: left;
            font-weight: 600;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        td {
            padding: 12px 15px;
            border-bottom: 1px solid #eee;
            font-size: 14px;
        }

        tbody tr:hover {
            background: #f8f9fa;
        }

        tbody tr:last-child td {
            border-bottom: 2px solid #667eea;
        }

        .text-right {
            text-align: right;
        }

        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
            font-size: 16px;
        }

        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 6px;
            margin: 20px 0;
            border-left: 4px solid #dc3545;
        }

        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #999;
        }

        .empty-state p {
            font-size: 16px;
            margin-top: 10px;
        }

        .special-row {
            background-color: #f0f0f0;
            font-weight: 600;
        }

        .special-row td {
            border-top: 2px solid #667eea;
            border-bottom: 2px solid #667eea;
        }

        .current-total-row {
            background-color: #e8e8e8;
        }

        .closing-balance-row {
            background-color: #d4e6f1;
            border-top: 3px solid #667eea !important;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Ledger Report</h1>
        
        <div class="controls">
            <div class="form-group">
                <label for="ledgerSelect">Select Ledger</label>
                <select id="ledgerSelect">
                    <option value="">-- Select Ledger --</option>
                </select>
            </div>
            <div class="form-group">
                <label for="fromDate">From Date</label>
                <input type="date" id="fromDate">
            </div>
            <div class="form-group">
                <label for="toDate">To Date</label>
                <input type="date" id="toDate">
            </div>
        </div>

        <div id="errorMessage" class="error" style="display: none;"></div>

        <div id="infoSection" class="info-section" style="display: none;">
            <h2>Ledger Information</h2>
            <div class="info-row">
                <div class="info-item">
                    <span class="info-label">Ledger Name</span>
                    <span class="info-value" id="ledgerName">-</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Period</span>
                    <span class="info-value" id="period">-</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Opening Balance</span>
                    <span class="info-value" id="openingBalance">-</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Total Debit</span>
                    <span class="info-value" id="totalDebit">-</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Total Credit</span>
                    <span class="info-value" id="totalCredit">-</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Closing Balance</span>
                    <span class="info-value" id="closingBalance">-</span>
                </div>
            </div>
        </div>

        <div class="table-container">
            <div id="loadingMessage" class="loading" style="display: none;">
                Loading ledger data...
            </div>
            <div id="emptyMessage" class="empty-state" style="display: none;">
                <p>No ledger selected or no transactions found.</p>
            </div>
            <table id="ledgerTable" style="display: none;">
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Particulars</th>
                        <th>Vch Type</th>
                        <th>Vch No</th>
                        <th class="text-right">Debit</th>
                        <th class="text-right">Credit</th>
                    </tr>
                </thead>
                <tbody id="ledgerTableBody">
                </tbody>
            </table>
        </div>
    </div>

    <script>
        // Format number with 2 decimal places
        function formatNumber(num) {
            if (num === null || num === undefined) return '0.00';
            return parseFloat(num).toFixed(2);
        }

        // Format currency with commas
        function formatCurrency(num) {
            if (num === null || num === undefined) return '0.00';
            const formatted = parseFloat(num).toLocaleString('en-IN', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });
            return formatted;
        }

        // Format date from YYYY-MM-DD to DD-MM-YYYY
        function formatDate(dateStr) {
            if (!dateStr) return '-';
            const date = new Date(dateStr);
            const day = String(date.getDate()).padStart(2, '0');
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const year = date.getFullYear();
            return `${day}-${month}-${year}`;
        }

        // Show error message
        function showError(message) {
            const errorDiv = document.getElementById('errorMessage');
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
            setTimeout(() => {
                errorDiv.style.display = 'none';
            }, 5000);
        }

        // Hide error message
        function hideError() {
            document.getElementById('errorMessage').style.display = 'none';
        }

        // Load all ledgers into dropdown
        async function loadLedgers() {
            try {
                const response = await fetch('/api/ledgers');
                if (!response.ok) {
                    throw new Error('Failed to load ledgers');
                }
                const ledgers = await response.json();
                
                const select = document.getElementById('ledgerSelect');
                select.innerHTML = '<option value="">-- Select Ledger --</option>';
                
                ledgers.forEach(ledger => {
                    const option = document.createElement('option');
                    option.value = ledger;
                    option.textContent = ledger;
                    select.appendChild(option);
                });
                
                console.log(`✅ Loaded ${ledgers.length} ledgers`);
            } catch (error) {
                console.error('Error loading ledgers:', error);
                showError('Failed to load ledgers: ' + error.message);
            }
        }

        // Load period info and set default dates (Financial Year: 01-04-2025 to 31-03-2026)
        async function loadPeriodInfo() {
            try {
                const response = await fetch('/api/period-info');
                if (!response.ok) {
                    console.warn('Failed to load period info, using financial year defaults');
                    document.getElementById('fromDate').value = '2025-04-01';
                    document.getElementById('toDate').value = '2026-03-31';
                    return;
                }
                const periodInfo = await response.json();
                
                document.getElementById('fromDate').value = periodInfo.from_date || '2025-04-01';
                document.getElementById('toDate').value = periodInfo.to_date || '2026-03-31';
            } catch (error) {
                console.warn('Error loading period info:', error);
                document.getElementById('fromDate').value = '2025-04-01';
                document.getElementById('toDate').value = '2026-03-31';
            }
        }

        // Render ledger data in table (Tally style)
        function renderLedger(data) {
            document.getElementById('loadingMessage').style.display = 'none';
            document.getElementById('emptyMessage').style.display = 'none';
            
            if (!Array.isArray(data)) {
                console.error('Data is not an array:', data);
                showError('Invalid data format received from server');
                document.getElementById('emptyMessage').style.display = 'block';
                document.getElementById('ledgerTable').style.display = 'none';
                return;
            }
            
            const tbody = document.getElementById('ledgerTableBody');
            tbody.innerHTML = '';
            
            if (data.length === 0) {
                document.getElementById('emptyMessage').style.display = 'block';
                document.getElementById('ledgerTable').style.display = 'none';
                return;
            }
            
            document.getElementById('ledgerTable').style.display = 'table';
            
            data.forEach((row, index) => {
                const tr = document.createElement('tr');
                
                const isSpecial = row.isSpecial || false;
                const dateStr = row.date ? formatDate(row.date) : '';
                
                let debitStr = '-';
                if (row.debit !== null && row.debit !== undefined) {
                    if (isSpecial) {
                        if (row.particulars === 'Closing Balance' && row.debit === 0) {
                            debitStr = '';
                        } else if (row.debit > 0) {
                            debitStr = formatCurrency(row.debit);
                        } else if (row.particulars === 'Current Total' && row.debit === 0) {
                            debitStr = '0.00';
                        }
                    } else {
                        if (row.debit > 0) {
                            debitStr = formatCurrency(row.debit);
                        }
                    }
                }
                
                let creditStr = '-';
                if (row.credit !== null && row.credit !== undefined) {
                    if (isSpecial) {
                        if (row.particulars === 'Closing Balance' && row.credit === 0) {
                            creditStr = '0.00';
                        } else if (row.credit > 0) {
                            creditStr = formatCurrency(row.credit);
                        } else if (row.particulars === 'Current Total' && row.credit === 0) {
                            creditStr = '0.00';
                        }
                    } else {
                        if (row.credit > 0) {
                            creditStr = formatCurrency(row.credit);
                        }
                    }
                }
                
                if (isSpecial) {
                    tr.className = 'special-row';
                    if (row.particulars === 'Current Total') {
                        tr.className += ' current-total-row';
                    } else if (row.particulars === 'Closing Balance') {
                        tr.className += ' closing-balance-row';
                    }
                }
                
                tr.innerHTML = `
                    <td>${dateStr}</td>
                    <td><strong>${row.particulars || '-'}</strong></td>
                    <td>${row.vchType || '-'}</td>
                    <td>${row.vchNo || '-'}</td>
                    <td class="text-right">${debitStr}</td>
                    <td class="text-right">${creditStr}</td>
                `;
                
                tbody.appendChild(tr);
            });
        }

        // Update info section
        function updateInfoSection(reportData) {
            const infoSection = document.getElementById('infoSection');
            const ledgerName = document.getElementById('ledgerName');
            const period = document.getElementById('period');
            const openingBalance = document.getElementById('openingBalance');
            const totalDebit = document.getElementById('totalDebit');
            const totalCredit = document.getElementById('totalCredit');
            const closingBalance = document.getElementById('closingBalance');
            
            ledgerName.textContent = reportData.ledger || '-';
            
            const fromDate = reportData.from_date ? formatDate(reportData.from_date) : '-';
            const toDate = reportData.to_date ? formatDate(reportData.to_date) : '-';
            period.textContent = `${fromDate} to ${toDate}`;
            
            const opBal = parseFloat(reportData.opening_balance || 0);
            openingBalance.textContent = formatCurrency(Math.abs(opBal));
            openingBalance.className = 'info-value ' + (opBal >= 0 ? 'positive' : 'negative');
            
            totalDebit.textContent = formatCurrency(reportData.total_debit || 0);
            totalCredit.textContent = formatCurrency(reportData.total_credit || 0);
            
            const clBal = parseFloat(reportData.closing_balance || 0);
            closingBalance.textContent = formatCurrency(Math.abs(clBal));
            closingBalance.className = 'info-value ' + (clBal >= 0 ? 'positive' : 'negative');
            
            infoSection.style.display = 'block';
        }

        // Load ledger report
        async function loadLedgerReport(ledgerName) {
            if (!ledgerName) {
                document.getElementById('infoSection').style.display = 'none';
                document.getElementById('ledgerTable').style.display = 'none';
                document.getElementById('emptyMessage').style.display = 'block';
                return;
            }
            
            hideError();
            document.getElementById('loadingMessage').style.display = 'block';
            document.getElementById('ledgerTable').style.display = 'none';
            document.getElementById('emptyMessage').style.display = 'none';
            
            const fromDate = document.getElementById('fromDate').value;
            const toDate = document.getElementById('toDate').value;
            
            if (fromDate && toDate && fromDate > toDate) {
                document.getElementById('loadingMessage').style.display = 'none';
                showError('Invalid date range: From Date cannot be after To Date. Please correct the date range.');
                return;
            }
            
            try {
                let url = `/api/ledger-report?ledger=${encodeURIComponent(ledgerName)}`;
                if (fromDate) {
                    url += `&from_date=${fromDate}`;
                }
                if (toDate) {
                    url += `&to_date=${toDate}`;
                }
                
                const response = await fetch(url);
                
                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
                    throw new Error(errorData.error || `Server error: ${response.status}`);
                }
                
                const reportData = await response.json();
                
                if (reportData.error) {
                    throw new Error(reportData.error);
                }
                
                console.log('📊 Received ledger report data:', reportData);
                console.log('📋 Number of rows:', reportData.data ? reportData.data.length : 0);
                
                updateInfoSection(reportData);
                
                if (reportData.data && Array.isArray(reportData.data)) {
                    renderLedger(reportData.data);
                } else {
                    console.error('Invalid data format:', reportData);
                    showError('Invalid data format received from server');
                    document.getElementById('emptyMessage').style.display = 'block';
                }
                
                document.getElementById('loadingMessage').style.display = 'none';
                
            } catch (error) {
                console.error('Error loading ledger report:', error);
                showError('Failed to load ledger report: ' + error.message);
                document.getElementById('loadingMessage').style.display = 'none';
                document.getElementById('emptyMessage').style.display = 'block';
                document.getElementById('infoSection').style.display = 'none';
            }
        }

        // Initialize on page load
        document.addEventListener('DOMContentLoaded', async () => {
            console.log('📋 Ledger Report Page Loaded');
            
            await Promise.all([loadLedgers(), loadPeriodInfo()]);
            
            document.getElementById('ledgerSelect').addEventListener('change', (e) => {
                loadLedgerReport(e.target.value);
            });
            
            document.getElementById('fromDate').addEventListener('change', () => {
                const ledger = document.getElementById('ledgerSelect').value;
                if (ledger) {
                    loadLedgerReport(ledger);
                }
            });
            
            document.getElementById('toDate').addEventListener('change', () => {
                const ledger = document.getElementById('ledgerSelect').value;
                if (ledger) {
                    loadLedgerReport(ledger);
                }
            });
        });
    </script>
</body>
</html>"""

# ============================================
# ROUTES
# ============================================

@app.route("/")
def index():
    """Serve the Ledger Report HTML page"""
    return LEDGER_HTML

# ============================================
# API: GET ALL LEDGERS
# ============================================
@app.route("/api/ledgers", methods=['GET', 'OPTIONS'])
def get_ledgers():
    """Get all unique ledger names from database"""
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        rows = cur.execute("""
            SELECT DISTINCT TRIM(led_name)
            FROM vouchers
            WHERE led_name IS NOT NULL AND TRIM(led_name) != ''
            ORDER BY led_name
        """).fetchall()

        conn.close()

        ledgers = [r[0] for r in rows if r[0]]
        print(f"✅ Found {len(ledgers)} ledgers")
        return jsonify(ledgers)

    except Exception as e:
        print(f"❌ Error fetching ledgers: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# ============================================
# API: GET LEDGER REPORT (TALLY LOGIC)
# ============================================
@app.route("/api/ledger-report", methods=['GET', 'OPTIONS'])
def get_ledger_report():
    """
    Get ledger report for selected ledger following Tally rules:
    - Show Opening Balance, Transactions, Current Total, and Closing Balance
    - Show counter ledger in Particulars (from other ledger in same voucher)
    - ONE row per voucher (NOT all ledger lines)
    """
    if request.method == 'OPTIONS':
        return '', 204
        
    ledger_name = request.args.get("ledger")
    from_date = request.args.get("from_date", "")
    to_date = request.args.get("to_date", "")

    if not ledger_name:
        return jsonify({"error": "Ledger name required"}), 400

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        # Get company name for this specific ledger
        company_query = """
            SELECT DISTINCT company_name 
            FROM vouchers 
            WHERE company_name IS NOT NULL 
            AND TRIM(UPPER(led_name)) = TRIM(UPPER(?))
            LIMIT 1
        """
        company_row = cur.execute(company_query, (ledger_name,)).fetchone()
        if not company_row or not company_row['company_name']:
            fallback_query = "SELECT DISTINCT company_name FROM vouchers WHERE company_name IS NOT NULL LIMIT 1"
            fallback_row = cur.execute(fallback_query).fetchone()
            company_name = fallback_row['company_name'] if fallback_row and fallback_row['company_name'] else 'Vrushali Infotech Pvt Ltd. 25-26'
        else:
            company_name = company_row['company_name']
        
        print(f"🏢 Using company: {company_name} for ledger: {ledger_name}")

        # Get period info
        min_max_dates = cur.execute("SELECT MIN(vch_date) as from_date, MAX(vch_date) as to_date FROM vouchers").fetchone()
        db_min_date = min_max_dates['from_date'] if min_max_dates and min_max_dates['from_date'] else datetime.now().strftime('%Y-%m-%d')
        db_max_date = min_max_dates['to_date'] if min_max_dates and min_max_dates['to_date'] else datetime.now().strftime('%Y-%m-%d')

        if not from_date:
            from_date = db_min_date
        if not to_date:
            to_date = db_max_date

        # Execute the final query with UNION for all sections
        query = """
        SELECT
            "Date",
            "Particulars",
            "Vch Type",
            "Vch No",
            "Debit",
            "Credit",
            sort_key
        FROM (
            SELECT
                0 AS sort_key,
                NULL AS "Date",
                'Opening Balance' AS "Particulars",
                NULL AS "Vch Type",
                NULL AS "Vch No",
                CASE
                    WHEN SUM(COALESCE(vch_dr_amt,0)) - SUM(COALESCE(vch_cr_amt,0)) > 0
                    THEN ABS(SUM(COALESCE(vch_dr_amt,0)) - SUM(COALESCE(vch_cr_amt,0)))
                    ELSE NULL
                END AS "Debit",
                CASE
                    WHEN SUM(COALESCE(vch_dr_amt,0)) - SUM(COALESCE(vch_cr_amt,0)) < 0
                    THEN ABS(SUM(COALESCE(vch_dr_amt,0)) - SUM(COALESCE(vch_cr_amt,0)))
                    ELSE NULL
                END AS "Credit"
            FROM vouchers
            WHERE company_name = ? AND led_name = ? AND DATE(vch_date) < DATE(?)
            
            UNION ALL
            
            SELECT
                1 AS sort_key,
                v.vch_date AS "Date",
                COALESCE(
                    (SELECT v2.led_name 
                     FROM vouchers v2 
                     WHERE v2.vch_mst_id = v.vch_mst_id 
                       AND v2.led_name != v.led_name
                     ORDER BY v2.id LIMIT 1),
                    v.vch_party_name,
                    v.vch_narration,
                    v.led_name
                ) AS "Particulars",
                v.vch_type AS "Vch Type",
                v.vch_no AS "Vch No",
                CASE WHEN COALESCE(v.vch_dr_amt,0) > 0 THEN v.vch_dr_amt ELSE NULL END AS "Debit",
                CASE WHEN COALESCE(v.vch_cr_amt,0) > 0 THEN v.vch_cr_amt ELSE NULL END AS "Credit"
            FROM vouchers v
            WHERE v.company_name = ? AND v.led_name = ? 
              AND DATE(v.vch_date) BETWEEN DATE(?) AND DATE(?)
            
            UNION ALL
            
            SELECT
                2 AS sort_key,
                NULL AS "Date",
                'Current Total' AS "Particulars",
                NULL AS "Vch Type",
                NULL AS "Vch No",
                SUM(COALESCE(vch_dr_amt,0)) AS "Debit",
                SUM(COALESCE(vch_cr_amt,0)) AS "Credit"
            FROM vouchers
            WHERE company_name = ? AND led_name = ? 
              AND DATE(vch_date) BETWEEN DATE(?) AND DATE(?)
            
            UNION ALL
            
            SELECT
                3 AS sort_key,
                NULL AS "Date",
                'Closing Balance' AS "Particulars",
                NULL AS "Vch Type",
                NULL AS "Vch No",
                CASE
                    WHEN SUM(COALESCE(vch_dr_amt,0)) - SUM(COALESCE(vch_cr_amt,0)) > 0
                    THEN ABS(SUM(COALESCE(vch_dr_amt,0)) - SUM(COALESCE(vch_cr_amt,0)))
                    ELSE 0
                END AS "Debit",
                CASE
                    WHEN SUM(COALESCE(vch_dr_amt,0)) - SUM(COALESCE(vch_cr_amt,0)) < 0
                    THEN ABS(SUM(COALESCE(vch_dr_amt,0)) - SUM(COALESCE(vch_cr_amt,0)))
                    WHEN SUM(COALESCE(vch_dr_amt,0)) - SUM(COALESCE(vch_cr_amt,0)) = 0
                    THEN 0
                    ELSE NULL
                END AS "Credit"
            FROM vouchers
            WHERE company_name = ? AND led_name = ? 
              AND DATE(vch_date) <= DATE(?)
        )
        ORDER BY sort_key, DATE("Date"), "Vch Type", "Vch No"
        """
        
        params = (
            company_name, ledger_name, from_date,
            company_name, ledger_name, from_date, to_date,
            company_name, ledger_name, from_date, to_date,
            company_name, ledger_name, to_date
        )
        
        rows = cur.execute(query, params).fetchall()
        
        # Convert rows to list of dictionaries
        data = []
        total_debit = 0
        total_credit = 0
        
        for row in rows:
            particulars = row['Particulars'] or ''
            debit_val = row['Debit']
            credit_val = row['Credit']
            
            if particulars == 'Current Total':
                total_debit = debit_val if debit_val is not None else 0
                total_credit = credit_val if credit_val is not None else 0
            
            if particulars == 'Closing Balance':
                if debit_val == 0 and credit_val == 0:
                    credit_val = 0
                elif debit_val == 0 and credit_val is None:
                    credit_val = 0
            
            data.append({
                "date": row['Date'],
                "particulars": particulars,
                "vchType": row['Vch Type'],
                "vchNo": row['Vch No'],
                "debit": debit_val,
                "credit": credit_val,
                "isSpecial": particulars in ['Opening Balance', 'Current Total', 'Closing Balance']
            })
        
        # Calculate opening and closing balances
        opening_debit = None
        opening_credit = None
        closing_debit = None
        closing_credit = None
        
        for row in rows:
            if row['Particulars'] == 'Opening Balance':
                opening_debit = row['Debit']
                opening_credit = row['Credit']
            elif row['Particulars'] == 'Closing Balance':
                closing_debit = row['Debit']
                closing_credit = row['Credit']
        
        opening_balance = (opening_debit if opening_debit else 0) - (opening_credit if opening_credit else 0)
        closing_balance = (closing_debit if closing_debit else 0) - (closing_credit if closing_credit else 0)
        
        conn.close()

        print(f"✅ Returning {len(data)} rows for {ledger_name}")
        
        return jsonify({
            "ledger": ledger_name,
            "company_name": company_name,
            "from_date": from_date,
            "to_date": to_date,
            "opening_balance": opening_balance,
            "data": data,
            "total_debit": total_debit,
            "total_credit": total_credit,
            "closing_balance": closing_balance
        })

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# ============================================
# API: GET PERIOD INFO
# ============================================
@app.route("/api/period-info", methods=['GET', 'OPTIONS'])
def get_period_info():
    """Get min and max dates from database"""
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        result = cur.execute("""
            SELECT MIN(vch_date) as from_date, MAX(vch_date) as to_date
            FROM vouchers
        """).fetchone()

        conn.close()

        return jsonify({
            "from_date": result[0] if result[0] else "2025-04-01",
            "to_date": result[1] if result[1] else "2026-03-31"
        })

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "from_date": "2025-04-01",
            "to_date": "2026-03-31"
        })

# ============================================
# RUN APPLICATION
# ============================================
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 Ledger Report Standalone Application")
    print("="*60)
    print(f"📂 Database: {DB_PATH}")
    print(f"🌐 Server: http://127.0.0.1:5000")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

