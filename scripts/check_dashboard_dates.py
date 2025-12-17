#!/usr/bin/env python3
"""Check voucher dates vs dashboard query dates."""

import sqlite3
from datetime import datetime

db_path = "TallyConnectDb.db"
guid = "8fdcfdd1-71cc-4873-99c6-95735225388e"
alterid = "95278.0"

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Get voucher date range
cur.execute("SELECT MIN(vch_date), MAX(vch_date) FROM vouchers WHERE company_guid=? AND company_alterid=?", (guid, alterid))
date_range = cur.fetchone()
print(f"1. Voucher date range in database:")
if date_range[0]:
    print(f"   Min date: {date_range[0]}")
    print(f"   Max date: {date_range[1]}")
else:
    print("   No dates found")

# Calculate current FY (what dashboard queries)
today = datetime.now()
if today.month >= 4:  # April to December
    fy_start = datetime(today.year, 4, 1)
    fy_end = datetime(today.year + 1, 3, 31)
else:  # January to March
    fy_start = datetime(today.year - 1, 4, 1)
    fy_end = datetime(today.year, 3, 31)

print(f"\n2. Dashboard query (Current FY):")
print(f"   {fy_start.date()} to {fy_end.date()}")

# Check vouchers in current FY
cur.execute("SELECT COUNT(*) FROM vouchers WHERE company_guid=? AND company_alterid=? AND vch_date BETWEEN ? AND ?", 
            (guid, alterid, fy_start.strftime('%Y-%m-%d'), fy_end.strftime('%Y-%m-%d')))
fy_count = cur.fetchone()[0]
print(f"   Vouchers in current FY: {fy_count}")

# Check sales vouchers in current FY
cur.execute("""SELECT COUNT(*) FROM vouchers 
               WHERE company_guid=? AND company_alterid=? 
               AND (UPPER(TRIM(vch_type)) = 'SALES' OR UPPER(TRIM(vch_type)) LIKE '%SALES%')
               AND vch_cr_amt > 0
               AND vch_date BETWEEN ? AND ?""", 
            (guid, alterid, fy_start.strftime('%Y-%m-%d'), fy_end.strftime('%Y-%m-%d')))
sales_count = cur.fetchone()[0]
print(f"   Sales vouchers in current FY: {sales_count}")

# Check all FYs with data
print(f"\n3. Vouchers by Financial Year:")
cur.execute("""SELECT 
    CASE 
        WHEN CAST(strftime('%m', vch_date) AS INTEGER) >= 4 
        THEN strftime('%Y', vch_date) || '-' || strftime('%Y', date(vch_date, '+1 year'))
        ELSE strftime('%Y', date(vch_date, '-1 year')) || '-' || strftime('%Y', vch_date)
    END as fy,
    COUNT(*) as cnt
FROM vouchers
WHERE company_guid=? AND company_alterid=?
GROUP BY fy
ORDER BY fy DESC""", (guid, alterid))
fy_data = cur.fetchall()
for fy_row in fy_data:
    print(f"   FY {fy_row[0]}: {fy_row[1]} vouchers")

# Check what the sync date range was
print(f"\n4. Sync was for: 01-04-2025 to 31-03-2026 (FY 2025-26)")
sync_start = datetime(2025, 4, 1)
sync_end = datetime(2026, 3, 31)
cur.execute("SELECT COUNT(*) FROM vouchers WHERE company_guid=? AND company_alterid=? AND vch_date BETWEEN ? AND ?", 
            (guid, alterid, sync_start.strftime('%Y-%m-%d'), sync_end.strftime('%Y-%m-%d')))
sync_count = cur.fetchone()[0]
print(f"   Vouchers in sync range: {sync_count}")

conn.close()

