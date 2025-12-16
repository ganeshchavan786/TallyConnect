# Tally Style Ledger Report Fix

## Problem Identified

**User Feedback:**
- Current ledger report shows both Debit and Credit in the same row
- Tally shows only Debit OR Credit per row (not both)
- Particulars column should show the OTHER ledger/party name (not narration)

## Tally's Format

In Tally, when viewing a ledger:
- Each row shows **either Debit OR Credit** (not both)
- **Particulars** column shows the **other ledger/party** involved in the transaction
- Example:
  - Receipt voucher (36):
    - Row 1: Date, "IndusInd Bank Limited" (other party), Receipt, 36, (empty), 21,240.00 (Credit)
    - Row 2: Date, "A P HOLDINGS PVT.LTD" (or other party), Receipt, 36, 21,240.00 (Debit), (empty)

## Solution Implemented

### 1. Updated SQL Query (`backend/database/queries.py`)
- Modified `LEDGER_TRANSACTIONS` query to find other ledgers in the same voucher
- Uses subquery to get other party/ledger names as "Particulars"
- Parameters: 10 parameters (4 for filtering other ledgers, 6 for main query)

### 2. Updated Backend Processing (`backend/portal_server.py`)
- Split debit and credit into separate rows if both exist
- Calculate running balance correctly for each entry
- Include "particulars" field in response

### 3. Updated Frontend Display (`frontend/portal/index.html`)
- Use "particulars" field instead of "narration" for display
- Show only debit OR credit per row (Tally style)
- Updated export functions to use "particulars"

## Key Changes

### Query Logic:
```sql
-- For each ledger entry, find other ledgers in the same voucher
SELECT 
    v1.vch_date,
    v1.vch_type,
    v1.vch_no,
    -- Subquery to get other party/ledger as Particulars
    COALESCE(
        (SELECT GROUP_CONCAT(other_ledger_name)
         FROM vouchers v2
         WHERE same_voucher AND different_ledger),
        v1.vch_narration,
        '-'
    ) as particulars,
    v1.vch_dr_amt as debit,
    v1.vch_cr_amt as credit
FROM vouchers v1
WHERE current_ledger
```

### Backend Processing:
- If both debit and credit exist → create 2 separate rows
- If only debit → single row with debit
- If only credit → single row with credit
- Calculate balance incrementally

### Frontend Display:
- Use `trans.particulars` for "Particulars" column
- Show debit OR credit (not both in same cell)
- Tally-style date formatting (DD-MMM-YY)

## Testing

1. **View Ledger Report:**
   - Select company
   - Select ledger
   - Check if "Particulars" shows other party name
   - Verify only Debit OR Credit per row

2. **Export Functions:**
   - CSV export should include "Particulars"
   - Excel export should include "Particulars"
   - PDF export should match display

## Status

✅ **Query Updated** - Finds other ledgers in same voucher
✅ **Backend Updated** - Splits debit/credit into separate rows
✅ **Frontend Updated** - Uses "particulars" field
✅ **Export Updated** - Includes "particulars" in exports

---

**Date:** December 2025  
**Issue:** Ledger report not matching Tally format  
**Status:** ✅ Fixed

