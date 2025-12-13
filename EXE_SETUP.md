# 🚀 TallyConnect Portal EXE - Setup Guide

## ✅ **EXE Mode Support**

Portal EXE आता **fully functional** आहे! Database path आणि file paths दोन्ही EXE mode मध्ये काम करतात.

---

## 📦 **Build EXE:**

```bash
build.bat
```

**Creates:**
- `dist\TallyConnect.exe` - Main application
- `dist\TallyConnectPortal.exe` - Portal server (standalone)

---

## 🔧 **EXE Requirements:**

### **1. Database File:**
- `TallyConnectDb.db` **EXE च्या same directory मध्ये** असले पाहिजे
- Installer automatically database create करतो (first run वर)
- Or manually copy database to EXE directory

### **2. Directory Structure (After Install):**
```
C:\Users\...\AppData\Local\Programs\TallyConnect\
├── TallyConnect.exe
├── TallyConnectPortal.exe
├── TallyConnectDb.db          ← Database (created automatically)
└── reports/                   ← Bundled with EXE
    └── portal/
        └── index.html
```

---

## 🎯 **How It Works:**

### **EXE Mode Detection:**
```python
def get_base_dir():
    if getattr(sys, 'frozen', False):
        # EXE mode - use executable directory
        return os.path.dirname(sys.executable)
    else:
        # Script mode - use script directory
        return os.path.dirname(os.path.abspath(__file__))
```

### **Database Path:**
- **EXE Mode:** `{EXE_DIR}\TallyConnectDb.db`
- **Script Mode:** `{SCRIPT_DIR}\TallyConnectDb.db`

### **Portal Directory:**
- **EXE Mode:** `{EXE_DIR}\reports\portal`
- **Script Mode:** `{SCRIPT_DIR}\reports\portal`

---

## ✅ **Testing EXE:**

1. **Build EXE:**
   ```bash
   build.bat
   ```

2. **Copy Database (if needed):**
   ```bash
   copy TallyConnectDb.db dist\
   ```

3. **Run Portal EXE:**
   ```bash
   dist\TallyConnectPortal.exe
   ```

4. **Verify:**
   - Server starts on `localhost:8000`
   - Browser opens automatically
   - Companies load from database
   - Reports generate on-demand

---

## 📝 **Installer Notes:**

Installer automatically:
- ✅ Installs both EXEs
- ✅ Creates desktop shortcuts
- ✅ Database created on first run (if not exists)
- ✅ Reports directory bundled

**Database Location:**
- Installer does NOT copy database (fresh install)
- Application creates blank database on first run
- User syncs companies → Database populated

---

## 🔍 **Troubleshooting:**

### **Companies not loading:**
1. Check database exists: `{EXE_DIR}\TallyConnectDb.db`
2. Check database has companies: Open with SQLite browser
3. Check server console for errors

### **Reports not generating:**
1. Check database has voucher data
2. Check console for error messages
3. Verify company GUID/AlterID in database

### **Portal not opening:**
1. Check port 8000 is not in use
2. Check firewall settings
3. Try different port (edit `portal_server.py`)

---

## ✅ **Summary:**

- ✅ EXE mode fully supported
- ✅ Database path works correctly
- ✅ Portal directory bundled
- ✅ On-demand report generation
- ✅ Works standalone (no Python needed)

**Ready for distribution!** 🎉

