/* ============================================
   Export - Data Export Functions
   ============================================ */

// Store current ledger data for export
let currentLedgerData = null;

/**
 * Export ledger report in specified format
 * @param {string} format - Export format ('csv', 'excel', 'pdf')
 */
function exportLedgerReport(format) {
    if (!currentLedgerData) {
        alert('No data to export');
        return;
    }
    
    const data = currentLedgerData;
    const fileName = `Ledger_${data.ledger_name.replace(/[^a-zA-Z0-9]/g, '_')}_${data.from_date.replace(/-/g, '')}_${data.to_date.replace(/-/g, '')}`;
    
    switch(format) {
        case 'csv':
            exportToCSV(data, fileName);
            break;
        case 'excel':
            exportToExcel(data, fileName);
            break;
        case 'pdf':
            exportToPDF(data, fileName);
            break;
    }
}

/**
 * Export data to CSV format
 * @param {object} data - Ledger report data
 * @param {string} fileName - File name without extension
 */
function exportToCSV(data, fileName) {
    let csv = 'Date,Particulars,Vch Type,Vch No.,Debit,Credit,Balance\n';
    
    data.transactions.forEach(trans => {
        const date = trans.date || '';
        const particulars = (trans.particulars || trans.narration || '').replace(/"/g, '""');
        const vchType = trans.voucher_type || '';
        const vchNo = trans.voucher_number || '';
        const debit = trans.debit > 0 ? trans.debit : '';
        const credit = trans.credit > 0 ? trans.credit : '';
        const balance = Math.abs(trans.balance);
        
        csv += `"${date}","${particulars}","${vchType}","${vchNo}","${debit}","${credit}","${balance}"\n`;
    });
    
    // Add totals
    csv += `"","","","","Current Total","${data.total_debit}","${data.total_credit}","${Math.abs(data.closing_balance)}"\n`;
    
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `${fileName}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

/**
 * Export data to Excel format
 * @param {object} data - Ledger report data
 * @param {string} fileName - File name without extension
 */
function exportToExcel(data, fileName) {
    // Create HTML table for Excel
    let html = `
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #000; padding: 8px; text-align: left; }
                th { background-color: #495057; color: white; font-weight: bold; }
                .text-right { text-align: right; }
                .footer { background-color: #f8f9fa; font-weight: bold; }
            </style>
        </head>
        <body>
            <h2>${data.company_name}</h2>
            <h3>Ledger: ${data.ledger_name}</h3>
            <p>Period: ${data.from_date} to ${data.to_date}</p>
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Particulars</th>
                        <th>Vch Type</th>
                        <th>Vch No.</th>
                        <th class="text-right">Debit</th>
                        <th class="text-right">Credit</th>
                        <th class="text-right">Balance</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    data.transactions.forEach(trans => {
        const debit = trans.debit > 0 ? trans.debit.toFixed(2) : '';
        const credit = trans.credit > 0 ? trans.credit.toFixed(2) : '';
        const balance = Math.abs(trans.balance).toFixed(2);
        
        const particulars = (trans.particulars || trans.narration || '').replace(/</g, '&lt;').replace(/>/g, '&gt;');
        
        html += `
            <tr>
                <td>${trans.date}</td>
                <td>${particulars}</td>
                <td>${trans.voucher_type || ''}</td>
                <td>${trans.voucher_number || ''}</td>
                <td class="text-right">${debit}</td>
                <td class="text-right">${credit}</td>
                <td class="text-right">${balance}</td>
            </tr>
        `;
    });
    
    html += `
                </tbody>
                <tfoot>
                    <tr class="footer">
                        <td colspan="4" class="text-right"><strong>Current Total:</strong></td>
                        <td class="text-right">${data.total_debit.toFixed(2)}</td>
                        <td class="text-right">${data.total_credit.toFixed(2)}</td>
                        <td class="text-right">${Math.abs(data.closing_balance).toFixed(2)}</td>
                    </tr>
                </tfoot>
            </table>
        </body>
        </html>
    `;
    
    const blob = new Blob([html], { type: 'application/vnd.ms-excel' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `${fileName}.xls`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

/**
 * Export data to PDF format
 * @param {object} data - Ledger report data
 * @param {string} fileName - File name without extension
 */
function exportToPDF(data, fileName) {
    // Use browser's print to PDF
    const printWindow = window.open('', '_blank');
    const content = document.getElementById('ledgerReportContent').innerHTML;
    
    printWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>${data.ledger_name} - Ledger Report</title>
            <style>
                @media print {
                    @page { margin: 1cm; }
                    body { font-family: Arial, sans-serif; }
                    table { border-collapse: collapse; width: 100%; font-size: 10px; }
                    th, td { border: 1px solid #000; padding: 6px; }
                    th { background-color: #495057; color: white; }
                    .text-right { text-align: right; }
                }
                body { font-family: Arial, sans-serif; padding: 20px; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #000; padding: 8px; }
                th { background-color: #495057; color: white; }
            </style>
        </head>
        <body>
            ${content}
        </body>
        </html>
    `);
    printWindow.document.close();
    
    setTimeout(() => {
        printWindow.print();
    }, 250);
}

/**
 * Export ledger list to CSV
 */
function exportLedgers() {
    if (filteredLedgers.length === 0) {
        alert('No ledgers to export');
        return;
    }
    
    // Create CSV content
    let csv = 'Ledger Name,Transactions\n';
    filteredLedgers.forEach(ledger => {
        csv += `"${ledger.name}",${ledger.count || 0}\n`;
    });
    
    // Create blob and download
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `ledgers_${selectedCompany?.name || 'export'}_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

