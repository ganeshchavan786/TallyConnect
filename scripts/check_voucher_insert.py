#!/usr/bin/env python3
"""Check if vouchers are actually being inserted."""

import sqlite3

db_path = "TallyConnectDb.db"
guid = "8fdcfdd1-71cc-4873-99c6-95735225388e"
alterid = "95278.0"

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Check total vouchers
cur.execute("SELECT COUNT(*) FROM vouchers")
total = cur.fetchone()[0]
print(f"Total vouchers in database: {total}")

# Check by AlterID
cur.execute("SELECT company_alterid, COUNT(*) FROM vouchers GROUP BY company_alterid")
rows = cur.fetchall()
print(f"\nVouchers by AlterID:")
for r in rows:
    print(f"  AlterID: {r[0]} | Count: {r[1]}")

# Check for our specific AlterID
cur.execute("SELECT COUNT(*) FROM vouchers WHERE company_guid=? AND company_alterid=?", (guid, alterid))
count = cur.fetchone()[0]
print(f"\nVouchers for AlterID {alterid}: {count}")

# Check sample vouchers if any exist
if count > 0:
    cur.execute("SELECT vch_date, vch_type, vch_no, led_name FROM vouchers WHERE company_guid=? AND company_alterid=? LIMIT 5", 
                (guid, alterid))
    samples = cur.fetchall()
    print(f"\nSample vouchers:")
    for s in samples:
        print(f"  Date: {s[0]}, Type: {s[1]}, No: {s[2]}, Ledger: {s[3]}")
else:
    print(f"\nNo vouchers found for AlterID {alterid}")

# Check if there are any vouchers with same GUID but different AlterID
cur.execute("SELECT DISTINCT company_alterid, COUNT(*) FROM vouchers WHERE company_guid=? GROUP BY company_alterid", (guid,))
guid_alterids = cur.fetchall()
print(f"\nAll AlterIDs for this GUID:")
for a in guid_alterids:
    print(f"  AlterID: {a[0]} | Count: {a[1]}")

conn.close()

