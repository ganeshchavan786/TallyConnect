# Portal Troubleshooting Guide

## Quick Diagnostic

Run the diagnostic tool:
```bash
python scripts/diagnose_portal.py
```

This will check:
- ✅ Database file existence and structure
- ✅ Companies in database
- ✅ Vouchers for each company
- ✅ API endpoint configuration
- ✅ Portal frontend files
- ✅ Test API responses

## Common Issues and Solutions

### Issue 1: "Loading ledgers..." or "No companies found"

**Symptoms:**
- Portal shows "Loading ledgers..." message
- Company list is empty
- Dashboard/Reports show no data

**Diagnosis:**
1. Run diagnostic tool: `python scripts/diagnose_portal.py`
2. Check browser console (F12) → Console tab
3. Check browser Network tab for API calls

**Solutions:**

#### A. Database Not Found
```
Error: Database file not found
```
**Fix:**
1. Open TallyConnect app
2. Sync at least one company
3. Database will be created automatically

#### B. No Synced Companies
```
Synced Companies: 0
```
**Fix:**
1. Open TallyConnect app
2. Click "➕ Add Company"
3. Select a company and click "Sync"
4. Wait for sync to complete
5. Refresh portal

#### C. No Vouchers
```
Total Vouchers: 0
```
**Fix:**
1. Re-sync the company in TallyConnect app
2. Check date range in sync settings
3. Ensure Tally is running and connected

#### D. Server Not Running
```
Network Error: Failed to fetch
```
**Fix:**
1. Start portal server:
   ```bash
   python -m backend.portal_launcher
   ```
2. Or use: `scripts/START_PORTAL.bat`
3. Check if port 8000 is available

### Issue 2: API Returns 404

**Symptoms:**
- Browser console shows: `404 Not Found`
- Network tab shows red requests

**Diagnosis:**
1. Check server console for error messages
2. Verify API endpoint path in browser Network tab
3. Check if server is running

**Solutions:**

#### A. Wrong API Path
```
/api/companies.json → 404
```
**Fix:**
- Ensure server is running
- Check URL: `http://localhost:8000/api/companies.json`
- Verify portal server code has correct route handlers

#### B. Server Not Started
```
Connection refused
```
**Fix:**
1. Start portal server
2. Check firewall settings
3. Verify port 8000 is not blocked

### Issue 3: API Returns 500 (Server Error)

**Symptoms:**
- Browser console shows: `500 Internal Server Error`
- Server console shows Python errors

**Diagnosis:**
1. Check server console output
2. Look for Python traceback errors
3. Run diagnostic tool

**Solutions:**

#### A. Database Connection Error
```
Error: unable to open database file
```
**Fix:**
1. Check database file permissions
2. Verify database path in portal_server.py
3. Ensure database file exists

#### B. SQL Query Error
```
Error: no such column
```
**Fix:**
1. Database schema might be outdated
2. Re-run database initialization
3. Check database structure with diagnostic tool

### Issue 4: Data Shows But Reports Are Empty

**Symptoms:**
- Companies list shows correctly
- Ledgers list is empty
- Reports show "No data"

**Diagnosis:**
1. Check vouchers count for company
2. Verify ledger names in database
3. Check API response for ledgers

**Solutions:**

#### A. No Ledgers Found
```
Distinct Ledgers: 0
```
**Fix:**
1. Vouchers might not have `vch_party_name` set
2. Re-sync company with proper date range
3. Check Tally data has party names

#### B. Ledger Names Are Null
```
vch_party_name IS NULL
```
**Fix:**
1. This is a data issue from Tally
2. Check Tally company data
3. Verify Tally ODBC connection

## Step-by-Step Debugging

### Step 1: Check Database
```bash
python scripts/diagnose_portal.py
```

Look for:
- ✅ Database exists
- ✅ Companies count > 0
- ✅ Vouchers count > 0

### Step 2: Check Server
1. Start portal server
2. Open browser: `http://localhost:8000`
3. Press F12 → Network tab
4. Look for API calls

### Step 3: Check API Response
1. Open: `http://localhost:8000/api/companies.json`
2. Should return JSON array
3. Check browser console for errors

### Step 4: Check Browser Console
1. Press F12
2. Console tab → Look for errors
3. Network tab → Check API requests
4. Look for red (failed) requests

### Step 5: Check Server Console
1. Look at portal server console output
2. Check for error messages
3. Look for debug logs

## API Endpoints Reference

### Companies List
```
GET /api/companies.json
```
**Response:**
```json
[
  {
    "name": "Company Name",
    "guid": "guid-here",
    "alterid": "102209.0",
    "status": "synced",
    "total_records": 647
  }
]
```

### Ledgers List
```
GET /api/ledgers/{guid}_{alterid}.json
```
**Example:**
```
GET /api/ledgers/8fdcfdd1_71cc_4873_99c6_95735225388e_102209_0.json
```
**Response:**
```json
[
  {
    "name": "Ledger Name",
    "count": 10
  }
]
```

### Ledger Data
```
GET /api/ledger-data/{guid}_{alterid}?ledger=Ledger%20Name
```

### Outstanding Data
```
GET /api/outstanding-data/{guid}_{alterid}
```

### Dashboard Data
```
GET /api/dashboard-data/{guid}_{alterid}
```

## Browser Console Commands

Test API directly in browser console:

```javascript
// Test companies API
fetch('api/companies.json')
  .then(r => r.json())
  .then(data => console.log('Companies:', data))
  .catch(e => console.error('Error:', e));

// Test ledgers API (replace with actual guid/alterid)
fetch('api/ledgers/8fdcfdd1_71cc_4873_99c6_95735225388e_102209_0.json')
  .then(r => r.json())
  .then(data => console.log('Ledgers:', data))
  .catch(e => console.error('Error:', e));
```

## Quick Fixes Checklist

- [ ] Database file exists (`TallyConnectDb.db`)
- [ ] At least one company is synced
- [ ] Company has vouchers in database
- [ ] Portal server is running
- [ ] Browser can access `localhost:8000`
- [ ] API endpoints return JSON (not HTML)
- [ ] No CORS errors in browser console
- [ ] No JavaScript errors in browser console
- [ ] Network requests show 200 status (not 404/500)

## Still Not Working?

1. **Run diagnostic tool:**
   ```bash
   python scripts/diagnose_portal.py
   ```

2. **Check server logs:**
   - Look at portal server console
   - Check for error messages
   - Verify database path

3. **Check browser:**
   - F12 → Console tab
   - F12 → Network tab
   - Look for failed requests

4. **Verify data:**
   - Open database with SQLite browser
   - Check companies table
   - Check vouchers table

5. **Test API directly:**
   - Open: `http://localhost:8000/api/companies.json`
   - Should return JSON, not HTML

## Contact Support

If issue persists:
1. Run diagnostic tool and save output
2. Take screenshot of browser console (F12)
3. Check server console for errors
4. Provide all information for debugging

