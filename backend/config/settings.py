"""
TallyConnect Settings
=====================

Application configuration constants and settings.
Phase 2: Uses environment variables for configuration.
"""

import os
from pathlib import Path

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Load .env file from project root
    project_root = Path(__file__).parent.parent.parent
    env_path = project_root / '.env'
    if env_path.exists():
        load_dotenv(env_path)
    else:
        # Try loading from current directory as fallback
        load_dotenv()
except ImportError:
    # python-dotenv not installed, use defaults
    pass

# Database Configuration
DB_FILE = os.getenv("DB_FILE", "TallyConnectDb.db")

# Sync Configuration
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "5000"))  # Default 5000 for batch operations

# Backup Configuration
BACKUP_DIR = os.getenv("BACKUP_DIR", "backups")
MAX_BACKUPS = int(os.getenv("MAX_BACKUPS", "30"))

# Log Configuration
LOG_RETENTION_DAYS = int(os.getenv("LOG_RETENTION_DAYS", "90"))

# Tally ODBC Configuration
COMMON_PORTS = [9000, 9001, 9999, 9002]  # Can be overridden via env if needed
DSN_PREFIX = os.getenv("DSN_PREFIX", "TallyODBC64_")

# Tally Queries
TALLY_COMPANY_QUERY = 'SELECT $Name, $GUID, $AlterID FROM Company'

VOUCHER_QUERY_TEMPLATE = """
SELECT $OwnerCompany, $OwnerGUID, $OnwerAlterID, $VchDate, $VchType, $VchNo, $VchLedName,
       $VchLedAmount, $VchDrCr, $VchLedDrAmt, $VchLedCrAmt, $VchPartyName, $VchLedParent,
       $VchNarration, $VchGstin, $VchLedGstin, $VchLedBillRef, $VchLedBillType, $VchLedPrimaryGrp,
       $VchLedNature, $VchLedBSGrp, $VchLedBSGrpNature, $VchIsOptional, $VchMstID, $VchledbillCount
FROM TallyVchLedCollectionCMP
WHERE $OwnerGUID = '{guid}'
  AND $VchDate >= $$Date:"{from_date}"
  AND $VchDate <= $$Date:"{to_date}"
"""

