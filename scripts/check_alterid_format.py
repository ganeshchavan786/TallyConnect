#!/usr/bin/env python3
"""Check AlterID format in database."""

import sqlite3

db_path = "TallyConnectDb.db"
guid = "8fdcfdd1-71cc-4873-99c6-95735225388e"

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Check all vouchers for this GUID
cur.execute("SELECT DISTINCT company_alterid, COUNT(*) as cnt FROM vouchers WHERE company_guid=? GROUP BY company_alterid ORDER BY cnt DESC", (guid,))
rows = cur.fetchall()

print(f"All AlterIDs in vouchers for GUID {guid[:20]}...:")
if rows:
    for r in rows:
        alterid = r[0]
        count = r[1]
        print(f"  AlterID: '{alterid}' (type: {type(alterid).__name__}, repr: {repr(alterid)}) | Count: {count}")
        
        # Try different format matches
        if str(alterid) == '95278.0':
            print(f"    ✅ Matches '95278.0' as string")
        if float(alterid) == 95278.0:
            print(f"    ✅ Matches 95278.0 as float")
else:
    print("  No vouchers found for this GUID")

# Check companies table
print(f"\nCompanies for this GUID:")
cur.execute("SELECT name, alterid, total_records FROM companies WHERE guid=?", (guid,))
companies = cur.fetchall()
for c in companies:
    print(f"  {c[0]} | AlterID: '{c[1]}' (type: {type(c[1]).__name__}) | Records: {c[2]}")

# Try querying with different AlterID formats
print(f"\nTesting queries with different AlterID formats:")
test_alterids = ['95278.0', 95278.0, '95278', 95278]

for test_alt in test_alterids:
    cur.execute("SELECT COUNT(*) FROM vouchers WHERE company_guid=? AND company_alterid=?", (guid, str(test_alt)))
    count = cur.fetchone()[0]
    if count > 0:
        print(f"  ✅ Found {count} vouchers with AlterID format: {repr(test_alt)} (type: {type(test_alt).__name__})")

conn.close()

