#!/usr/bin/env python3
"""Check ledger report fields from database"""

import sqlite3

conn = sqlite3.connect('TallyConnectDb.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get sample data
cursor.execute("""
    SELECT 
        vch_date, vch_type, vch_no, 
        vch_party_name, led_name, 
        vch_dr_amt, vch_cr_amt, vch_narration
    FROM vouchers 
    WHERE company_guid = ? AND company_alterid = ? 
    LIMIT 5
""", ('8fdcfdd1-71cc-4873-99c6-95735225388e', '102209.0'))

rows = cursor.fetchall()

print("="*80)
print("LEDGER REPORT - DATABASE FIELDS CHECK")
print("="*80)
print(f"\nFound {len(rows)} sample transactions\n")

for i, r in enumerate(rows, 1):
    print(f"Transaction {i}:")
    print(f"  Date: {r['vch_date']}")
    print(f"  Voucher Type: {r['vch_type']}")
    print(f"  Voucher No: {r['vch_no']}")
    print(f"  Party Name: {r['vch_party_name']}")
    print(f"  Ledger Name: {r['led_name']}")
    print(f"  Debit Amount: {r['vch_dr_amt']}")
    print(f"  Credit Amount: {r['vch_cr_amt']}")
    print(f"  Narration: {r['vch_narration']}")
    print()

# Check for A P HOLDINGS
print("\n" + "="*80)
print("Checking for 'A P HOLDINGS' ledger:")
print("="*80)

cursor.execute("""
    SELECT COUNT(*) as count
    FROM vouchers 
    WHERE company_guid = ? 
        AND company_alterid = ? 
        AND (vch_party_name LIKE '%A P HOLDINGS%' OR led_name LIKE '%A P HOLDINGS%')
""", ('8fdcfdd1-71cc-4873-99c6-95735225388e', '102209.0'))

result = cursor.fetchone()
print(f"Total transactions for 'A P HOLDINGS': {result['count']}")

conn.close()

