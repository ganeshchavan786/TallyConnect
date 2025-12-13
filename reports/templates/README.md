# Report Templates

HTML templates for different report types.

## Template Files

### `base.html`
Base template with common header/footer.
Variables: TITLE, COMPANY_NAME, REPORT_TYPE, CONTENT, GENERATED_DATE

### `outstanding.html`
Outstanding report (Receivables/Payables) with age analysis.

### `ledger.html`
Ledger report showing transaction details.

### `dashboard.html`
Dashboard with summary and charts.

## Template Variables

Templates use simple string replacement with `{% VARIABLE %}` syntax:

```html
<h1>{% COMPANY_NAME %}</h1>
<!-- Will be replaced with actual company name -->
```

## Usage

```python
from reports import ReportGenerator

generator = ReportGenerator('TallyConnectDb.db')
generator.generate_outstanding_report('ABC Ltd', guid, alterid)
```

