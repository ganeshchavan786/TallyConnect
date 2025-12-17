# TallyConnect - Coding Standards & Best Practices

## 📋 Overview

या project मध्ये professional coding standards follow केले आहेत जे maintainability, scalability, आणि code quality साठी important आहेत.

---

## 🏗️ Architecture Patterns

### 1. **Layered Architecture (3-Tier)**

```
┌─────────────────────────────────────┐
│   Presentation Layer (UI)           │
│   - Tkinter GUI (app.py)            │
│   - Portal HTML/JS (frontend/)      │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│   Business Logic Layer              │
│   - Services (services/)            │
│   - DAO (database/)                 │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│   Data Access Layer                 │
│   - SQLite Database                 │
│   - Tally ODBC                      │
└─────────────────────────────────────┘
```

**Benefits:**
- Clear separation of concerns
- Easy to test each layer
- Easy to modify without affecting other layers

---

## 📁 Project Structure Standards

### **Directory Organization**

```
TallyConnect/
├── backend/                    # Python Backend Code
│   ├── config/                 # Configuration
│   ├── database/               # Database Layer (DAO Pattern)
│   ├── services/               # Business Logic
│   ├── utils/                  # Utilities
│   └── ui/                     # UI Components
│
├── frontend/                   # Frontend Code
│   ├── portal/                 # Portal HTML Pages
│   └── assets/                 # CSS, JS, Images
│
├── docs/                       # Documentation
├── tests/                      # Unit Tests
└── scripts/                    # Build Scripts
```

**Standards:**
- ✅ Backend/Frontend separation
- ✅ Feature-based organization
- ✅ Clear naming conventions
- ✅ Modular structure

---

## 🎯 Design Patterns Used

### 1. **DAO (Data Access Object) Pattern**

**Example:** `backend/database/company_dao.py`

```python
class CompanyDAO:
    """Data Access Object for Company operations."""
    
    def __init__(self, db_conn: sqlite3.Connection, db_lock=None):
        self.db_conn = db_conn
        self.db_lock = db_lock
    
    def get_by_guid_alterid(self, guid: str, alterid: str):
        """Get company by GUID and AlterID."""
        query = "SELECT * FROM companies WHERE guid=? AND alterid=?"
        cur = self._execute(query, (guid, alterid))
        return cur.fetchone()
```

**Benefits:**
- Database operations encapsulated
- Easy to test
- Reusable across modules

### 2. **Singleton Pattern**

**Example:** Database connection

```python
def init_db(db_path=DB_FILE):
    """Initialize SQLite database (singleton)."""
    conn = sqlite3.connect(db_path, check_same_thread=False)
    # ... initialization
    return conn
```

### 3. **Factory Pattern**

**Example:** Logger factory

```python
def get_sync_logger(db_path: str = None, db_lock=None):
    """Factory function to create SyncLogger instance."""
    return SyncLogger(db_path, db_lock)
```

### 4. **Observer Pattern**

**Example:** Progress updates

```python
def _update_progress(self, percent):
    """Update progress bar (observer pattern)."""
    self.progress_var.set(percent)
    self.progress_bar.update()
```

---

## 📝 Code Style Standards

### 1. **Naming Conventions**

#### **Python (PEP 8)**

```python
# Classes: PascalCase
class CompanyDAO:
    pass

# Functions/Methods: snake_case
def get_by_guid_alterid(self, guid, alterid):
    pass

# Constants: UPPER_SNAKE_CASE
DB_FILE = "TallyConnectDb.db"
BATCH_SIZE = 100

# Private methods: _prefix
def _execute(self, query):
    pass

# Variables: snake_case
company_name = "Vrushali Infotech"
total_records = 1000
```

#### **JavaScript (CamelCase)**

```javascript
// Classes: PascalCase
class ReportService {
    constructor() {}
}

// Functions: camelCase
function loadDashboardData() {}

// Variables: camelCase
let companyName = "Vrushali Infotech";
const totalRecords = 1000;
```

### 2. **File Organization**

#### **Python Files**

```python
#!/usr/bin/env python3
"""
Module Docstring
================
Brief description of the module.
"""

# Standard library imports
import os
import sys
from datetime import datetime

# Third-party imports
import sqlite3
import pyodbc

# Local imports
from backend.config import DB_FILE
from backend.database.company_dao import CompanyDAO

# Constants
DEFAULT_TIMEOUT = 30

# Classes
class MyClass:
    """Class docstring."""
    pass

# Functions
def my_function():
    """Function docstring."""
    pass

# Main execution
if __name__ == "__main__":
    main()
```

### 3. **Documentation Standards**

#### **Docstrings (Google Style)**

```python
def update_sync_complete(self, guid: str, alterid: str, total_records: int, 
                        company_name: str = None, logger=None) -> bool:
    """
    Update company after sync completion.
    If company doesn't exist, insert it.
    
    Args:
        guid: Company GUID
        alterid: Company AlterID
        total_records: Total number of records synced
        company_name: Company name (optional, used if company doesn't exist)
        logger: Optional SyncLogger instance for logging
        
    Returns:
        True if successful
        
    Raises:
        Exception: If database operation fails
    """
    pass
```

### 4. **Error Handling**

#### **Try-Except Blocks**

```python
try:
    # Main operation
    result = risky_operation()
except SpecificException as e:
    # Handle specific error
    logger.error(f"Specific error: {e}")
    raise
except Exception as e:
    # Handle general error
    logger.error(f"Unexpected error: {e}")
    # Fallback or re-raise
finally:
    # Cleanup
    cleanup_resources()
```

#### **Non-Blocking Error Handling**

```python
# Logger calls should not block main operations
if sync_logger:
    try:
        sync_logger.info(guid, alterid, name, "Sync started")
    except Exception as log_err:
        print(f"[WARNING] Failed to log: {log_err}")
        # Continue execution - don't fail sync due to logging error
```

### 5. **Thread Safety**

#### **Lock Usage**

```python
# Use locks for thread-safe database operations
with self.db_lock:
    db_cur = self.db_conn.cursor()
    db_cur.execute(query, params)
    self.db_conn.commit()
```

#### **Threading Pattern**

```python
# Use daemon threads for background tasks
t = threading.Thread(
    target=self._sync_worker, 
    args=(name, guid, alterid, dsn, from_date, to_date, lock), 
    daemon=True
)
t.start()
```

---

## 🔒 Security Standards

### 1. **SQL Injection Prevention**

```python
# ✅ CORRECT: Parameterized queries
query = "SELECT * FROM companies WHERE guid=? AND alterid=?"
cur.execute(query, (guid, alterid))

# ❌ WRONG: String concatenation
query = f"SELECT * FROM companies WHERE guid='{guid}'"  # Vulnerable!
```

### 2. **Input Validation**

```python
def validate_date(date_str: str) -> bool:
    """Validate date format."""
    try:
        datetime.strptime(date_str, "%d-%m-%Y")
        return True
    except ValueError:
        return False
```

### 3. **Error Message Sanitization**

```python
# Don't expose internal errors to users
try:
    operation()
except Exception as e:
    # Log full error internally
    logger.error(f"Internal error: {e}")
    # Show user-friendly message
    messagebox.showerror("Error", "Operation failed. Please try again.")
```

---

## 🧪 Testing Standards

### 1. **Unit Test Structure**

```python
import unittest
from backend.database.company_dao import CompanyDAO

class TestCompanyDAO(unittest.TestCase):
    """Test cases for CompanyDAO."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.conn = sqlite3.connect(":memory:")
        self.dao = CompanyDAO(self.conn)
    
    def test_get_by_guid_alterid(self):
        """Test getting company by GUID and AlterID."""
        # Arrange
        # Act
        # Assert
        pass
    
    def tearDown(self):
        """Clean up after tests."""
        self.conn.close()
```

### 2. **Test Naming**

- Test methods: `test_<functionality>`
- Descriptive names
- One assertion per test (when possible)

---

## 📊 Database Standards

### 1. **Schema Design**

```sql
-- Table naming: plural, lowercase, snake_case
CREATE TABLE IF NOT EXISTS companies (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  guid TEXT NOT NULL,
  alterid TEXT NOT NULL,
  status TEXT DEFAULT 'new',
  total_records INTEGER DEFAULT 0,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(guid, alterid)  -- Composite unique constraint
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_companies_guid_alterid 
ON companies(guid, alterid);
```

### 2. **Query Standards**

```python
# Use parameterized queries
query = """
SELECT name, guid, alterid, status, total_records 
FROM companies 
WHERE status = ? 
ORDER BY name ASC
"""
cur.execute(query, ('synced',))

# Use transactions for multiple operations
with self.db_lock:
    cur = self.db_conn.cursor()
    cur.execute("BEGIN TRANSACTION")
    try:
        cur.execute(query1, params1)
        cur.execute(query2, params2)
        self.db_conn.commit()
    except:
        self.db_conn.rollback()
        raise
```

---

## 🎨 Frontend Standards

### 1. **JavaScript Organization**

```javascript
// Module pattern
class ReportService {
    constructor() {
        this.baseUrl = '/api';
    }
    
    async loadData(params) {
        try {
            const response = await fetch(`${this.baseUrl}/data`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(params)
            });
            return await response.json();
        } catch (error) {
            console.error('Error loading data:', error);
            throw error;
        }
    }
}
```

### 2. **CSS Organization**

```css
/* BEM (Block Element Modifier) naming */
.company-card { }
.company-card__title { }
.company-card__status { }
.company-card--synced { }
.company-card--failed { }
```

### 3. **HTML Structure**

```html
<!-- Semantic HTML -->
<section class="company-list">
    <header class="company-list__header">
        <h2>Select Company</h2>
    </header>
    <div class="company-list__content">
        <!-- Company cards -->
    </div>
</section>
```

---

## 🔄 Code Quality Standards

### 1. **DRY (Don't Repeat Yourself)**

```python
# ❌ BAD: Repeated code
def sync_company_1():
    conn = pyodbc.connect("DSN=TallyODBC64_9000")
    # ... sync logic

def sync_company_2():
    conn = pyodbc.connect("DSN=TallyODBC64_9000")
    # ... same sync logic

# ✅ GOOD: Reusable function
def sync_company(company_name, guid, alterid, dsn):
    conn = pyodbc.connect(f"DSN={dsn}")
    # ... sync logic
```

### 2. **Single Responsibility Principle**

```python
# Each class/function should do one thing
class CompanyDAO:
    """Only handles company database operations."""
    pass

class SyncLogger:
    """Only handles sync logging."""
    pass
```

### 3. **Open/Closed Principle**

```python
# Open for extension, closed for modification
class BaseReport:
    def generate(self):
        raise NotImplementedError

class SalesReport(BaseReport):
    def generate(self):
        # Implementation
        pass
```

---

## 📦 Module Organization

### 1. **Import Organization**

```python
# 1. Standard library
import os
import sys
from datetime import datetime

# 2. Third-party
import sqlite3
import pyodbc

# 3. Local imports
from backend.config import DB_FILE
from backend.database.company_dao import CompanyDAO
```

### 2. **Circular Import Prevention**

```python
# Use type hints with string literals
from __future__ import annotations

def process_company(dao: 'CompanyDAO'):
    pass
```

---

## 🚀 Performance Standards

### 1. **Database Optimization**

```python
# Use PRAGMA for performance
db_cur.execute("PRAGMA synchronous = NORMAL")
db_cur.execute("PRAGMA temp_store = MEMORY")
db_cur.execute("PRAGMA cache_size = 10000")

# Use batch inserts
db_cur.executemany(query, params_list)  # Faster than loop
```

### 2. **Query Optimization**

```python
# Use indexes
CREATE INDEX idx_vouchers_company ON vouchers(company_guid, company_alterid);

# Use LIMIT for large datasets
SELECT * FROM vouchers WHERE company_guid = ? LIMIT 100;
```

### 3. **UI Responsiveness**

```python
# Use threading for long operations
t = threading.Thread(target=long_operation, daemon=True)
t.start()

# Update UI in main thread
self.root.after(0, lambda: self.update_ui())
```

---

## 📋 Code Review Checklist

### **Before Committing:**

- [ ] Code follows PEP 8 (Python) / ESLint (JavaScript)
- [ ] All functions have docstrings
- [ ] Error handling is proper
- [ ] No hardcoded values (use constants)
- [ ] Thread safety considered
- [ ] SQL injection prevention
- [ ] Logging added for important operations
- [ ] Comments for complex logic
- [ ] No unused imports/variables
- [ ] Tests pass (if applicable)

---

## 🎯 Best Practices Summary

### **DO:**
✅ Use type hints
✅ Write docstrings
✅ Handle errors gracefully
✅ Use parameterized queries
✅ Follow naming conventions
✅ Keep functions small (< 50 lines)
✅ Use meaningful variable names
✅ Add comments for complex logic
✅ Use constants for magic numbers
✅ Test your code

### **DON'T:**
❌ Use global variables
❌ Ignore exceptions
❌ Use string concatenation for SQL
❌ Write functions > 100 lines
❌ Use magic numbers
❌ Commit commented-out code
❌ Use `print()` for logging (use logger)
❌ Hardcode paths (use config)
❌ Mix business logic with UI
❌ Skip error handling

---

## 📚 References

- **PEP 8**: Python Style Guide
- **Google Python Style Guide**: Docstring format
- **JavaScript ES6+**: Modern JS standards
- **SQLite Best Practices**: Database optimization
- **Threading Best Practices**: Concurrency patterns

---

## 🔄 Continuous Improvement

Coding standards evolve with the project. Regular reviews ensure:
- Consistency across codebase
- Better maintainability
- Easier onboarding for new developers
- Higher code quality

**Last Updated:** 2025-12-16

