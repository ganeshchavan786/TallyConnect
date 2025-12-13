# 📊 TallyConnect Reports Module

Professional HTML/CSS/JS reporting system for Tally data.

---

## 📁 Module Structure

```
reports/
├── __init__.py              # Module initialization
├── report_generator.py      # Main report generation logic
├── utils.py                 # Utility functions (currency, dates, age calculation)
├── README.md               # This file
├── templates/              # HTML templates
│   ├── README.md
│   ├── base.html           # Base template (header/footer)
│   ├── outstanding.html    # Outstanding report (TODO)
│   ├── ledger.html         # Ledger report (TODO)
│   └── dashboard.html      # Dashboard (TODO)
└── static/                 # Static assets (CSS/JS/Images)
    ├── css/
    │   ├── main.css        # Base styles
    │   └── reports.css     # Report-specific styles (TODO)
    ├── js/
    │   ├── filters.js      # Search/filter/sort functionality
    │   ├── export.js       # Export to PDF/CSV/Excel
    │   └── charts.js       # Chart.js integration (TODO)
    └── img/
        └── logo.png        # Company logo (TODO)
```

---

## 🚀 Quick Start

### Installation

```python
# Already part of TallyConnect - no separate installation needed
```

### Basic Usage

```python
from reports import ReportGenerator

# Initialize
generator = ReportGenerator('TallyConnectDb.db')

# Generate outstanding report
generator.generate_outstanding_report(
    company_name="ABC Company Ltd",
    guid="abc-123-guid",
    alterid="456",
    as_on_date="31-03-2024"  # Optional, defaults to today
)

# Generate ledger report
generator.generate_ledger_report(
    company_name="ABC Company Ltd",
    guid="abc-123-guid",
    alterid="456",
    ledger_name="Cash",
    from_date="01-04-2023",
    to_date="31-03-2024"
)

# Generate dashboard
generator.generate_dashboard(
    company_name="ABC Company Ltd",
    guid="abc-123-guid",
    alterid="456"
)
```

---

## 📋 Report Types

### 1. Outstanding Report
**Purpose:** Receivables/Payables analysis  
**Features:**
- Party-wise outstanding summary
- Age analysis (0-30, 30-60, 60-90, >90 days)
- Drill-down to invoice level
- Charts for visualization

### 2. Ledger Report
**Purpose:** Transaction-wise details  
**Features:**
- Date range filtering
- Opening balance, transactions, closing balance
- Month-wise summary
- Search and filter options

### 3. Dashboard
**Purpose:** Company overview  
**Features:**
- Key metrics (total parties, transactions, balances)
- Top 10 debtors/creditors
- Voucher type analysis
- Monthly trend charts

---

## 🛠️ Development Guide

### Adding New Report Type

1. **Create HTML Template**
   ```html
   <!-- reports/templates/my_report.html -->
   <!DOCTYPE html>
   <html>
   <head>
       <link rel="stylesheet" href="../static/css/main.css">
   </head>
   <body>
       <!-- Your report content -->
   </body>
   </html>
   ```

2. **Add Generation Method**
   ```python
   # In reports/report_generator.py
   def generate_my_report(self, ...):
       template = self._load_template('my_report.html')
       # Process data
       # Replace variables
       # Save and open
   ```

3. **Add Database Queries**
   ```python
   # In database/queries.py
   MY_REPORT_QUERY = """
       SELECT ... FROM vouchers WHERE ...
   """
   ```

### Customization

#### Change Colors/Styling
Edit `reports/static/css/main.css`:
```css
.report-header {
    background: linear-gradient(135deg, #YOUR_COLOR 0%, #YOUR_COLOR2 100%);
}
```

#### Add Custom JavaScript
Create new file in `reports/static/js/` and include in template:
```html
<script src="../static/js/my_script.js"></script>
```

---

## 🎨 Features

### Current Features ✅
- ✅ Modular structure
- ✅ Base template system
- ✅ Professional CSS styling
- ✅ Search/filter/sort (filters.js)
- ✅ Export to CSV/PDF (export.js)
- ✅ Responsive design
- ✅ Print-friendly layout
- ✅ Utility functions (currency, dates, age)

### Planned Features 🚧
- 🚧 Outstanding report template
- 🚧 Ledger report template
- 🚧 Dashboard template
- 🚧 Chart.js integration
- 🚧 Excel export (advanced)
- 🚧 Email reports
- 🚧 Custom report builder

---

## 📊 Database Schema

Reports read from these tables:

```sql
-- Companies table
companies (name, guid, alterid, status, total_records, last_sync)

-- Vouchers table
vouchers (
    date,
    voucher_type,
    voucher_number,
    party_name,
    amount,
    narration,
    company_guid,
    company_alterid
)
```

---

## 🔧 Utilities

### Currency Formatting
```python
from reports.utils import format_currency

amount = 1234567.89
formatted = format_currency(amount)  # ₹ 12,34,567.89
```

### Age Calculation
```python
from reports.utils import calculate_age, get_age_bucket

days = calculate_age("01-01-2024", "31-03-2024")  # 90
bucket = get_age_bucket(days)  # "60-90 days"
```

### Date Formatting
```python
from reports.utils import format_date

date = format_date("2024-01-01", "%d-%m-%Y")  # 01-01-2024
```

---

## 🐛 Troubleshooting

### Report not generating?
1. Check database path is correct
2. Verify company GUID/AlterID exists in database
3. Check console for Python errors

### Styles not loading?
1. Verify `static/css/main.css` exists
2. Check file paths in HTML templates
3. Open HTML in browser and check DevTools console

### Charts not showing?
1. Install Chart.js: `charts.js` will include CDN link
2. Verify data format is correct
3. Check browser console for JavaScript errors

---

## 📝 Best Practices

1. **Always use utility functions** for formatting
   ```python
   # Good
   from reports.utils import format_currency
   formatted = format_currency(amount)
   
   # Bad
   formatted = f"₹ {amount:,.2f}"
   ```

2. **Close database connections**
   ```python
   generator._connect()
   try:
       # Query data
   finally:
       generator._close()
   ```

3. **Sanitize HTML output**
   ```python
   from reports.utils import sanitize_html
   safe_text = sanitize_html(user_input)
   ```

4. **Use meaningful filenames**
   ```python
   # Generated reports will have timestamps
   # outstanding_ABC_Company_20241213_123456.html
   ```

---

## 🚀 Next Steps

1. **Implement Outstanding Report Template**
2. **Implement Ledger Report Template**
3. **Implement Dashboard Template**
4. **Add Chart.js Integration**
5. **Test with Real Data**
6. **Add More Report Types**

---

## 📞 Support

- **GitHub:** https://github.com/ganeshchavan786/TallyConnect
- **Issues:** https://github.com/ganeshchavan786/TallyConnect/issues

---

**Happy Reporting! 📊**

