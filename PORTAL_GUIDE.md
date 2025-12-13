# 🌐 TallyConnect - Portal Guide

Standalone HTML Portal for viewing reports with sidebar navigation.

---

## 🎯 What is the Portal?

A beautiful web-based interface that lets you:
- ✅ Select company from sidebar
- ✅ Choose report type (Outstanding, Ledger, Dashboard)
- ✅ Select ledger for ledger reports
- ✅ View reports in integrated viewer
- ✅ Multi-company support

---

## 🚀 Quick Start

### Step 1: Generate Portal
```bash
python generate_portal.py
```

This will:
- Create portal directories
- Generate all reports for all companies
- Create company and ledger JSON files
- Make portal ready to use

### Step 2: Open Portal
**Option A: Direct Open**
```
Double-click: reports/portal/index.html
```

**Option B: Desktop Shortcut**
```bash
create_desktop_shortcut.bat
```
Then double-click "TallyConnect Portal" on desktop

**Option C: Browser**
```
Right-click index.html → Open with → Browser
```

---

## 📁 Portal Structure

```
reports/portal/
├── index.html              # Main portal interface
└── api/
    ├── companies.json       # Company list
    ├── ledgers/            # Ledger lists (per company)
    │   └── {guid}_{alterid}.json
    └── reports/            # Generated reports
        ├── outstanding_{guid}_{alterid}.html
        ├── ledger_{guid}_{alterid}_{ledger}.html
        └── dashboard_{guid}_{alterid}.html
```

---

## 🎨 Portal Features

### 1. **Sidebar Navigation**
- 🏢 Companies - Select company
- 📊 Reports - Choose report type
- 📗 Ledgers - Select ledger

### 2. **Company Selection**
- Grid view of all synced companies
- Shows company name, record count, status
- Click to select

### 3. **Report Selection**
- **Outstanding Report** - Party-wise receivables/payables
- **Ledger Report** - Transaction details (requires ledger selection)
- **Dashboard** - Business overview with charts

### 4. **Ledger Selection**
- List of all ledgers for selected company
- Click ledger to view its report
- Shows transaction count

### 5. **Report Viewer**
- Integrated iframe viewer
- Full report display
- Back button to navigate

---

## 🔄 Workflow

### For Outstanding Report:
```
1. Open Portal
2. Click Company
3. Click "Outstanding Report"
4. View report
```

### For Ledger Report:
```
1. Open Portal
2. Click Company
3. Click "Ledger Report"
4. Select Ledger
5. View ledger's outstanding report
```

### For Dashboard:
```
1. Open Portal
2. Click Company
3. Click "Dashboard"
4. View analytics
```

---

## 🔧 Regenerating Portal

When you add new companies or sync new data:

```bash
# Regenerate portal with latest data
python generate_portal.py
```

This will:
- Update company list
- Regenerate all reports
- Update ledger lists
- Refresh portal data

---

## 💡 Tips

### Desktop Shortcut
- Run `create_desktop_shortcut.bat` once
- Portal opens with double-click
- No need to navigate to folder

### Browser Compatibility
- Works in all modern browsers
- Chrome, Edge, Firefox, Brave
- No internet required (standalone)

### Performance
- First load may take time (generating reports)
- Subsequent opens are instant
- Reports are pre-generated

---

## 🎯 Use Cases

### For End Users:
- Simple interface
- No technical knowledge needed
- Just click and view

### For Distribution:
- Share portal folder
- Users open index.html
- No installation required

### For Multi-Company:
- All companies in one place
- Easy switching
- Centralized access

---

## 📊 Portal vs C2.py

| Feature | Portal | C2.py |
|---------|--------|-------|
| **Interface** | Web-based | Desktop app |
| **Reports** | View only | Generate + View |
| **Sync** | No | Yes |
| **Multi-Company** | Yes | Yes |
| **Distribution** | Easy (share folder) | EXE required |
| **Updates** | Regenerate portal | Update EXE |

---

## 🐛 Troubleshooting

### Portal shows "Loading companies..."
**Solution:** Run `python generate_portal.py`

### Reports not showing
**Solution:** 
1. Check `api/reports/` folder has HTML files
2. Regenerate portal
3. Check browser console for errors

### Desktop shortcut not working
**Solution:**
1. Check path in shortcut properties
2. Re-run `create_desktop_shortcut.bat`
3. Or create manually

### Ledger list empty
**Solution:**
1. Ensure company has synced data
2. Regenerate portal
3. Check database has voucher data

---

## 📝 Files

### Portal Files:
- `reports/portal/index.html` - Main interface
- `generate_portal.py` - Generator script
- `create_desktop_shortcut.bat` - Shortcut creator

### Generated Files:
- `api/companies.json` - Company data
- `api/ledgers/*.json` - Ledger lists
- `api/reports/*.html` - Generated reports

---

## 🎉 Benefits

✅ **Standalone** - No server needed  
✅ **Portable** - Copy folder anywhere  
✅ **Simple** - Just HTML/CSS/JS  
✅ **Professional** - Beautiful UI  
✅ **Multi-Company** - All in one place  
✅ **Easy Distribution** - Share folder  

---

## 🚀 Next Steps

1. **Generate Portal:**
   ```bash
   python generate_portal.py
   ```

2. **Create Shortcut:**
   ```bash
   create_desktop_shortcut.bat
   ```

3. **Use Portal:**
   - Double-click desktop shortcut
   - Select company
   - View reports!

---

**Happy Reporting! 📊**

