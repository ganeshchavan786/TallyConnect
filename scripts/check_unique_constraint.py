"""
Check if vch_mst_id and led_name combinations already exist for the Vrushali GUID
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
print()

conn = sqlite3.connect(DB_FILE)
cur = conn.cursor()

# Check for Vrushali GUID
guid = "8fdcfdd1-71cc-4873-99c6-95735225388e"
print(f"Checking for GUID: {guid}")
print()

# Get all existing vouchers for this GUID (any AlterID)
cur.execute("""
    SELECT company_alterid, vch_mst_id, led_name, COUNT(*) as count
    FROM vouchers 
    WHERE company_guid = ?
    GROUP BY company_alterid, vch_mst_id, led_name
    ORDER BY count DESC
    LIMIT 20
""", (guid,))

existing = cur.fetchall()
print(f"Found {len(existing)} unique (AlterID, vch_mst_id, led_name) combinations:")
for row in existing:
    alterid, vch_mst_id, led_name, count = row
    print(f"  AlterID: {repr(alterid)} | vch_mst_id: {repr(vch_mst_id)} | led_name: {repr(led_name)} | Count: {count}")

print()

# Check if there are any vouchers with NULL or empty vch_mst_id or led_name
cur.execute("""
    SELECT COUNT(*) 
    FROM vouchers 
    WHERE company_guid = ? 
    AND (vch_mst_id IS NULL OR vch_mst_id = '' OR led_name IS NULL OR led_name = '')
""", (guid,))

null_count = cur.fetchone()[0]
print(f"Vouchers with NULL/empty vch_mst_id or led_name: {null_count}")

print()

# Check the UNIQUE constraint definition
print("Checking UNIQUE constraint on vouchers table:")
cur.execute("""
    SELECT sql 
    FROM sqlite_master 
    WHERE type='table' AND name='vouchers'
""")

table_sql = cur.fetchone()
if table_sql:
    sql = table_sql[0]
    if 'UNIQUE' in sql:
        print("  ✅ UNIQUE constraint found in table definition")
        # Extract UNIQUE constraint
        unique_start = sql.find('UNIQUE')
        if unique_start != -1:
            unique_end = sql.find(')', unique_start)
            if unique_end != -1:
                unique_constraint = sql[unique_start:unique_end+1]
                print(f"  Constraint: {unique_constraint}")
    else:
        print("  ❌ No UNIQUE constraint found")

conn.close()

