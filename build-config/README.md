# Build Configuration
## EXE Build & Packaging Files

This folder contains all files required for building TallyConnect executables and installers.

### 📦 Files in this Folder

#### PyInstaller Specification Files
- **`TallyConnect.spec`** - Main application EXE build configuration
  - Entry point: `backend/app.py`
  - Includes: `frontend/`, `backend/` folders
  - Output: `dist/TallyConnect.exe`

- **`TallyConnectPortal.spec`** - Portal server EXE build configuration
  - Entry point: `backend/portal_launcher.py`
  - Includes: `frontend/`, `backend/` folders
  - Output: `dist/TallyConnectPortal.exe`

#### Build Scripts
- **`build.bat`** - Main build script
  - Builds both TallyConnect.exe and TallyConnectPortal.exe
  - Optionally creates installer using Inno Setup
  - Usage: Run `build.bat` from project root

- **`REBUILD_PORTAL_EXE.bat`** - Quick rebuild script for portal EXE only
  - Kills running portal EXE if needed
  - Rebuilds TallyConnectPortal.exe
  - Usage: Run `REBUILD_PORTAL_EXE.bat` from project root

#### Installer Configuration
- **`TallyConnectInstaller.iss`** - Inno Setup installer script
  - Creates Windows installer (TallyConnectSetup_v5.6.exe)
  - Includes both EXEs, desktop shortcuts, startup configuration
  - Requires Inno Setup 6 to compile

### 🚀 Building EXEs

#### Quick Build (Recommended)
```bash
# From project root
build.bat
```

#### Manual Build
```bash
# Build main application
pyinstaller build-config/TallyConnect.spec

# Build portal server
pyinstaller build-config/TallyConnectPortal.spec
```

#### Rebuild Portal Only
```bash
# From project root
build-config/REBUILD_PORTAL_EXE.bat
```

### 📋 Build Requirements

1. **Python 3.8+** with PyInstaller
   ```bash
   pip install pyinstaller
   ```

2. **Inno Setup 6** (for installer creation)
   - Download from: https://jrsoftware.org/isinfo.php
   - Default location: `C:\Program Files (x86)\Inno Setup 6\`

3. **Dependencies**
   - pyodbc (for Tally connection)
   - pystray, Pillow (for system tray)
   - All listed in `requirements.txt`

### 📁 Build Output

All built files are created in the `dist/` folder:
- `dist/TallyConnect.exe` - Main application
- `dist/TallyConnectPortal.exe` - Portal server
- `dist/TallyConnectSetup_v5.6.exe` - Windows installer

### ⚙️ Configuration Details

#### TallyConnect.spec
- **Entry Point:** `backend/app.py`
- **Data Files:** `frontend/`, `backend/`
- **Hidden Imports:** `backend.*`, `backend.config.*`, `backend.database.*`
- **Console:** No (windowed application)

#### TallyConnectPortal.spec
- **Entry Point:** `backend/portal_launcher.py`
- **Data Files:** `frontend/`, `backend/`
- **Hidden Imports:** `backend.*`, `backend.config.*`, `backend.database.*`
- **Console:** Yes (for debugging)

### 🔧 Customization

To modify build settings:
1. Edit the respective `.spec` file
2. Run build script again
3. Test the new EXE

**Note:** Always test EXEs after building to ensure all dependencies are included.

---

**Last Updated:** December 2025  
**Maintained by:** Vrushali Infotech Pvt Ltd, Pune, Maharashtra

