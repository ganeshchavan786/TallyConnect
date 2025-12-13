# 🚀 TallyConnect Portal - Start Guide (Marathi)

सोप्या पद्धतीने Portal कसे start करायचे.

---

## 📋 Step-by-Step Instructions

### **Step 1: Portal Generate करा** ⚙️

```bash
# PowerShell/CMD मध्ये project folder मध्ये:
python generate_portal.py
```

**हे करेल:**
- सगळ्या companies साठी reports generate
- सगळ्या ledgers साठी reports generate
- Portal ready करेल

**Output:**
```
[SUCCESS] Portal generation complete!
Portal location: reports/portal/
```

---

### **Step 2: Portal Open करा** 🌐

**Option A: Direct Open (सर्वात सोपा)**
```
1. File Explorer मध्ये जा
2. reports/portal/ folder मध्ये जा
3. index.html file वर double-click करा
4. Browser मध्ये portal उघडेल
```

**Option B: Desktop Shortcut (Recommended)**
```bash
# PowerShell मध्ये:
create_desktop_shortcut.bat
```
Desktop वर "TallyConnect Portal" shortcut दिसेल. Double-click करा.

**Option C: Browser मधून**
```
1. Browser open करा (Chrome/Edge/Brave)
2. Ctrl+O press करा (Open File)
3. reports/portal/index.html select करा
4. Open click करा
```

---

### **Step 3: Portal Use करा** 📊

#### **3.1 Company Select करा**
```
1. Portal open झाल्यावर "Companies" page दिसेल
2. Company card वर click करा
3. Reports page दिसेल
```

#### **3.2 Report Type Select करा**
```
तीन options दिसतील:

📊 Outstanding Report
   → Click करा → Report direct दिसेल

📗 Ledger Report  
   → Click करा → Ledger list दिसेल
   → Ledger select करा → Report दिसेल

📈 Dashboard
   → Click करा → Dashboard direct दिसेल
```

#### **3.3 Ledger Report साठी:**
```
1. "Ledger Report" click करा
2. Ledger list दिसेल
3. कोणताही ledger click करा
4. त्या ledger चा report दिसेल
```

---

## 🔧 Troubleshooting

### **Problem 1: "Loading companies..." दिसत आहे**
**Solution:**
```bash
python generate_portal.py
```
हे run करा - companies data generate होईल.

---

### **Problem 2: Company click केल्यावर काही होत नाही**
**Solution:**
1. Browser refresh करा (F5)
2. `python generate_portal.py` run करा
3. Browser refresh करा

---

### **Problem 3: Report "Loading..." मध्ये अडकले**
**Possible Causes:**
- Report file generate झाला नाही
- File path wrong आहे

**Solution:**
```bash
# Portal regenerate करा
python generate_portal.py

# Browser refresh करा (F5)
```

---

### **Problem 4: "Report file not found" error**
**Solution:**
```bash
# सगळे reports generate करा
python generate_portal.py

# Check करा:
# reports/portal/api/reports/ folder मध्ये HTML files आहेत का?
```

---

## 📁 File Locations

```
Project Folder/
├── generate_portal.py          ← Run हे file
├── create_desktop_shortcut.bat ← Desktop shortcut साठी
└── reports/
    └── portal/
        └── index.html          ← Portal open करा हे file
```

---

## ⚡ Quick Commands

### **Portal Generate:**
```bash
python generate_portal.py
```

### **Portal Open:**
```
Double-click: reports/portal/index.html
```

### **Desktop Shortcut:**
```bash
create_desktop_shortcut.bat
```

---

## 🎯 Complete Workflow

```
1. python generate_portal.py     ← Generate reports
2. reports/portal/index.html      ← Open portal
3. Company select करा
4. Report type select करा
5. (Ledger select करा - जर ledger report असेल)
6. Report view करा!
```

---

## 💡 Tips

### **Portal Regenerate कधी करायचे:**
- नवीन company add केल्यावर
- नवीन data sync केल्यावर
- Reports update करायचे असल्यास

### **Browser:**
- कोणताही browser चालेल (Chrome, Edge, Brave, Firefox)
- Internet नको (standalone आहे)

### **Performance:**
- पहिल्या वेळी थोडा वेळ लागू शकतो (reports generate होतात)
- पुढच्या वेळी instant load होईल

---

## 🎉 Success Checklist

✅ `python generate_portal.py` run केले  
✅ Portal open केले (index.html)  
✅ Company दिसत आहे  
✅ Company click केल्यावर reports दिसतात  
✅ Ledger report साठी ledger select करता येते  
✅ Reports load होतात  

---

## 📞 अजून Problem असल्यास

1. **Error message** screenshot घ्या
2. **Browser console** check करा (F12 → Console)
3. **File path** check करा (error message मध्ये दिसेल)

---

**Happy Reporting! 📊**

