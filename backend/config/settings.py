"""
TallyConnect Settings
=====================

Application configuration constants and settings.
"""

# Database Configuration
DB_FILE = "TallyConnectDb.db"

# Sync Configuration
BATCH_SIZE = 100  # Reduced from 500 (Tally returns in smaller chunks)

# Tally ODBC Configuration
COMMON_PORTS = [9000, 9001, 9999, 9002]
DSN_PREFIX = "TallyODBC64_"

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

