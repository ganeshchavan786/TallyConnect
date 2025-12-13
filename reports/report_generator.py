"""
Report Generator Module
=======================

Handles all report generation logic for TallyConnect.
Generates beautiful HTML reports from SQLite data.
"""

import os
import sqlite3
import webbrowser
from datetime import datetime
from typing import Optional, Dict, List
from .utils import format_currency, calculate_age, get_report_path


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
        # TODO: Implement outstanding report generation
        # This will be filled in next step
        pass
    
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
        # TODO: Implement ledger report generation
        # This will be filled in next step
        pass
    
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
        # TODO: Implement dashboard generation
        # This will be filled in next step
        pass
    
    def _open_in_browser(self, file_path: str):
        """
        Open generated report in default browser.
        
        Args:
            file_path: Path to HTML file
        """
        webbrowser.open(f'file:///{file_path}')

