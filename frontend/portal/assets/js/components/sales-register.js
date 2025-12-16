/* ============================================
   Sales Register Component
   ============================================ */

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
    
    // Store data globally for view toggle and drill-down
    if (typeof window !== 'undefined') {
        window.salesRegisterData = data;
    }
    
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
    
    // Calculate totals for the month
    const monthTotalDebit = monthVouchers.reduce((sum, vch) => sum + (vch.debit || 0), 0);
    const monthTotalCredit = monthVouchers.reduce((sum, vch) => sum + (vch.credit || 0), 0);
    
    const contentDiv = document.getElementById('reportContent');
    
    let html = `
        <div style="padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <div style="margin-bottom: 15px;">
                <button onclick="renderSalesRegister(window.salesRegisterData, 'monthly')" style="padding: 8px 15px; background: #95a5a6; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; margin-bottom: 10px;">
                    ← Back to Monthly Summary
                </button>
            </div>
            <h2 style="color: #2c3e50; margin-bottom: 10px;">${data.company_name || 'Company'}</h2>
            <h3 style="color: #34495e; margin-bottom: 5px;">Sales Register - ${monthName} ${new Date(monthKey + '-01').getFullYear()}</h3>
            <div style="margin-bottom: 20px; color: #7f8c8d; font-size: 14px;">
                Period: ${formatDateTally(data.from_date)} to ${formatDateTally(data.to_date)}
            </div>
            
            <div style="overflow-x: auto; margin-top: 20px;">
                <table style="width: 100%; border-collapse: collapse;">
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
                    <tbody>
    `;
    
    if (monthVouchers.length > 0) {
        monthVouchers.forEach(vch => {
            // Tally style: Backend already sends sales amount in debit field, credit is 0
            const debitDisplay = vch.debit > 0 ? formatCurrency(vch.debit) : '';
            const creditDisplay = ''; // Credit column always empty for Sales in Tally
            
            html += `
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
    } else {
        html += `
            <tr>
                <td colspan="6" style="text-align: center; padding: 20px; color: #7f8c8d;">No vouchers found for ${monthName}</td>
            </tr>
        `;
    }
    
    // Total: Show total sales in Debit column, Credit empty
    // Recalculate from filtered vouchers
    const monthTotalSales = monthVouchers.reduce((sum, vch) => sum + (vch.debit || 0), 0);
    html += `
                    </tbody>
                    <tfoot>
                        <tr style="background: #ecf0f1; font-weight: 600;">
                            <td colspan="4" style="padding: 12px; border-top: 2px solid #34495e;">Total for ${monthName}</td>
                            <td style="padding: 12px; text-align: right; border-top: 2px solid #34495e; color: #27ae60;">${monthTotalSales > 0 ? formatCurrency(monthTotalSales) : ''}</td>
                            <td style="padding: 12px; text-align: right; border-top: 2px solid #34495e; color: #e74c3c;"></td>
                        </tr>
                    </tfoot>
                </table>
            </div>
        </div>
    `;
    
    contentDiv.innerHTML = html;
    
    // Update view toggle buttons to show we're in drill-down mode
    const viewMonthlyBtn = document.getElementById('viewMonthly');
    const viewVouchersBtn = document.getElementById('viewVouchers');
    if (viewMonthlyBtn) viewMonthlyBtn.style.background = '#95a5a6';
    if (viewVouchersBtn) viewVouchersBtn.style.background = '#95a5a6';
}

/**
 * Render Voucher List view
 */
function renderSalesRegisterVouchers(data) {
    const contentDiv = document.getElementById('reportContent');
    
    // Store data globally
    if (typeof window !== 'undefined') {
        window.salesRegisterData = data;
    }
    
    let html = `
        <div style="padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h2 style="color: #2c3e50; margin-bottom: 10px;">${data.company_name || 'Company'}</h2>
            <h3 style="color: #34495e; margin-bottom: 5px;">Sales Register - Voucher List</h3>
            <div style="margin-bottom: 20px; color: #7f8c8d; font-size: 14px;">
                Period: ${formatDateTally(data.from_date)} to ${formatDateTally(data.to_date)}
            </div>
            
            <div style="overflow-x: auto; margin-top: 20px;">
                <table style="width: 100%; border-collapse: collapse;">
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
                    <tbody>
    `;
    
    if (data.vouchers && Array.isArray(data.vouchers)) {
        data.vouchers.forEach(vch => {
            // Tally style: Backend already sends sales amount in debit field, credit is 0
            const debitDisplay = vch.debit > 0 ? formatCurrency(vch.debit) : '';
            const creditDisplay = ''; // Credit column always empty for Sales in Tally
            
            html += `
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
    } else {
        html += `
            <tr>
                <td colspan="6" style="text-align: center; padding: 20px; color: #7f8c8d;">No vouchers found for the selected period</td>
            </tr>
        `;
    }
    
    // Total: Show total sales in Debit column, Credit empty
    // Backend sends total_credit as the total sales amount
    const totalSales = data.total_credit || 0;
    html += `
                    </tbody>
                    <tfoot>
                        <tr style="background: #ecf0f1; font-weight: 600;">
                            <td colspan="4" style="padding: 12px; border-top: 2px solid #34495e;">Total</td>
                            <td style="padding: 12px; text-align: right; border-top: 2px solid #34495e; color: #27ae60;">${totalSales > 0 ? formatCurrency(totalSales) : ''}</td>
                            <td style="padding: 12px; text-align: right; border-top: 2px solid #34495e; color: #e74c3c;"></td>
                        </tr>
                    </tfoot>
                </table>
            </div>
        </div>
    `;
    
    contentDiv.innerHTML = html;
}

