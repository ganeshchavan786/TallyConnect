"""
TallyConnect Configuration Module
==================================

Configuration constants and settings for TallyConnect application.
"""

from .settings import (
    DB_FILE,
    BATCH_SIZE,
    COMMON_PORTS,
    DSN_PREFIX,
    TALLY_COMPANY_QUERY,
    VOUCHER_QUERY_TEMPLATE
)

from .themes import THEMES, DEFAULT_THEME

__all__ = [
    'DB_FILE',
    'BATCH_SIZE',
    'COMMON_PORTS',
    'DSN_PREFIX',
    'TALLY_COMPANY_QUERY',
    'VOUCHER_QUERY_TEMPLATE',
    'THEMES',
    'DEFAULT_THEME'
]

