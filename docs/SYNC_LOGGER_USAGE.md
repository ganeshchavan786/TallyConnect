# Sync Logger - Usage Guide

## Overview
Professional logging system for sync operations. All sync logs are stored in database for persistence and retrieval through the portal.

## Architecture

### Files Created:
1. **`backend/database/connection.py`** - Added `sync_logs` table schema
2. **`backend/database/sync_log_dao.py`** - Database operations for sync logs
3. **`backend/utils/sync_logger.py`** - Professional logging module
4. **`backend/portal_server.py`** - API endpoint `/api/sync-logs/`
5. **`frontend/portal/sync-logs.html`** - Frontend page to view logs

## Database Schema

### `sync_logs` Table:
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

**Indexes:**
- `idx_sync_logs_company` - For faster company-based queries
- `idx_sync_logs_created_at` - For date-based sorting
- `idx_sync_logs_level` - For level-based filtering

## Usage in Sync Operations

### Step 1: Import SyncLogger

```python
from backend.utils.sync_logger import SyncLogger, get_sync_logger

# Option 1: Use global logger (recommended)
logger = get_sync_logger()

# Option 2: Create instance with custom db_path and lock
logger = SyncLogger(db_path="path/to/db.db", db_lock=threading_lock)
```

### Step 2: Log Sync Events

```python
# Sync Started
logger.sync_started(company_guid, company_alterid, company_name, 
                   details="Starting sync from 01-04-2024 to 31-03-2025")

# Sync Progress
logger.sync_progress(company_guid, company_alterid, company_name,
                    records_synced=500, 
                    message="Batch 5 completed",
                    details="Syncing vouchers...")

# Info Messages
logger.info(company_guid, company_alterid, company_name,
           "Connected to Tally successfully",
           details="DSN: TallyODBC64_9000")

# Warnings
logger.warning(company_guid, company_alterid, company_name,
              "Some vouchers skipped due to missing data",
              details="Skipped 10 vouchers")

# Sync Completed
import time
start_time = time.time()
# ... sync operations ...
duration = time.time() - start_time

logger.sync_completed(company_guid, company_alterid, company_name,
                     records_synced=1000,
                     duration_seconds=duration,
                     details="Sync completed successfully")

# Sync Failed
try:
    # ... sync operations ...
except Exception as e:
    logger.sync_failed(company_guid, company_alterid, company_name,
                       error_message=str(e),
                       error_code="SYNC_ERROR_001",
                       details="Failed during voucher insertion",
                       records_synced=500)
```

### Step 3: Integration Example

```python
def sync_company_worker(name, guid, alterid, dsn, from_date, to_date, lock):
    """Sync worker function with logging."""
    from backend.utils.sync_logger import get_sync_logger
    import time
    
    logger = get_sync_logger()
    start_time = time.time()
    records_synced = 0
    
    try:
        # Log sync start
        logger.sync_started(guid, alterid, name, 
                           details=f"Sync from {from_date} to {to_date}")
        
        # Connect to Tally
        logger.info(guid, alterid, name, 
                   f"Connecting to Tally via {dsn}")
        
        # ... connection code ...
        
        # Sync in batches
        batch_size = 100
        batch_num = 0
        
        while True:
            # ... fetch batch from Tally ...
            batch_num += 1
            records_synced += len(batch)
            
            # Log progress
            logger.sync_progress(guid, alterid, name,
                               records_synced=records_synced,
                               message=f"Batch {batch_num} completed",
                               details=f"Synced {len(batch)} vouchers")
            
            # ... insert batch into database ...
            
            if len(batch) < batch_size:
                break
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Log completion
        logger.sync_completed(guid, alterid, name,
                            records_synced=records_synced,
                            duration_seconds=duration,
                            details=f"All {records_synced} records synced successfully")
        
    except Exception as e:
        duration = time.time() - start_time
        logger.sync_failed(guid, alterid, name,
                          error_message=str(e),
                          error_code="SYNC_ERROR",
                          details=f"Failed after syncing {records_synced} records",
                          records_synced=records_synced)
    finally:
        lock.release()
```

## API Endpoints

### Get Sync Logs

**Endpoint:** `GET /api/sync-logs/`

**Query Parameters:**
- `company_guid` (optional) - Filter by company GUID
- `company_alterid` (optional) - Filter by company AlterID
- `log_level` (optional) - Filter by log level (INFO, WARNING, ERROR, SUCCESS)
- `sync_status` (optional) - Filter by sync status (started, in_progress, completed, failed)
- `limit` (optional, default: 100) - Number of logs to return
- `offset` (optional, default: 0) - Offset for pagination

**Examples:**
```
# Get all logs
GET /api/sync-logs/

# Get logs for specific company
GET /api/sync-logs/?company_guid=xxx&company_alterid=yyy

# Get error logs only
GET /api/sync-logs/?log_level=ERROR

# Get completed syncs
GET /api/sync-logs/?sync_status=completed

# Pagination
GET /api/sync-logs/?limit=50&offset=100
```

**Response:**
```json
{
  "logs": [
    {
      "id": 1,
      "company_guid": "xxx",
      "company_alterid": "yyy",
      "company_name": "Company Name",
      "log_level": "SUCCESS",
      "log_message": "Sync completed successfully",
      "log_details": "All records synced",
      "sync_status": "completed",
      "records_synced": 1000,
      "error_code": null,
      "error_message": null,
      "duration_seconds": 45.5,
      "created_at": "2025-12-16 10:20:30"
    }
  ],
  "total_count": 150,
  "limit": 100,
  "offset": 0,
  "has_more": true
}
```

## Frontend Page

**URL:** `http://localhost:8000/sync-logs.html`

**Features:**
- View all sync logs
- Filter by company
- Filter by log level (INFO, WARNING, ERROR, SUCCESS)
- Filter by sync status (started, in_progress, completed, failed)
- Pagination (50 logs per page)
- Real-time refresh
- Color-coded log levels and statuses
- Detailed error messages

## Log Levels

- **INFO** - General information messages
- **WARNING** - Warning messages (non-critical issues)
- **ERROR** - Error messages (sync failures, exceptions)
- **SUCCESS** - Success messages (completed operations)

## Sync Status

- **started** - Sync operation started
- **in_progress** - Sync operation in progress
- **completed** - Sync operation completed successfully
- **failed** - Sync operation failed

## Best Practices

1. **Always log sync start and completion**
   ```python
   logger.sync_started(...)
   # ... sync operations ...
   logger.sync_completed(...)
   ```

2. **Log progress for long operations**
   ```python
   # Log every 100 records or every batch
   if records_synced % 100 == 0:
       logger.sync_progress(...)
   ```

3. **Include error details**
   ```python
   logger.sync_failed(..., 
                     error_message=str(e),
                     error_code="CUSTOM_ERROR_CODE",
                     details="Additional context")
   ```

4. **Use appropriate log levels**
   - INFO: Normal operations
   - WARNING: Non-critical issues
   - ERROR: Failures that need attention
   - SUCCESS: Completed operations

5. **Clean old logs periodically**
   ```python
   from backend.database.sync_log_dao import SyncLogDAO
   dao = SyncLogDAO(conn)
   deleted = dao.delete_old_logs(days=90)  # Keep last 90 days
   ```

## Integration Checklist

- [ ] Import `SyncLogger` in sync worker function
- [ ] Log sync start with `sync_started()`
- [ ] Log progress updates with `sync_progress()`
- [ ] Log completion with `sync_completed()`
- [ ] Log errors with `sync_failed()`
- [ ] Include relevant details in log messages
- [ ] Test logging with actual sync operations
- [ ] Verify logs appear in sync-logs.html page

## Next Steps

1. **Integrate into `backend/app.py`** - Add logging to `_sync_worker()` function
2. **Test logging** - Run a sync and verify logs appear
3. **View logs** - Check sync-logs.html page
4. **Monitor** - Use logs to debug sync issues

---

**Note:** All logs are stored in database and persist across application restarts. Logs can be viewed through the portal at any time.

