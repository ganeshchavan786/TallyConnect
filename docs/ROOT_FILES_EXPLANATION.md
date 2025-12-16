# Root Directory Files Explanation
## Why Certain Files Stay in Root

### ✅ Files That Should Stay in Root

#### 1. **`build.bat`** (Wrapper Script)
**Why it stays in root:**
- ✅ **Easy Access** - Users can run `build.bat` directly from project root
- ✅ **Standard Practice** - Build scripts are commonly in root for quick access
- ✅ **Wrapper Pattern** - It's a simple wrapper that calls the main script in `build-config/`
- ✅ **User Convenience** - No need to navigate to subfolders

**Location:** Root directory  
**Purpose:** Wrapper that calls `build-config/build.bat`

#### 2. **`TallyConnectDb.db`** (Database File)
**Why it stays in root:**
- ✅ **Application Expectation** - Code looks for it in root/base directory
- ✅ **Relative Path** - `DB_FILE = "TallyConnectDb.db"` in `config/settings.py`
- ✅ **EXE Compatibility** - When running as EXE, database is in EXE directory (root)
- ✅ **Data File** - It's runtime data, not source code
- ✅ **Standard Practice** - Database files are typically at project root

**Location:** Root directory  
**Purpose:** SQLite database file used by the application

**Code References:**
- `backend/config/settings.py`: `DB_FILE = "TallyConnectDb.db"` (relative path)
- `backend/portal_server.py`: `DB_FILE = os.path.join(get_base_dir(), "TallyConnectDb.db")`
- `backend/app.py`: Uses `DB_FILE` from config

### 📁 Current Root Structure

```
Project Root/
├── build.bat              ← Wrapper (stays in root)
├── main.py                ← Entry point (stays in root)
├── requirements.txt       ← Dependencies (stays in root)
├── LICENSE.txt            ← License (stays in root)
├── TallyConnectDb.db      ← Database (stays in root)
└── [folders]
    ├── backend/
    ├── frontend/
    ├── build-config/
    ├── scripts/
    ├── docs/
    └── tests/
```

### 🎯 Organization Rationale

**Root Level Files:**
- Essential files needed to run/build the project
- Files that users interact with directly
- Configuration/data files expected at root

**Organized Folders:**
- Source code → `backend/`
- Web assets → `frontend/`
- Build configs → `build-config/`
- Utilities → `scripts/`
- Documentation → `docs/`
- Tests → `tests/`

### ✅ Benefits

1. **Clean Root** - Only essential files visible
2. **Easy Access** - Important files easily accessible
3. **Standard Structure** - Follows common project organization patterns
4. **Application Compatibility** - Database location matches code expectations

---

**Conclusion:** Both `build.bat` and `TallyConnectDb.db` should **stay in root** for the reasons above.

**Last Updated:** December 2025

