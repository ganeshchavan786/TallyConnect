# Portal Diagnostic Tool - Summary

## ✅ Completed Work

### 1. Diagnostic Tool Created
**File:** `scripts/diagnose_portal.py`

**Features:**
- ✅ Database file existence check
- ✅ Database connection verification
- ✅ Tables structure validation
- ✅ Companies count and status check
- ✅ Vouchers count per company
- ✅ Ledgers count per company
- ✅ API endpoint configuration check
- ✅ Portal frontend files check
- ✅ Test API response generation
- ✅ Comprehensive troubleshooting recommendations

**Usage:**
```bash
python scripts/diagnose_portal.py
```

### 2. Troubleshooting Guide Created
**File:** `docs/PORTAL_TROUBLESHOOTING.md`

**Contents:**
- Quick diagnostic steps
- Common issues and solutions:
  - "Loading ledgers..." or "No companies found"
  - API returns 404
  - API returns 500 (Server Error)
  - Data shows but reports are empty
- Step-by-step debugging guide
- API endpoints reference
- Browser console commands for testing
- Quick fixes checklist

### 3. Documentation Updated
**File:** `docs/INDEX.md`
- Added link to PORTAL_TROUBLESHOOTING.md

## 🔍 What the Diagnostic Tool Checks

### Database Check
- ✅ Database file exists
- ✅ File size > 0
- ✅ Connection successful
- ✅ Required tables exist (companies, vouchers)

### Companies Check
- ✅ Total companies count
- ✅ Synced companies count
- ✅ Company details (name, GUID, AlterID, status, records)
- ⚠️ Warns if no synced companies

### Vouchers Check
- ✅ Voucher count per company
- ✅ Distinct ledgers count per company
- ⚠️ Warns if no vouchers found
- ⚠️ Warns if no ledgers (null party names)

### API Endpoints Check
- ✅ Portal server module import
- ✅ Base directory path
- ✅ Database file path
- ✅ Database file existence

### Portal Files Check
- ✅ Portal directory exists
- ✅ index.html exists
- ✅ File sizes

### Test API Responses
- ✅ Generates sample companies.json response
- ✅ Generates sample ledgers.json response
- ✅ Shows actual data structure

## 🎯 How to Use When UI Doesn't Show Data

### Step 1: Run Diagnostic Tool
```bash
python scripts/diagnose_portal.py
```

### Step 2: Check Output
Look for:
- [WARNING] messages - these indicate issues
- [ERROR] messages - these indicate failures
- Counts (companies, vouchers, ledgers)

### Step 3: Follow Recommendations
The tool provides specific solutions for each issue found.

### Step 4: Check Browser Console
1. Open portal in browser
2. Press F12
3. Check Console tab for errors
4. Check Network tab for failed API requests

### Step 5: Check Server Console
1. Look at portal server output
2. Check for error messages
3. Verify database path

## 📋 Common Issues Identified

### Issue 1: No Database
**Symptom:** `Database file not found`
**Solution:** Run TallyConnect app and sync at least one company

### Issue 2: No Synced Companies
**Symptom:** `Synced Companies: 0`
**Solution:** Open TallyConnect app, add and sync a company

### Issue 3: No Vouchers
**Symptom:** `Total Vouchers: 0`
**Solution:** Re-sync the company in TallyConnect app

### Issue 4: No Ledgers
**Symptom:** `Distinct Ledgers: 0`
**Solution:** Check if vouchers have party names, re-sync if needed

### Issue 5: Server Not Running
**Symptom:** `Connection refused` or `Failed to fetch`
**Solution:** Start portal server using `python -m backend.portal_launcher`

## 🛠️ Troubleshooting Workflow

```
UI Not Showing Data?
    ↓
Run Diagnostic Tool
    ↓
Check Database
    ↓
Check Companies
    ↓
Check Vouchers
    ↓
Check API Endpoints
    ↓
Check Browser Console
    ↓
Check Server Console
    ↓
Follow Recommendations
```

## 📝 Files Created/Modified

1. ✅ `scripts/diagnose_portal.py` - Diagnostic tool (NEW)
2. ✅ `docs/PORTAL_TROUBLESHOOTING.md` - Troubleshooting guide (NEW)
3. ✅ `docs/INDEX.md` - Updated with new documentation link
4. ✅ `docs/DIAGNOSTIC_TOOL_SUMMARY.md` - This summary (NEW)

## 🎉 Benefits

1. **Quick Problem Identification:** Run one command to identify all issues
2. **Clear Solutions:** Each issue comes with specific fix instructions
3. **Comprehensive Check:** Covers database, API, and frontend
4. **User-Friendly:** Plain text output, no special characters
5. **Future-Proof:** Can be extended with more checks

## 🔄 Next Steps (If Needed)

If diagnostic tool identifies issues:
1. Follow the recommended solutions
2. Re-run diagnostic tool to verify fixes
3. Check portal UI again
4. If still not working, check browser console and server logs

---

**Created:** December 2025  
**Purpose:** Help identify and fix portal UI data display issues  
**Status:** ✅ Complete and Ready to Use

