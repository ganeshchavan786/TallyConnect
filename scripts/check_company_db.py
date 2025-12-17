#!/usr/bin/env python3
"""Check if company exists in database."""

import sqlite3

db_path = "TallyConnectDb.db"
guid = "8fdcfdd1-71cc-4873-99c6-95735225388e"
alterid = "95278.0"

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Check specific company
cur.execute("SELECT name, guid, alterid, status, total_records FROM companies WHERE guid=? AND alterid=?", (guid, alterid))
row = cur.fetchone()

print(f"1. Company with GUID={guid[:20]}... and AlterID={alterid}:")
if row:
    print(f"   FOUND: {row[0]}")
    print(f"      Status: {row[3]}, Records: {row[4]}")
else:
    print(f"   NOT FOUND")

# Check all companies with same GUID
print(f"\n2. All companies with same GUID:")
cur.execute("SELECT name, guid, alterid, status, total_records FROM companies WHERE guid=?", (guid,))
all_guid = cur.fetchall()
print(f"   Found {len(all_guid)} companies:")
for r in all_guid:
    print(f"      - {r[0]} | AlterID: {r[2]} | Status: {r[3]} | Records: {r[4]}")

# Check all companies
print(f"\n3. All companies in database:")
cur.execute("SELECT name, guid, alterid, status, total_records FROM companies ORDER BY name")
all_companies = cur.fetchall()
print(f"   Total: {len(all_companies)}")
for r in all_companies:
    print(f"      - {r[0]} | AlterID: {r[2]} | Status: {r[3]} | Records: {r[4]}")

conn.close()

