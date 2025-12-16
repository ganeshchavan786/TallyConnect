# Portal Startup Fix

## Problem
Portal server was not starting when running `main.py` or the EXE. Browser showed "ERR_CONNECTION_REFUSED" error.

## Root Cause
1. **Path Detection Issue:** `get_base_dir()` and `get_resource_dir()` in `portal_server.py` were returning the `backend` directory instead of the project root when running as a script.
2. **Silent Error Handling:** Errors were being silently caught, making it impossible to diagnose the issue.
3. **Portal Directory Not Found:** Server was looking for `frontend/portal` in the wrong location.

## Fixes Applied

### 1. Fixed Path Detection in `portal_server.py`
**Before:**
```python
def get_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))  # Returns backend/
```

**After:**
```python
def get_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # If we're in backend folder, go up one level to project root
        if os.path.basename(script_dir) == 'backend':
            return os.path.dirname(script_dir)  # Returns project root
        return script_dir
```

### 2. Improved Error Handling in `main.py`
- Added portal directory existence check before starting
- Added error logging to console
- Added error logging to file (`portal_startup_error.log`)
- Added server status verification after startup
- Better error messages with debug information

### 3. Better Startup Verification
- Checks if portal directory exists before attempting to start
- Verifies server is actually running by checking port
- Opens browser only if server is confirmed running
- Provides clear error messages if startup fails

## Testing

### Test Portal Startup:
```bash
python main.py
```

**Expected Output:**
```
[INFO] Portal directory found: D:\Project\...\frontend\portal
[SUCCESS] Portal server started on port 8000
[INFO] Portal opened in browser: http://localhost:8000
```

**If Portal Fails:**
```
[WARNING] Portal directory not found: ...
[DEBUG] Current directory: ...
[DEBUG] Project root: ...
[INFO] Portal will not start. Main app will continue.
```

## Verification

1. **Check Console Output:**
   - Look for `[SUCCESS] Portal server started` message
   - Check for any `[WARNING]` or `[ERROR]` messages

2. **Check Browser:**
   - Browser should automatically open to `http://localhost:8000`
   - Portal should load without "ERR_CONNECTION_REFUSED" error

3. **Check Log File:**
   - If portal fails, check `portal_startup_error.log` in project root
   - Contains detailed error information

4. **Manual Test:**
   - Open browser manually: `http://localhost:8000`
   - Should see portal dashboard

## Files Modified

1. ✅ `main.py` - Added better error handling and verification
2. ✅ `backend/portal_server.py` - Fixed path detection functions

## Status

✅ **Fixed** - Portal should now start automatically with main app.

---

**Date:** December 2025  
**Issue:** Portal not starting with main.py  
**Status:** ✅ Resolved

