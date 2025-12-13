# 👨‍💻 TallyConnect - Developer Guide

## 🚀 **Quick Start for Developers**

---

## 📋 **Prerequisites:**

### **1. Python 3.x**
```bash
python --version
# Should show Python 3.7 or higher
```

### **2. Required Packages:**
```bash
pip install pyodbc pyinstaller
```

### **3. Tally ODBC Driver**
- Install Tally ODBC 64-bit driver
- Configure DSN if needed

---

## 🔧 **Step-by-Step Setup:**

### **Step 1: Clone/Download Project**
```bash
cd "D:\Project\Katara Dental\TDL\Pramit\Tally Ledger Report"
```

### **Step 2: Install Dependencies**
```bash
pip install -r requirements.txt
```

### **Step 3: Database Setup**
- Database auto-creates on first run
- Or copy existing `TallyConnectDb.db` to project root

---

## 🏃 **Running as Developer:**

### **Option A: Main Application (TallyConnect.exe)**

#### **Method 1: Run Python Script**
```bash
python C2.py
```

**What it does:**
- Opens Tkinter GUI
- Connects to Tally via ODBC
- Syncs data to SQLite database
- Manages companies

#### **Method 2: Build & Run EXE**
```bash
# Build EXE
build.bat
# Or just build main app:
python -m PyInstaller TallyConnect.spec

# Run EXE
dist\TallyConnect.exe
```

---

### **Option B: Portal Server**

#### **Method 1: Run Python Script (Recommended for Development)**
```bash
python portal_server.py
```

**What it does:**
- Starts HTTP server on `localhost:8000`
- Opens browser automatically
- Serves portal interface
- Generates reports on-demand

#### **Method 2: Use Batch Script (Easiest)**
```bash
START_PORTAL.bat
```

**Double-click करा** → Portal starts automatically!

#### **Method 3: Build & Run EXE**
```bash
# Build Portal EXE
python -m PyInstaller TallyConnectPortal.spec

# Run EXE
dist\TallyConnectPortal.exe
```

---

## 🎯 **Complete Development Workflow:**

### **Scenario 1: Testing Main App**

```
1. Open terminal
   ↓
2. cd "D:\Project\Katara Dental\TDL\Pramit\Tally Ledger Report"
   ↓
3. python C2.py
   ↓
4. App opens → Test features
   ↓
5. Add companies → Sync data
   ↓
6. Check database: TallyConnectDb.db
```

---

### **Scenario 2: Testing Portal**

```
1. Open terminal
   ↓
2. cd "D:\Project\Katara Dental\TDL\Pramit\Tally Ledger Report"
   ↓
3. python portal_server.py
   ↓
4. Browser opens → localhost:8000
   ↓
5. Select company → View reports
   ↓
6. Test ledger reports
```

---

### **Scenario 3: Full Testing (Both Apps)**

```
Terminal 1:
python C2.py
→ Sync data

Terminal 2:
python portal_server.py
→ View reports
```

---

## 🛠️ **Development Commands:**

### **Quick Commands:**

```bash
# Run main app
python C2.py

# Run portal server
python portal_server.py

# Or use batch files
START_PORTAL.bat

# Build EXEs
build.bat

# Rebuild portal only
REBUILD_PORTAL_EXE.bat
```

---

## 📁 **Project Structure:**

```
Tally Ledger Report/
├── C2.py                    # Main application
├── portal_server.py         # Portal server
├── portal_launcher.py      # Portal launcher (for EXE)
├── generate_portal.py        # Generate static portal
├── test_reports.py          # Test reports
│
├── database/
│   ├── __init__.py
│   └── queries.py          # SQL queries
│
├── reports/
│   ├── report_generator.py # Report generation
│   ├── utils.py            # Utility functions
│   ├── templates/          # HTML templates
│   ├── static/             # CSS/JS files
│   └── portal/             # Portal HTML
│
├── build.bat               # Build script
├── START_PORTAL.bat        # Start portal
├── REBUILD_PORTAL_EXE.bat  # Rebuild portal EXE
│
├── TallyConnect.spec       # Main EXE config
├── TallyConnectPortal.spec # Portal EXE config
└── TallyConnectInstaller.iss # Installer config
```

---

## 🔍 **Testing Checklist:**

### **Main App (C2.py):**
- [ ] App opens correctly
- [ ] Companies load from Tally
- [ ] Add company works
- [ ] Sync data works
- [ ] Database created/updated
- [ ] Reports button works

### **Portal Server (portal_server.py):**
- [ ] Server starts on port 8000
- [ ] Browser opens automatically
- [ ] Companies load from database
- [ ] Outstanding report works
- [ ] Ledger list shows
- [ ] Ledger report generates
- [ ] Dashboard works

---

## 🐛 **Debugging:**

### **Check Database:**
```bash
# Using Python
python -c "import sqlite3; conn = sqlite3.connect('TallyConnectDb.db'); cursor = conn.cursor(); cursor.execute('SELECT name FROM companies'); print(cursor.fetchall())"
```

### **Check Server Logs:**
- Portal server shows console output
- Check for error messages
- Verify database path

### **Check Port:**
```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000
```

---

## 📝 **Common Issues:**

### **Issue 1: "Python not found"**
**Solution:**
```bash
# Add Python to PATH
# Or use full path:
C:\Python39\python.exe C2.py
```

### **Issue 2: "Module not found"**
**Solution:**
```bash
pip install pyodbc pyinstaller
```

### **Issue 3: "Database not found"**
**Solution:**
- Run C2.py once (creates database)
- Or copy existing database

### **Issue 4: "Port 8000 in use"**
**Solution:**
```bash
# Kill process using port 8000
netstat -ano | findstr :8000
taskkill /PID <process_id> /F

# Or change port in portal_server.py
PORT = 8001
```

---

## 🎯 **Development Tips:**

### **1. Use Python Scripts for Development:**
- Faster iteration
- Better error messages
- Easy debugging

### **2. Use EXEs for Testing:**
- Test final product
- Verify bundling works
- Check distribution

### **3. Database Location:**
- Development: Project root (`TallyConnectDb.db`)
- EXE: Same directory as EXE

### **4. Portal Testing:**
- Always use `python portal_server.py` for development
- EXE only for final testing

---

## ✅ **Quick Reference:**

| Task | Command |
|------|---------|
| Run Main App | `python C2.py` |
| Run Portal | `python portal_server.py` |
| Start Portal (Batch) | `START_PORTAL.bat` |
| Build EXEs | `build.bat` |
| Rebuild Portal | `REBUILD_PORTAL_EXE.bat` |
| Test Reports | `python test_reports.py` |
| Generate Portal | `python generate_portal.py` |

---

## 🎉 **Ready to Develop!**

**Start with:**
```bash
python C2.py          # Main app
python portal_server.py  # Portal
```

**Happy Coding!** 🚀

