# Sync Logs - Complete Documentation

## 📋 Overview

Sync Logs system provides comprehensive logging for all Tally sync operations. All logs are stored in database for persistence and can be viewed through the portal UI.

---

## 🏗️ Architecture

### Components

1. **Database Table** (`sync_logs`)
   - Location: `backend/database/connection.py`
   - Stores all sync operation logs
   - Indexed for fast queries

2. **Data Access Object (DAO)**
   - Location: `backend/database/sync_log_dao.py`
   - Handles all database operations
   - Methods: `add_log()`, `get_logs_by_company()`, `get_all_logs()`, etc.

3. **Sync Logger Utility**
   - Location: `backend/utils/sync_logger.py`
   - High-level logging interface
   - Methods: `sync_started()`, `sync_progress()`, `sync_completed()`, `sync_failed()`

4. **Portal API Endpoint**
   - Location: `backend/portal_server.py`
   - Endpoint: `/api/sync-logs/`
   - Returns JSON data for frontend

5. **Frontend Page**
   - Location: `frontend/portal/sync-logs.html`
   - UI for viewing sync logs with filters

---

## 📊 Database Schema

### `sync_logs` Table

```sql
CREATE TABLE sync_logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  company_guid TEXT NOT NULL,
  company_alterid TEXT NOT NULL,
  company_name TEXT NOT NULL,
  log_level TEXT NOT NULL DEFAULT 'INFO',  -- INFO, WARNING, ERROR, SUCCESS
  log_message TEXT NOT NULL,
  log_details TEXT,                        -- Additional details
  sync_status TEXT,                        -- started, in_progress, completed, failed
  records_synced INTEGER DEFAULT 0,
  error_code TEXT,
  error_message TEXT,
  duration_seconds REAL,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
```

### Indexes

- `idx_sync_logs_company` - For faster company-based queries
- `idx_sync_logs_created_at` - For date-based sorting
- `idx_sync_logs_level` - For level-based filtering

---

## 🔧 Implementation Details

### 1. SyncLogDAO (Data Access Object)

**File:** `backend/database/sync_log_dao.py`

**Key Methods:**

- `add_log()` - Add a new log entry
- `get_logs_by_company()` - Get logs for specific company
- `get_all_logs()` - Get all logs with filters
- `get_log_count()` - Get total count with filters
- `get_latest_sync_log()` - Get latest log for company
- `delete_old_logs()` - Cleanup old logs (90 days default)
- `delete_logs_by_company()` - Delete logs for company

**Features:**
- ✅ UTC timestamps (Phase 1)
- ✅ Thread-safe operations (with lock)
- ✅ Pagination support (limit, offset)
- ✅ Filtering (log_level, sync_status)

---

### 2. SyncLogger (High-Level Interface)

**File:** `backend/utils/sync_logger.py`

**Key Methods:**

- `sync_started()` - Log sync start
- `sync_progress()` - Log sync progress
- `sync_completed()` - Log sync completion
- `sync_failed()` - Log sync failure
- `info()`, `warning()`, `error()`, `success()` - General logging

**Usage Example:**
```python
from backend.utils.sync_logger import get_sync_logger

logger = get_sync_logger()

# Sync started
logger.sync_started(guid, alterid, name, details="Starting sync...")

# Sync progress
logger.sync_progress(guid, alterid, name, records_synced=1000, 
                   message="Batch 10 completed")

# Sync completed
logger.sync_completed(guid, alterid, name, records_synced=5000, 
                     duration_seconds=120.5)

# Sync failed
logger.sync_failed(guid, alterid, name, error_message="Connection timeout")
```

---

### 3. Portal API Endpoint

**File:** `backend/portal_server.py`  
**Method:** `send_sync_logs()`

**Endpoint:** `/api/sync-logs/`

**Query Parameters:**
- `company_guid` - Filter by company GUID
- `company_alterid` - Filter by company AlterID
- `log_level` - Filter by log level (INFO, WARNING, ERROR, SUCCESS)
- `sync_status` - Filter by status (started, in_progress, completed, failed)
- `limit` - Number of logs per page (default: 50)
- `offset` - Pagination offset (default: 0)

**Response Format:**
```json
{
  "logs": [
    {
      "id": 1,
      "company_guid": "guid-here",
      "company_alterid": "95278",
      "company_name": "Company Name",
      "log_level": "SUCCESS",
      "log_message": "Sync completed successfully",
      "log_details": "Details here",
      "sync_status": "completed",
      "records_synced": 5000,
      "error_code": null,
      "error_message": null,
      "duration_seconds": 120.5,
      "created_at": "2025-01-17 14:10:00"
    }
  ],
  "total_count": 100,
  "limit": 50,
  "offset": 0,
  "has_more": true
}
```

---

## 📝 Log Levels

1. **INFO** - General information
   - Sync started
   - Progress updates
   - General messages

2. **WARNING** - Warnings
   - Non-critical issues
   - Data inconsistencies
   - Performance warnings

3. **ERROR** - Errors
   - Sync failures
   - Connection errors
   - Data errors

4. **SUCCESS** - Success
   - Sync completed
   - Successful operations

---

## 📊 Sync Status

1. **started** - Sync operation started
2. **in_progress** - Sync in progress
3. **completed** - Sync completed successfully
4. **failed** - Sync failed

---

## 🔄 Integration in Sync Process

**File:** `backend/app.py`

Sync logs are integrated in the sync worker (`_sync_worker` method):

1. **Sync Start:**
   ```python
   sync_logger.sync_started(guid, alterid_str_log, name, 
                           details=f"Starting sync from {from_date} to {to_date}")
   ```

2. **Sync Progress:**
   ```python
   sync_logger.sync_progress(guid, alterid_str_log, name,
                            records_synced=approx_inserted,
                            message=f"Batch {batch_count}: {rows_inserted} vouchers inserted")
   ```

3. **Sync Completed:**
   ```python
   sync_logger.sync_completed(guid, alterid_str_log, name,
                             records_synced=actual_vouchers,
                             duration_seconds=sync_duration)
   ```

4. **Sync Failed:**
   ```python
   sync_logger.sync_failed(guid, alterid_str_log, name,
                          error_message=str(e),
                          error_code="SYNC_ERROR")
   ```

---

## 🎯 Features

### ✅ Implemented

1. **Database Storage**
   - All logs stored in `sync_logs` table
   - UTC timestamps for consistency
   - Indexed for fast queries

2. **Logging Methods**
   - `sync_started()` - Log sync start
   - `sync_progress()` - Log progress updates
   - `sync_completed()` - Log completion
   - `sync_failed()` - Log failures

3. **Portal API**
   - `/api/sync-logs/` endpoint
   - Filtering by company, level, status
   - Pagination support

4. **Frontend UI**
   - `sync-logs.html` page
   - Filters (Company, Level, Status)
   - Table view with sorting

5. **Thread Safety**
   - Thread-safe operations with locks
   - Safe for concurrent syncs

6. **Error Handling**
   - Fallback to console if DB fails
   - Graceful error handling

---

## 🔍 Query Examples

### Get logs for specific company:
```python
dao = SyncLogDAO(conn)
logs = dao.get_logs_by_company(guid, alterid, limit=50, offset=0)
```

### Get all logs with filters:
```python
logs = dao.get_all_logs(limit=100, offset=0, 
                        log_level='ERROR', sync_status='failed')
```

### Get log count:
```python
count = dao.get_log_count(guid, alterid, log_level='ERROR')
```

---

## 🧹 Maintenance

### Delete Old Logs

```python
dao = SyncLogDAO(conn)
deleted = dao.delete_old_logs(days=90)  # Delete logs older than 90 days
```

### Delete Company Logs

```python
deleted = dao.delete_logs_by_company(guid, alterid)
```

---

## 📈 Performance

- **Indexes:** Fast queries on company, date, level
- **Pagination:** Efficient for large datasets
- **Thread-Safe:** Safe for concurrent operations
- **UTC Timestamps:** Consistent across timezones

---

## 🐛 Known Issues

None currently. All features working as expected.

---

## 🚀 Future Enhancements

1. **Caching** - Cache frequently accessed logs
2. **Export** - Export logs to CSV/Excel
3. **Search** - Full-text search in log messages
4. **Alerts** - Email notifications for errors
5. **Analytics** - Sync performance analytics

---

**Last Updated:** 2025-01-17  
**Status:** ✅ Fully Implemented and Working

