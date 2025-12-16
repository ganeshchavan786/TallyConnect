# Ledger Report - Database Fields Required

## VOUCHERS Table Structure

### All Available Fields (27 total):
1. `id` - INTEGER (Primary key)
2. `company_guid` - TEXT
3. `company_alterid` - TEXT
4. `company_name` - TEXT
5. `vch_date` - TEXT ⭐
6. `vch_type` - TEXT ⭐
7. `vch_no` - TEXT ⭐
8. `vch_mst_id` - TEXT
9. `led_name` - TEXT ⭐
10. `led_amount` - REAL
11. `vch_dr_cr` - TEXT
12. `vch_dr_amt` - REAL ⭐
13. `vch_cr_amt` - REAL ⭐
14. `vch_party_name` - TEXT ⭐
15. `vch_led_parent` - TEXT
16. `vch_narration` - TEXT ⭐
17. `vch_gstin` - TEXT
18. `vch_led_gstin` - TEXT
19. `vch_led_bill_ref` - TEXT
20. `vch_led_bill_type` - TEXT
21. `vch_led_primary_grp` - TEXT
22. `vch_led_nature` - TEXT
23. `vch_led_bs_grp` - TEXT
24. `vch_led_bs_grp_nature` - TEXT
25. `vch_is_optional` - TEXT
26. `vch_led_bill_count` - INTEGER
27. `created_at` - TEXT

---

## Fields Used in Ledger Report (⭐ = Required)

### **Core Fields (Mandatory):**

1. **`vch_date`** ⭐
   - **Purpose:** Transaction date
   - **Usage:** Display date, sorting, date range filtering
   - **Format:** YYYY-MM-DD (stored), DD-MM-YYYY (displayed)

2. **`vch_type`** ⭐
   - **Purpose:** Voucher type (Sales, Purchase, Receipt, Payment, etc.)
   - **Usage:** Display in "Vch Type" column

3. **`vch_no`** ⭐
   - **Purpose:** Voucher number
   - **Usage:** Display in "Vch No." column, grouping vouchers

4. **`vch_dr_amt`** ⭐
   - **Purpose:** Debit amount for this ledger entry
   - **Usage:** Calculate debit, running balance, totals

5. **`vch_cr_amt`** ⭐
   - **Purpose:** Credit amount for this ledger entry
   - **Usage:** Calculate credit, running balance, totals

6. **`vch_party_name`** ⭐
   - **Purpose:** Party/Ledger name (for matching selected ledger)
   - **Usage:** 
     - Filter transactions for selected ledger
     - Find counter ledger (Particulars)

7. **`led_name`** ⭐
   - **Purpose:** Ledger name (alternative to vch_party_name)
   - **Usage:**
     - Filter transactions for selected ledger
     - Find counter ledger (Particulars)

8. **`vch_narration`** ⭐
   - **Purpose:** Transaction narration/description
   - **Usage:** Fallback for Particulars if counter ledger not found

### **Supporting Fields:**

9. **`company_guid`** ⭐
   - **Purpose:** Company identifier
   - **Usage:** Filter transactions by company

10. **`company_alterid`** ⭐
    - **Purpose:** Company alternate ID
    - **Usage:** Filter transactions by company

11. **`vch_mst_id`** (Optional)
    - **Purpose:** Voucher master ID
    - **Usage:** Grouping related voucher entries

---

## How Fields Are Used in SQL Query

### Current Query Structure:

```sql
WITH ledger_vouchers AS (
    SELECT 
        vch_date,           -- Date
        vch_type,           -- Voucher Type
        vch_no,             -- Voucher Number
        company_guid,       -- Company filter
        company_alterid,    -- Company filter
        SUM(vch_dr_amt) as total_debit,    -- Debit amount
        SUM(vch_cr_amt) as total_credit,    -- Credit amount
        MAX(vch_narration) as narration     -- Narration
    FROM vouchers
    WHERE company_guid = ? 
        AND company_alterid = ?
        AND (vch_party_name LIKE ? OR led_name LIKE ?)  -- Selected ledger match
        AND vch_date BETWEEN ? AND ?        -- Date range
    GROUP BY vch_date, vch_no, vch_type
)
SELECT 
    date,
    voucher_type,
    voucher_number,
    particulars,           -- Counter ledger (from subquery)
    debit,                 -- Total debit per voucher
    credit,                -- Total credit per voucher
    narration              -- Narration
FROM ledger_vouchers
```

---

## Field Mapping to Report Columns

| Report Column | Database Field(s) | Notes |
|---------------|-------------------|-------|
| **Date** | `vch_date` | Formatted as DD-MM-YYYY |
| **Particulars** | `led_name` or `vch_party_name` (from OTHER ledger in same voucher) | Counter ledger name |
| **Vch Type** | `vch_type` | Voucher type |
| **Vch No.** | `vch_no` | Voucher number |
| **Debit** | `vch_dr_amt` (SUM per voucher) | Only if debit > 0 |
| **Credit** | `vch_cr_amt` (SUM per voucher) | Only if credit > 0 |
| **Balance** | Calculated from `vch_dr_amt` - `vch_cr_amt` | Running balance |

---

## Summary

### **Total Fields Used: 8 Core + 2 Supporting = 10 Fields**

**Core Fields (8):**
1. `vch_date` - Transaction date
2. `vch_type` - Voucher type
3. `vch_no` - Voucher number
4. `vch_dr_amt` - Debit amount
5. `vch_cr_amt` - Credit amount
6. `vch_party_name` - Party/Ledger name (for matching)
7. `led_name` - Ledger name (alternative matching)
8. `vch_narration` - Narration (fallback)

**Supporting Fields (2):**
9. `company_guid` - Company identifier
10. `company_alterid` - Company alternate ID

**Not Used (17 fields):**
- `id`, `company_name`, `vch_mst_id`, `led_amount`, `vch_dr_cr`
- `vch_led_parent`, `vch_gstin`, `vch_led_gstin`
- `vch_led_bill_ref`, `vch_led_bill_type`, `vch_led_primary_grp`
- `vch_led_nature`, `vch_led_bs_grp`, `vch_led_bs_grp_nature`
- `vch_is_optional`, `vch_led_bill_count`, `created_at`

---

## Notes

1. **Ledger Matching:** Uses both `vch_party_name` and `led_name` with LIKE pattern matching
2. **Voucher Grouping:** Groups by `vch_date`, `vch_no`, `vch_type` to show ONE line per voucher
3. **Counter Ledger:** Finds other ledgers in same voucher (same `vch_date` + `vch_no`) excluding selected ledger
4. **Amount Calculation:** Sums `vch_dr_amt` and `vch_cr_amt` per voucher for Tally-style display

