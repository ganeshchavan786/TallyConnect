"""
Check ALL AlterIDs in vouchers table to see what's actually stored
"""
import sys
import sqlite3
import os

# Fix Unicode encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Database path
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "TallyConnectDb.db")

print(f"Database path: {DB_FILE}")
print(f"Database exists: {os.path.exists(DB_FILE)}")
print()

conn = sqlite3.connect(DB_FILE)
cur = conn.cursor()

# Get ALL distinct AlterIDs in the entire vouchers table
print("All AlterIDs in vouchers table:")
cur.execute("""
    SELECT DISTINCT company_alterid, 
           COUNT(*) as count,
           typeof(company_alterid) as type,
           company_guid,
           (SELECT name FROM companies WHERE companies.guid = vouchers.company_guid AND companies.alterid = vouchers.company_alterid LIMIT 1) as company_name
    FROM vouchers 
    GROUP BY company_alterid, company_guid
    ORDER BY company_alterid
""")

results = cur.fetchall()
print(f"Found {len(results)} distinct AlterID/GUID combinations:")
for row in results:
    alterid, count, dtype, guid, company_name = row
    guid_short = guid[:20] + "..." if guid and len(guid) > 20 else guid
    print(f"  AlterID: {repr(alterid)} (type: {dtype}) | Count: {count} | GUID: {guid_short} | Company: {company_name}")

print()

# Check companies table
print("All companies in companies table:")
cur.execute("""
    SELECT name, guid, alterid, total_records, status
    FROM companies
    ORDER BY name, alterid
""")

companies = cur.fetchall()
print(f"Found {len(companies)} companies:")
for row in companies:
    name, guid, alterid, total_records, status = row
    guid_short = guid[:20] + "..." if guid and len(guid) > 20 else guid
    print(f"  Name: {name}")
    print(f"    GUID: {guid_short}")
    print(f"    AlterID: {repr(alterid)} (type: {type(alterid).__name__})")
    print(f"    Total Records: {total_records}")
    print(f"    Status: {status}")
    
    # Check vouchers for this company
    cur.execute("SELECT COUNT(*) FROM vouchers WHERE company_guid=? AND company_alterid=?", (guid, str(alterid)))
    vch_count = cur.fetchone()[0]
    print(f"    Actual Vouchers in DB: {vch_count}")
    if vch_count != total_records:
        print(f"    ⚠️  MISMATCH: Company says {total_records} but DB has {vch_count}")
    print()

conn.close()

