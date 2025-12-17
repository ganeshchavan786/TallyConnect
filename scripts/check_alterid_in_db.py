"""
Check AlterID formats in vouchers table
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

# Check all AlterIDs for the Vrushali GUID
guid = "8fdcfdd1-71cc-4873-99c6-95735225388e"
print(f"Checking vouchers for GUID: {guid}")
print()

# Get all distinct AlterIDs for this GUID
cur.execute("""
    SELECT DISTINCT company_alterid, 
           COUNT(*) as count,
           typeof(company_alterid) as type
    FROM vouchers 
    WHERE company_guid = ?
    GROUP BY company_alterid
    ORDER BY company_alterid
""", (guid,))

results = cur.fetchall()
print(f"Found {len(results)} distinct AlterIDs for this GUID:")
for row in results:
    alterid, count, dtype = row
    print(f"  AlterID: {repr(alterid)} (type: {dtype}) | Count: {count}")
    # Try to match with '95278.0'
    if str(alterid) == '95278.0' or str(alterid) == '95278':
        print(f"    ✅ This matches '95278.0'!")
    elif '95278' in str(alterid):
        print(f"    ⚠️  Contains '95278' but doesn't match exactly")

print()

# Check for exact match with different formats
print("Checking for exact matches with '95278.0':")
test_formats = [
    ("'95278.0'", "company_alterid = '95278.0'"),
    ("'95278'", "company_alterid = '95278'"),
    ("95278.0 (CAST)", "CAST(company_alterid AS TEXT) = '95278.0'"),
    ("95278 (CAST)", "CAST(company_alterid AS TEXT) = '95278'"),
    ("95278.0 (REAL)", "CAST(company_alterid AS REAL) = 95278.0"),
]

for label, condition in test_formats:
    cur.execute(f"SELECT COUNT(*) FROM vouchers WHERE company_guid = ? AND {condition}", (guid,))
    count = cur.fetchone()[0]
    print(f"  {label}: {count} vouchers")

print()

# Check raw values in database
print("Sample raw AlterID values from database:")
cur.execute("""
    SELECT DISTINCT company_alterid, typeof(company_alterid)
    FROM vouchers 
    WHERE company_guid = ?
    LIMIT 5
""", (guid,))

samples = cur.fetchall()
for alterid, dtype in samples:
    print(f"  Value: {repr(alterid)} | Type: {dtype} | String: '{str(alterid)}'")

conn.close()

