# 📦 TallyConnect - Distribution & Database Setup Guide

## 🎯 **Overview**

हा guide customer ला EXE distribute करणे आणि database setup करणे साठी आहे.

---

## 📦 **Part 1: EXE Distribution**

### **Option A: Installer (Recommended) ✅**

**Best for:** Professional distribution, multiple customers

**Steps:**
1. **Build Installer:**
   ```bash
   build.bat
   # Select "Y" when asked to create installer
   ```

2. **Output:**
   - `dist\TallyConnectSetup_v5.6.exe` (Single installer file)

3. **Distribution:**
   - Email करा customer ला
   - USB drive वर copy करा
   - Cloud storage (Google Drive, OneDrive) वर upload करा
   - Website वर download link द्या

**Advantages:**
- ✅ Professional installer
- ✅ Automatic desktop shortcuts
- ✅ Easy uninstall
- ✅ Single file distribution
- ✅ No admin rights needed (per-user install)

**Customer Installation:**
1. Double-click `TallyConnectSetup_v5.6.exe`
2. Follow installer wizard
3. Desktop shortcuts automatically created
4. Done!

---

### **Option B: Direct EXE Files**

**Best for:** Quick testing, single customer

**Steps:**
1. **Build EXEs:**
   ```bash
   build.bat
   # Skip installer creation
   ```

2. **Files to distribute:**
   - `dist\TallyConnect.exe` (Main app)
   - `dist\TallyConnectPortal.exe` (Portal server)

3. **Create ZIP:**
   ```
   TallyConnect_v5.6.zip
   ├── TallyConnect.exe
   ├── TallyConnectPortal.exe
   └── README.txt (instructions)
   ```

**Advantages:**
- ✅ No installer needed
- ✅ Quick distribution
- ✅ Portable (can run from USB)

**Disadvantages:**
- ❌ No automatic shortcuts
- ❌ Manual setup required

---

## 💾 **Part 2: Database Setup**

### **Scenario 1: Fresh Installation (New Customer)**

**What Happens:**
1. Customer installs EXE
2. First time `TallyConnect.exe` run करते
3. Application automatically creates `TallyConnectDb.db` (blank database)
4. Customer adds companies → Syncs data → Database populated

**Location:**
```
C:\Users\{Username}\AppData\Local\Programs\TallyConnect\
└── TallyConnectDb.db  (created automatically)
```

**Code (Already Implemented):**
```python
# C2.py - Line 172
self.db_conn = init_db()  # Creates database if not exists

# init_db() function (Line 46-96)
# Creates companies and vouchers tables automatically
```

**✅ No Action Needed** - Application handles this automatically!

---

### **Scenario 2: Existing Database (Migration/Backup)**

**Use Case:** Customer already has data, wants to transfer to new computer

**Method 1: Manual Copy (Simple)**
1. Old computer: Copy `TallyConnectDb.db` from:
   ```
   C:\Users\{Username}\AppData\Local\Programs\TallyConnect\
   ```
2. New computer: Paste to same location after installation
3. Done!

**Method 2: Export/Import (Advanced)**
1. Use SQLite browser to export data
2. Import on new computer
3. More control over what to transfer

**Method 3: Backup Feature (Future Enhancement)**
- Add "Export Database" button in app
- Add "Import Database" button in app
- User-friendly backup/restore

---

### **Scenario 3: Multiple Companies Setup**

**Current Flow:**
1. Customer installs TallyConnect
2. Opens `TallyConnect.exe`
3. Clicks "➕ Add Company"
4. Selects Tally company from list
5. Clicks "Sync Selected"
6. Data syncs → Database populated
7. Repeat for each company

**Database Structure:**
```sql
companies table:
- id, name, guid, alterid, status, total_records, last_sync

vouchers table:
- All transaction data linked by company_guid + company_alterid
```

**✅ Works Automatically** - No manual database setup needed!

---

## 🔧 **Part 3: Customer Setup Checklist**

### **Pre-Installation:**
- [ ] Tally Prime installed and running
- [ ] Tally ODBC driver installed
- [ ] Windows 10/11 (64-bit)
- [ ] Internet connection (for initial download)

### **Installation:**
- [ ] Run `TallyConnectSetup_v5.6.exe`
- [ ] Follow installer wizard
- [ ] Desktop shortcuts created

### **First Run:**
- [ ] Open `TallyConnect.exe`
- [ ] Database automatically created
- [ ] Add companies
- [ ] Sync data
- [ ] Verify data in "Synced Companies"

### **Portal Setup:**
- [ ] Double-click "TallyConnect Portal" desktop shortcut
- [ ] Browser opens automatically
- [ ] Companies visible in portal
- [ ] Reports generate on-demand

---

## 📋 **Part 4: Distribution Package Contents**

### **Option A: Installer Package**
```
TallyConnect_v5.6_Installer.zip
└── TallyConnectSetup_v5.6.exe
└── README.txt (installation instructions)
└── USER_GUIDE.pdf (optional)
```

### **Option B: Direct EXE Package**
```
TallyConnect_v5.6_Portable.zip
├── TallyConnect.exe
├── TallyConnectPortal.exe
├── README.txt
└── USER_GUIDE.pdf (optional)
```

---

## 🎓 **Part 5: Customer Training Points**

### **Key Points to Explain:**
1. **Database Location:**
   - Automatically created on first run
   - Located in AppData (hidden folder)
   - No manual setup needed

2. **Data Sync:**
   - Click "Add Company" → Select company → Sync
   - Data syncs from Tally to local database
   - Can sync multiple companies

3. **Reports:**
   - Portal automatically reads from database
   - Reports generate on-demand
   - No pre-generation needed

4. **Backup:**
   - Database file can be copied for backup
   - Location: `AppData\Local\Programs\TallyConnect\`

---

## 🚀 **Part 6: Best Practices**

### **For Distribution:**
1. ✅ Always use installer for customers
2. ✅ Include README with instructions
3. ✅ Test on clean Windows machine first
4. ✅ Version number in filename
5. ✅ Digital signature (optional, for trust)

### **For Database:**
1. ✅ Let application create database automatically
2. ✅ Don't distribute pre-filled database (privacy)
3. ✅ Provide backup instructions
4. ✅ Document database location

### **For Support:**
1. ✅ Document common issues
2. ✅ Provide troubleshooting guide
3. ✅ Include contact information
4. ✅ Version number visible in app

---

## 📝 **Part 7: Quick Reference**

### **Database File:**
- **Name:** `TallyConnectDb.db`
- **Location:** `{InstallDir}\TallyConnectDb.db`
- **Created:** Automatically on first run
- **Size:** Depends on data (typically 1-100 MB)

### **Installation Directory:**
- **Default:** `C:\Users\{Username}\AppData\Local\Programs\TallyConnect\`
- **No Admin Rights:** Required
- **Per-User:** Each user has separate installation

### **Portal:**
- **URL:** `http://localhost:8000`
- **Port:** 8000 (can be changed in code)
- **Access:** Local only (not accessible from network)

---

## ✅ **Summary**

### **EXE Distribution:**
- ✅ Use installer for professional distribution
- ✅ Single file: `TallyConnectSetup_v5.6.exe`
- ✅ Automatic shortcuts and setup

### **Database Setup:**
- ✅ Automatic creation on first run
- ✅ No manual setup needed
- ✅ Customer just syncs companies

### **Customer Experience:**
1. Install EXE
2. Run TallyConnect
3. Add companies
4. Sync data
5. View reports in portal

**Simple and automated!** 🎉

