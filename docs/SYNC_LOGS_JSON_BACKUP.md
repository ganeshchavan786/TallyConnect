# Sync Logs JSON Backup

**Date:** 2025-12-17

---

## 📋 Overview

Sync logs are now saved to both:
1. **Database** (`sync_logs` table) - Primary storage
2. **JSON File** (`sync_logs_backup.jsonl`) - Backup storage

---

## 🔧 Implementation

### JSON Backup Location:
- **File:** `sync_logs_backup.jsonl` (in project root)
- **Format:** JSON Lines (one JSON object per line)
- **Encoding:** UTF-8

### Log Data Structure:
```json
{
  "log_id": 174,
  "company_guid": "8fdcfdd1-71cc-4873-99c6-95735225388e",
  "company_alterid": "102209.0",
  "company_name": "Vrushali Infotech Pvt Ltd. 25-26",
  "log_level": "INFO",
  "log_message": "Sync started for Vrushali Infotech Pvt Ltd. 25-26",
  "log_details": "Starting sync from 01-04-2025 to 31-03-2026",
  "sync_status": "started",
  "records_synced": 0,
  "error_code": null,
  "error_message": null,
  "duration_seconds": null,
  "timestamp": "2025-12-17T15:29:22.123456"
}
```

---

## ✅ Benefits

1. **Backup:** If database commit fails, logs are still saved to JSON
2. **Debugging:** Easy to check what logs were created
3. **Recovery:** Can restore logs from JSON if needed
4. **Analysis:** Can analyze logs using JSON tools

---

## 🔍 How to Check JSON Logs

### View JSON Logs:
```bash
# View last 10 logs
tail -n 10 sync_logs_backup.jsonl

# View all logs
cat sync_logs_backup.jsonl

# Count logs
wc -l sync_logs_backup.jsonl
```

### Parse JSON Logs (Python):
```python
import json

with open("sync_logs_backup.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        log = json.loads(line)
        print(f"ID: {log['log_id']}, Company: {log['company_name']}, Level: {log['log_level']}")
```

---

## 📊 Status

**Current:** ✅ JSON backup enabled

**Next Steps:**
1. Test sync operation
2. Check `sync_logs_backup.jsonl` file
3. Verify logs in database
4. Check UI for logs

---

**Last Updated:** 2025-12-17

