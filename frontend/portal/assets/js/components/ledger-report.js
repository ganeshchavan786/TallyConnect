/* ============================================
   Ledger Report Component - Report Rendering
   ============================================ */

/**
 * Render ledger report
 * @param {object} data - Ledger report data
 */
function renderLedgerReport(data) {
    // Store data for export
    currentLedgerData = data;
    
    const contentDiv = document.getElementById('reportContent');
    if (!contentDiv) {
        console.error('reportContent element not found');
        return;
    }
    
    // Ensure period controls are visible
    const periodControls = document.getElementById('periodControls');
    if (periodControls) {
        periodControls.style.display = 'block';
    }
    
    // Build HTML - Tally Style
    let html = `
        <div style="padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" id="ledgerReportContent">
            <!-- Header with Export Buttons -->
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 10px;">
                <div>
                    <h2 style="color: #2c3e50; margin-bottom: 5px; font-size: 24px;">${data.company_name}</h2>
                    <h3 style="color: #34495e; margin-bottom: 0; font-size: 18px;">Ledger: ${data.ledger_name}</h3>
                </div>
                <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                    <button onclick="exportLedgerReport('csv')" style="padding: 10px 20px; background: #27ae60; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 14px; display: flex; align-items: center; gap: 8px;">
                        📄 CSV
                    </button>
                    <button onclick="exportLedgerReport('excel')" style="padding: 10px 20px; background: #2980b9; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 14px; display: flex; align-items: center; gap: 8px;">
                        📊 Excel
                    </button>
                    <button onclick="exportLedgerReport('pdf')" style="padding: 10px 20px; background: #e74c3c; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 14px; display: flex; align-items: center; gap: 8px;">
                        📑 PDF
                    </button>
                </div>
            </div>
            
            <!-- Summary Box - Tally Style -->
            <div style="margin-bottom: 20px; padding: 15px; background: #f8f9fa; border-radius: 4px; border: 1px solid #dee2e6;">
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; text-align: center;">
                    <div>
                        <div style="font-size: 11px; color: #6c757d; text-transform: uppercase; margin-bottom: 5px;">Opening Balance</div>
                        <div style="font-size: 16px; font-weight: 600; color: #2c3e50;">${formatCurrency(data.opening_balance)}</div>
                    </div>
                    <div>
                        <div style="font-size: 11px; color: #6c757d; text-transform: uppercase; margin-bottom: 5px;">Total Debit</div>
                        <div style="font-size: 16px; font-weight: 600; color: #27ae60;">${formatCurrency(data.total_debit)}</div>
                    </div>
                    <div>
                        <div style="font-size: 11px; color: #6c757d; text-transform: uppercase; margin-bottom: 5px;">Total Credit</div>
                        <div style="font-size: 16px; font-weight: 600; color: #e74c3c;">${formatCurrency(data.total_credit)}</div>
                    </div>
                    <div>
                        <div style="font-size: 11px; color: #6c757d; text-transform: uppercase; margin-bottom: 5px;">Closing Balance</div>
                        <div style="font-size: 16px; font-weight: 600; color: #3498db;">${formatCurrency(data.closing_balance)}</div>
                    </div>
                </div>
            </div>
            
            <!-- Period Info -->
            <div style="margin-bottom: 15px; color: #6c757d; font-size: 13px; padding: 8px; background: #f8f9fa; border-radius: 4px;">
                <strong>Period:</strong> ${data.from_date} to ${data.to_date} | <strong>Transactions:</strong> ${data.total_transactions}
            </div>
            
            <!-- Transaction Table - Tally Style -->
            <div style="overflow-x: auto; border: 1px solid #dee2e6; border-radius: 4px;">
                <table style="width: 100%; border-collapse: collapse; font-size: 13px;" id="ledgerTable">
                    <thead>
                        <tr style="background: #495057; color: white;">
                            <th style="padding: 10px 8px; text-align: left; border: 1px solid #343a40; font-weight: 600; white-space: nowrap;">Date</th>
                            <th style="padding: 10px 8px; text-align: left; border: 1px solid #343a40; font-weight: 600; white-space: nowrap;">Particulars</th>
                            <th style="padding: 10px 8px; text-align: left; border: 1px solid #343a40; font-weight: 600; white-space: nowrap;">Vch Type</th>
                            <th style="padding: 10px 8px; text-align: left; border: 1px solid #343a40; font-weight: 600; white-space: nowrap;">Vch No.</th>
                            <th style="padding: 10px 8px; text-align: right; border: 1px solid #343a40; font-weight: 600; white-space: nowrap;">Debit</th>
                            <th style="padding: 10px 8px; text-align: right; border: 1px solid #343a40; font-weight: 600; white-space: nowrap;">Credit</th>
                            <th style="padding: 10px 8px; text-align: right; border: 1px solid #343a40; font-weight: 600; white-space: nowrap;">Balance</th>
                        </tr>
                    </thead>
                    <tbody>
    `;
    
    data.transactions.forEach(trans => {
        const dateFormatted = formatDateTally(trans.date);
        const balanceValue = Math.abs(trans.balance);
        const balanceClass = trans.balance > 0 ? 'color: #27ae60;' : trans.balance < 0 ? 'color: #e74c3c;' : 'color: #3498db;';
        
        // Tally style: Show only debit OR credit, not both
        const debitDisplay = trans.debit > 0 ? formatCurrency(trans.debit) : '';
        const creditDisplay = trans.credit > 0 ? formatCurrency(trans.credit) : '';
        
        // Use particulars if available, otherwise narration
        const particulars = (trans.particulars || trans.narration || '').substring(0, 60);
        
        html += `
            <tr style="border-bottom: 1px solid #dee2e6;">
                <td style="padding: 8px; border-right: 1px solid #dee2e6; white-space: nowrap;">${dateFormatted}</td>
                <td style="padding: 8px; border-right: 1px solid #dee2e6; max-width: 300px;">${particulars || '-'}</td>
                <td style="padding: 8px; border-right: 1px solid #dee2e6; white-space: nowrap;">${trans.voucher_type || '-'}</td>
                <td style="padding: 8px; border-right: 1px solid #dee2e6; white-space: nowrap;">${trans.voucher_number || '-'}</td>
                <td style="padding: 8px; text-align: right; border-right: 1px solid #dee2e6; color: #27ae60; white-space: nowrap; font-weight: ${trans.debit > 0 ? '600' : '400'};">${debitDisplay}</td>
                <td style="padding: 8px; text-align: right; border-right: 1px solid #dee2e6; color: #e74c3c; white-space: nowrap; font-weight: ${trans.credit > 0 ? '600' : '400'};">${creditDisplay}</td>
                <td style="padding: 8px; text-align: right; ${balanceClass} white-space: nowrap; font-weight: 600;">${formatCurrency(balanceValue)}</td>
            </tr>
        `;
    });
    
    // Add totals row
    html += `
                    </tbody>
                    <tfoot>
                        <tr style="background: #f8f9fa; font-weight: 600; border-top: 2px solid #495057;">
                            <td colspan="4" style="padding: 10px 8px; text-align: right; border: 1px solid #dee2e6;"><strong>Current Total:</strong></td>
                            <td style="padding: 10px 8px; text-align: right; border: 1px solid #dee2e6; color: #27ae60;">${formatCurrency(data.total_debit)}</td>
                            <td style="padding: 10px 8px; text-align: right; border: 1px solid #dee2e6; color: #e74c3c;">${formatCurrency(data.total_credit)}</td>
                            <td style="padding: 10px 8px; text-align: right; border: 1px solid #dee2e6; color: #3498db;">${formatCurrency(Math.abs(data.closing_balance))}</td>
                        </tr>
                    </tfoot>
                </table>
            </div>
        </div>
    `;
    
    contentDiv.innerHTML = html;
}
