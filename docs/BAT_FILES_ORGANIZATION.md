# BAT Files Organization
## Batch Scripts Location Guide

### 📁 Current Organization

#### **Root Directory** (1 file)
- **`build.bat`** - Main build script
  - **Purpose:** Builds both TallyConnect.exe and TallyConnectPortal.exe
  - **Location:** Root (for easy access)
  - **Usage:** `build.bat` from project root

#### **build-config/** (1 file)
- **`REBUILD_PORTAL_EXE.bat`** - Quick portal rebuild script
  - **Purpose:** Rebuilds only TallyConnectPortal.exe
  - **Location:** `build-config/` (build-related)
  - **Usage:** `build-config\REBUILD_PORTAL_EXE.bat` from project root
  - **Note:** Script automatically changes to project root before building

#### **scripts/** (1 file)
- **`START_PORTAL.bat`** - Portal launcher script
  - **Purpose:** Starts portal server for development
  - **Location:** `scripts/` (utility script)
  - **Usage:** `scripts\START_PORTAL.bat` from project root
  - **Note:** Script automatically changes to project root before running

### 🚀 Usage

#### Build Application
```bash
# From project root
build.bat
```

#### Rebuild Portal Only
```bash
# From project root
build-config\REBUILD_PORTAL_EXE.bat
```

#### Start Portal (Development)
```bash
# From project root
scripts\START_PORTAL.bat
```

### 📋 Organization Rationale

1. **`build.bat` in root** - Most frequently used, easy access
2. **`REBUILD_PORTAL_EXE.bat` in build-config/** - Build-related, grouped with other build configs
3. **`START_PORTAL.bat` in scripts/** - Utility script, grouped with other utilities

### ✅ Benefits

- **Clean root directory** - Only essential `build.bat` visible
- **Logical grouping** - Related files in appropriate folders
- **Easy navigation** - Clear organization
- **Auto path handling** - Scripts handle directory changes automatically

---

**Last Updated:** December 2025

