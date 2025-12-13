# 🏗️ TallyConnect - Project Structure

Complete overview of project organization.

---

## 📁 Directory Tree

```
TallyConnect/
│
├── 📄 C2.py                         # Main application (Tkinter UI + Sync logic)
├── 📄 TallyConnectDb.db            # SQLite database (auto-created)
│
├── 📦 Build & Distribution
│   ├── TallyConnect.spec            # PyInstaller configuration
│   ├── TallyConnectInstaller.iss    # Inno Setup installer script
│   ├── build.bat                    # One-click build script
│   ├── dist/                        # Build output folder
│   │   ├── TallyConnect.exe         # Standalone executable
│   │   └── TallyConnectSetup_v5.6.exe  # Windows installer
│   └── build/                       # Temporary build artifacts
│
├── 🎨 Reports Module (NEW!)
│   ├── reports/
│   │   ├── __init__.py              # Module initialization
│   │   ├── report_generator.py     # Report generation logic
│   │   ├── utils.py                 # Utility functions
│   │   ├── README.md               # Reports documentation
│   │   │
│   │   ├── templates/              # HTML templates
│   │   │   ├── README.md
│   │   │   ├── base.html           # Base template
│   │   │   ├── outstanding.html    # Outstanding report (TODO)
│   │   │   ├── ledger.html         # Ledger report (TODO)
│   │   │   └── dashboard.html      # Dashboard (TODO)
│   │   │
│   │   └── static/                 # Static assets
│   │       ├── css/
│   │       │   ├── main.css        # Base styles
│   │       │   └── reports.css     # Report styles (TODO)
│   │       ├── js/
│   │       │   ├── filters.js      # Search/filter/sort
│   │       │   ├── export.js       # Export utilities
│   │       │   └── charts.js       # Charts (TODO)
│   │       └── img/
│   │           └── logo.png        # Logo (TODO)
│   │
│   └── generated_reports/          # Output folder (auto-created)
│       └── *.html                   # Generated report files
│
├── 💾 Database Module (NEW!)
│   └── database/
│       ├── __init__.py              # Module initialization
│       └── queries.py               # SQL queries for reports
│
├── 📝 Documentation
│   ├── README.md                    # Main project documentation
│   ├── CONTRIBUTING.md              # Contribution guidelines
│   ├── CHANGELOG.md                 # Version history
│   ├── LICENSE.txt                  # Software license
│   ├── GITHUB_SETUP.md             # GitHub setup guide
│   └── PROJECT_STRUCTURE.md        # This file
│
├── 🔧 Configuration
│   ├── requirements.txt             # Python dependencies
│   ├── .gitignore                   # Git ignore rules
│   └── github_push.bat             # GitHub push helper
│
└── 📁 Other Folders
    ├── notes/                       # User notes (auto-created)
    ├── .git/                        # Git repository
    ├── .venv_build/                 # Virtual environment (optional)
    └── __pycache__/                 # Python cache (auto-created)
```

---

## 🎯 Module Responsibilities

### Core Application (`C2.py`)
**Purpose:** Main application with UI and sync logic

**Responsibilities:**
- Tkinter-based user interface
- Tally ODBC connection
- Data synchronization (Tally → SQLite)
- Database management
- Auto-sync functionality
- Theme system (5 themes)
- Company management

**Key Classes:**
- `BizAnalystApp` - Main application class

---

### Reports Module (`reports/`)
**Purpose:** HTML report generation

**Responsibilities:**
- Generate HTML/CSS/JS reports
- Format data for presentation
- Export to PDF/CSV/Excel
- Interactive features (search, filter, sort)

**Key Classes:**
- `ReportGenerator` - Main report generation

**Key Files:**
- `report_generator.py` - Core logic
- `utils.py` - Helper functions
- `templates/*.html` - HTML templates
- `static/css/*.css` - Styling
- `static/js/*.js` - Interactivity

---

### Database Module (`database/`)
**Purpose:** Database query utilities

**Responsibilities:**
- SQL queries for reports
- Query optimization
- Data aggregation

**Key Classes:**
- `ReportQueries` - SQL query collection

---

## 🔄 Data Flow

```
┌─────────────┐
│    Tally    │
│   (ODBC)    │
└──────┬──────┘
       │ 1. Sync
       ↓
┌─────────────┐
│    C2.py    │ ← Main Application
│  (Sync UI)  │
└──────┬──────┘
       │ 2. Store
       ↓
┌─────────────┐
│  SQLite DB  │
│TallyConnect │
│    Db.db    │
└──────┬──────┘
       │ 3. Query
       ↓
┌─────────────┐
│  database/  │ ← SQL Queries
│  queries.py │
└──────┬──────┘
       │ 4. Generate
       ↓
┌─────────────┐
│   reports/  │ ← Report Generation
│report_gen.py│
└──────┬──────┘
       │ 5. Render
       ↓
┌─────────────┐
│HTML/CSS/JS  │ ← Beautiful Reports
│   Reports   │
└─────────────┘
```

---

## 🚀 Development Workflow

### 1. Sync Data (Existing)
```
Tally → C2.py → SQLite
```

### 2. Generate Reports (New!)
```
SQLite → reports/ → HTML
```

### 3. Build Executable
```
PyInstaller → TallyConnect.exe
```

### 4. Create Installer
```
Inno Setup → TallyConnectSetup.exe
```

---

## 📦 Build Process

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Build executable
build.bat
# OR manually:
python -m PyInstaller TallyConnect.spec

# 3. Test executable
dist\TallyConnect.exe

# 4. Create installer (optional)
# Compile TallyConnectInstaller.iss in Inno Setup
```

---

## 🎨 UI Components

### Main Application (C2.py)
1. **Header** - Title, status indicator
2. **Toolbar** - Quick actions (3 buttons)
3. **Views:**
   - Synced Companies
   - Add Company
   - Sync Settings
4. **Footer** - Progress bar, status

### Reports (HTML)
1. **Header** - Logo, company info
2. **Content** - Tables, charts, data
3. **Footer** - Actions (print, export)

---

## 🔧 Configuration Files

### `TallyConnect.spec`
PyInstaller configuration for building EXE
- Entry point: C2.py
- Hidden imports
- Optimization settings

### `TallyConnectInstaller.iss`
Inno Setup configuration for Windows installer
- Installation path: `{localappdata}\Programs\TallyConnect`
- No admin rights required
- Desktop shortcut option

### `requirements.txt`
Python dependencies
- pyodbc (Tally connection)
- pyinstaller (build tool)

### `.gitignore`
Files to exclude from Git
- Database files (*.db)
- Build artifacts (build/, dist/)
- Python cache (__pycache__/)

---

## 📊 Database Schema

### Table: `companies`
```sql
CREATE TABLE companies (
    id INTEGER PRIMARY KEY,
    name TEXT,
    guid TEXT,
    alterid TEXT,
    dsn TEXT,
    status TEXT,
    total_records INTEGER,
    last_sync TEXT,
    created_at TEXT
)
```

### Table: `vouchers`
```sql
CREATE TABLE vouchers (
    id INTEGER PRIMARY KEY,
    company_guid TEXT,
    company_alterid TEXT,
    date TEXT,
    voucher_type TEXT,
    voucher_number TEXT,
    party_name TEXT,
    amount REAL,
    narration TEXT
)
```

---

## 🎯 Next Development Steps

### Phase 1: Complete Reports Module ✅
- [x] Create folder structure
- [x] Setup base files
- [x] Create utility functions
- [ ] Implement outstanding report
- [ ] Implement ledger report
- [ ] Implement dashboard

### Phase 2: Integration
- [ ] Add report button to C2.py UI
- [ ] Connect to database
- [ ] Test with real data

### Phase 3: Enhancement
- [ ] Add Chart.js
- [ ] Excel export
- [ ] Email functionality
- [ ] Custom templates

---

## 📚 Key Technologies

- **Python 3.13** - Core language
- **Tkinter** - GUI framework
- **SQLite3** - Local database
- **PyODBC** - Tally ODBC connection
- **HTML/CSS/JS** - Reports
- **PyInstaller** - EXE builder
- **Inno Setup** - Windows installer

---

## 📞 Getting Help

- **README.md** - Project overview
- **reports/README.md** - Reports module docs
- **GITHUB_SETUP.md** - GitHub instructions
- **CONTRIBUTING.md** - Contribution guidelines

---

**Project Status:** 🟢 Active Development  
**Current Version:** 5.6.0  
**Last Updated:** December 13, 2025

