#!/usr/bin/env python3
"""Check if vouchers exist in database."""

import sqlite3

db_path = "TallyConnectDb.db"
guid = "8fdcfdd1-71cc-4873-99c6-95735225388e"
alterid = "95278.0"

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Check vouchers
cur.execute("SELECT COUNT(*) FROM vouchers WHERE company_guid=? AND company_alterid=?", (guid, alterid))
count = cur.fetchone()[0]
print(f"1. Vouchers for AlterID {alterid}: {count}")

if count > 0:
    cur.execute("SELECT MIN(vch_date), MAX(vch_date) FROM vouchers WHERE company_guid=? AND company_alterid=?", (guid, alterid))
    date_range = cur.fetchone()
    print(f"   Date range: {date_range[0]} to {date_range[1]}")
    
    cur.execute("SELECT COUNT(*) FROM vouchers WHERE company_guid=? AND company_alterid=? AND (UPPER(TRIM(vch_type)) = 'SALES' OR UPPER(TRIM(vch_type)) LIKE '%SALES%')", (guid, alterid))
    sales_count = cur.fetchone()[0]
    print(f"   Sales vouchers: {sales_count}")
    
    cur.execute("SELECT SUM(vch_cr_amt) FROM vouchers WHERE company_guid=? AND company_alterid=? AND (UPPER(TRIM(vch_type)) = 'SALES' OR UPPER(TRIM(vch_type)) LIKE '%SALES%') AND vch_cr_amt > 0", (guid, alterid))
    sales_amount = cur.fetchone()[0]
    print(f"   Total sales amount: {sales_amount or 0}")
else:
    print("   WARNING: No vouchers found!")

# Check all AlterIDs
print(f"\n2. All AlterIDs in vouchers table:")
cur.execute("SELECT company_alterid, COUNT(*) as cnt FROM vouchers GROUP BY company_alterid ORDER BY cnt DESC")
rows = cur.fetchall()
for r in rows:
    print(f"   AlterID: {r[0]} | Count: {r[1]}")

# Check if alterid format matches
print(f"\n3. Checking AlterID format:")
cur.execute("SELECT DISTINCT company_alterid FROM vouchers WHERE company_guid=?", (guid,))
all_alterids = cur.fetchall()
print(f"   All AlterIDs for this GUID:")
for a in all_alterids:
    print(f"     - '{a[0]}' (type: {type(a[0]).__name__})")
    print(f"       Matches '95278.0': {str(a[0]) == '95278.0'}")

conn.close()

