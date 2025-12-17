# TallyConnect EXE - सोपी समज

## 🎯 EXE साठी कोणती Files लागतात?

### मुख्य Files:
1. **`backend/app.py`** - Main application (UI + Sync)
2. **`backend/config/settings.py`** - Tally queries defined here
3. **`backend/database/`** - Database operations
4. **`frontend/`** - Web UI files
5. **`build-config/TallyConnect.spec`** - Build configuration

### Build Process:
```
build-config/build.bat चालवा
    ↓
PyInstaller सर्व files package करते
    ↓
dist/TallyConnect.exe तयार होते
```

---

## 🔄 EXE कसा काम करतो?

### Step 1: EXE Start होतो
```
User double-clicks TallyConnect.exe
    ↓
UI window open होते
    ↓
Database initialize होते (SQLite)
```

### Step 2: Tally Connect होते
```
EXE → ODBC Driver → Tally
(DSN: TallyODBC64_9000)
```

### Step 3: SQL Query Request
```
EXE मध्ये query तयार होते:
SELECT ... FROM TallyVchLedCollectionCMP
WHERE $OwnerGUID = '...'
  AND $VchDate >= $$Date:"01-04-2025"
  AND $VchDate <= $$Date:"31-03-2026"
```

### Step 4: Tally Response
```
Tally query process करते (2-5 minutes)
    ↓
Tally data return करते (row by row)
    ↓
EXE receives data in batches (5000 rows)
```

### Step 5: Data Store
```
EXE filters data (AlterID match करते)
    ↓
SQLite database मध्ये insert करते
    ↓
Company status update करते
```

---

## 📤 Tally SQL Query Flow (सोपी भाषा)

### Request (EXE → Tally):
```
EXE: "मला या company चे vouchers द्या"
     GUID: 8fdcfdd1-...
     Date: 01-04-2025 to 31-03-2026

Tally: "ठीक आहे, process करत आहे..."
       (2-5 minutes wait)
```

### Response (Tally → EXE):
```
Tally: "हे data आहे:"
       Row 1: [Company, GUID, AlterID, Date, Type, ...]
       Row 2: [Company, GUID, AlterID, Date, Type, ...]
       ...
       (5000 rows per batch)

EXE: "ठीक आहे, मी store करत आहे..."
```

### Storage (EXE → SQLite):
```
EXE: "हे data SQLite मध्ये save करत आहे"
     - Filter by AlterID
     - Insert vouchers
     - Update company status
```

---

## 🔑 Key Points

### 1. Query Format
- **Tally-specific syntax** वापरते
- `$OwnerGUID`, `$$Date:"..."` - Tally चे special syntax
- Standard SQL नाही

### 2. Response Format
- Tally **tuples** मध्ये data देते
- प्रत्येक row मध्ये **25 columns**
- **Batch by batch** data येते (5000 rows)

### 3. Processing Time
- **Query execution**: 2-5 minutes (large data साठी)
- **First batch**: 2-5 minutes (Tally processing)
- **Next batches**: जलद (already processed)

### 4. AlterID Filtering
- **IMPORTANT**: Tally सर्व AlterIDs चे vouchers देते
- EXE मध्ये filter करावे लागते
- फक्त matching AlterID चे vouchers insert करावे

---

## 📁 EXE मध्ये काय असते?

### Included:
- ✅ Python runtime
- ✅ pyodbc (Tally connection)
- ✅ sqlite3 (Database)
- ✅ tkinter (UI)
- ✅ सर्व backend code
- ✅ सर्व frontend files

### Required (Runtime):
- ⚠️ Tally (running)
- ⚠️ Tally ODBC Driver (installed)
- ⚠️ ODBC DSN (configured)

---

## 🎬 Complete Example

### Scenario: "Vrushali Infotech" sync करणे

```
1. User clicks "Sync"
   ↓
2. EXE connects to Tally
   DSN: TallyODBC64_9000
   ↓
3. EXE sends query:
   "मला GUID 8fdcfdd1... चे vouchers द्या"
   "Date: 01-04-2025 to 31-03-2026"
   ↓
4. Tally processes (2-5 minutes)
   ↓
5. Tally returns data:
   Batch 1: 5000 rows
   Batch 2: 5000 rows
   ...
   ↓
6. EXE filters by AlterID
   (Only 95278.0 matching rows)
   ↓
7. EXE stores in SQLite
   INSERT INTO vouchers ...
   ↓
8. EXE updates company status
   Status: "synced"
   Total: 644 vouchers
```

---

## 🛠️ Build करणे

### Command:
```batch
cd build-config
build.bat
```

### Output:
```
dist/TallyConnect.exe
```

### What Happens:
1. PyInstaller reads `TallyConnect.spec`
2. Packages all files
3. Creates single EXE file
4. All dependencies included

---

## 📝 Summary

### EXE Build:
- **Input**: `backend/app.py` + सर्व files
- **Process**: PyInstaller packages
- **Output**: `TallyConnect.exe`

### EXE Working:
1. **Start** → UI open
2. **Connect** → Tally via ODBC
3. **Query** → SQL send to Tally
4. **Receive** → Data from Tally
5. **Store** → SQLite database
6. **Display** → UI/Portal

### Tally Communication:
- **Request**: SQL query (Tally syntax)
- **Response**: Voucher data (rows)
- **Format**: 25 columns per row
- **Processing**: Batch by batch

---

**Last Updated**: December 2025

