# Build Instructions
## TallyConnect v5.6

## 🚀 Quick Build

### Option 1: Using build.bat (Recommended)
```powershell
# PowerShell में
.\build.bat

# या CMD में
build.bat
```

### Option 2: Direct Build
```powershell
# Main app build
python -m PyInstaller --clean --noconfirm build-config/TallyConnect.spec

# Portal build
python -m PyInstaller --clean --noconfirm build-config/TallyConnectPortal.spec
```

## 📋 Build Process

### Step 1: Check Dependencies
- ✅ Python 3.x installed
- ✅ PyInstaller installed (`pip install pyinstaller`)
- ✅ pyodbc installed (`pip install pyodbc`)

### Step 2: Run Build Script
```bash
build.bat
```

**Build script will:**
1. Check dependencies
2. Clean previous builds
3. Build `TallyConnect.exe`
4. Build `TallyConnectPortal.exe`
5. Optionally create installer

### Step 3: Output Files
After successful build, you'll find:
- `dist/TallyConnect.exe` - Main application
- `dist/TallyConnectPortal.exe` - Portal server
- `dist/TallyConnectSetup_v5.6.exe` - Installer (if created)

## 🧪 Testing After Build

### Test Main Application
```bash
dist\TallyConnect.exe
```

**Expected:**
- GUI window opens
- Portal server starts automatically
- Browser opens to `http://localhost:8000`

### Test Portal UI
1. Open browser to `http://localhost:8000`
2. Navigate through:
   - Companies page
   - Reports page
   - Ledgers page
   - Ledger Report
   - Outstanding Report
   - Dashboard

## ✅ Build Verification Checklist

- [ ] `TallyConnect.exe` created in `dist/`
- [ ] `TallyConnectPortal.exe` created in `dist/`
- [ ] Application starts without errors
- [ ] Portal server starts
- [ ] All HTML pages load
- [ ] All CSS files load
- [ ] All JavaScript files load
- [ ] Navigation works between pages
- [ ] API endpoints respond correctly

## 🔧 Troubleshooting

### Build Fails
- Check Python version: `python --version`
- Check PyInstaller: `pip show pyinstaller`
- Check dependencies: `pip list`

### Portal Not Starting
- Check port 8000 is available
- Check `frontend/portal` folder exists
- Check database exists: `TallyConnectDb.db`

### Files Not Found in EXE
- Verify `TallyConnect.spec` includes:
  - `('frontend', 'frontend')`
  - `('backend', 'backend')`

## 📝 Notes

- Build process takes 2-5 minutes
- EXE files will be large (50-100MB) - this is normal
- First build may take longer
- Subsequent builds are faster


