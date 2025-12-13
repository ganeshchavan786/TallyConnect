"""
Report Generator Module
=======================

Handles all report generation logic for TallyConnect.
Generates beautiful HTML reports from SQLite data.
"""

import os
import sqlite3
import webbrowser
import json
from datetime import datetime
from typing import Optional, Dict, List
from .utils import format_currency, calculate_age, get_report_path, get_age_bucket
from database.queries import ReportQueries


class ReportGenerator:
    """
    Main class for generating HTML reports from Tally data.
    
    Supports:
    - Outstanding Reports
    - Ledger Reports  
    - Dashboard/Summary
    """
    
    def __init__(self, db_path: str):
        """
        Initialize report generator.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self.templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
        self.static_dir = os.path.join(os.path.dirname(__file__), 'static')
        
    def _connect(self):
        """Create database connection."""
        if not self.conn:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
    
    def _close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def _load_template(self, template_name: str) -> str:
        """
        Load HTML template file.
        
        Args:
            template_name: Name of template file (e.g., 'outstanding.html')
            
        Returns:
            Template content as string
        """
        template_path = os.path.join(self.templates_dir, template_name)
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _load_css(self, css_file: str) -> str:
        """Load CSS file and return as string."""
        css_path = os.path.join(self.static_dir, 'css', css_file)
        with open(css_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _load_js(self, js_file: str) -> str:
        """Load JavaScript file and return as string."""
        js_path = os.path.join(self.static_dir, 'js', js_file)
        with open(js_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _embed_assets(self, html: str) -> str:
        """Embed CSS and JS inline in HTML."""
        # Replace CSS links with inline styles
        html = html.replace(
            '<link rel="stylesheet" href="../static/css/main.css">',
            f'<style>\n{self._load_css("main.css")}\n</style>'
        )
        html = html.replace(
            '<link rel="stylesheet" href="../static/css/reports.css">',
            f'<style>\n{self._load_css("reports.css")}\n</style>'
        )
        
        # Replace JS scripts with inline scripts
        html = html.replace(
            '<script src="../static/js/filters.js"></script>',
            f'<script>\n{self._load_js("filters.js")}\n</script>'
        )
        html = html.replace(
            '<script src="../static/js/export.js"></script>',
            f'<script>\n{self._load_js("export.js")}\n</script>'
        )
        
        return html
    
    def generate_outstanding_report(
        self,
        company_name: str,
        guid: str,
        alterid: str,
        as_on_date: Optional[str] = None
    ) -> str:
        """
        Generate Outstanding Report (Receivables/Payables).
        
        Args:
            company_name: Name of the company
            guid: Company GUID
            alterid: Company AlterID
            as_on_date: Date for outstanding calculation (DD-MM-YYYY)
            
        Returns:
            Path to generated HTML file
        """
        try:
            self._connect()
            cursor = self.conn.cursor()
            
            # Use today if no date specified
            if not as_on_date:
                as_on_date = datetime.now().strftime("%d-%m-%Y")
            
            # Query outstanding summary
            cursor.execute(ReportQueries.OUTSTANDING_SUMMARY, (guid, str(alterid)))
            parties = cursor.fetchall()
            
            # Calculate age analysis and generate rows
            age_buckets = {"0-30": 0, "30-60": 0, "60-90": 0, "90+": 0}
            party_rows = []
            total_debit = 0
            total_credit = 0
            total_balance = 0
            
            for party in parties:
                debit = party['debit'] or 0
                credit = party['credit'] or 0
                balance = party['balance'] or 0
                last_trans_date = party['last_transaction']
                
                # Calculate age
                age_days = calculate_age(last_trans_date, as_on_date)
                age_bucket = get_age_bucket(age_days)
                
                # Update age analysis (only for debtors - positive balance)
                if balance > 0:
                    if age_days <= 30:
                        age_buckets["0-30"] += balance
                    elif age_days <= 60:
                        age_buckets["30-60"] += balance
                    elif age_days <= 90:
                        age_buckets["60-90"] += balance
                    else:
                        age_buckets["90+"] += balance
                
                # Determine balance color
                balance_class = "amount-positive" if balance > 0 else "amount-negative" if balance < 0 else ""
                
                # Generate table row
                party_rows.append(f"""
                    <tr>
                        <td>{party['party_name']}</td>
                        <td class="text-right">{format_currency(debit)}</td>
                        <td class="text-right">{format_currency(credit)}</td>
                        <td class="text-right {balance_class}"><strong>{format_currency(abs(balance))}</strong></td>
                        <td class="text-center">{age_days}</td>
                        <td class="text-center">{party['transaction_count']}</td>
                    </tr>
                """)
                
                total_debit += debit
                total_credit += credit
                total_balance += balance
            
            # Load template
            template = self._load_template('outstanding.html')
            
            # Replace variables
            html = template.replace('{% COMPANY_NAME %}', company_name)
            html = html.replace('{% AS_ON_DATE %}', as_on_date)
            html = html.replace('{% AGE_0_30 %}', format_currency(age_buckets["0-30"]))
            html = html.replace('{% AGE_30_60 %}', format_currency(age_buckets["30-60"]))
            html = html.replace('{% AGE_60_90 %}', format_currency(age_buckets["60-90"]))
            html = html.replace('{% AGE_90_PLUS %}', format_currency(age_buckets["90+"]))
            html = html.replace('{% PARTY_ROWS %}', '\n'.join(party_rows))
            html = html.replace('{% TOTAL_DEBIT %}', format_currency(total_debit))
            html = html.replace('{% TOTAL_CREDIT %}', format_currency(total_credit))
            html = html.replace('{% TOTAL_BALANCE %}', format_currency(abs(total_balance)))
            html = html.replace('{% TOTAL_COUNT %}', str(len(parties)))
            html = html.replace('{% TOTAL_PARTIES %}', str(len(parties)))
            html = html.replace('{% GENERATED_DATE %}', datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
            
            # Embed CSS and JS inline
            html = self._embed_assets(html)
            
            # Save report
            report_path = get_report_path('outstanding', company_name)
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html)
            
            # Open in browser
            self._open_in_browser(report_path)
            
            return report_path
            
        finally:
            self._close()
    
    def generate_ledger_report(
        self,
        company_name: str,
        guid: str,
        alterid: str,
        ledger_name: str,
        from_date: str,
        to_date: str
    ) -> str:
        """
        Generate Ledger Report (Transaction-wise details).
        
        Args:
            company_name: Name of the company
            guid: Company GUID
            alterid: Company AlterID
            ledger_name: Name of ledger/party
            from_date: Start date (DD-MM-YYYY)
            to_date: End date (DD-MM-YYYY)
            
        Returns:
            Path to generated HTML file
        """
        try:
            self._connect()
            cursor = self.conn.cursor()
            
            # Convert DD-MM-YYYY to YYYY-MM-DD for SQL
            from_date_sql = datetime.strptime(from_date, "%d-%m-%Y").strftime("%Y-%m-%d")
            to_date_sql = datetime.strptime(to_date, "%d-%m-%Y").strftime("%Y-%m-%d")
            
            # Query transactions
            cursor.execute(ReportQueries.LEDGER_TRANSACTIONS, 
                         (guid, str(alterid), ledger_name, ledger_name, from_date_sql, to_date_sql))
            transactions = cursor.fetchall()
            
            # Calculate balances
            opening_balance = 0  # Can be enhanced to calculate actual opening
            running_balance = opening_balance
            total_debit = 0
            total_credit = 0
            
            transaction_rows = []
            for trans in transactions:
                debit = trans['debit'] or 0
                credit = trans['credit'] or 0
                running_balance += (debit - credit)
                
                total_debit += debit
                total_credit += credit
                
                # Format date
                trans_date = datetime.strptime(trans['date'], "%Y-%m-%d").strftime("%d-%m-%Y")
                
                # Determine balance color
                balance_class = "amount-positive" if running_balance > 0 else "amount-negative" if running_balance < 0 else ""
                
                # Generate row
                narration = trans['narration'] or '-'
                transaction_rows.append(f"""
                    <tr>
                        <td>{trans_date}</td>
                        <td>{trans['voucher_type']}</td>
                        <td>{trans['voucher_number']}</td>
                        <td>{narration[:50]}</td>
                        <td class="text-right">{format_currency(debit) if debit else '-'}</td>
                        <td class="text-right">{format_currency(credit) if credit else '-'}</td>
                        <td class="text-right {balance_class}"><strong>{format_currency(abs(running_balance))}</strong></td>
                    </tr>
                """)
            
            closing_balance = running_balance
            net_movement = total_debit - total_credit
            
            # Load template
            template = self._load_template('ledger.html')
            
            # Replace variables
            html = template.replace('{% COMPANY_NAME %}', company_name)
            html = html.replace('{% LEDGER_NAME %}', ledger_name)
            html = html.replace('{% FROM_DATE %}', from_date)
            html = html.replace('{% TO_DATE %}', to_date)
            html = html.replace('{% OPENING_BALANCE %}', format_currency(abs(opening_balance)))
            html = html.replace('{% PERIOD_DEBIT %}', format_currency(total_debit))
            html = html.replace('{% PERIOD_CREDIT %}', format_currency(total_credit))
            html = html.replace('{% CLOSING_BALANCE %}', format_currency(abs(closing_balance)))
            html = html.replace('{% TRANSACTION_ROWS %}', '\n'.join(transaction_rows))
            html = html.replace('{% TOTAL_DEBIT %}', format_currency(total_debit))
            html = html.replace('{% TOTAL_CREDIT %}', format_currency(total_credit))
            html = html.replace('{% NET_MOVEMENT %}', format_currency(abs(net_movement)))
            html = html.replace('{% TOTAL_TRANSACTIONS %}', str(len(transactions)))
            html = html.replace('{% GENERATED_DATE %}', datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
            
            # Embed CSS and JS inline
            html = self._embed_assets(html)
            
            # Save report
            report_path = get_report_path('ledger', f"{company_name}_{ledger_name}")
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html)
            
            # Open in browser
            self._open_in_browser(report_path)
            
            return report_path
            
        finally:
            self._close()
    
    def generate_dashboard(
        self,
        company_name: str,
        guid: str,
        alterid: str
    ) -> str:
        """
        Generate Dashboard with summary and charts.
        
        Args:
            company_name: Name of the company
            guid: Company GUID
            alterid: Company AlterID
            
        Returns:
            Path to generated HTML file
        """
        try:
            self._connect()
            cursor = self.conn.cursor()
            
            # 1. Get summary statistics
            cursor.execute(ReportQueries.DASHBOARD_STATS, (guid, str(alterid)))
            stats = cursor.fetchone()
            
            # 2. Get top debtors
            cursor.execute(ReportQueries.TOP_DEBTORS, (guid, str(alterid)))
            debtors = cursor.fetchall()
            
            # 3. Get top creditors
            cursor.execute(ReportQueries.TOP_CREDITORS, (guid, str(alterid)))
            creditors = cursor.fetchall()
            
            # 4. Get voucher type summary
            cursor.execute(ReportQueries.VOUCHER_TYPE_SUMMARY, (guid, str(alterid)))
            voucher_types = cursor.fetchall()
            
            # 5. Get monthly trend
            cursor.execute(ReportQueries.MONTHLY_TREND, (guid, str(alterid)))
            monthly_data = cursor.fetchall()
            
            # Generate debtors table rows
            debtors_rows = []
            for idx, debtor in enumerate(debtors, 1):
                debtors_rows.append(f"""
                    <tr>
                        <td class="text-center">{idx}</td>
                        <td>{debtor['party_name']}</td>
                        <td class="text-right amount-positive"><strong>{format_currency(debtor['balance'])}</strong></td>
                        <td class="text-center">{debtor['transaction_count']}</td>
                    </tr>
                """)
            
            # Generate creditors table rows
            creditors_rows = []
            for idx, creditor in enumerate(creditors, 1):
                creditors_rows.append(f"""
                    <tr>
                        <td class="text-center">{idx}</td>
                        <td>{creditor['party_name']}</td>
                        <td class="text-right amount-negative"><strong>{format_currency(creditor['balance'])}</strong></td>
                        <td class="text-center">{creditor['transaction_count']}</td>
                    </tr>
                """)
            
            # Prepare chart data - Debtors
            debtors_chart_data = {
                'labels': [d['party_name'][:20] for d in debtors],  # Truncate long names
                'values': [float(d['balance']) for d in debtors]
            }
            
            # Prepare chart data - Creditors
            creditors_chart_data = {
                'labels': [c['party_name'][:20] for c in creditors],
                'values': [float(c['balance']) for c in creditors]
            }
            
            # Prepare chart data - Voucher Types
            voucher_type_chart_data = {
                'labels': [v['voucher_type'] for v in voucher_types],
                'values': [int(v['count']) for v in voucher_types]
            }
            
            # Prepare chart data - Monthly Trend
            monthly_trend_chart_data = {
                'labels': [m['month'] for m in monthly_data],
                'debit': [float(m['total_debit']) for m in monthly_data],
                'credit': [float(m['total_credit']) for m in monthly_data]
            }
            
            # Format dates
            first_date = datetime.strptime(stats['first_transaction_date'], "%Y-%m-%d").strftime("%d-%m-%Y") if stats['first_transaction_date'] else "N/A"
            last_date = datetime.strptime(stats['last_transaction_date'], "%Y-%m-%d").strftime("%d-%m-%Y") if stats['last_transaction_date'] else "N/A"
            
            # Load template
            template = self._load_template('dashboard.html')
            
            # Replace variables
            html = template.replace('{% COMPANY_NAME %}', company_name)
            html = html.replace('{% DATE_RANGE %}', f"{first_date} to {last_date}")
            html = html.replace('{% TOTAL_PARTIES %}', str(stats['total_parties'] or 0))
            html = html.replace('{% TOTAL_DEBIT %}', format_currency(stats['total_debit'] or 0))
            html = html.replace('{% TOTAL_CREDIT %}', format_currency(stats['total_credit'] or 0))
            html = html.replace('{% NET_BALANCE %}', format_currency(abs(stats['net_balance'] or 0)))
            html = html.replace('{% TOTAL_TRANSACTIONS %}', str(stats['total_transactions'] or 0))
            html = html.replace('{% FIRST_DATE %}', first_date)
            html = html.replace('{% LAST_DATE %}', last_date)
            html = html.replace('{% DEBTORS_ROWS %}', '\n'.join(debtors_rows) if debtors_rows else '<tr><td colspan="4" class="text-center">No debtors found</td></tr>')
            html = html.replace('{% CREDITORS_ROWS %}', '\n'.join(creditors_rows) if creditors_rows else '<tr><td colspan="4" class="text-center">No creditors found</td></tr>')
            html = html.replace('{% DEBTORS_CHART_DATA %}', json.dumps(debtors_chart_data))
            html = html.replace('{% CREDITORS_CHART_DATA %}', json.dumps(creditors_chart_data))
            html = html.replace('{% VOUCHER_TYPE_CHART_DATA %}', json.dumps(voucher_type_chart_data))
            html = html.replace('{% MONTHLY_TREND_CHART_DATA %}', json.dumps(monthly_trend_chart_data))
            html = html.replace('{% GENERATED_DATE %}', datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
            
            # Embed CSS and JS inline (Chart.js CDN link remains)
            html = self._embed_assets(html)
            
            # Save report
            report_path = get_report_path('dashboard', company_name)
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html)
            
            # Open in browser
            self._open_in_browser(report_path)
            
            return report_path
            
        finally:
            self._close()
    
    def _open_in_browser(self, file_path: str):
        """
        Open generated report in default browser.
        
        Args:
            file_path: Path to HTML file
        """
        webbrowser.open(f'file:///{file_path}')

