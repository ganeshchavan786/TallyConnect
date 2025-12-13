# 🚀 TallyConnect - Build & Distribution Guide

Complete guide to build EXE and distribute your application.

---

## 📋 Prerequisites

### Required Software:
1. **Python 3.13** (or 3.11+) - [Download](https://www.python.org/downloads/)
2. **PyInstaller** - Will be installed automatically
3. **Inno Setup** (for Windows installer) - [Download](https://jrsoftware.org/isdl.php)

### Check Installation:
```bash
python --version
# Should show: Python 3.13.x

pip list | findstr pyinstaller
# Should show: pyinstaller
```

---

## 🔨 Method 1: Quick Build (Recommended)

### Step 1: Run Build Script
```bash
# Open PowerShell/CMD in project folder
cd "D:\Project\Katara Dental\TDL\Pramit\Tally Ledger Report"

# Run build script
build.bat
```

### Step 2: Check Output
After build completes, check:
```
dist/
└── TallyConnect.exe  ← Your executable!
```

### Step 3: Test EXE
```bash
# Run the executable
dist\TallyConnect.exe
```

---

## 🛠️ Method 2: Manual Build

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Build with PyInstaller
```bash
python -m PyInstaller TallyConnect.spec
```

### Step 3: Verify Build
```
dist/
└── TallyConnect.exe
```

---

## 📦 Create Windows Installer (Optional but Recommended)

### Step 1: Install Inno Setup
1. Download from: https://jrsoftware.org/isdl.php
2. Install with default settings

### Step 2: Compile Installer
1. Open **Inno Setup Compiler**
2. File → Open → Select `TallyConnectInstaller.iss`
3. Build → Compile (or press F9)
4. Wait for compilation

### Step 3: Find Installer
```
Output/
└── TallyConnectSetup_v5.6.exe  ← Your installer!
```

---

## 📁 Build Output Structure

```
Project Root/
├── build/                    # Temporary build files (can delete)
├── dist/                     # Final executable
│   └── TallyConnect.exe
└── Output/                   # Installer (if created)
    └── TallyConnectSetup_v5.6.exe
```

---

## ✅ Testing Checklist

Before distributing, test:

### 1. Basic Functionality
- [ ] Application starts without errors
- [ ] UI displays correctly
- [ ] Database connection works
- [ ] Company sync works

### 2. Reports
- [ ] Outstanding Report generates
- [ ] Ledger Report generates
- [ ] Dashboard generates
- [ ] Reports open in browser
- [ ] Export CSV works
- [ ] Print works

### 3. File Structure
- [ ] All required files included
- [ ] Reports templates included
- [ ] CSS/JS files included
- [ ] Database created on first run

---

## 📤 Distribution Methods

### Option 1: Direct EXE Distribution
**Best for:** Internal use, single user

1. Copy `TallyConnect.exe` to USB/Network
2. User runs directly (no installation needed)
3. Database created in same folder as EXE

**Pros:**
- ✅ No installation required
- ✅ Portable
- ✅ Quick distribution

**Cons:**
- ❌ No Start Menu shortcut
- ❌ No uninstaller
- ❌ Database in same folder

---

### Option 2: Installer Distribution (Recommended)
**Best for:** Multiple users, professional distribution

1. Share `TallyConnectSetup_v5.6.exe`
2. User runs installer
3. Application installed in: `C:\Users\Username\AppData\Local\Programs\TallyConnect`
4. Database created in: `C:\Users\Username\AppData\Local\Programs\TallyConnect\`

**Pros:**
- ✅ Professional installation
- ✅ Start Menu shortcut
- ✅ Uninstaller included
- ✅ Per-user installation (no admin needed)

**Cons:**
- ❌ Requires Inno Setup
- ❌ Slightly larger file

---

## 🎯 Distribution Checklist

### Before Sharing:
- [ ] Test EXE on clean Windows machine
- [ ] Verify all features work
- [ ] Check file size (should be ~50-100 MB)
- [ ] Create README with instructions
- [ ] Include license file (if needed)

### Files to Include:
```
Distribution Package/
├── TallyConnect.exe (or Setup.exe)
├── README.txt (instructions)
├── LICENSE.txt
└── CHANGELOG.md (optional)
```

---

## 📝 README.txt Template

Create a simple README.txt for users:

```
TallyConnect v5.6
=================

Modern Tally Sync Platform with Professional Reports

INSTALLATION:
-------------
1. Run TallyConnectSetup_v5.6.exe
2. Follow installation wizard
3. Launch from Start Menu

OR

1. Extract TallyConnect.exe
2. Run TallyConnect.exe directly

REQUIREMENTS:
-------------
- Windows 10/11
- Tally ODBC Driver installed
- Internet connection (for reports)

FEATURES:
---------
- Multi-company synchronization
- Outstanding Reports
- Ledger Reports
- Dashboard with Charts
- Auto-sync functionality
- Professional themes

SUPPORT:
--------
GitHub: https://github.com/ganeshchavan786/TallyConnect
Issues: https://github.com/ganeshchavan786/TallyConnect/issues

© 2025 Katara Dental
```

---

## 🔧 Troubleshooting Build Issues

### Issue 1: PyInstaller not found
```bash
# Solution:
pip install pyinstaller
python -m PyInstaller TallyConnect.spec
```

### Issue 2: Missing modules
```bash
# Check TallyConnect.spec file
# Add missing modules to hiddenimports
```

### Issue 3: Reports not working in EXE
```bash
# Check TallyConnect.spec includes:
datas=[('reports', 'reports')]
```

### Issue 4: Database path issues
```bash
# EXE uses relative path
# Database created in same folder as EXE
# This is correct behavior
```

---

## 📊 Build Configuration

### TallyConnect.spec Key Settings:

```python
# Entry point
a = Analysis(['C2.py'])

# Hidden imports (if needed)
hiddenimports=['reports', 'database']

# Data files (reports folder)
datas=[('reports', 'reports')]

# Output name
name='TallyConnect'

# One-file mode
exe = EXE(pyz, a.scripts, a.binaries, ...,
          name='TallyConnect',
          onefile=True)
```

---

## 🎨 Customization Before Build

### 1. Update Version
Edit `C2.py`:
```python
# Find version string
VERSION = "5.6.0"
```

### 2. Update Installer Info
Edit `TallyConnectInstaller.iss`:
```ini
AppVersion=5.6.0
OutputBaseFilename=TallyConnectSetup_v5.6
```

### 3. Add Icon (Optional)
```python
# In TallyConnect.spec
icon='icon.ico'  # Add your icon file
```

---

## 🚀 Quick Build Commands

### Full Build (EXE + Installer):
```bash
# 1. Build EXE
build.bat

# 2. Create installer (in Inno Setup)
# Open TallyConnectInstaller.iss → Compile
```

### Clean Build:
```bash
# Delete old builds
rmdir /s /q build dist

# Rebuild
build.bat
```

---

## 📦 Distribution Sizes

Typical file sizes:
- **TallyConnect.exe**: ~50-80 MB
- **TallyConnectSetup.exe**: ~50-85 MB

---

## ✅ Final Checklist

Before distributing:
- [ ] EXE tested on clean machine
- [ ] All features working
- [ ] Reports generating correctly
- [ ] Database created properly
- [ ] No error messages
- [ ] README included
- [ ] Version number correct
- [ ] Installer tested (if using)

---

## 🎯 Distribution Channels

### Internal Distribution:
- Network share
- USB drive
- Email (if size allows)
- Cloud storage (Google Drive, OneDrive)

### External Distribution:
- GitHub Releases
- Website download
- Cloud storage link

---

## 📞 Support

If users face issues:
1. Check Windows version (10/11)
2. Verify ODBC driver installed
3. Check database file permissions
4. Review error logs

---

## 🎉 Success!

Once built and tested, your TallyConnect application is ready for distribution!

**Next Steps:**
1. Test on multiple machines
2. Gather user feedback
3. Create user documentation
4. Set up support channel

---

**Happy Distributing! 🚀**

