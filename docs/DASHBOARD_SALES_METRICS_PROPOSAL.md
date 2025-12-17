# Dashboard Sales Metrics/KPIs - Discussion Document

## Overview
Add Sales-specific metrics and KPIs to the Dashboard to provide better business insights. These metrics will use the same Sales Register data logic to ensure consistency.

## Proposed Sales Metrics/KPIs

### 1. **Sales Summary Cards** (Top Section)
Add 3-4 new metric cards alongside existing ones:

#### A. **Total Sales Amount** 💰
- **Description**: Total sales revenue for the period (Sales + GST)
- **Data Source**: Sales Register query (sum of all sales voucher amounts)
- **Display**: Large number with currency formatting
- **Color**: Green gradient (success color)
- **Calculation**: Sum of all credit amounts from Sales vouchers (matching Sales Register logic)

#### B. **Total Sales Count** 📊
- **Description**: Number of sales vouchers/transactions
- **Data Source**: Count of unique Sales vouchers
- **Display**: Number of sales transactions
- **Color**: Blue gradient
- **Calculation**: COUNT(DISTINCT voucher_key) from Sales vouchers

#### C. **Average Sales per Transaction** 📈
- **Description**: Average invoice value
- **Data Source**: Total Sales / Sales Count
- **Display**: Currency value
- **Color**: Purple gradient
- **Calculation**: Total Sales Amount / Total Sales Count

#### D. **Sales Growth %** (Optional - if period comparison available)
- **Description**: Month-over-month or period-over-period growth
- **Data Source**: Compare current period with previous period
- **Display**: Percentage with up/down arrow
- **Color**: Green (positive) / Red (negative)

---

### 2. **Sales Trend Chart** (New Section)
Visual representation of sales over time:

#### **Monthly Sales Trend**
- **Type**: Line chart or Bar chart
- **Data**: Monthly sales amounts (from Sales Register monthly summary)
- **X-axis**: Months (Apr, May, Jun, etc.)
- **Y-axis**: Sales Amount
- **Features**: 
  - Hover to see exact amount
  - Color-coded bars/lines
  - Show trend line if possible

---

### 3. **Top Sales Customers** (New Table)
Similar to Top Debtors/Creditors:

#### **Top 10 Sales Customers**
- **Columns**: 
  - Rank
  - Customer Name
  - Total Sales Amount
  - Number of Invoices
  - Average Invoice Value
- **Data Source**: Group Sales vouchers by customer (vch_party_name)
- **Sort**: By Total Sales Amount (descending)
- **Display**: Table with clickable rows (link to customer ledger)

---

### 4. **Sales by Voucher Type** (Enhanced)
If there are different sales voucher types:

#### **Sales Voucher Type Breakdown**
- **Columns**:
  - Voucher Type (e.g., Sales, Sales Return)
  - Count
  - Total Amount
  - Percentage of Total Sales
- **Display**: Table or Pie chart

---

### 5. **Sales Period Comparison** (Optional)
Compare current period with previous period:

#### **Period-over-Period Comparison**
- **Metrics**:
  - Current Period Sales
  - Previous Period Sales
  - Change Amount
  - Change Percentage
- **Display**: Side-by-side cards with comparison

---

## Implementation Approach

### Backend Changes Required:

1. **New Query in `queries.py`**:
```sql
# Dashboard - Sales Summary
DASHBOARD_SALES_SUMMARY = """
    SELECT 
        COUNT(DISTINCT COALESCE(NULLIF(TRIM(vch_mst_id), ''), vch_date || '|' || vch_no)) as total_sales_count,
        SUM(vch_cr_amt) as total_sales_amount
    FROM vouchers
    WHERE company_guid = ?
        AND company_alterid = ?
        AND UPPER(TRIM(vch_type)) = 'SALES'
        AND vch_cr_amt > 0
"""

# Dashboard - Top Sales Customers
TOP_SALES_CUSTOMERS = """
    SELECT 
        vch_party_name as customer_name,
        SUM(vch_cr_amt) as total_sales,
        COUNT(DISTINCT COALESCE(NULLIF(TRIM(vch_mst_id), ''), vch_date || '|' || vch_no)) as invoice_count
    FROM vouchers
    WHERE company_guid = ?
        AND company_alterid = ?
        AND UPPER(TRIM(vch_type)) = 'SALES'
        AND vch_party_name IS NOT NULL
        AND vch_party_name != ''
        AND vch_cr_amt > 0
    GROUP BY vch_party_name
    ORDER BY SUM(vch_cr_amt) DESC
    LIMIT 10
"""

# Dashboard - Monthly Sales Trend
MONTHLY_SALES_TREND = """
    SELECT 
        strftime('%Y-%m', vch_date) as month_key,
        strftime('%b %Y', vch_date) as month_name,
        SUM(vch_cr_amt) as sales_amount,
        COUNT(DISTINCT COALESCE(NULLIF(TRIM(vch_mst_id), ''), vch_date || '|' || vch_no)) as sales_count
    FROM vouchers
    WHERE company_guid = ?
        AND company_alterid = ?
        AND UPPER(TRIM(vch_type)) = 'SALES'
        AND vch_cr_amt > 0
    GROUP BY month_key
    ORDER BY month_key
"""
```

2. **Update `portal_server.py` - `send_dashboard_data()`**:
   - Add queries for sales summary, top customers, monthly trend
   - Include in response JSON

### Frontend Changes Required:

1. **Update `dashboard.js` - `renderDashboardReport()`**:
   - Add Sales Summary Cards section (3-4 cards)
   - Add Monthly Sales Trend chart/table
   - Add Top Sales Customers table
   - Update layout to accommodate new sections

2. **CSS Styling**:
   - Add styles for sales metric cards
   - Chart styling (if using charts)
   - Responsive layout adjustments

---

## Layout Proposal

```
┌─────────────────────────────────────────────────────────┐
│  Dashboard Header                                        │
├─────────────────────────────────────────────────────────┤
│  [General Stats Cards]                                   │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐                   │
│  │Total │ │Total │ │ Net  │ │Sales │  ← New Sales Card │
│  │Trans │ │Parties│ │Balance│ │Amount│                   │
│  └──────┘ └──────┘ └──────┘ └──────┘                   │
├─────────────────────────────────────────────────────────┤
│  [Sales Summary Cards]  ← NEW SECTION                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                │
│  │Total     │ │Sales     │ │Avg Sales │                │
│  │Sales     │ │Count     │ │per Trans │                │
│  │Amount    │ │          │ │          │                │
│  └──────────┘ └──────────┘ └──────────┘                │
├─────────────────────────────────────────────────────────┤
│  [Monthly Sales Trend]  ← NEW CHART/TABLE                │
│  ┌─────────────────────────────────────┐                │
│  │  Sales Amount by Month (Chart)      │                │
│  └─────────────────────────────────────┘                │
├─────────────────────────────────────────────────────────┤
│  [Top Sales Customers]  ← NEW TABLE                      │
│  ┌─────────────────────────────────────┐                │
│  │  Rank │ Customer │ Amount │ Invoices │                │
│  └─────────────────────────────────────┘                │
├─────────────────────────────────────────────────────────┤
│  [Top Debtors]  [Top Creditors]  (Existing)              │
└─────────────────────────────────────────────────────────┘
```

---

## Data Consistency

**Important**: Use the **same Sales Register logic** to ensure:
- Sales amounts match Sales Register report
- Same voucher identification logic (vch_mst_id or vch_date+vch_no)
- Same amount calculation (sum of all credit lines for Sales vouchers)

---

## Questions for Discussion

1. **Which metrics are most important?**
   - Total Sales Amount? ✅ (Must have)
   - Sales Count? ✅ (Must have)
   - Average Sales per Transaction? (Nice to have)
   - Sales Growth %? (Requires period comparison)

2. **Chart Library?**
   - Simple HTML/CSS tables?
   - Chart.js (lightweight, easy to integrate)?
   - Google Charts?
   - No charts, just tables?

3. **Period Selection?**
   - Show current financial year?
   - Allow period selection (From/To Date)?
   - Show last 12 months?

4. **Top Customers Count?**
   - Top 5?
   - Top 10?
   - Configurable?

5. **Priority Order?**
   - Phase 1: Sales Summary Cards (Total Sales, Count, Average)
   - Phase 2: Top Sales Customers table
   - Phase 3: Monthly Sales Trend chart
   - Phase 4: Period comparison (if needed)

---

## Recommendation

**Start with Phase 1** (Sales Summary Cards):
- ✅ Total Sales Amount
- ✅ Total Sales Count  
- ✅ Average Sales per Transaction

These are the most important metrics and easiest to implement. They provide immediate value and match the Sales Register data.

**Next**: Add Top Sales Customers table (Phase 2)

**Later**: Add Monthly Trend chart if charts are desired (Phase 3)

---

## Next Steps

1. **Confirm which metrics to implement**
2. **Decide on chart library (if any)**
3. **Implement backend queries**
4. **Update frontend dashboard**
5. **Test with real data**
6. **Verify amounts match Sales Register**

---

**Note**: All sales calculations should use the same logic as Sales Register to ensure consistency across reports.

