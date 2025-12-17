# Sync Logs Table - Explanation (मराठी)

## Sync Logs Table मध्ये काय दिसेल?

Sync Logs page (`sync-logs.html`) मध्ये एक table आहे ज्यामध्ये सर्व sync operations ची माहिती दिसते.

### Table Columns (स्तंभ):

1. **Timestamp** - Log कधी create झाला (Date & Time)
2. **Company** - Company चे नाव
3. **Level** - Log level (INFO, WARNING, ERROR, SUCCESS) - रंगीन badges
4. **Status** - Sync status (started, in_progress, completed, failed) - रंगीन badges
5. **Message** - Log message + details + error (if any)
6. **Records** - किती vouchers synced झाले
7. **Duration** - Sync किती वेळ लागला (seconds)

---

## Log Types आणि Table मध्ये काय दिसेल:

### ✅ 1. Sync Started
**Table मध्ये दिसेल:**
- **Timestamp**: Sync start time
- **Company**: Company name
- **Level**: `INFO` (निळा badge)
- **Status**: `started` (निळा badge)
- **Message**: "Sync started for [Company Name]"
- **Details**: "Date range: 01-04-2021 to 31-03-2026"
- **Records**: `-` (अजून नाही)
- **Duration**: `-` (अजून नाही)

**Example:**
```
Timestamp: 16-12-2025, 11:20:06
Company: Vrushali Infotech Pvt Ltd -21 -25
Level: INFO (blue)
Status: started (blue)
Message: Sync started for Vrushali Infotech Pvt Ltd -21 -25
Details: Date range: 01-04-2021 to 31-03-2026
Records: -
Duration: -
```

---

### ✅ 2. Vouchers Inserted (Progress)
**Table मध्ये दिसेल:**
- **Timestamp**: Batch insert time
- **Company**: Company name
- **Level**: `INFO` (निळा badge)
- **Status**: `in_progress` (नारंगी badge)
- **Message**: "Batch 10: 100 vouchers inserted"
- **Details**: "Total inserted so far: 1000 vouchers"
- **Records**: `1,000` (अजून synced)
- **Duration**: `-`

**Example:**
```
Timestamp: 16-12-2025, 11:20:07
Company: Vrushali Infotech Pvt Ltd -21 -25
Level: INFO (blue)
Status: in_progress (orange)
Message: Batch 10: 100 vouchers inserted
Details: Total inserted so far: 1000 vouchers
Records: 1,000
Duration: -
```

**Note:** हे logs every 10 batches मध्ये दिसतील (too many logs टाळण्यासाठी)

---

### ✅ 3. Voucher Count Verification
**Table मध्ये दिसेल:**

**Case A: Match (सर्व ठीक):**
- **Level**: `INFO` (निळा badge)
- **Status**: `completed` (हिरवा badge)
- **Message**: "Voucher insertion verified: 28038 vouchers in database"
- **Details**: "All 28038 vouchers successfully inserted"
- **Records**: `28,038`

**Case B: Mismatch (समस्या):**
- **Level**: `WARNING` (नारंगी badge)
- **Status**: `completed` (हिरवा badge)
- **Message**: "Voucher count mismatch: Expected 28038, Actual in DB: 0"
- **Details**: "Sync reported 28038 vouchers but database has 0 vouchers"
- **Records**: `0`

**Example (Mismatch):**
```
Timestamp: 16-12-2025, 11:20:13
Company: Vrushali Infotech Pvt Ltd -21 -25
Level: WARNING (orange)
Status: completed (green)
Message: Voucher count mismatch: Expected 28038, Actual in DB: 0
Details: Sync reported 28038 vouchers but database has 0 vouchers
Records: 0
Duration: -
```

---

### ✅ 4. Company Updated/Added
**Table मध्ये दिसेल:**

**Case A: Company Updated (अस्तित्वात होती):**
- **Level**: `INFO` (निळा badge)
- **Status**: `completed` (हिरवा badge)
- **Message**: "Company updated in database: total_records=28038, status=synced"
- **Details**: "Previous records: 0, New records: 28038"
- **Records**: `28,038`

**Case B: Company Added (नवीन):**
- **Level**: `INFO` (निळा badge)
- **Status**: `completed` (हिरवा badge)
- **Message**: "Company added to database: total_records=28038, status=synced"
- **Details**: "New company inserted: Vrushali Infotech Pvt Ltd -21 -25"
- **Records**: `28,038`

**Example (Added):**
```
Timestamp: 16-12-2025, 11:20:13
Company: Vrushali Infotech Pvt Ltd -21 -25
Level: INFO (blue)
Status: completed (green)
Message: Company added to database: total_records=28038, status=synced
Details: New company inserted: Vrushali Infotech Pvt Ltd -21 -25
Records: 28,038
Duration: -
```

---

### ✅ 5. Sync Completed
**Table मध्ये दिसेल:**
- **Timestamp**: Completion time
- **Company**: Company name
- **Level**: `SUCCESS` (हिरवा badge)
- **Status**: `completed` (हिरवा badge)
- **Message**: "Sync completed successfully: 28038 records synced in 7.25 seconds"
- **Details**: "Sync completed in 281 batches. Duration: 7.25 seconds"
- **Records**: `28,038`
- **Duration**: `7.25s`

**Example:**
```
Timestamp: 16-12-2025, 11:20:13
Company: Vrushali Infotech Pvt Ltd -21 -25
Level: SUCCESS (green)
Status: completed (green)
Message: Sync completed successfully: 28038 records synced in 7.25 seconds
Details: Sync completed in 281 batches. Duration: 7.25 seconds
Records: 28,038
Duration: 7.25s
```

---

### ❌ 6. Sync Failed
**Table मध्ये दिसेल:**
- **Timestamp**: Failure time
- **Company**: Company name
- **Level**: `ERROR` (लाल badge)
- **Status**: `failed` (लाल badge)
- **Message**: "Sync failed: [Error Message]"
- **Details**: "Sync failed after 5.23 seconds. Error: Connection timeout"
- **Error Message**: "Connection timeout to Tally DSN"
- **Records**: `5,000` (failure आधी synced)
- **Duration**: `5.23s`

**Example:**
```
Timestamp: 16-12-2025, 11:20:10
Company: Vrushali Infotech Pvt Ltd -21 -25
Level: ERROR (red)
Status: failed (red)
Message: Sync failed: Connection timeout
Details: Sync failed after 5.23 seconds. Error: Connection timeout to Tally DSN
Error: Connection timeout to Tally DSN
Records: 5,000
Duration: 5.23s
```

---

## Filters (Table वर):

1. **Company Filter** - Specific company चे logs दाखवा
2. **Level Filter** - INFO, WARNING, ERROR, SUCCESS
3. **Status Filter** - started, in_progress, completed, failed

---

## Summary:

**Sync Logs Table मध्ये आपल्याला दिसेल:**
- ✅ Sync कधी start झाला
- ✅ Vouchers insert होत आहेत का (progress)
- ✅ Vouchers खरोखर database मध्ये आहेत का (verification)
- ✅ Company update/insert झाला का
- ✅ Sync complete झाला का (किती records, किती वेळ)
- ❌ Sync fail झाला का (कुठे, काय error)

**हे सर्व logs database मध्ये store होतात आणि `sync-logs.html` page मध्ये table format मध्ये दिसतात.**

