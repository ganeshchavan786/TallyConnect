# TallyConnect Quick Reference Guide

## 🚀 Quick Start

### Starting the Application
```bash
python main.py
```

### Starting the Portal
```bash
python backend/portal_server.py
# Or use: scripts/START_PORTAL.bat
```

---

## 🔍 Common Tasks

### Check Company Status
```bash
cd scripts
python check_all_alterids.py
```

### Verify Vouchers
```bash
cd scripts
python check_vouchers.py
```

### Check Dashboard Dates
```bash
cd scripts
python check_dashboard_dates.py
```

---

## 🐛 Troubleshooting

### Dashboard shows 0 data
1. Check financial year filter matches synced data
2. Verify voucher dates: `scripts/check_dashboard_dates.py`
3. Check AlterID matches: `scripts/check_all_alterids.py`

### Sync completes but 0 vouchers
1. Check sync logs for AlterID filtering
2. Verify Tally has vouchers in date range
3. Check ODBC connection

### Company not appearing
1. Check database: `scripts/check_company_db.py`
2. Verify AlterID format (should be TEXT/string)
3. Check commit was successful

---

## 📊 Database Queries

### List All Companies
```sql
SELECT name, guid, alterid, status, total_records 
FROM companies 
ORDER BY name, alterid;
```

### Count Vouchers by AlterID
```sql
SELECT company_alterid, COUNT(*) as count 
FROM vouchers 
WHERE company_guid = 'YOUR_GUID'
GROUP BY company_alterid;
```

### Check Voucher Date Range
```sql
SELECT 
    MIN(vch_date) as min_date,
    MAX(vch_date) as max_date,
    COUNT(*) as total
FROM vouchers 
WHERE company_alterid = 'YOUR_ALTERID';
```

### Find Duplicate Vouchers
```sql
SELECT company_guid, company_alterid, vch_mst_id, led_name, COUNT(*) as count
FROM vouchers
GROUP BY company_guid, company_alterid, vch_mst_id, led_name
HAVING count > 1;
```

---

## 🔧 Configuration

### Database Path
- Default: `TallyConnectDb.db` (project root)
- Config: `backend/config/settings.py` → `DB_FILE`

### Batch Size
- Default: 5000 vouchers per batch
- Location: `backend/app.py` → `BATCH_SIZE`

### Sync Settings
- Date slice size: Auto-calculated based on range
- PRAGMA settings: Applied before transactions
- Lock timeout: 1 second (retry with 5 seconds)

---

## 📁 File Locations

### Main Files
- `main.py` - Application entry point
- `backend/app.py` - Main application logic
- `backend/portal_server.py` - Web portal server

### Database
- `backend/database/connection.py` - DB initialization
- `backend/database/company_dao.py` - Company operations
- `TallyConnectDb.db` - SQLite database

### Utilities
- `backend/utils/sync_logger.py` - Sync logging
- `scripts/` - Diagnostic scripts

---

## 🎯 Key Concepts

### AlterID
- Unique identifier for company's financial year version
- Increments when company is altered in Tally
- Stored as TEXT in database

### GUID
- Global Unique Identifier for company
- Remains constant across AlterIDs
- Used to group related AlterIDs

### Sync Process
1. User selects company + date range
2. Worker fetches vouchers from Tally (ODBC)
3. **Filter by AlterID** (critical step)
4. Insert vouchers in batches
5. Update company status

---

## ⚠️ Important Notes

### AlterID Filtering
- **CRITICAL**: Tally query returns vouchers for ALL AlterIDs
- Must filter rows to match target AlterID
- Location: `backend/app.py` lines 1309-1321

### PRAGMA Settings
- Must be applied **before** transaction starts
- Commit pending transaction first
- Location: `backend/app.py` lines 1398-1405

### Database Locking
- Use `threading.Lock` for thread safety
- Timeout: 1 second (retry with 5 seconds)
- Minimal lock time (only during insert)

---

## 📞 Support

### Diagnostic Scripts
All in `scripts/` folder:
- `check_all_alterids.py` - List all AlterIDs
- `check_company_db.py` - Verify companies
- `check_vouchers.py` - Check vouchers
- `check_dashboard_dates.py` - Verify dates
- `verify_vouchers_direct.py` - Direct verification

### Logs
- Sync logs: `sync_logs` table in database
- Application logs: Terminal output
- Error logs: Check terminal for exceptions

---

## 🔄 Common Workflows

### Sync New Company
1. Open TallyConnect app
2. Click "Add Company"
3. Select company from Tally
4. Set date range
5. Click "Sync"
6. Wait for completion
7. Check dashboard

### Sync Existing Company
1. Select company from list
2. Click "Sync" button
3. Set date range (if needed)
4. Wait for completion
5. Verify in dashboard

### Troubleshoot Missing Data
1. Run `scripts/check_all_alterids.py`
2. Verify AlterID matches
3. Check voucher dates
4. Verify financial year filter
5. Re-sync if needed

---

**Last Updated**: December 2025

