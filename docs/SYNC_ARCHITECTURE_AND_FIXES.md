# TallyConnect Sync Architecture & Fixes Documentation

## 📋 Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Critical Fixes Applied](#critical-fixes-applied)
4. [AlterID Handling](#alterid-handling)
5. [Sync Process Flow](#sync-process-flow)
6. [Database Schema](#database-schema)
7. [Performance Optimizations](#performance-optimizations)
8. [Future Improvements](#future-improvements)
9. [Troubleshooting Guide](#troubleshooting-guide)

---

## Overview

TallyConnect is a desktop application that syncs financial data from Tally (via ODBC) to a local SQLite database and provides a web-based reporting portal. The application handles multiple companies, each with unique GUIDs and AlterIDs that change when companies are modified in Tally.

### Key Concepts

- **GUID**: Global Unique Identifier for a company (remains constant)
- **AlterID**: Unique identifier for a company's financial year version (increments when company is altered in Tally)
- **Sync**: Process of fetching vouchers from Tally and storing them in SQLite
- **Dashboard**: Web portal displaying synced data with financial year filters

---

## Architecture

### Component Structure

```
TallyConnect/
├── backend/
│   ├── app.py                 # Main application (UI + Sync Worker)
│   ├── database/
│   │   ├── connection.py      # DB initialization
│   │   ├── company_dao.py     # Company CRUD operations
│   │   └── sync_log_dao.py    # Sync log operations
│   ├── utils/
│   │   └── sync_logger.py     # Sync operation logging
│   └── portal_server.py       # Web portal server
├── frontend/
│   └── portal/                # Web UI files
├── scripts/                   # Diagnostic/utility scripts
└── TallyConnectDb.db          # SQLite database
```

### Data Flow

```
Tally (ODBC) 
    ↓
Sync Worker (app.py)
    ↓
AlterID Filtering (Critical Fix)
    ↓
SQLite Database
    ↓
Portal Server (portal_server.py)
    ↓
Web Dashboard (frontend/portal/)
```

---

## Critical Fixes Applied

### 1. AlterID Filtering in Sync Worker ⚠️ **CRITICAL**

**Problem**: 
- Tally ODBC query returns vouchers for **ALL AlterIDs** associated with a GUID
- Sync worker was attempting to insert all fetched vouchers with the **target AlterID**
- This caused `IntegrityError` due to `UNIQUE(company_guid, company_alterid, vch_mst_id, led_name)` constraint
- `INSERT OR IGNORE` was silently skipping conflicting rows, resulting in 0 vouchers inserted

**Solution**:
```python
# Filter rows to only include those matching the target AlterID
for r in rows:
    tally_alterid = r[2]  # Extract AlterID from Tally result
    tally_alterid_str = str(tally_alterid) if tally_alterid is not None else ""
    
    # Skip rows that don't match our target AlterID
    if tally_alterid_str != alterid_str_target:
        continue  # Skip this row - it belongs to a different AlterID
    
    # Process only matching rows...
```

**Location**: `backend/app.py` lines 1309-1321

**Impact**: 
- ✅ Vouchers now correctly inserted for target AlterID only
- ✅ No more IntegrityError for duplicate vouchers
- ✅ Dashboard shows correct data for selected financial year

---

### 2. Company Insert/Update Logic

**Problem**:
- Companies with new AlterID were not being inserted (only updated)
- UI showed 0 companies despite successful syncs

**Solution**:
- Modified `update_sync_complete` in `company_dao.py` to check if AlterID changed
- If AlterID is new → INSERT new record
- If AlterID exists → UPDATE existing record
- Explicit `commit()` after operations

**Location**: `backend/database/company_dao.py`

---

### 3. Sync Logger Initialization

**Problem**:
- Sync logs were not being written to database
- Logger was using stale database connections

**Solution**:
- Modified `get_sync_logger` to always create a new instance
- Ensured AlterID is converted to string before logging

**Location**: `backend/utils/sync_logger.py`

---

### 4. PRAGMA Transaction Issue

**Problem**:
- `PRAGMA synchronous = OFF` was being executed inside a transaction
- SQLite error: "Safety level may not be changed inside a transaction"

**Solution**:
- Commit any pending transaction **before** applying PRAGMA settings
- Apply PRAGMA settings **before** starting new transaction

**Location**: `backend/app.py` lines 1398-1405

---

### 5. Database Path Resolution

**Problem**:
- Database path was relative, causing issues when working directory changed
- Verification queries were hitting wrong database file

**Solution**:
- Resolve database path to absolute path relative to project root
- Use consistent path resolution in all database operations

**Location**: `backend/database/connection.py`

---

## AlterID Handling

### What is AlterID?

- **AlterID** is a unique identifier for a company's financial year version
- When a company is altered in Tally, AlterID increments
- Same company (GUID) can have multiple AlterIDs (one per financial year/alteration)

### Database Storage

- **Companies Table**: `UNIQUE(guid, alterid)` - allows multiple records per GUID
- **Vouchers Table**: `UNIQUE(company_guid, company_alterid, vch_mst_id, led_name)`
- AlterID stored as **TEXT** (string) for consistency

### Sync Process

1. User selects company with specific AlterID
2. Sync worker fetches vouchers from Tally (via ODBC)
3. **CRITICAL**: Filter fetched rows to match target AlterID
4. Insert only matching vouchers into database
5. Update company record with voucher count

### Example Scenario

```
Company: "Vrushali Infotech Pvt Ltd"
GUID: 8fdcfdd1-71cc-4873-9...

AlterID 95278.0 → FY 2024-25 (644 vouchers)
AlterID 102209.0 → FY 2025-26 (644 vouchers)

When syncing AlterID 95278.0:
- Tally query returns vouchers for BOTH AlterIDs
- Filter: Only process rows where AlterID = 95278.0
- Insert: Only 644 vouchers for AlterID 95278.0
```

---

## Sync Process Flow

### Step-by-Step Process

1. **User Initiates Sync**
   - Selects company from UI
   - Sets date range (from_date, to_date)
   - Clicks "Sync" button

2. **Sync Worker Starts** (`_sync_worker`)
   - Initialize sync logger
   - Update company status to "syncing"
   - Connect to Tally via ODBC

3. **Date Range Slicing**
   - Calculate total days in range
   - Choose slice size based on range:
     - >2 years: 365 days (financial year slices)
     - 1-2 years: 30 days (monthly slices)
     - <1 year: 30 days or divided into ~12 chunks

4. **Execute Window Function** (`_execute_window`)
   - For each date slice:
     - Build Tally query with date range
     - Execute ODBC query
     - Fetch results in batches (5000 rows per batch)

5. **AlterID Filtering** ⚠️ **CRITICAL STEP**
   - Extract AlterID from each row (column index 2)
   - Compare with target AlterID
   - Skip rows that don't match
   - Process only matching rows

6. **Batch Insert**
   - Apply PRAGMA settings (before transaction)
   - Acquire database lock
   - Bulk insert vouchers (5000 per batch)
   - Commit transaction
   - Release lock

7. **Verification** (first batch only)
   - Open new database connection
   - Query inserted vouchers
   - Log verification results

8. **Complete Sync**
   - Update company status to "synced"
   - Update total_records count
   - Log sync completion

### Error Handling

- **Database Lock Timeout**: Retry with longer timeout
- **IntegrityError**: Log and skip (should not occur after AlterID filtering)
- **ODBC Connection Error**: Log and abort sync
- **Row Parse Error**: Log and continue with next row

---

## Database Schema

### Companies Table

```sql
CREATE TABLE companies (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  guid TEXT NOT NULL,
  alterid TEXT NOT NULL,
  dsn TEXT,
  status TEXT DEFAULT 'new',
  total_records INTEGER DEFAULT 0,
  last_sync TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(guid, alterid)
)
```

**Key Points**:
- `UNIQUE(guid, alterid)` allows multiple records per GUID (different AlterIDs)
- `alterid` stored as TEXT for consistency
- `status`: 'new', 'syncing', 'synced', 'failed'

### Vouchers Table

```sql
CREATE TABLE vouchers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  company_guid TEXT NOT NULL,
  company_alterid TEXT NOT NULL,
  company_name TEXT,
  vch_date TEXT,
  vch_type TEXT,
  vch_no TEXT,
  vch_mst_id TEXT,
  led_name TEXT,
  -- ... other fields ...
  UNIQUE(company_guid, company_alterid, vch_mst_id, led_name)
)
```

**Key Points**:
- `UNIQUE(company_guid, company_alterid, vch_mst_id, led_name)` prevents duplicate vouchers
- `company_alterid` must match the AlterID used during sync
- `vch_date` used for financial year filtering in dashboard

### Sync Logs Table

```sql
CREATE TABLE sync_logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  company_guid TEXT NOT NULL,
  company_alterid TEXT NOT NULL,
  company_name TEXT,
  log_level TEXT,
  message TEXT,
  timestamp TEXT DEFAULT CURRENT_TIMESTAMP
)
```

---

## Performance Optimizations

### 1. Date Range Slicing

- Large ranges (>2 years) use 365-day slices (fastest)
- Medium ranges (1-2 years) use 30-day slices (best progress tracking)
- Small ranges (<1 year) divided into ~12 chunks

### 2. Batch Processing

- Fetch 5000 rows per batch from Tally
- Insert 5000 vouchers per batch to SQLite
- Reduces memory usage and improves performance

### 3. PRAGMA Settings

```python
PRAGMA synchronous = OFF        # Disable synchronous writes (faster)
PRAGMA temp_store = MEMORY      # Use memory for temp tables
PRAGMA cache_size = -64000      # 64MB cache
```

**Note**: PRAGMA settings must be applied **before** starting transaction

### 4. Database Locking

- Thread-safe operations using `threading.Lock`
- Timeout mechanism to prevent deadlocks
- Minimal lock time (only during insert)

---

## Future Improvements

### 1. Incremental Sync
- Track last sync timestamp
- Only fetch vouchers modified after last sync
- Reduce sync time for large datasets

### 2. Sync Progress UI
- Real-time progress bar
- Show current batch number
- Display estimated time remaining

### 3. Error Recovery
- Resume failed syncs
- Skip already-synced vouchers
- Retry failed batches

### 4. Multi-threaded Sync
- Sync multiple companies simultaneously
- Parallel batch processing
- Improved performance for multiple companies

### 5. Data Validation
- Validate voucher data before insert
- Check date ranges
- Verify AlterID consistency

### 6. Dashboard Enhancements
- Financial year selector
- Date range filters
- Export to Excel/PDF
- Custom report generation

---

## Troubleshooting Guide

### Issue: Dashboard shows 0 data

**Symptoms**:
- Company appears in UI
- Dashboard shows ₹0.00 for all metrics
- Vouchers count shows 0

**Possible Causes**:
1. **Wrong Financial Year Filter**: Dashboard filtered for different FY than synced data
2. **Date Range Mismatch**: Vouchers synced for different date range
3. **AlterID Mismatch**: Vouchers stored with different AlterID

**Solutions**:
1. Check dashboard filter (FY selector)
2. Verify voucher dates in database:
   ```sql
   SELECT MIN(vch_date), MAX(vch_date), COUNT(*) 
   FROM vouchers 
   WHERE company_alterid = '95278.0';
   ```
3. Verify AlterID matches:
   ```sql
   SELECT DISTINCT company_alterid FROM vouchers WHERE company_guid = '...';
   ```

---

### Issue: Sync completes but 0 vouchers inserted

**Symptoms**:
- Sync shows "Complete" status
- Company shows 0 total_records
- Database has 0 vouchers

**Possible Causes**:
1. **AlterID Filter Too Strict**: All rows filtered out
2. **Date Range Issue**: No vouchers in specified range
3. **Tally Connection Issue**: Query returned 0 rows

**Solutions**:
1. Check sync logs for AlterID filtering messages
2. Verify Tally has vouchers in date range
3. Check ODBC connection and query execution
4. Run diagnostic script: `scripts/check_all_alterids.py`

---

### Issue: IntegrityError during sync

**Symptoms**:
- Sync fails with `UNIQUE constraint failed`
- Error mentions `vouchers.company_guid, company_alterid, vch_mst_id, led_name`

**Possible Causes**:
1. **AlterID Filter Not Working**: Rows from different AlterID being inserted
2. **Duplicate Vouchers**: Same voucher already exists

**Solutions**:
1. Verify AlterID filtering is working (check logs)
2. Check for existing vouchers:
   ```sql
   SELECT COUNT(*) FROM vouchers 
   WHERE company_guid = '...' 
   AND company_alterid = '...' 
   AND vch_mst_id = '...' 
   AND led_name = '...';
   ```
3. Use `INSERT OR IGNORE` for duplicates (already implemented)

---

### Issue: Company not appearing in UI

**Symptoms**:
- Sync completed successfully
- Company not in companies list

**Possible Causes**:
1. **Commit Issue**: Company record not committed to database
2. **AlterID Format Mismatch**: Query using wrong AlterID format
3. **GUID Mismatch**: Company stored with different GUID

**Solutions**:
1. Check database directly:
   ```sql
   SELECT * FROM companies WHERE name LIKE '%CompanyName%';
   ```
2. Verify AlterID format (should be TEXT/string)
3. Check `get_all_synced()` query in `company_dao.py`

---

### Issue: Sync logs not appearing

**Symptoms**:
- Sync operations complete
- No logs in sync_logs table

**Possible Causes**:
1. **Logger Not Initialized**: `get_sync_logger` failed
2. **Database Connection Issue**: Logger using wrong database
3. **AlterID Format Issue**: Logger failing on AlterID conversion

**Solutions**:
1. Check terminal for logger initialization errors
2. Verify `sync_logs` table exists
3. Check AlterID format in logger calls

---

## Diagnostic Scripts

All diagnostic scripts are located in `scripts/` folder:

- `check_all_alterids.py` - List all AlterIDs and voucher counts
- `check_company_db.py` - Verify company records
- `check_vouchers.py` - Check voucher counts and dates
- `check_dashboard_dates.py` - Verify date ranges for dashboard
- `verify_vouchers_direct.py` - Direct database verification

**Usage**:
```bash
cd scripts
python check_all_alterids.py
```

---

## Summary

### Key Fixes
1. ✅ **AlterID Filtering**: Only process vouchers matching target AlterID
2. ✅ **Company Insert/Update**: Proper handling of new vs existing AlterIDs
3. ✅ **Sync Logger**: Fixed initialization and connection issues
4. ✅ **PRAGMA Transactions**: Apply settings before transaction
5. ✅ **Database Paths**: Consistent absolute path resolution

### Current Status
- ✅ Sync process working correctly
- ✅ Vouchers inserted with correct AlterID
- ✅ Dashboard displaying data for correct financial year
- ✅ Companies appearing in UI
- ✅ Sync logs being written

### Next Steps
- Implement incremental sync
- Add progress UI
- Enhance error recovery
- Optimize for large datasets

---

**Last Updated**: December 2025
**Version**: 5.6+
**Author**: TallyConnect Development Team

