#!/usr/bin/env python3
"""
Manually insert the missing company that was synced but not in database.
"""

import sqlite3
from datetime import datetime

db_path = "TallyConnectDb.db"
guid = "8fdcfdd1-71cc-4873-99c6-95735225388e"
alterid = "95278.0"
company_name = "Vrushali Infotech Pvt Ltd -21 -25"
total_records = 26790

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Check if company already exists
cur.execute("SELECT name, alterid, status, total_records FROM companies WHERE guid=? AND alterid=?", (guid, alterid))
existing = cur.fetchone()

if existing:
    print(f"Company already exists:")
    print(f"  Name: {existing[0]}")
    print(f"  AlterID: {existing[1]}")
    print(f"  Status: {existing[2]}")
    print(f"  Records: {existing[3]}")
    print("\nNo action needed.")
else:
    print(f"Company NOT found. Inserting...")
    print(f"  Name: {company_name}")
    print(f"  GUID: {guid}")
    print(f"  AlterID: {alterid}")
    print(f"  Records: {total_records}")
    
    last_sync = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        cur.execute("""
            INSERT INTO companies (name, guid, alterid, status, total_records, last_sync)
            VALUES (?, ?, ?, 'synced', ?, ?)
        """, (company_name, guid, alterid, total_records, last_sync))
        
        conn.commit()
        
        # Verify insert
        cur.execute("SELECT name, alterid, status, total_records FROM companies WHERE guid=? AND alterid=?", (guid, alterid))
        verify = cur.fetchone()
        
        if verify:
            print(f"\nSUCCESS: Company inserted and verified!")
            print(f"  Name: {verify[0]}")
            print(f"  AlterID: {verify[1]}")
            print(f"  Status: {verify[2]}")
            print(f"  Records: {verify[3]}")
        else:
            print(f"\nERROR: Company insert failed - not found after insert!")
    except sqlite3.IntegrityError as e:
        print(f"\nERROR: Integrity error - {e}")
        print("Company might already exist with different AlterID")
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()

# Show all companies with same GUID
print(f"\nAll companies with same GUID:")
cur.execute("SELECT name, alterid, status, total_records FROM companies WHERE guid=?", (guid,))
all_guid = cur.fetchall()
for r in all_guid:
    print(f"  - {r[0]} | AlterID: {r[1]} | Status: {r[2]} | Records: {r[3]}")

conn.close()

