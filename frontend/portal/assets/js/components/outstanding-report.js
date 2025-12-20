/* ============================================
   Outstanding Report Component - Bill-wise Outstanding
   ============================================ */

// Format number with 2 decimal places
function formatNumber(num) {
    if (num === null || num === undefined) return '0.00';
    return parseFloat(num).toFixed(2);
}

// Format currency with commas
function formatCurrency(num) {
    if (num === null || num === undefined) return '0.00';
    const formatted = parseFloat(num).toLocaleString('en-IN', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
    return formatted;
}

// Format date from YYYY-MM-DD to DD-MM-YYYY
function formatDate(dateStr) {
    if (!dateStr) return '-';
    try {
        const date = new Date(dateStr + 'T00:00:00');
        const day = String(date.getDate()).padStart(2, '0');
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const year = date.getFullYear();
        return `${day}-${month}-${year}`;
    } catch (e) {
        return dateStr;
    }
}

// Show error message
function showError(message) {
    const errorDiv = document.getElementById('errorMessage');
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
        setTimeout(() => {
            errorDiv.style.display = 'none';
        }, 5000);
    }
    console.error('[Outstanding Report]', message);
}

// Hide error message
function hideError() {
    const errorDiv = document.getElementById('errorMessage');
    if (errorDiv) errorDiv.style.display = 'none';
}

// Get company from sessionStorage
function getSelectedCompany() {
    const savedCompany = sessionStorage.getItem('selectedCompany');
    if (!savedCompany) {
        return null;
    }
    
    try {
        const company = JSON.parse(savedCompany);
        return company.name || null;
    } catch (e) {
        console.warn('Error parsing saved company:', e);
        return null;
    }
}

// Load period info and set default as on date
async function loadPeriodInfoForOutstanding() {
    try {
        const companyName = getSelectedCompany();
        if (!companyName) {
            // Set default as today
            const today = new Date().toISOString().split('T')[0];
            const asOnDateInput = document.getElementById('asOnDate');
            if (asOnDateInput) asOnDateInput.value = today;
            return;
        }
        
        const response = await fetch(`/api/period-info?company=${encodeURIComponent(companyName)}`);
        if (!response.ok) {
            console.warn('Failed to load period info, using defaults');
            const today = new Date().toISOString().split('T')[0];
            const asOnDateInput = document.getElementById('asOnDate');
            if (asOnDateInput) asOnDateInput.value = today;
            return;
        }
        const periodInfo = await response.json();
        
        // Set as on date to max date (most recent date)
        const asOnDateInput = document.getElementById('asOnDate');
        if (asOnDateInput) {
            asOnDateInput.value = periodInfo.to_date || new Date().toISOString().split('T')[0];
        }
    } catch (error) {
        console.warn('Error loading period info:', error);
        const today = new Date().toISOString().split('T')[0];
        const asOnDateInput = document.getElementById('asOnDate');
        if (asOnDateInput) asOnDateInput.value = today;
    }
}

// Render outstanding data in table (Bill-wise) - Original function name
function renderOutstandingReport(data) {
    // If data is from old API format, convert it
    if (data && !data.data && data.parties) {
        // Old format - show message to use new format
        const contentDiv = document.getElementById('reportContent');
        if (contentDiv) {
            contentDiv.innerHTML = `
                <div style="text-align: center; padding: 50px; color: #e74c3c;">
                    <div style="font-size: 48px; margin-bottom: 20px;">⚠️</div>
                    <div style="font-size: 20px; font-weight: 600; margin: 20px 0;">Please use the new Bill-wise Outstanding Report</div>
                    <div style="color: #7f8c8d; font-size: 14px;">This report now uses bill-wise outstanding logic.</div>
                </div>
            `;
        }
        return;
    }
    
    // New format - bill-wise data
    const reportData = data;
    const billData = reportData.data || [];
    const reportType = reportData.report_type || 'both';
    
    renderOutstandingTable(billData, reportType);
    updateInfoSection(reportData);
    
    // Store data for export
    if (typeof window !== 'undefined') {
        window.currentOutstandingData = reportData;
    }
}

// Render outstanding table (internal function)
function renderOutstandingTable(data, reportType) {
    const tbody = document.getElementById('outstandingTableBody');
    const table = document.getElementById('outstandingTable');
    const loadingMessage = document.getElementById('loadingMessage');
    const emptyMessage = document.getElementById('emptyMessage');
    
    if (!tbody || !table) return;
    
    // Hide loading and empty messages
    if (loadingMessage) loadingMessage.style.display = 'none';
    if (emptyMessage) emptyMessage.style.display = 'none';
    
    // Check if data is an array
    if (!Array.isArray(data)) {
        console.error('Data is not an array:', data);
        showError('Invalid data format received from server');
        if (emptyMessage) emptyMessage.style.display = 'block';
        table.style.display = 'none';
        return;
    }
    
    tbody.innerHTML = '';
    
    if (data.length === 0) {
        if (emptyMessage) emptyMessage.style.display = 'block';
        table.style.display = 'none';
        return;
    }
    
    table.style.display = 'table';
    
    let totalReceivables = 0;
    let totalPayables = 0;
    let currentLedger = '';
    
    data.forEach((row, index) => {
        const outstandingAmt = parseFloat(row.outstanding_amount || 0);
        const balance = parseFloat(row.balance || 0);
        const isReceivable = row.is_receivable !== undefined ? row.is_receivable : balance > 0;
        
        if (isReceivable) {
            totalReceivables += outstandingAmt;
        } else {
            totalPayables += outstandingAmt;
        }
        
        // Add ledger separator row if ledger changed
        if (currentLedger !== row.ledger_name) {
            if (currentLedger !== '') {
                // Add subtotal row for previous ledger
                const subtotalRow = document.createElement('tr');
                subtotalRow.className = 'subtotal-row';
                subtotalRow.innerHTML = `
                    <td colspan="8" style="text-align: right; font-weight: 600; font-size: 12px;">Subtotal (${currentLedger}):</td>
                    <td colspan="3" style="text-align: right; font-weight: 600; font-size: 12px;"></td>
                `;
                tbody.appendChild(subtotalRow);
            }
            currentLedger = row.ledger_name;
        }
        
        // Color code: Green for receivables (+), Red for payables (-)
        const typeClass = isReceivable ? 'tc-text-success' : 'tc-text-danger';
        const typeLabel = isReceivable ? 'Receivable (+) ' : 'Payable (-)';
        const typeSymbol = isReceivable ? '+' : '-';
        
        // Get Ref Type, Due On, and Overdue Days
        const billType = row.bill_type || '-';
        const dueDate = row.due_date ? formatDate(row.due_date) : '-';
        const overdueDays = row.overdue_days !== undefined && row.overdue_days !== null ? row.overdue_days : 0;
        
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td class="tc-center" style="font-size: 13px;">${index + 1}</td>
            <td style="font-size: 13px;">${row.ledger_name || '-'}</td>
            <td style="font-size: 13px;">${row.bill_ref || '-'}</td>
            <td style="font-size: 13px;">${row.bill_date ? formatDate(row.bill_date) : '-'}</td>
            <td style="font-size: 13px;">${billType}</td>
            <td style="font-size: 13px;">${row.voucher_type || '-'}</td>
            <td style="font-size: 13px;">${row.voucher_no || '-'}</td>
            <td class="tc-right ${typeClass}" style="font-weight: 600; font-size: 13px;">${typeSymbol} ${formatCurrency(outstandingAmt)}</td>
            <td class="${typeClass}" style="font-size: 13px;">${typeLabel}</td>
            <td style="font-size: 13px;">${dueDate}</td>
            <td class="tc-right" style="font-size: 13px;">${overdueDays > 0 ? overdueDays : '-'}</td>
        `;
        
        tbody.appendChild(tr);
    });
    
    // Add final subtotal row for last ledger
    if (currentLedger !== '') {
        const subtotalRow = document.createElement('tr');
        subtotalRow.className = 'subtotal-row';
        subtotalRow.innerHTML = `
            <td colspan="8" style="text-align: right; font-weight: 600; font-size: 12px;">Subtotal (${currentLedger}):</td>
            <td colspan="3" style="text-align: right; font-weight: 600; font-size: 12px;"></td>
        `;
        tbody.appendChild(subtotalRow);
    }
    
    // Add grand total rows
    const totalReceivablesRow = document.createElement('tr');
    totalReceivablesRow.className = 'total-row';
    totalReceivablesRow.innerHTML = `
        <td colspan="8" style="text-align: right; font-weight: 700; font-size: 13px; color: #1b5e20;">Total Receivables (+):</td>
        <td class="tc-right tc-text-success" style="font-weight: 700; font-size: 13px; color: #28a745;">+ ${formatCurrency(totalReceivables)}</td>
        <td class="tc-text-success" style="font-size: 13px; color: #28a745;">Receivable</td>
        <td colspan="1"></td>
    `;
    tbody.appendChild(totalReceivablesRow);
    
    const totalPayablesRow = document.createElement('tr');
    totalPayablesRow.className = 'total-row';
    totalPayablesRow.innerHTML = `
        <td colspan="8" style="text-align: right; font-weight: 700; font-size: 13px; color: #b71c1c;">Total Payables (-):</td>
        <td class="tc-right tc-text-danger" style="font-weight: 700; font-size: 13px; color: #dc3545;">- ${formatCurrency(totalPayables)}</td>
        <td class="tc-text-danger" style="font-size: 13px; color: #dc3545;">Payable</td>
        <td colspan="1"></td>
    `;
    tbody.appendChild(totalPayablesRow);
}

// Update info section
function updateInfoSection(reportData) {
    const infoSection = document.getElementById('infoSection');
    const companyNameLabel = document.getElementById('companyNameLabel');
    const reportTypeLabel = document.getElementById('reportTypeLabel');
    const asOnDateLabel = document.getElementById('asOnDateLabel');
    const totalOutstanding = document.getElementById('totalOutstanding');
    const ledgerCount = document.getElementById('ledgerCount');
    const receivablesPayables = document.getElementById('receivablesPayables');
    
    if (!infoSection) return;
    
    // Update company name
    const companyName = reportData.company_name || '-';
    if (companyNameLabel) companyNameLabel.textContent = companyName;
    
    const reportType = reportData.report_type || 'both';
    let typeLabel = 'Both (Receivables + Payables)';
    if (reportType === 'receivables') {
        typeLabel = 'Receivables (Sundry Debtors)';
    } else if (reportType === 'payables') {
        typeLabel = 'Payables (Sundry Creditors)';
    }
    
    if (reportTypeLabel) {
        reportTypeLabel.textContent = typeLabel;
        reportTypeLabel.className = 'tc-metric__value';
        if (reportType === 'receivables') {
            reportTypeLabel.style.color = '#28a745';
        } else if (reportType === 'payables') {
            reportTypeLabel.style.color = '#dc3545';
        }
    }
    
    const asOnDate = reportData.as_on_date ? formatDate(reportData.as_on_date) : '-';
    if (asOnDateLabel) asOnDateLabel.textContent = asOnDate;
    
    // Show total outstanding
    const totalRec = parseFloat(reportData.total_outstanding_receivables || 0);
    const totalPay = parseFloat(reportData.total_outstanding_payables || 0);
    
    if (totalOutstanding) {
        if (reportType === 'both') {
            totalOutstanding.textContent = `+${formatCurrency(totalRec)} / -${formatCurrency(totalPay)}`;
            totalOutstanding.style.color = '#475569';
        } else if (reportType === 'receivables') {
            // For receivables, show with + sign
            totalOutstanding.textContent = `+${formatCurrency(totalRec)}`;
            totalOutstanding.style.color = '#16a34a';
            totalOutstanding.style.fontWeight = '600';
        } else if (reportType === 'payables') {
            // For payables, show with - sign
            totalOutstanding.textContent = `-${formatCurrency(totalPay)}`;
            totalOutstanding.style.color = '#dc2626';
            totalOutstanding.style.fontWeight = '600';
        } else {
            // Fallback: calculate from receivables and payables
            const netTotal = totalRec - totalPay;
            if (netTotal >= 0) {
                totalOutstanding.textContent = `+${formatCurrency(netTotal)}`;
                totalOutstanding.style.color = '#16a34a';
            } else {
                totalOutstanding.textContent = `${formatCurrency(netTotal)}`;
                totalOutstanding.style.color = '#dc2626';
            }
            totalOutstanding.style.fontWeight = '600';
        }
    }
    
    if (ledgerCount) ledgerCount.textContent = reportData.count || 0;
    
    if (receivablesPayables) {
        receivablesPayables.textContent = `+${formatCurrency(totalRec)} / -${formatCurrency(totalPay)}`;
    }
    
    infoSection.style.display = 'block';
}

// Load outstanding report
async function loadOutstandingReport() {
    hideError();
    
    // Check if company is selected from sessionStorage
    const companyName = getSelectedCompany();
    if (!companyName) {
        // No company selected, redirect to companies page
        window.location.href = 'companies.html';
        return;
    }
    
    const loadingMessage = document.getElementById('loadingMessage');
    const table = document.getElementById('outstandingTable');
    const emptyMessage = document.getElementById('emptyMessage');
    
    if (loadingMessage) loadingMessage.style.display = 'block';
    if (table) table.style.display = 'none';
    if (emptyMessage) emptyMessage.style.display = 'none';
    
    const reportTypeSelect = document.getElementById('reportType');
    const asOnDateInput = document.getElementById('asOnDate');
    
    if (!reportTypeSelect || !asOnDateInput) {
        if (loadingMessage) loadingMessage.style.display = 'none';
        return;
    }
    
    const company = companyName;
    const reportType = reportTypeSelect.value;
    const asOnDate = asOnDateInput.value;
    
    if (!asOnDate) {
        showError('Please select As On Date');
        if (loadingMessage) loadingMessage.style.display = 'none';
        return;
    }
    
    try {
        let url = `/api/outstanding-report-1?company=${encodeURIComponent(company)}&type=${encodeURIComponent(reportType)}&as_on_date=${encodeURIComponent(asOnDate)}`;
        
        const response = await fetch(url);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
            throw new Error(errorData.error || `Server error: ${response.status}`);
        }
        
        const reportData = await response.json();
        
        // Check if reportData has error
        if (reportData.error) {
            throw new Error(reportData.error);
        }
        
        // Update info section
        updateInfoSection(reportData);
        
        // Render outstanding data
        if (reportData.data && Array.isArray(reportData.data)) {
            renderOutstandingTable(reportData.data, reportType);
            
            // Store data for export (same as original Outstanding Report)
            if (typeof window !== 'undefined') {
                window.currentOutstandingData = reportData;
            }
        } else {
            console.error('Invalid data format:', reportData);
            showError('Invalid data format received from server');
            if (emptyMessage) emptyMessage.style.display = 'block';
        }
        
        if (loadingMessage) loadingMessage.style.display = 'none';
        
    } catch (error) {
        console.error('Error loading outstanding report:', error);
        showError('Failed to load outstanding report: ' + error.message);
        if (loadingMessage) loadingMessage.style.display = 'none';
        if (emptyMessage) emptyMessage.style.display = 'block';
        const infoSection = document.getElementById('infoSection');
        if (infoSection) infoSection.style.display = 'none';
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
    console.log('📋 Outstanding Report Page Loaded');
    
    // Check if company is selected from sessionStorage
    const companyName = getSelectedCompany();
    if (!companyName) {
        // No company selected, redirect to companies page
        window.location.href = 'companies.html';
        return;
    }
    
    // Load period info to set default date
    await loadPeriodInfoForOutstanding();
    
    // Handle report type change
    const reportTypeSelect = document.getElementById('reportType');
    if (reportTypeSelect) {
        reportTypeSelect.addEventListener('change', () => {
            loadOutstandingReport();
        });
    }
    
    // Handle as on date change - immediate feedback
    const asOnDateInput = document.getElementById('asOnDate');
    if (asOnDateInput) {
        let dateChangeTimeout;
        asOnDateInput.addEventListener('change', () => {
            // Clear any pending timeout
            if (dateChangeTimeout) {
                clearTimeout(dateChangeTimeout);
            }
            
            // Show loading immediately
            const loadingMessage = document.getElementById('loadingMessage');
            const table = document.getElementById('outstandingTable');
            const emptyMessage = document.getElementById('emptyMessage');
            
            if (loadingMessage) loadingMessage.style.display = 'block';
            if (table) table.style.display = 'none';
            if (emptyMessage) emptyMessage.style.display = 'none';
            
            // Load report with small delay to ensure UI updates
            dateChangeTimeout = setTimeout(() => {
                loadOutstandingReport();
            }, 50);
        });
    }
    
    // Load initial report
    loadOutstandingReport();
});

/**
 * Export outstanding report (Bill-wise) - Original function name
 * @param {string} format - Export format ('csv', 'excel', 'pdf')
 */
function exportOutstandingReport(format) {
    if (!window.currentOutstandingData) {
        alert('No data available to export');
        return;
    }
    
    const data = window.currentOutstandingData;
    const bills = data.data || [];
    
    if (format === 'csv') {
        // CSV Header
        let csv = 'Sr. No.,Ledger Name,Bill Ref,Bill Date,Ref Type,Vch Type,Vch No,Outstanding Amount,Type,Due On,Overdue Days\n';
        
        // CSV Data rows
        bills.forEach((bill, index) => {
            const outstandingAmt = parseFloat(bill.outstanding_amount || 0);
            const balance = parseFloat(bill.balance || 0);
            const isReceivable = bill.is_receivable !== undefined ? bill.is_receivable : balance > 0;
            const typeSymbol = isReceivable ? '+' : '-';
            const typeLabel = isReceivable ? 'Receivable' : 'Payable';
            const billDate = bill.bill_date ? formatDate(bill.bill_date) : '-';
            const dueDate = bill.due_date ? formatDate(bill.due_date) : '-';
            const overdueDays = bill.overdue_days !== undefined && bill.overdue_days !== null ? bill.overdue_days : 0;
            
            csv += `${index + 1},"${bill.ledger_name || ''}","${bill.bill_ref || ''}",${billDate},"${bill.bill_type || ''}","${bill.voucher_type || ''}","${bill.voucher_no || ''}",${typeSymbol}${outstandingAmt},"${typeLabel}",${dueDate},${overdueDays > 0 ? overdueDays : ''}\n`;
        });
        
        // Add totals
        const totalRec = parseFloat(data.total_outstanding_receivables || 0);
        const totalPay = parseFloat(data.total_outstanding_payables || 0);
        csv += `\nTotal Receivables,${totalRec}\n`;
        csv += `Total Payables,${totalPay}\n`;
        
        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        const companyName = (data.company_name || 'report').replace(/[^a-zA-Z0-9]/g, '_');
        const dateStr = data.as_on_date || new Date().toISOString().split('T')[0];
        a.download = `outstanding-report-${companyName}-${dateStr}.csv`;
        a.click();
        window.URL.revokeObjectURL(url);
    } else if (format === 'excel') {
        // For Excel, use CSV format (browsers will open in Excel)
        exportOutstandingReport('csv');
    } else if (format === 'pdf') {
        alert('PDF export coming soon!');
    }
}
