#!/usr/bin/env python3
"""Check synced companies in database."""
import sqlite3
import os

db_path = "TallyConnectDb.db"
if not os.path.exists(db_path):
    print(f"[ERROR] Database not found: {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Check all companies
cursor.execute("SELECT name, guid, alterid, status, total_records FROM companies")
all_companies = cursor.fetchall()

print(f"\n{'='*60}")
print(f"Total companies in database: {len(all_companies)}")
print(f"{'='*60}\n")

# Check all companies by status
print("Companies by Status:\n")
cursor.execute("SELECT status, COUNT(*) as count FROM companies GROUP BY status")
status_counts = cursor.fetchall()
for row in status_counts:
    print(f"  {row['status'] or 'NULL'}: {row['count']}")

print("\n" + "="*60)
print("All Companies (All Statuses):")
print("="*60 + "\n")

for idx, row in enumerate(all_companies, 1):
    print(f"{idx}. {row['name']}")
    print(f"   GUID: {row['guid']}")
    print(f"   AlterID: {row['alterid']}")
    print(f"   Status: {row['status'] or 'NULL'}")
    print(f"   Records: {row['total_records'] or 0}")
    print()

# Check synced companies
cursor.execute("SELECT name, guid, alterid, status, total_records FROM companies WHERE status='synced'")
synced_companies = cursor.fetchall()

print(f"\n{'='*60}")
print(f"Synced companies (status='synced'): {len(synced_companies)}")
print(f"{'='*60}\n")

if len(synced_companies) == 0:
    print("⚠️  No synced companies found!")
    print("\nTo sync companies:")
    print("1. Open TallyConnect app")
    print("2. Click '➕ Add Company'")
    print("3. Select and sync companies")
else:
    for idx, row in enumerate(synced_companies, 1):
        print(f"{idx}. {row['name']}")
        print(f"   GUID: {row['guid']}")
        print(f"   AlterID: {row['alterid']}")
        print(f"   Status: {row['status']}")
        print(f"   Records: {row['total_records'] or 0}")
        print()

conn.close()

