"""
TallyConnect - Reports Module
==============================

This module handles report generation with HTML/CSS/JS.

Features:
- Outstanding Reports (Party-wise, Age analysis)
- Ledger Reports (Transaction details)
- Dashboard (Summary with charts)
- Export to PDF/Excel
- Interactive filters and search

Author: Katara Dental
Version: 5.6
"""

from .report_generator import ReportGenerator

__all__ = ['ReportGenerator']
__version__ = '5.6.0'

