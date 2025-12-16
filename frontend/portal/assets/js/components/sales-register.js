/* ============================================
   Sales Register Component
   Uses ReportService for Voucher List view
   ============================================ */

// Global ReportService instance for voucher list
let salesRegisterVoucherService = null;

/**
 * Render Sales Register report (Monthly or Voucher List view)
 * @param {object} data - Sales Register data
 * @param {string} viewType - 'monthly' or 'vouchers'
 */
function renderSalesRegister(data, viewType = 'monthly') {
    const contentDiv = document.getElementById('reportContent');
    if (!contentDiv) {
        console.error('reportContent element not found');
        return;
    }
    
    // Store data globally for view toggle and drill-down
    if (typeof window !== 'undefined') {
        window.salesRegisterData = data;
    }
    
    if (viewType === 'monthly') {
        renderSalesRegisterMonthly(data);
    } else {
        renderSalesRegisterVouchers(data);
    }
}

/**
 * Render Monthly Summary view
 */
function renderSalesRegisterMonthly(data) {
    const contentDiv = document.getElementById('reportContent');
    
    let html = `
        <div style="padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h2 style="color: #2c3e50; margin-bottom: 10px;">${data.company_name || 'Company'}</h2>
            <h3 style="color: #34495e; margin-bottom: 5px;">Sales Register</h3>
            <div style="margin-bottom: 20px; color: #7f8c8d; font-size: 14px;">
                Period: ${formatDateTally(data.from_date)} to ${formatDateTally(data.to_date)}
            </div>
            
            <div style="overflow-x: auto; margin-top: 20px;">
                <table style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr style="background: #34495e; color: white;">
                            <th style="padding: 12px; text-align: left; border: 1px solid #2c3e50;">Particulars</th>
                            <th style="padding: 12px; text-align: right; border: 1px solid #2c3e50;">Debit</th>
                            <th style="padding: 12px; text-align: right; border: 1px solid #2c3e50;">Credit</th>
                            <th style="padding: 12px; text-align: right; border: 1px solid #2c3e50;">Closing Balance</th>
                        </tr>
                    </thead>
                    <tbody>
    `;
    
    if (data.monthly_summary && Array.isArray(data.monthly_summary)) {
        data.monthly_summary.forEach((month, index) => {
            const balanceText = month.closing_balance >= 0 
                ? `${formatCurrency(month.closing_balance)} Cr` 
                : `${formatCurrency(Math.abs(month.closing_balance))} Dr`;
            
            // Make month row clickable for drill-down (only if there's data)
            const hasData = month.credit > 0 || month.debit > 0;
            const rowId = `month-row-${index}`;
            const rowStyle = hasData 
                ? 'cursor: pointer; border-bottom: 1px solid #ecf0f1; transition: background 0.2s;' 
                : 'border-bottom: 1px solid #ecf0f1;';
            
            html += `
                <tr id="${rowId}" style="${rowStyle}" data-month-key="${month.month_key || ''}" data-month-name="${month.month_name || ''}" data-has-data="${hasData}">
                    <td style="padding: 10px; font-weight: 600; ${hasData ? 'color: #3498db;' : ''}">${month.month_name || '-'}${hasData ? ' 👆' : ''}</td>
                    <td style="padding: 10px; text-align: right; color: #27ae60;">${month.debit > 0 ? formatCurrency(month.debit) : ''}</td>
                    <td style="padding: 10px; text-align: right; color: #e74c3c;">${month.credit > 0 ? formatCurrency(month.credit) : ''}</td>
                    <td style="padding: 10px; text-align: right; font-weight: 600; color: #3498db;">${balanceText}</td>
                </tr>
            `;
        });
    } else {
        html += `
            <tr>
                <td colspan="4" style="text-align: center; padding: 20px; color: #7f8c8d;">No sales data found for the selected period</td>
            </tr>
        `;
    }
    
    const grandTotal = data.total_credit || 0;
    html += `
                    </tbody>
                    <tfoot>
                        <tr style="background: #ecf0f1; font-weight: 600;">
                            <td style="padding: 12px; border-top: 2px solid #34495e;">Grand Total</td>
                            <td style="padding: 12px; text-align: right; border-top: 2px solid #34495e; color: #27ae60;">${data.total_debit > 0 ? formatCurrency(data.total_debit) : ''}</td>
                            <td style="padding: 12px; text-align: right; border-top: 2px solid #34495e; color: #e74c3c;">${formatCurrency(grandTotal)}</td>
                            <td style="padding: 12px; text-align: right; border-top: 2px solid #34495e; color: #3498db; font-weight: 600;">${formatCurrency(grandTotal)} Cr</td>
                        </tr>
                    </tfoot>
                </table>
            </div>
        </div>
    `;
    
    contentDiv.innerHTML = html;
    
    // Add click handlers for month rows after rendering
    if (data.monthly_summary && Array.isArray(data.monthly_summary)) {
        data.monthly_summary.forEach((month, index) => {
            const hasData = month.credit > 0 || month.debit > 0;
            if (hasData) {
                const rowId = `month-row-${index}`;
                const row = document.getElementById(rowId);
                if (row) {
                    row.addEventListener('click', function() {
                        drillDownToMonth(month.month_key, month.month_name);
                    });
                    row.addEventListener('mouseenter', function() {
                        this.style.background = '#f0f0f0';
                    });
                    row.addEventListener('mouseleave', function() {
                        this.style.background = 'white';
                    });
                }
            }
        });
    }
}

/**
 * Render voucher table rows (used by ReportService)
 * @param {Array} vouchers - Array of voucher objects
 * @param {object} originalData - Original report data (for totals)
 */
function renderVoucherTableRows(vouchers, originalData) {
    if (!vouchers || vouchers.length === 0) {
        return '<tr><td colspan="6" style="text-align: center; padding: 20px; color: #7f8c8d;">No vouchers found</td></tr>';
    }
    
    let rowsHtml = '';
    vouchers.forEach(vch => {
        // Tally style: Backend already sends sales amount in debit field, credit is 0
        const debitDisplay = vch.debit > 0 ? formatCurrency(vch.debit) : '';
        const creditDisplay = ''; // Credit column always empty for Sales in Tally
        
        rowsHtml += `
            <tr style="border-bottom: 1px solid #ecf0f1;">
                <td style="padding: 10px;">${formatDateTally(vch.date)}</td>
                <td style="padding: 10px; font-weight: 600;">${vch.particulars || '-'}</td>
                <td style="padding: 10px; text-align: center;">${vch.voucher_type || 'Sales'}</td>
                <td style="padding: 10px;">${vch.voucher_number || '-'}</td>
                <td style="padding: 10px; text-align: right; color: #27ae60;">${debitDisplay}</td>
                <td style="padding: 10px; text-align: right; color: #e74c3c;">${creditDisplay}</td>
            </tr>
        `;
    });
    
    return rowsHtml;
}

/**
 * Render voucher table with ReportService
 * @param {Array} vouchers - Array of vouchers to display
 * @param {object} originalData - Original report data
 * @param {string} title - Title for the report
 * @param {string} subtitle - Subtitle (e.g., month name)
 * @param {boolean} showBackButton - Whether to show back button
 */
function renderVoucherTableWithService(vouchers, originalData, title, subtitle, showBackButton = false) {
    const contentDiv = document.getElementById('reportContent');
    if (!contentDiv) return;
    
    // Clear previous content
    contentDiv.innerHTML = '';
    
    // Create report header
    let headerHtml = `
        <div style="padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px;">
    `;
    
    if (showBackButton) {
        headerHtml += `
            <div style="margin-bottom: 15px;">
                <button onclick="renderSalesRegister(window.salesRegisterData, 'monthly')" style="padding: 8px 15px; background: #95a5a6; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 14px;">
                    ← Back to Monthly Summary
                </button>
            </div>
        `;
    }
    
    headerHtml += `
            <h2 style="color: #2c3e50; margin-bottom: 10px;">${originalData.company_name || 'Company'}</h2>
            <h3 style="color: #34495e; margin-bottom: 5px;">${title}${subtitle ? ' - ' + subtitle : ''}</h3>
            <div style="margin-bottom: 20px; color: #7f8c8d; font-size: 14px;">
                Period: ${formatDateTally(originalData.from_date)} to ${formatDateTally(originalData.to_date)}
            </div>
        </div>
    `;
    
    contentDiv.innerHTML = headerHtml;
    
    // Initialize ReportService for voucher list
    if (typeof ReportService === 'undefined') {
        console.error('ReportService not loaded');
        return;
    }
    
    // Calculate total sales for footer
    const totalSales = vouchers.reduce((sum, vch) => sum + (vch.debit || 0), 0);
    
    // Custom sort functions for Sales Register
    // Note: 'name-asc' and 'name-desc' from default dropdown map to 'particulars'
    const sortColumns = {
        'date-desc': (a, b) => {
            const dateA = new Date(a.date || 0);
            const dateB = new Date(b.date || 0);
            return dateB - dateA;
        },
        'date-asc': (a, b) => {
            const dateA = new Date(a.date || 0);
            const dateB = new Date(b.date || 0);
            return dateA - dateB;
        },
        'name-asc': (a, b) => {
            // Map 'name' to 'particulars' for Sales Register
            const nameA = (a.particulars || '').toLowerCase();
            const nameB = (b.particulars || '').toLowerCase();
            return nameA.localeCompare(nameB);
        },
        'name-desc': (a, b) => {
            // Map 'name' to 'particulars' for Sales Register
            const nameA = (a.particulars || '').toLowerCase();
            const nameB = (b.particulars || '').toLowerCase();
            return nameB.localeCompare(nameA);
        },
        'particulars-asc': (a, b) => {
            const nameA = (a.particulars || '').toLowerCase();
            const nameB = (b.particulars || '').toLowerCase();
            return nameA.localeCompare(nameB);
        },
        'particulars-desc': (a, b) => {
            const nameA = (a.particulars || '').toLowerCase();
            const nameB = (b.particulars || '').toLowerCase();
            return nameB.localeCompare(nameA);
        },
        'amount-desc': (a, b) => (b.debit || 0) - (a.debit || 0),
        'amount-asc': (a, b) => (a.debit || 0) - (b.debit || 0)
    };
    
    salesRegisterVoucherService = new ReportService({
        reportName: 'salesRegisterVouchers',
        containerId: 'reportContent',
        tableId: 'salesRegisterVoucherTable',
        searchInputId: 'salesRegisterSearch',
        sortSelectId: 'salesRegisterSort',
        paginationId: 'salesRegisterPagination',
        contextId: 'salesRegisterContext',
        exportButtonsId: 'salesRegisterExport',
        dataField: 'vouchers',
        searchFields: ['particulars', 'voucher_number', 'voucher_type', 'date'],
        sortColumns: sortColumns,
        defaultSort: 'date-desc',
        itemsPerPage: 20,
        storageKey: 'sales_register_voucher_prefs',
        showSearch: true,
        showSort: true,
        showPagination: true,
        showExport: true,
        showContext: true,
        exportFileName: (data, format) => {
            const companyName = (originalData.company_name || 'Company').replace(/[^a-z0-9]/gi, '_');
            const dateStr = new Date().toISOString().split('T')[0];
            return `Sales_Register_${companyName}_${dateStr}`;
        },
        exportColumns: ['date', 'particulars', 'voucher_type', 'voucher_number', 'debit', 'credit'],
        onRender: function(paginatedData, info, fullData) {
            // Custom render function for voucher table
            const tableId = this.config.tableId;
            let table = document.getElementById(tableId);
            
            if (!table) {
                // Create table structure
                const container = document.getElementById(this.config.containerId);
                container.insertAdjacentHTML('beforeend', `
                    <div style="padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <div style="overflow-x: auto; margin-top: 20px;">
                            <table id="${tableId}" style="width: 100%; border-collapse: collapse;">
                                <thead>
                                    <tr style="background: #34495e; color: white;">
                                        <th style="padding: 12px; text-align: left; border: 1px solid #2c3e50;">Date</th>
                                        <th style="padding: 12px; text-align: left; border: 1px solid #2c3e50;">Particulars</th>
                                        <th style="padding: 12px; text-align: center; border: 1px solid #2c3e50;">Vch Type</th>
                                        <th style="padding: 12px; text-align: left; border: 1px solid #2c3e50;">Vch No</th>
                                        <th style="padding: 12px; text-align: right; border: 1px solid #2c3e50;">Debit</th>
                                        <th style="padding: 12px; text-align: right; border: 1px solid #2c3e50;">Credit</th>
                                    </tr>
                                </thead>
                                <tbody id="${tableId}Body"></tbody>
                                <tfoot id="${tableId}Foot"></tfoot>
                            </table>
                        </div>
                    </div>
                `);
                table = document.getElementById(tableId);
            }
            
            const tbody = document.getElementById(`${tableId}Body`);
            const tfoot = document.getElementById(`${tableId}Foot`);
            
            if (!tbody) return;
            
            // Render rows
            tbody.innerHTML = renderVoucherTableRows(paginatedData, originalData);
            
            // Render footer with totals
            // Calculate total from all vouchers (not just paginated)
            const allVouchers = this.filterManager ? this.filterManager.config.filteredData : vouchers;
            const displayTotal = allVouchers.reduce((sum, vch) => sum + (vch.debit || 0), 0);
            
            tfoot.innerHTML = `
                <tr style="background: #ecf0f1; font-weight: 600;">
                    <td colspan="4" style="padding: 12px; border-top: 2px solid #34495e;">Total${subtitle ? ' for ' + subtitle : ''}</td>
                    <td style="padding: 12px; text-align: right; border-top: 2px solid #34495e; color: #27ae60;">${displayTotal > 0 ? formatCurrency(displayTotal) : ''}</td>
                    <td style="padding: 12px; text-align: right; border-top: 2px solid #34495e; color: #e74c3c;"></td>
                </tr>
            `;
        }
    });
    
    // Initialize with voucher data
    salesRegisterVoucherService.init({
        vouchers: vouchers,
        company_name: originalData.company_name,
        from_date: originalData.from_date,
        to_date: originalData.to_date
    });
    
    // Customize sort dropdown options for Sales Register
    const sortSelect = document.getElementById('salesRegisterSort');
    if (sortSelect) {
        sortSelect.innerHTML = `
            <option value="date-desc">Date (Newest First)</option>
            <option value="date-asc">Date (Oldest First)</option>
            <option value="name-asc">Customer (A-Z)</option>
            <option value="name-desc">Customer (Z-A)</option>
            <option value="amount-desc">Amount (High-Low)</option>
            <option value="amount-asc">Amount (Low-High)</option>
        `;
        sortSelect.value = 'date-desc'; // Set default
    }
    
    // Store service globally for access
    if (typeof window !== 'undefined') {
        window.salesRegisterVoucherService = salesRegisterVoucherService;
    }
}

/**
 * Drill down to show vouchers for a specific month
 * @param {string} monthKey - Month key (YYYY-MM format)
 * @param {string} monthName - Month name for display
 */
function drillDownToMonth(monthKey, monthName) {
    if (!window.salesRegisterData) {
        console.error('Sales register data not available');
        return;
    }
    
    const data = window.salesRegisterData;
    
    // Filter vouchers for the selected month
    const monthVouchers = data.vouchers.filter(vch => {
        if (!vch.date) return false;
        const vchDate = new Date(vch.date);
        const vchMonthKey = `${vchDate.getFullYear()}-${String(vchDate.getMonth() + 1).padStart(2, '0')}`;
        return vchMonthKey === monthKey;
    });
    
    // Render using ReportService
    const year = new Date(monthKey + '-01').getFullYear();
    renderVoucherTableWithService(
        monthVouchers, 
        data, 
        'Sales Register', 
        `${monthName} ${year}`,
        true // Show back button
    );
    
    // Update view toggle buttons to show we're in drill-down mode
    const viewMonthlyBtn = document.getElementById('viewMonthly');
    const viewVouchersBtn = document.getElementById('viewVouchers');
    if (viewMonthlyBtn) viewMonthlyBtn.style.background = '#95a5a6';
    if (viewVouchersBtn) viewVouchersBtn.style.background = '#95a5a6';
}

/**
 * Render Voucher List view using ReportService
 */
function renderSalesRegisterVouchers(data) {
    // Use ReportService for voucher list with filtering, sorting, pagination
    if (!data.vouchers || !Array.isArray(data.vouchers)) {
        const contentDiv = document.getElementById('reportContent');
        contentDiv.innerHTML = `
            <div style="padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <h2 style="color: #2c3e50; margin-bottom: 10px;">${data.company_name || 'Company'}</h2>
                <h3 style="color: #34495e; margin-bottom: 5px;">Sales Register - Voucher List</h3>
                <div style="text-align: center; padding: 20px; color: #7f8c8d;">No vouchers found for the selected period</div>
            </div>
        `;
        return;
    }
    
    renderVoucherTableWithService(
        data.vouchers, 
        data, 
        'Sales Register - Voucher List', 
        null,
        false // No back button for main voucher list
    );
}
