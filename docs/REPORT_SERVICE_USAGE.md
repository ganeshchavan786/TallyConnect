# Report Service - Usage Guide

## Overview

`ReportService` is a common, reusable service for all reports. It provides:
- ✅ Filter, Sort, Pagination
- ✅ Export (CSV, Excel, PDF)
- ✅ Loading States
- ✅ Data Context Display
- ✅ Persistent Preferences

## Quick Start

### 1. Include Required Files

```html
<!-- In your HTML file -->
<script src="assets/js/utils/filters.js"></script>
<script src="assets/js/utils/export.js"></script>
<script src="assets/js/utils/report-service.js"></script>
```

### 2. Basic Usage

```javascript
// Initialize report service
const salesRegisterService = new ReportService({
    reportName: 'salesRegister',
    containerId: 'reportContent',
    tableId: 'salesRegisterTable',
    searchInputId: 'salesRegisterSearch',
    sortSelectId: 'salesRegisterSort',
    paginationId: 'salesRegisterPagination',
    contextId: 'salesRegisterContext',
    storageKey: 'sales_register_preferences',
    dataField: 'vouchers', // Field name in data object
    searchFields: ['particulars', 'voucher_number', 'date'],
    defaultSort: 'date-desc',
    itemsPerPage: 20,
    
    // Custom render function
    onRender: function(paginatedData, info, originalData) {
        const tbody = document.getElementById('salesRegisterTableBody');
        tbody.innerHTML = '';
        
        paginatedData.forEach(vch => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${formatDateTally(vch.date)}</td>
                <td>${vch.particulars || '-'}</td>
                <td>${formatCurrency(vch.debit || 0)}</td>
            `;
            tbody.appendChild(row);
        });
    }
});

// Initialize with data
salesRegisterService.init(data);

// Store globally for export buttons
window.salesRegisterService = salesRegisterService;
```

## Configuration Options

### Required Options

```javascript
{
    reportName: 'myReport',        // Unique name for this report
    containerId: 'reportContent',  // Container element ID
}
```

### Optional Options

```javascript
{
    // Element IDs
    tableId: 'myTable',              // Table element ID
    searchInputId: 'mySearch',       // Search input ID
    sortSelectId: 'mySort',          // Sort select ID
    paginationId: 'myPagination',   // Pagination container ID
    contextId: 'myContext',         // Context display ID
    exportButtonsId: 'myExport',    // Export buttons container ID
    
    // Data Configuration
    dataField: 'transactions',      // Field name in data object
    searchFields: ['name', 'date'], // Fields to search in
    defaultSort: 'date-desc',       // Default sort option
    itemsPerPage: 20,               // Items per page
    
    // Custom Sort Functions
    sortColumns: {
        'date-asc': (a, b) => new Date(a.date) - new Date(b.date),
        'amount-desc': (a, b) => (b.amount || 0) - (a.amount || 0)
    },
    
    // Export Configuration
    exportFileName: (data, format) => {
        return `Sales_Register_${data.from_date}`;
    },
    exportColumns: ['date', 'particulars', 'debit', 'credit'],
    
    // Storage
    storageKey: 'my_report_prefs',
    
    // Callbacks
    onRender: function(data, info, originalData) {
        // Custom render logic
    },
    onRowClick: function(row, index) {
        // Handle row click
    },
    onDataLoad: function(data) {
        // Called when data is loaded
    },
    
    // UI Features (all default to true)
    showSearch: true,
    showSort: true,
    showFilter: false,
    showPagination: true,
    showExport: true,
    showContext: true
}
```

## Examples

### Example 1: Sales Register Report

```javascript
const salesRegisterService = new ReportService({
    reportName: 'salesRegister',
    containerId: 'reportContent',
    tableId: 'salesRegisterTable',
    searchInputId: 'salesRegisterSearch',
    sortSelectId: 'salesRegisterSort',
    paginationId: 'salesRegisterPagination',
    contextId: 'salesRegisterContext',
    storageKey: 'sales_register_preferences',
    dataField: 'vouchers',
    searchFields: ['particulars', 'voucher_number'],
    defaultSort: 'date-desc',
    itemsPerPage: 20,
    sortColumns: {
        'date-asc': (a, b) => new Date(a.date) - new Date(b.date),
        'date-desc': (a, b) => new Date(b.date) - new Date(a.date),
        'debit-desc': (a, b) => (b.debit || 0) - (a.debit || 0)
    },
    onRender: function(paginatedData, info, originalData) {
        const tbody = document.getElementById('salesRegisterTableBody');
        if (!tbody) return;
        
        tbody.innerHTML = '';
        paginatedData.forEach(vch => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${formatDateTally(vch.date)}</td>
                <td>${vch.particulars || '-'}</td>
                <td>${vch.voucher_number || '-'}</td>
                <td>${formatCurrency(vch.debit || 0)}</td>
            `;
            tbody.appendChild(tr);
        });
    },
    exportFileName: (data, format) => {
        return `Sales_Register_${data.from_date}_${data.to_date}`;
    }
});

// Initialize
salesRegisterService.init(apiData);
window.salesRegisterService = salesRegisterService;
```

### Example 2: Ledger Report

```javascript
const ledgerReportService = new ReportService({
    reportName: 'ledgerReport',
    containerId: 'reportContent',
    tableId: 'ledgerReportTable',
    searchInputId: 'ledgerReportSearch',
    sortSelectId: 'ledgerReportSort',
    paginationId: 'ledgerReportPagination',
    contextId: 'ledgerReportContext',
    storageKey: 'ledger_report_preferences',
    dataField: 'transactions',
    searchFields: ['particulars', 'voucher_number', 'narration'],
    defaultSort: 'date-desc',
    itemsPerPage: 50,
    sortColumns: {
        'date-asc': (a, b) => new Date(a.date) - new Date(b.date),
        'date-desc': (a, b) => new Date(b.date) - new Date(a.date),
        'balance-desc': (a, b) => Math.abs(b.balance || 0) - Math.abs(a.balance || 0)
    },
    onRender: function(paginatedData, info, originalData) {
        // Render ledger transactions
        const tbody = document.getElementById('ledgerReportTableBody');
        // ... render logic
    },
    exportColumns: ['date', 'particulars', 'voucher_number', 'debit', 'credit', 'balance']
});

ledgerReportService.init(ledgerData);
window.ledgerReportService = ledgerReportService;
```

### Example 3: Simple List (No Table)

```javascript
const outstandingService = new ReportService({
    reportName: 'outstanding',
    containerId: 'reportContent',
    reportType: 'list', // Not a table
    dataField: 'parties',
    searchFields: ['party_name'],
    defaultSort: 'balance-desc',
    itemsPerPage: 30,
    onRender: function(paginatedData, info, originalData) {
        const container = document.getElementById('reportContent');
        container.innerHTML = '';
        
        paginatedData.forEach(party => {
            const card = document.createElement('div');
            card.className = 'party-card';
            card.innerHTML = `
                <h3>${party.party_name}</h3>
                <p>Balance: ${formatCurrency(party.balance)}</p>
            `;
            container.appendChild(card);
        });
    }
});

outstandingService.init(outstandingData);
```

## Methods

### `init(data)`
Initialize the service with data.

```javascript
service.init(apiData);
```

### `updateData(data)`
Update data without re-initializing.

```javascript
service.updateData(newData);
```

### `clearFilters()`
Clear all filters and reset to default.

```javascript
service.clearFilters();
```

### `export(format)`
Export data in specified format ('csv', 'excel', 'pdf').

```javascript
service.export('csv');
service.export('excel');
service.export('pdf');
```

### `showLoading()`
Show loading state.

```javascript
service.showLoading();
```

### `showError(message)`
Show error state.

```javascript
service.showError('Failed to load data');
```

## Integration with Existing Code

### Step 1: Replace existing render function

**Before:**
```javascript
function renderSalesRegisterVouchers(data) {
    // Manual rendering code
    const html = `...`;
    contentDiv.innerHTML = html;
}
```

**After:**
```javascript
function renderSalesRegisterVouchers(data) {
    if (!window.salesRegisterService) {
        // Initialize service
        window.salesRegisterService = new ReportService({
            // ... config
        });
    }
    window.salesRegisterService.init(data);
}
```

### Step 2: Add export buttons (if not auto-generated)

The service automatically creates export buttons if `showExport: true`. If you want custom buttons:

```html
<button onclick="window.salesRegisterService.export('csv')">Export CSV</button>
```

## Benefits

1. **Reusable** - Same code for all reports
2. **Consistent** - Same UI/UX across reports
3. **Maintainable** - One place to update
4. **Feature-rich** - All features included
5. **Flexible** - Customizable per report

## Next Steps

1. Integrate `ReportService` in Sales Register
2. Integrate in Ledger Report
3. Integrate in Outstanding Report
4. Integrate in Dashboard

Each integration takes 5-10 minutes!

