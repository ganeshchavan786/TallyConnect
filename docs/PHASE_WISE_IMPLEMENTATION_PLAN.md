# Phase-wise Database Practices Implementation Plan

## 📋 Overview

या document मध्ये सर्व missing database practices चा phase-wise implementation plan आहे. प्रत्येक phase मध्ये specific tasks, timeline, आणि priority दिली आहे.

---

## 🎯 Phase 1: Critical Fixes (Week 1-2)

### Priority: **CRITICAL** ⚠️
### Timeline: **1-2 weeks**
### Impact: **High Performance & Data Protection**

---

### Task 1.1: Add Indexes to Vouchers Table

**Priority**: 🔴 **CRITICAL**

**Why**: Dashboard queries खूप slow आहेत (no date index)

**Implementation**:
```python
# File: backend/database/connection.py
# Add after line 118 (after sync_logs indexes)

# Vouchers table indexes
cur.execute("""
CREATE INDEX IF NOT EXISTS idx_vouchers_company_date 
ON vouchers(company_guid, company_alterid, vch_date)
""")

cur.execute("""
CREATE INDEX IF NOT EXISTS idx_vouchers_date 
ON vouchers(vch_date)
""")

cur.execute("""
CREATE INDEX IF NOT EXISTS idx_vouchers_type 
ON vouchers(vch_type)
""")

cur.execute("""
CREATE INDEX IF NOT EXISTS idx_vouchers_company 
ON vouchers(company_guid, company_alterid)
""")
```

**Expected Impact**:
- Dashboard queries: **10x faster**
- Report generation: **5x faster**
- Overall performance: **Significant improvement**

**Testing**:
1. Run dashboard queries before/after
2. Measure query execution time
3. Verify no breaking changes

**Estimated Time**: **30 minutes**

---

### Task 1.2: Add Indexes to Companies Table

**Priority**: 🟡 **HIGH**

**Why**: Company lookups slow आहेत

**Implementation**:
```python
# File: backend/database/connection.py
# Add after vouchers indexes

# Companies table indexes
cur.execute("""
CREATE INDEX IF NOT EXISTS idx_companies_status 
ON companies(status)
""")

cur.execute("""
CREATE INDEX IF NOT EXISTS idx_companies_guid_alterid 
ON companies(guid, alterid)
""")
```

**Expected Impact**:
- Company queries: **3x faster**
- UI loading: **Faster**

**Estimated Time**: **15 minutes**

---

### Task 1.3: Implement Database Backup System

**Priority**: 🔴 **CRITICAL**

**Why**: Data loss prevention

**Implementation**:

**Step 1**: Create backup utility
```python
# File: backend/utils/backup.py (NEW FILE)
import shutil
import os
from datetime import datetime
from pathlib import Path

def backup_database(db_path, backup_dir="backups", max_backups=30):
    """
    Create database backup.
    
    Args:
        db_path: Path to database file
        backup_dir: Directory to store backups
        max_backups: Maximum number of backups to keep
    
    Returns:
        Path to backup file
    """
    # Create backup directory if not exists
    backup_path = Path(backup_dir)
    backup_path.mkdir(parents=True, exist_ok=True)
    
    # Generate backup filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    db_name = Path(db_path).stem
    backup_file = backup_path / f"{db_name}_{timestamp}.db"
    
    # Copy database file
    shutil.copy2(db_path, backup_file)
    
    # Clean old backups (keep only max_backups)
    backups = sorted(backup_path.glob(f"{db_name}_*.db"), reverse=True)
    for old_backup in backups[max_backups:]:
        old_backup.unlink()
    
    return str(backup_file)

def restore_database(backup_path, db_path):
    """
    Restore database from backup.
    
    Args:
        backup_path: Path to backup file
        db_path: Path to restore to
    """
    shutil.copy2(backup_path, db_path)
```

**Step 2**: Add backup to sync completion
```python
# File: backend/app.py
# Add after sync completes (around line 1600)

from backend.utils.backup import backup_database

# After successful sync
try:
    backup_path = backup_database(DB_FILE)
    self.log(f"[{name}] 💾 Backup created: {backup_path}")
except Exception as backup_err:
    self.log(f"[{name}] ⚠️ Backup failed: {backup_err}")
```

**Step 3**: Add scheduled backup (optional)
```python
# File: backend/utils/scheduled_backup.py (NEW FILE)
import schedule
import time
from backend.utils.backup import backup_database
from backend.config.settings import DB_FILE

def run_scheduled_backup():
    """Run daily backup at 2 AM"""
    try:
        backup_path = backup_database(DB_FILE)
        print(f"✅ Scheduled backup created: {backup_path}")
    except Exception as e:
        print(f"❌ Scheduled backup failed: {e}")

# Schedule daily backup at 2 AM
schedule.every().day.at("02:00").do(run_scheduled_backup)

# Run in background thread
def start_backup_scheduler():
    import threading
    def run():
        while True:
            schedule.run_pending()
            time.sleep(60)
    thread = threading.Thread(target=run, daemon=True)
    thread.start()
```

**Expected Impact**:
- Data protection
- Disaster recovery capability
- Peace of mind

**Testing**:
1. Create backup
2. Verify backup file exists
3. Test restore process
4. Verify data integrity after restore

**Estimated Time**: **2-3 hours**

---

### Task 1.4: Use UTC Timestamps

**Priority**: 🟡 **HIGH**

**Why**: Timezone consistency

**Implementation**:

**Step 1**: Update sync_log_dao.py
```python
# File: backend/database/sync_log_dao.py
# Replace line 78

from datetime import datetime, timezone

# OLD:
created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# NEW:
created_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
```

**Step 2**: Update company_dao.py
```python
# File: backend/database/company_dao.py
# Replace line 209

from datetime import datetime, timezone

# OLD:
last_sync = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# NEW:
last_sync = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
```

**Step 3**: Update database schema (optional - for new records)
```sql
-- For new records, CURRENT_TIMESTAMP uses UTC in SQLite
-- But explicit UTC in Python code is better
```

**Expected Impact**:
- Consistent timestamps across timezones
- No timezone confusion

**Testing**:
1. Create new records
2. Verify timestamps are UTC
3. Check timezone conversion in UI

**Estimated Time**: **30 minutes**

---

## 📊 Phase 1 Summary

| Task | Priority | Time | Impact |
|------|----------|------|--------|
| Add Vouchers Indexes | 🔴 Critical | 30 min | 10x faster queries |
| Add Companies Indexes | 🟡 High | 15 min | 3x faster queries |
| Implement Backups | 🔴 Critical | 2-3 hrs | Data protection |
| UTC Timestamps | 🟡 High | 30 min | Consistency |
| **Total** | | **3-4 hours** | **High** |

---

## 🎯 Phase 2: Security & Best Practices (Week 3-4)

### Priority: **HIGH** 🟡
### Timeline: **2 weeks**
### Impact: **Security & Code Quality**

---

### Task 2.1: Implement Environment Variables

**Priority**: 🟡 **HIGH**

**Why**: Security - sensitive config should not be hardcoded

**Implementation**:

**Step 1**: Install python-dotenv
```bash
pip install python-dotenv
```

**Step 2**: Create .env file
```bash
# File: .env (NEW FILE)
DB_FILE=TallyConnectDb.db
BATCH_SIZE=5000
BACKUP_DIR=backups
MAX_BACKUPS=30
LOG_RETENTION_DAYS=90
```

**Step 3**: Update settings.py
```python
# File: backend/config/settings.py
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database Configuration
DB_FILE = os.getenv("DB_FILE", "TallyConnectDb.db")

# Sync Configuration
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "5000"))

# Backup Configuration
BACKUP_DIR = os.getenv("BACKUP_DIR", "backups")
MAX_BACKUPS = int(os.getenv("MAX_BACKUPS", "30"))

# Log Configuration
LOG_RETENTION_DAYS = int(os.getenv("LOG_RETENTION_DAYS", "90"))
```

**Step 4**: Add .env to .gitignore
```gitignore
# File: .gitignore
.env
.env.local
```

**Expected Impact**:
- Secure configuration
- Easy environment-specific settings
- No hardcoded values

**Testing**:
1. Test with .env file
2. Test without .env (defaults)
3. Verify no breaking changes

**Estimated Time**: **1 hour**

---

### Task 2.2: Improve Connection Closing

**Priority**: 🟡 **MEDIUM**

**Why**: Resource management best practices

**Implementation**:

**Step 1**: Update connection.py
```python
# File: backend/database/connection.py
# Add context manager support

from contextlib import contextmanager

@contextmanager
def get_db_connection(db_path=DB_FILE):
    """
    Get database connection with context manager.
    Auto-closes connection when done.
    """
    # Resolve path
    if not os.path.isabs(db_path):
        current_file = os.path.abspath(__file__)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
        db_path = os.path.join(project_root, db_path)
        db_path = os.path.abspath(db_path)
    
    conn = sqlite3.connect(db_path, check_same_thread=False)
    try:
        yield conn
    finally:
        conn.close()
```

**Step 2**: Update report_generator.py
```python
# File: backend/report_generator.py
# Replace _connect() and _close() with context manager

def _get_connection(self):
    """Get database connection with context manager."""
    from backend.database.connection import get_db_connection
    return get_db_connection(self.db_path)

# Usage:
with self._get_connection() as conn:
    cur = conn.cursor()
    # ... operations
# Auto-closes
```

**Expected Impact**:
- Better resource management
- No connection leaks
- Cleaner code

**Testing**:
1. Verify connections close properly
2. Check for connection leaks
3. Test with multiple concurrent operations

**Estimated Time**: **2 hours**

---

### Task 2.3: Replace SELECT * with Specific Columns

**Priority**: 🟡 **MEDIUM**

**Why**: Performance - only fetch needed data

**Implementation**:

**Step 1**: Update company_dao.py
```python
# File: backend/database/company_dao.py
# Replace line 75

# OLD:
query = "SELECT * FROM companies WHERE guid=? AND CAST(alterid AS TEXT)=?"

# NEW:
query = """
SELECT id, name, guid, alterid, dsn, status, total_records, last_sync, created_at 
FROM companies 
WHERE guid=? AND CAST(alterid AS TEXT)=?
"""
```

**Step 2**: Review all queries
- Search for `SELECT *` in codebase
- Replace with specific columns
- Test each change

**Expected Impact**:
- Faster queries (less data transfer)
- Better memory usage
- Clearer code intent

**Testing**:
1. Test each query after change
2. Verify same results
3. Measure performance improvement

**Estimated Time**: **1-2 hours**

---

## 📊 Phase 2 Summary

| Task | Priority | Time | Impact |
|------|----------|------|--------|
| Environment Variables | 🟡 High | 1 hr | Security |
| Connection Closing | 🟡 Medium | 2 hrs | Best practices |
| Replace SELECT * | 🟡 Medium | 1-2 hrs | Performance |
| **Total** | | **4-5 hours** | **Medium-High** |

---

## 🎯 Phase 3: Maintenance & Optimization (Week 5-6)

### Priority: **MEDIUM** 🟢
### Timeline: **2 weeks**
### Impact: **Long-term Maintenance**

---

### Task 3.1: Implement Database Vacuuming

**Priority**: 🟢 **MEDIUM**

**Why**: Reduce database file size, improve performance

**Implementation**:

**Step 1**: Create vacuum utility
```python
# File: backend/utils/database_maintenance.py (NEW FILE)
import sqlite3
from backend.config.settings import DB_FILE
from backend.database.connection import get_db_connection

def vacuum_database(db_path=DB_FILE):
    """
    Vacuum database to reclaim space and optimize.
    
    Args:
        db_path: Path to database file
    
    Returns:
        Tuple (success: bool, message: str)
    """
    try:
        with get_db_connection(db_path) as conn:
            cur = conn.cursor()
            
            # Get size before
            cur.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
            size_before = cur.fetchone()[0]
            
            # Vacuum
            cur.execute("VACUUM")
            conn.commit()
            
            # Get size after
            cur.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
            size_after = cur.fetchone()[0]
            
            saved = size_before - size_after
            return True, f"Vacuum completed. Saved {saved:,} bytes"
    except Exception as e:
        return False, f"Vacuum failed: {str(e)}"
```

**Step 2**: Add scheduled vacuum
```python
# File: backend/utils/scheduled_backup.py
# Add to existing file

from backend.utils.database_maintenance import vacuum_database

def run_scheduled_vacuum():
    """Run weekly vacuum on Sunday at 3 AM"""
    try:
        success, message = vacuum_database(DB_FILE)
        print(f"✅ {message}")
    except Exception as e:
        print(f"❌ Vacuum failed: {e}")

# Schedule weekly vacuum
schedule.every().sunday.at("03:00").do(run_scheduled_vacuum)
```

**Step 3**: Add manual vacuum option (optional)
```python
# File: backend/app.py
# Add menu option or button for manual vacuum

def vacuum_database_manual(self):
    """Manual database vacuum."""
    from backend.utils.database_maintenance import vacuum_database
    
    result = messagebox.askyesno(
        "Vacuum Database",
        "This will optimize the database and may take a few minutes.\nContinue?"
    )
    
    if result:
        self.log("🔄 Starting database vacuum...")
        success, message = vacuum_database(DB_FILE)
        if success:
            self.log(f"✅ {message}")
            messagebox.showinfo("Success", message)
        else:
            self.log(f"❌ {message}")
            messagebox.showerror("Error", message)
```

**Expected Impact**:
- Reduced database file size
- Better performance
- Optimized storage

**Testing**:
1. Run vacuum on test database
2. Verify size reduction
3. Test performance improvement

**Estimated Time**: **2 hours**

---

### Task 3.2: Improve Log Cleaning

**Priority**: 🟢 **LOW**

**Why**: Already implemented, but can be automated

**Implementation**:

**Step 1**: Add scheduled log cleaning
```python
# File: backend/utils/scheduled_backup.py
# Add to existing file

from backend.database.connection import get_db_connection
from backend.database.sync_log_dao import SyncLogDAO
from backend.config.settings import LOG_RETENTION_DAYS

def run_scheduled_log_cleaning():
    """Run daily log cleaning at 1 AM"""
    try:
        with get_db_connection() as conn:
            log_dao = SyncLogDAO(conn)
            deleted = log_dao.delete_old_logs(LOG_RETENTION_DAYS)
            print(f"✅ Deleted {deleted} old log entries")
    except Exception as e:
        print(f"❌ Log cleaning failed: {e}")

# Schedule daily log cleaning
schedule.every().day.at("01:00").do(run_scheduled_log_cleaning)
```

**Expected Impact**:
- Automated maintenance
- Consistent log retention
- No manual intervention needed

**Estimated Time**: **1 hour**

---

### Task 3.3: Add Database Health Check

**Priority**: 🟢 **LOW**

**Why**: Proactive monitoring

**Implementation**:
```python
# File: backend/utils/database_maintenance.py
# Add to existing file

def check_database_health(db_path=DB_FILE):
    """
    Check database health and return status.
    
    Returns:
        Dict with health metrics
    """
    try:
        with get_db_connection(db_path) as conn:
            cur = conn.cursor()
            
            # Get database size
            cur.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
            db_size = cur.fetchone()[0]
            
            # Get table counts
            cur.execute("SELECT COUNT(*) FROM companies")
            company_count = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM vouchers")
            voucher_count = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM sync_logs")
            log_count = cur.fetchone()[0]
            
            # Check integrity
            cur.execute("PRAGMA integrity_check")
            integrity = cur.fetchone()[0]
            
            return {
                'status': 'healthy' if integrity == 'ok' else 'unhealthy',
                'size_mb': db_size / (1024 * 1024),
                'company_count': company_count,
                'voucher_count': voucher_count,
                'log_count': log_count,
                'integrity': integrity
            }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }
```

**Expected Impact**:
- Proactive monitoring
- Early problem detection
- Better maintenance

**Estimated Time**: **1-2 hours**

---

## 📊 Phase 3 Summary

| Task | Priority | Time | Impact |
|------|----------|------|--------|
| Database Vacuuming | 🟢 Medium | 2 hrs | Optimization |
| Log Cleaning Automation | 🟢 Low | 1 hr | Maintenance |
| Health Check | 🟢 Low | 1-2 hrs | Monitoring |
| **Total** | | **4-5 hours** | **Medium** |

---

## 📅 Complete Timeline

### Week 1-2: Phase 1 (Critical)
- ✅ Add indexes (vouchers, companies)
- ✅ Implement backups
- ✅ UTC timestamps
- **Total Time**: 3-4 hours

### Week 3-4: Phase 2 (Security)
- ✅ Environment variables
- ✅ Connection closing improvements
- ✅ Replace SELECT *
- **Total Time**: 4-5 hours

### Week 5-6: Phase 3 (Maintenance)
- ✅ Database vacuuming
- ✅ Log cleaning automation
- ✅ Health checks
- **Total Time**: 4-5 hours

**Grand Total**: **11-14 hours** over 6 weeks

---

## 🎯 Success Metrics

### Phase 1
- Dashboard queries: < 2 seconds (currently 10-20 seconds)
- Backup created: Daily automated backups
- Timestamps: All UTC format

### Phase 2
- Configuration: All in .env file
- Connections: All using context managers
- Queries: No SELECT * usage

### Phase 3
- Database size: Reduced by 20-30% after vacuum
- Logs: Automated cleanup
- Health: Regular monitoring

---

## 📝 Notes

1. **Testing**: Each phase should be tested before moving to next
2. **Backup**: Always backup before making changes
3. **Gradual**: Implement one task at a time
4. **Documentation**: Update docs after each phase
5. **Monitoring**: Track performance improvements

---

**Last Updated**: December 2025  
**Next Review**: After Phase 1 completion

