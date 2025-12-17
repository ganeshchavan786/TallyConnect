# TallyConnect EXE Build & Working Explanation

## 📋 Overview

या document मध्ये TallyConnect EXE कसा build होतो, कोणती files लागतात, आणि Tally सोबत SQL query request/response कसा काम करतो हे समजावले आहे.

---

## 🏗️ EXE Build Process

### Files Needed for EXE

#### 1. **Main Application File**
- **File**: `backend/app.py`
- **Purpose**: Main application logic, UI, sync worker
- **Location in EXE**: Included as main entry point

#### 2. **Backend Files** (All included)
```
backend/
├── app.py                    # Main application
├── config/
│   ├── settings.py          # Configuration (Tally queries, DB path)
│   └── themes.py            # UI themes
├── database/
│   ├── connection.py        # SQLite database initialization
│   ├── company_dao.py      # Company CRUD operations
│   ├── sync_log_dao.py    # Sync log operations
│   └── queries.py          # Database queries
├── utils/
│   ├── sync_logger.py      # Sync logging
│   ├── error_handler.py    # Error handling
│   └── portal_starter.py   # Portal startup
├── portal_server.py        # Web portal server
└── report_generator.py    # Report generation
```

#### 3. **Frontend Files** (All included)
```
frontend/
├── portal/                 # Web UI files (HTML, CSS, JS)
├── static/                 # Static assets
└── templates/             # HTML templates
```

#### 4. **Build Configuration**
- **File**: `build-config/TallyConnect.spec`
- **Purpose**: PyInstaller specification file
- **Defines**: Which files to include, how to package

#### 5. **Build Script**
- **File**: `build-config/build.bat`
- **Purpose**: Automated build process
- **Steps**: Clean → Build → Package → Installer

---

## 🔨 How EXE is Built

### Step 1: Build Script Execution
```batch
build-config/build.bat
```

### Step 2: PyInstaller Process
1. **Reads** `TallyConnect.spec` file
2. **Includes** all files specified:
   - `backend/` folder (all Python files)
   - `frontend/` folder (all UI files)
   - Hidden imports (pyodbc, sqlite3, tkinter, etc.)
3. **Packages** everything into single EXE
4. **Creates** `dist/TallyConnect.exe`

### Step 3: What Gets Included

From `TallyConnect.spec`:
```python
datas=[
    ('frontend', 'frontend'),      # Frontend files
    ('backend', 'backend'),        # Backend files
],
hiddenimports=[
    'pyodbc',                      # Tally ODBC connection
    'sqlite3',                     # SQLite database
    'tkinter',                     # UI framework
    'backend',                     # Backend modules
    'backend.database',            # Database modules
    'backend.config',              # Config modules
    # ... more imports
],
```

### Step 4: Final EXE Structure
```
TallyConnect.exe (Single file)
├── Python runtime
├── All backend code
├── All frontend files
├── Dependencies (pyodbc, sqlite3, etc.)
└── Embedded resources
```

---

## 🚀 How EXE Works

### Application Startup Flow

```
1. User double-clicks TallyConnect.exe
   ↓
2. PyInstaller extracts files to temp directory
   ↓
3. Python runtime starts
   ↓
4. backend/app.py loads
   ↓
5. UI window opens (Tkinter)
   ↓
6. Database initialized (SQLite)
   ↓
7. Ready for user interaction
```

---

## 🔌 Tally ODBC Connection Flow

### Step 1: DSN Detection
```python
# Location: backend/app.py - auto_detect_dsn()

1. Try common DSN names:
   - TallyODBC64_9000
   - TallyODBC64_9001
   - TallyODBC64_9999
   - TallyODBC64_9002

2. For each DSN:
   - Try to connect: pyodbc.connect(f"DSN={dsn_name}")
   - Execute test query: SELECT $Name, $GUID, $AlterID FROM Company
   - If successful → DSN found
```

### Step 2: Connection Establishment
```python
# Location: backend/app.py - _sync_worker()

conn = pyodbc.connect(f"DSN={dsn_name};", timeout=5)
cur = conn.cursor()
```

**What Happens**:
- EXE connects to Tally via ODBC driver
- Tally must be running
- ODBC driver must be installed
- Connection uses DSN (Data Source Name)

---

## 📤 Tally SQL Query Request/Response Flow

### Complete Flow Diagram

```
┌─────────────┐
│   EXE App   │
│ (TallyConnect)
└──────┬──────┘
       │
       │ 1. User clicks "Sync"
       │
       ▼
┌─────────────────┐
│  _sync_worker() │
│  (Thread)       │
└──────┬──────────┘
       │
       │ 2. Connect to Tally
       │    pyodbc.connect("DSN=TallyODBC64_9000")
       │
       ▼
┌─────────────────┐
│  Tally ODBC     │
│  Connection     │
└──────┬──────────┘
       │
       │ 3. Build SQL Query
       │    VOUCHER_QUERY_TEMPLATE.format(...)
       │
       ▼
┌─────────────────────────────────────────┐
│  SQL Query (Example)                    │
│  ─────────────────────────────────────  │
│  SELECT $OwnerCompany, $OwnerGUID,      │
│         $OnwerAlterID, $VchDate,        │
│         $VchType, $VchNo, ...           │
│  FROM TallyVchLedCollectionCMP          │
│  WHERE $OwnerGUID = '8fdcfdd1-...'      │
│    AND $VchDate >= $$Date:"01-04-2025"  │
│    AND $VchDate <= $$Date:"31-03-2026"  │
└──────┬──────────────────────────────────┘
       │
       │ 4. Execute Query
       │    cur.execute(query)
       │
       ▼
┌─────────────────┐
│     Tally       │
│   (Database)    │
└──────┬──────────┘
       │
       │ 5. Tally Processes Query
       │    (May take 2-5 minutes for large data)
       │
       │ 6. Tally Returns Results
       │    (Row by row, in batches)
       │
       ▼
┌─────────────────┐
│  EXE Receives   │
│  Results        │
└──────┬──────────┘
       │
       │ 7. Fetch in Batches
       │    rows = cur.fetchmany(5000)
       │
       │ 8. Filter by AlterID
       │    (Only process matching rows)
       │
       │ 9. Insert to SQLite
       │    INSERT INTO vouchers ...
       │
       ▼
┌─────────────────┐
│  SQLite Database│
│  (Local)        │
└─────────────────┘
```

---

## 📝 Detailed SQL Query Flow

### Step 1: Query Construction

**Location**: `backend/config/settings.py`

```python
VOUCHER_QUERY_TEMPLATE = """
SELECT $OwnerCompany, $OwnerGUID, $OnwerAlterID, $VchDate, $VchType, $VchNo, $VchLedName,
       $VchLedAmount, $VchDrCr, $VchLedDrAmt, $VchLedCrAmt, $VchPartyName, $VchLedParent,
       $VchNarration, $VchGstin, $VchLedGstin, $VchLedBillRef, $VchLedBillType, $VchLedPrimaryGrp,
       $VchLedNature, $VchLedBSGrp, $VchLedBSGrpNature, $VchIsOptional, $VchMstID, $VchledbillCount
FROM TallyVchLedCollectionCMP
WHERE $OwnerGUID = '{guid}'
  AND $VchDate >= $$Date:"{from_date}"
  AND $VchDate <= $$Date:"{to_date}"
"""
```

**Example Query** (After formatting):
```sql
SELECT $OwnerCompany, $OwnerGUID, $OnwerAlterID, $VchDate, $VchType, $VchNo, $VchLedName,
       $VchLedAmount, $VchDrCr, $VchLedDrAmt, $VchLedCrAmt, $VchPartyName, $VchLedParent,
       $VchNarration, $VchGstin, $VchLedGstin, $VchLedBillRef, $VchLedBillType, $VchLedPrimaryGrp,
       $VchLedNature, $VchLedBSGrp, $VchLedBSGrpNature, $VchIsOptional, $VchMstID, $VchledbillCount
FROM TallyVchLedCollectionCMP
WHERE $OwnerGUID = '8fdcfdd1-71cc-4873-9...'
  AND $VchDate >= $$Date:"01-04-2025"
  AND $VchDate <= $$Date:"31-03-2026"
```

### Step 2: Query Execution

**Location**: `backend/app.py` - `_execute_window()` function

```python
# 1. Format query with parameters
q = VOUCHER_QUERY_TEMPLATE.format(guid=guid, from_date=f_d, to_date=t_d)

# 2. Execute query (sends to Tally)
cur.execute(q)

# 3. Tally processes query (may take 2-5 minutes)
#    - Tally reads from its database
#    - Filters by GUID and date range
#    - Prepares results

# 4. Fetch results in batches
rows = cur.fetchmany(5000)  # Get 5000 rows at a time
```

### Step 3: Response Processing

**Location**: `backend/app.py` - `_sync_worker()` function

```python
# Tally returns rows like this:
# Each row is a tuple with 25 columns:
row = (
    'Company Name',           # $OwnerCompany
    '8fdcfdd1-...',          # $OwnerGUID
    '95278.0',               # $OnwerAlterID
    '15-04-2025',            # $VchDate
    'Sales',                  # $VchType
    '1',                     # $VchNo
    'Customer Name',         # $VchLedName
    10000.00,                # $VchLedAmount
    'Dr',                    # $VchDrCr
    # ... more columns
)

# Process each row:
for r in rows:
    # Extract AlterID from Tally response
    tally_alterid = r[2]  # Column index 2
    
    # Filter: Only process if AlterID matches
    if str(tally_alterid) != str(target_alterid):
        continue  # Skip this row
    
    # Extract other fields
    vch_date = r[3]
    vch_type = r[4]
    # ... etc
    
    # Prepare for SQLite insert
    params.append((guid, alterid, name, vch_date, ...))
```

### Step 4: Data Storage

```python
# Insert into SQLite database
INSERT INTO vouchers (
    company_guid, company_alterid, company_name,
    vch_date, vch_type, vch_no, ...
) VALUES (?, ?, ?, ?, ?, ?, ...)
```

---

## 🔄 Complete Example Flow

### Scenario: Sync "Vrushali Infotech Pvt Ltd -21 -25"

#### Step 1: User Action
```
User clicks "Sync" button
↓
Selects date range: 01-04-2025 to 31-03-2026
```

#### Step 2: EXE Processing
```python
# backend/app.py - sync_selected()
1. Get company details (GUID, AlterID)
2. Start sync thread
3. Call _sync_worker()
```

#### Step 3: Tally Connection
```python
# Connect to Tally
conn = pyodbc.connect("DSN=TallyODBC64_9000")
cur = conn.cursor()
```

#### Step 4: Query Construction
```python
# Build query
query = """
SELECT ... FROM TallyVchLedCollectionCMP
WHERE $OwnerGUID = '8fdcfdd1-71cc-4873-9...'
  AND $VchDate >= $$Date:"01-04-2025"
  AND $VchDate <= $$Date:"31-03-2026"
"""
```

#### Step 5: Send Query to Tally
```python
# Execute query (sends to Tally)
cur.execute(query)

# Tally processes:
# - Reads voucher data
# - Filters by GUID and date
# - Prepares results
# (Takes 2-5 minutes for large data)
```

#### Step 6: Receive Results
```python
# Fetch in batches
while True:
    rows = cur.fetchmany(5000)  # Get 5000 rows
    if not rows:
        break  # No more data
    
    # Process each row
    for row in rows:
        # Filter by AlterID
        if row[2] != target_alterid:
            continue
        
        # Extract data
        vch_date = row[3]
        vch_type = row[4]
        # ... etc
        
        # Insert to SQLite
        insert_to_database(...)
```

#### Step 7: Store in SQLite
```python
# Insert vouchers
INSERT INTO vouchers VALUES (...)
# Commit transaction
db_conn.commit()
```

#### Step 8: Update Company Status
```python
# Update company record
UPDATE companies 
SET status = 'synced', 
    total_records = 644,
    last_sync = '2025-12-16 17:30:00'
WHERE guid = '...' AND alterid = '95278.0'
```

---

## 📊 Key Points

### 1. Tally Query Format
- Uses **Tally-specific syntax**: `$OwnerGUID`, `$$Date:"..."`, etc.
- **Not standard SQL** - Tally's custom query language
- Queries **TallyVchLedCollectionCMP** table (Tally's internal structure)

### 2. Response Format
- Tally returns **rows as tuples**
- Each row has **25 columns** (voucher fields)
- Results come **in batches** (not all at once)

### 3. Processing Time
- **Query execution**: 2-5 minutes for large date ranges
- **First batch fetch**: 2-5 minutes (Tally processing)
- **Subsequent batches**: Faster (already processed)

### 4. AlterID Filtering
- **CRITICAL**: Tally returns vouchers for ALL AlterIDs
- Must filter at application level
- Only insert vouchers matching target AlterID

### 5. Database Storage
- **SQLite** (local database)
- **Batch inserts** (5000 vouchers per batch)
- **Thread-safe** (using locks)

---

## 🛠️ EXE Dependencies

### Required at Runtime
1. **Tally** - Must be running
2. **Tally ODBC Driver** - Must be installed
3. **ODBC DSN** - Must be configured (TallyODBC64_9000, etc.)

### Included in EXE
1. **Python runtime** - Embedded
2. **pyodbc** - ODBC connection library
3. **sqlite3** - Database library
4. **tkinter** - UI framework
5. **All backend/frontend code** - Embedded

---

## 📁 File Structure in EXE

When EXE runs, files are extracted to temp directory:
```
C:\Users\...\AppData\Local\Temp\_MEIxxxxx\
├── backend/
│   ├── app.py
│   ├── config/
│   ├── database/
│   └── utils/
├── frontend/
│   ├── portal/
│   └── templates/
└── TallyConnectDb.db (created in EXE directory)
```

**Note**: Database file (`TallyConnectDb.db`) is created in **same directory as EXE**, not in temp folder.

---

## 🔍 Troubleshooting

### EXE Not Connecting to Tally
1. **Check Tally is running**
2. **Check ODBC DSN exists**: Control Panel → ODBC Data Sources
3. **Check DSN name**: Should be `TallyODBC64_9000` (or similar)
4. **Check Tally ODBC port**: Usually 9000, 9001, 9999

### Query Taking Too Long
1. **Normal for large date ranges**: 2-5 minutes is expected
2. **First batch always slow**: Tally needs to process data
3. **Use smaller date ranges**: Split into multiple syncs

### No Data Returned
1. **Check date range**: Ensure vouchers exist in that range
2. **Check GUID**: Verify company GUID is correct
3. **Check Tally data**: Ensure Tally has vouchers

---

## 📝 Summary

### EXE Build
- **Input**: `backend/app.py` + all backend/frontend files
- **Process**: PyInstaller packages everything
- **Output**: `TallyConnect.exe` (single file)

### EXE Working
1. **Starts**: Loads UI, initializes database
2. **Connects**: To Tally via ODBC
3. **Queries**: Sends SQL to Tally
4. **Receives**: Data from Tally
5. **Stores**: In SQLite database
6. **Displays**: In UI/Portal

### Tally Communication
- **Request**: SQL query (Tally syntax)
- **Response**: Rows of voucher data
- **Format**: Tuples with 25 columns
- **Processing**: Batch by batch (5000 rows)

---

**Last Updated**: December 2025  
**Version**: 5.6+

