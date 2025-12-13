# 🌐 TallyConnect Portal - Quick Start

**Two Ways to Use Portal:**

---

## 🚀 **Method 1: One-Click Server** ⭐ (Recommended for Customers)

### **सर्वात सोपा - Customer-Friendly!**

```bash
start_portal_server.bat → Double-click करा
```

**हे करेल:**
- ✅ HTTP server start होईल
- ✅ Browser automatically open होईल
- ✅ Reports **auto-generate** होतील (click केल्यावर)
- ✅ **No manual steps** - सगळं automatic!

**Benefits:**
- 🎯 **One-click** - फक्त double-click
- ⚡ **Auto-generation** - Reports on-demand generate होतात
- 🔄 **Always fresh** - Latest data automatically
- 👥 **Customer-friendly** - कोणालाही वापरता येते

**Usage:**
1. `start_portal_server.bat` double-click करा
2. Browser मध्ये portal open होईल
3. Company select करा
4. Report click करा - **automatic generate होईल!**

---

## 📁 **Method 2: Static Portal** (For Distribution)

### **Pre-generated Reports**

```bash
python generate_portal.py
start reports\portal\index.html
```

**हे करेल:**
- ✅ सगळे reports पहिल्यांदा generate करेल
- ✅ Static HTML files create करेल
- ✅ Portal folder share करता येते

**Benefits:**
- 📦 **Portable** - Folder copy करून share करा
- 🌐 **No server** - Direct HTML files
- ⚡ **Fast** - Pre-generated reports

**Usage:**
1. `python generate_portal.py` run करा (once)
2. `reports/portal/` folder share करा
3. Users `index.html` open करतील

---

## 🎯 **Which Method to Use?**

### **Use Server Method (Method 1) If:**
- ✅ Customers/users साठी
- ✅ One-click solution हवे
- ✅ Always latest data हवे
- ✅ No technical knowledge

### **Use Static Method (Method 2) If:**
- ✅ Folder distribution
- ✅ No server needed
- ✅ Pre-generated reports
- ✅ Offline use

---

## 📋 **Quick Comparison**

| Feature | Server (Method 1) | Static (Method 2) |
|---------|------------------|-------------------|
| **Start** | One-click | Two steps |
| **Generation** | Auto (on-demand) | Manual (pre-generate) |
| **Updates** | Automatic | Regenerate needed |
| **Distribution** | Share project | Share folder |
| **Customer-Friendly** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

---

## 🚀 **For Customers (Recommended):**

### **Just One File:**
```
start_portal_server.bat → Double-click
```

**That's it!** Portal opens, reports work automatically!

---

## 📝 **Files:**

### **Server Method:**
- `start_portal_server.bat` - One-click start
- `portal_server.py` - HTTP server

### **Static Method:**
- `generate_portal.py` - Generate reports
- `reports/portal/index.html` - Portal file

---

## 💡 **Tips:**

1. **First Time:**
   - Use `start_portal_server.bat` (easiest!)

2. **For Distribution:**
   - Use `generate_portal.py` (pre-generate)
   - Share `reports/portal/` folder

3. **For Customers:**
   - Always use `start_portal_server.bat`
   - No technical knowledge needed!

---

**🎉 Choose the method that works best for you!**

