"""
Scheduled Maintenance Utilities
================================

Handles scheduled maintenance tasks for TallyConnect.
Part of Phase 3: Maintenance & Optimization implementation.

Includes:
- Scheduled database vacuuming
- Scheduled log cleaning
- Maintenance task scheduling
"""

import schedule
import time
import threading
from datetime import datetime
from backend.config.settings import DB_FILE, LOG_RETENTION_DAYS
from backend.utils.database_maintenance import vacuum_database, check_database_health
from backend.database.connection import get_db_connection_with_context
from backend.database.sync_log_dao import SyncLogDAO


def run_scheduled_vacuum():
    """
    Run scheduled database vacuum.
    Executes weekly on Sunday at 3 AM.
    """
    try:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔄 Starting scheduled database vacuum...")
        success, message = vacuum_database(DB_FILE)
        if success:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ {message}")
        else:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ {message}")
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Vacuum failed: {e}")


def run_scheduled_log_cleaning():
    """
    Run scheduled log cleaning.
    Executes daily at 1 AM.
    """
    try:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🧹 Starting scheduled log cleaning...")
        
        with get_db_connection_with_context(DB_FILE) as conn:
            log_dao = SyncLogDAO(conn)
            deleted = log_dao.delete_old_logs(LOG_RETENTION_DAYS)
            
            if deleted > 0:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ Deleted {deleted} old log entries (older than {LOG_RETENTION_DAYS} days)")
            else:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ℹ️ No old logs to clean")
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Log cleaning failed: {e}")


def run_health_check():
    """
    Run database health check.
    Executes daily at 4 AM.
    """
    try:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🏥 Running database health check...")
        
        health = check_database_health(DB_FILE)
        
        if health['status'] == 'healthy':
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ Database health: {health['status']}")
            print(f"   Size: {health['size_mb']:.2f} MB")
            print(f"   Companies: {health['company_count']}")
            print(f"   Vouchers: {health['voucher_count']}")
            print(f"   Logs: {health['log_count']}")
        else:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚠️ Database health: {health['status']}")
            if health['errors']:
                for error in health['errors']:
                    print(f"   Error: {error}")
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Health check failed: {e}")


def setup_scheduled_maintenance():
    """
    Setup scheduled maintenance tasks.
    
    Schedule:
    - Log Cleaning: Daily at 1 AM
    - Vacuum: Weekly on Sunday at 3 AM
    - Health Check: Daily at 4 AM
    """
    # Schedule log cleaning (daily at 1 AM)
    schedule.every().day.at("01:00").do(run_scheduled_log_cleaning)
    
    # Schedule vacuum (weekly on Sunday at 3 AM)
    schedule.every().sunday.at("03:00").do(run_scheduled_vacuum)
    
    # Schedule health check (daily at 4 AM)
    schedule.every().day.at("04:00").do(run_health_check)
    
    print("✅ Scheduled maintenance tasks configured:")
    print("   - Log Cleaning: Daily at 1:00 AM")
    print("   - Database Vacuum: Weekly on Sunday at 3:00 AM")
    print("   - Health Check: Daily at 4:00 AM")


def start_maintenance_scheduler():
    """
    Start maintenance scheduler in background thread.
    """
    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    thread = threading.Thread(target=run_scheduler, daemon=True, name="MaintenanceScheduler")
    thread.start()
    print("✅ Maintenance scheduler started in background thread")
    return thread


def run_maintenance_now(task: str = "all"):
    """
    Run maintenance tasks immediately (for testing or manual execution).
    
    Args:
        task: Task to run ('vacuum', 'log_cleaning', 'health_check', or 'all')
    """
    if task == "all" or task == "vacuum":
        print("🔄 Running vacuum now...")
        run_scheduled_vacuum()
    
    if task == "all" or task == "log_cleaning":
        print("🧹 Running log cleaning now...")
        run_scheduled_log_cleaning()
    
    if task == "all" or task == "health_check":
        print("🏥 Running health check now...")
        run_health_check()

