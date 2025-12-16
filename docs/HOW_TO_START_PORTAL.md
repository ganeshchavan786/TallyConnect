# Portal कसा Start करावा - Complete Guide

## 🚀 Portal Start करण्याच्या पद्धती

### Method 0: Main App सोबत (सर्वात सोपा) ⭐⭐⭐

**स्टेप्स:**
1. `main.py` run करा:
   ```bash
   python main.py
   ```
2. Portal automatically start होईल
3. Browser automatically उघडेल
4. Main app आणि portal दोन्ही एकत्र चालतील

**काय होते:**
- Main TallyConnect GUI application start होते
- Portal server background मध्ये start होते
- Browser automatically `http://localhost:8000` उघडते
- Main app बंद केल्यावर portal देखील बंद होते

**✅ Recommended:** ही सर्वात सोपी पद्धत आहे!

---

### Method 1: BAT File (सर्वात सोपा) ⭐

**स्टेप्स:**
1. `scripts` folder मध्ये जा
2. `START_PORTAL.bat` file वर double-click करा
3. Portal automatically browser मध्ये उघडेल

**Location:**
```
scripts/START_PORTAL.bat
```

**काय होते:**
- Python check करते
- Portal server start करते
- Browser automatically उघडते
- `http://localhost:8000` वर portal दिसेल

---

### Method 2: Python Command (Development)

**⚠️ IMPORTANT: Project Root Directory मधून run करा!**

**स्टेप्स:**
1. Terminal/Command Prompt उघडा
2. **Project root directory मध्ये जा** (scripts folder नाही!)
   ```bash
   cd "D:\Project\Katara Dental\TDL\Pramit\Tally Ledger Report"
   ```
3. ही command run करा:

```bash
python -m backend.portal_launcher
```

**❌ चुकीचे (scripts folder मधून):**
```bash
cd scripts
python -m backend.portal_launcher  # ❌ Error: No module named 'backend'
```

**✅ बरोबर (project root मधून):**
```bash
cd "D:\Project\Katara Dental\TDL\Pramit\Tally Ledger Report"
python -m backend.portal_launcher  # ✅ Works!
```

**काय होते:**
- Portal server start होते
- Browser automatically उघडते
- Console मध्ये server status दिसेल
- `Ctrl+C` दाबून server stop करू शकता

---

### Method 3: EXE File (Production)

**स्टेप्स:**
1. `TallyConnectPortal.exe` file वर double-click करा
2. Portal automatically browser मध्ये उघडेल

**Location (after build):**
```
dist/TallyConnectPortal.exe
```

**काय होते:**
- Portal server background मध्ये start होते
- System tray मध्ये icon दिसेल
- Browser automatically उघडते
- Right-click tray icon → Exit करून stop करू शकता

---

## 📋 Step-by-Step Instructions

### Option A: BAT File वापरून (Recommended)

```
1. File Explorer उघडा
2. Project folder मध्ये जा
3. scripts folder उघडा
4. START_PORTAL.bat वर double-click करा
5. Browser automatically उघडेल
6. Portal ready आहे!
```

### Option B: Command Line वापरून

```
1. Windows Key + R दाबा
2. "cmd" टाइप करा आणि Enter दाबा
3. Project ROOT folder मध्ये navigate करा (scripts folder नाही!):
   cd "D:\Project\Katara Dental\TDL\Pramit\Tally Ledger Report"
4. Command run करा:
   python -m backend.portal_launcher
5. Browser automatically उघडेल

⚠️ IMPORTANT: Project root मधून run करा, scripts folder मधून नाही!
```

### Option C: PowerShell वापरून

```
1. Windows Key + X दाबा
2. "Windows PowerShell" निवडा
3. Project ROOT folder मध्ये navigate करा (scripts folder नाही!):
   cd "D:\Project\Katara Dental\TDL\Pramit\Tally Ledger Report"
4. Command run करा:
   python -m backend.portal_launcher

⚠️ IMPORTANT: Project root मधून run करा, scripts folder मधून नाही!
```

---

## ✅ Portal Start झाल्यानंतर काय दिसेल?

### Browser मध्ये:
- Portal URL: `http://localhost:8000`
- Dashboard page
- Companies list
- Ledgers list
- Reports section

### Console/Terminal मध्ये:
```
============================================================
TallyConnect Portal Server
============================================================

Server running at: http://localhost:8000
Portal URL: http://localhost:8000/index.html

Press Ctrl+C to stop the server
============================================================
```

---

## ⚠️ Common Issues आणि Solutions

### Issue 1: "Python not found"
**Error:** `[ERROR] Python not found!`

**Solution:**
1. Python install करा (Python 3.8+)
2. Python PATH मध्ये add करा
3. Terminal मध्ये `python --version` run करून verify करा

### Issue 2: "Port 8000 already in use"
**Error:** `[ERROR] Port 8000 is already in use!`

**Solution:**
1. Portal already running आहे का check करा
2. Task Manager मध्ये `python.exe` processes check करा
3. किंवा दुसरा port use करा (portal_server.py मध्ये PORT change करा)

### Issue 3: "No module named 'backend'"
**Error:** `ModuleNotFoundError: No module named 'backend'`

**Solution:**
1. **Project ROOT directory मधून run करा**, scripts folder मधून नाही!
2. Current directory check करा:
   ```bash
   cd  # Current directory दाखवते
   ```
3. Project root मध्ये navigate करा:
   ```bash
   cd "D:\Project\Katara Dental\TDL\Pramit\Tally Ledger Report"
   ```
4. मग command run करा:
   ```bash
   python -m backend.portal_launcher
   ```
5. किंवा `scripts/START_PORTAL.bat` use करा (ते automatically project root मध्ये navigate करते)

### Issue 4: "Portal directory not found"
**Error:** `[ERROR] Portal directory not found!`

**Solution:**
1. `frontend/portal` folder exists आहे का check करा
2. Project structure verify करा
3. Diagnostic tool run करा: `python scripts/diagnose_portal.py`

### Issue 4: Browser automatically उघडत नाही
**Solution:**
1. Manual browser उघडा
2. URL टाइप करा: `http://localhost:8000`
3. किंवा: `http://localhost:8000/index.html`

---

## 🛑 Portal कसा Stop करावा?

### Method 1: Console/Terminal मध्ये
- `Ctrl+C` दाबा
- Server stop होईल

### Method 2: EXE मध्ये
- System tray icon वर right-click करा
- "Exit" निवडा

### Method 3: Task Manager
- Task Manager उघडा (Ctrl+Shift+Esc)
- `python.exe` process शोधा
- "End Task" करा

---

## 🔍 Portal Running आहे का Check करणे

### Method 1: Browser मध्ये
- URL उघडा: `http://localhost:8000`
- Portal load होतो का check करा

### Method 2: API Test
- Browser मध्ये: `http://localhost:8000/api/companies.json`
- JSON data दिसतो का check करा

### Method 3: Diagnostic Tool
```bash
python scripts/diagnose_portal.py
```

---

## 📝 Quick Reference

| Method | Command/File | Use Case |
|--------|-------------|----------|
| **Main App** | `python main.py` | **Recommended: Main app + Portal together** |
| BAT File | `scripts/START_PORTAL.bat` | Portal only, quick start |
| Python | `python -m backend.portal_launcher` | Portal only, development |
| EXE | `TallyConnectPortal.exe` | Portal only, production |

---

## 🎯 Recommended Workflow

### Development मध्ये (सर्वात सोपा):
1. `python main.py` run करा
2. Main app आणि portal दोन्ही start होतील
3. Browser automatically उघडेल
4. Code changes करा
5. Browser refresh करा (F5)

### Portal फक्त (Standalone):
1. `scripts/START_PORTAL.bat` double-click करा
2. किंवा `python -m backend.portal_launcher` command run करा
3. Browser automatically उघडेल

### Production मध्ये:
1. `TallyConnect.exe` run करा (main app + portal)
2. किंवा `TallyConnectPortal.exe` run करा (portal only)
3. Portal background मध्ये run होईल
4. System tray icon दिसेल
5. Browser automatically उघडेल

---

## 📞 Help

जर portal start होत नसेल:
1. Diagnostic tool run करा: `python scripts/diagnose_portal.py`
2. `docs/PORTAL_TROUBLESHOOTING.md` check करा
3. Console/Terminal मध्ये error messages check करा

---

**Created:** December 2025  
**Last Updated:** December 2025  
**Status:** ✅ Complete

