#!/usr/bin/env python3
"""Direct verification of vouchers using the same database path as the app."""

import sqlite3
import os
from pathlib import Path

# Get the database path the same way the app does
script_dir = Path(__file__).parent.absolute()
db_path = script_dir / "TallyConnectDb.db"

print(f"Database path: {db_path}")
print(f"Database exists: {os.path.exists(db_path)}")
print(f"Database size: {os.path.getsize(db_path) if os.path.exists(db_path) else 0} bytes")

conn = sqlite3.connect(str(db_path))
cur = conn.cursor()

guid = "8fdcfdd1-71cc-4873-99c6-95735225388e"
alterid = "95278.0"

# Check total vouchers
cur.execute("SELECT COUNT(*) FROM vouchers")
total = cur.fetchone()[0]
print(f"\nTotal vouchers in database: {total}")

# Check by AlterID
cur.execute("SELECT company_alterid, COUNT(*) FROM vouchers GROUP BY company_alterid")
rows = cur.fetchall()
print(f"\nVouchers by AlterID:")
for r in rows:
    print(f"  AlterID: '{r[0]}' (type: {type(r[0]).__name__}) | Count: {r[1]}")

# Check for our specific AlterID with different formats
print(f"\nChecking for AlterID '{alterid}':")
test_formats = [alterid, str(alterid), float(alterid) if '.' in alterid else None]
for test_alt in test_formats:
    if test_alt is None:
        continue
    cur.execute("SELECT COUNT(*) FROM vouchers WHERE company_guid=? AND company_alterid=?", (guid, str(test_alt)))
    count = cur.fetchone()[0]
    print(f"  Format '{test_alt}' (type: {type(test_alt).__name__}): {count} vouchers")

# Check with CAST
cur.execute("SELECT COUNT(*) FROM vouchers WHERE company_guid=? AND CAST(company_alterid AS TEXT)=?", (guid, alterid))
cast_count = cur.fetchone()[0]
print(f"  CAST(company_alterid AS TEXT)='{alterid}': {cast_count} vouchers")

# Check all AlterIDs for this GUID
cur.execute("SELECT DISTINCT company_alterid, COUNT(*) FROM vouchers WHERE company_guid=? GROUP BY company_alterid", (guid,))
guid_alterids = cur.fetchall()
print(f"\nAll AlterIDs for GUID {guid[:20]}...:")
for a in guid_alterids:
    print(f"  AlterID: '{a[0]}' (type: {type(a[0]).__name__}, repr: {repr(a[0])}) | Count: {a[1]}")

conn.close()

