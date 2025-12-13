# 🚀 TallyConnect - Quick Start Guide

**सर्वात सोपा मार्ग Portal start करण्यासाठी!**

---

## ⚡ **One-Click Start (Recommended)**

### **Option 1: Desktop Shortcut (After Install)**
```
Desktop → "TallyConnect Portal" → Double-click
```

### **Option 2: Before Building EXE**
```bash
start_portal_server.bat → Double-click
```

### **Option 3: After Building EXE**
```
dist\TallyConnectPortal.exe → Double-click
```

---

## 📦 **Build EXE with Portal**

### **Step 1: Build Both EXEs**
```bash
build.bat
```

**Creates:**
- `dist\TallyConnect.exe` - Main application
- `dist\TallyConnectPortal.exe` - Portal server

### **Step 2: Create Installer**
```bash
# Inno Setup मध्ये:
TallyConnectInstaller.iss → Compile
```

**Installer creates:**
- Desktop shortcut for "TallyConnect Portal"
- Double-click → Portal opens automatically!

---

## 🎯 **Usage After Install**

### **For Customers:**
```
1. Install TallyConnectSetup_v5.6.exe
2. Desktop वर "TallyConnect Portal" shortcut दिसेल
3. Double-click करा
4. Portal opens → Reports work automatically!
```

---

## 🔧 **For Development/Testing**

### **Test Reports:**
```bash
python test_reports.py
```

### **Generate Portal (Static):**
```bash
python generate_portal.py
```

### **Start Portal Server:**
```bash
python portal_server.py
# Or:
start_portal_server.bat
```

---

## 📁 **Essential Files**

### **Core Application:**
- `C2.py` - Main app
- `portal_server.py` - Portal server
- `portal_launcher.py` - Portal launcher

### **Build Files:**
- `build.bat` - Build script
- `TallyConnect.spec` - Main EXE config
- `TallyConnectPortal.spec` - Portal EXE config
- `TallyConnectInstaller.iss` - Installer config

### **Testing:**
- `test_reports.py` - Test reports
- `generate_portal.py` - Generate static portal

### **Documentation:**
- `README.md` - Main documentation
- `LICENSE.txt` - License
- `CONTRIBUTING.md` - Contribution guide
- `CHANGELOG.md` - Version history

---

## ✅ **What's Fixed**

- ✅ Buffering issue - Reports generate without browser popup
- ✅ Desktop shortcut - Automatic on install
- ✅ One-click start - Just double-click
- ✅ Clean project - Only essential files
- ✅ EXE ready - Both apps bundled

---

**🎉 Ready for distribution!**

