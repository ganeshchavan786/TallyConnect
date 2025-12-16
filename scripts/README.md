# Utility Scripts
## Development & Testing Scripts

This folder contains utility and test scripts for development and debugging purposes.

### 📋 Scripts

#### Database Utilities
- **`check_companies.py`** - Check synced companies in database
  - Usage: `python scripts/check_companies.py`
  - Shows all companies, their status, and record counts

#### Test Scripts
- **`test_database.py`** - Test database connection and queries
  - Usage: `python scripts/test_database.py`
  - Tests database operations and ledger data retrieval

- **`test_portal_report.py`** - Test portal report generation
  - Usage: `python scripts/test_portal_report.py`
  - Simulates portal server report generation

- **`test_reports.py`** - Test all report types
  - Usage: `python scripts/test_reports.py`
  - Tests outstanding, ledger, and dashboard reports

### ⚠️ Note

These scripts are for **development and debugging only**. They are not part of the main application and are not included in EXE builds.

### 🚀 Usage

All scripts should be run from the **project root** directory:

```bash
# Check companies
python scripts/check_companies.py

# Test database
python scripts/test_database.py

# Test portal reports
python scripts/test_portal_report.py

# Test all reports
python scripts/test_reports.py
```

### 📝 Requirements

- Python 3.8+
- Database file: `TallyConnectDb.db` in project root
- All dependencies from `requirements.txt`

---

**Note:** These scripts may need path updates if project structure changes.

