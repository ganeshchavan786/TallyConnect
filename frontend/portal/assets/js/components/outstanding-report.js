/* ============================================
   Outstanding Report Component
   ============================================ */

/**
 * Render outstanding report
 * @param {object} data - Outstanding report data
 */
function renderOutstandingReport(data) {
    const contentDiv = document.getElementById('reportContent');
    if (!contentDiv) {
        console.error('reportContent element not found');
        return;
    }
    
    let html = `
        <div style="padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h2 style="color: #2c3e50; margin-bottom: 10px;">${data.company_name}</h2>
            <h3 style="color: #34495e; margin-bottom: 20px;">Outstanding Report</h3>
            <div style="margin-bottom: 20px; padding: 15px; background: #ecf0f1; border-radius: 4px;">
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; text-align: center;">
                    <div>
                        <div style="font-size: 12px; color: #7f8c8d;">Total Parties</div>
                        <div style="font-size: 18px; font-weight: 600; color: #2c3e50;">${data.total_parties || 0}</div>
                    </div>
                    <div>
                        <div style="font-size: 12px; color: #7f8c8d;">Total Debit</div>
                        <div style="font-size: 18px; font-weight: 600; color: #27ae60;">${formatCurrency(data.total_debit || 0)}</div>
                    </div>
                    <div>
                        <div style="font-size: 12px; color: #7f8c8d;">Total Credit</div>
                        <div style="font-size: 18px; font-weight: 600; color: #e74c3c;">${formatCurrency(data.total_credit || 0)}</div>
                    </div>
                    <div>
                        <div style="font-size: 12px; color: #7f8c8d;">Total Outstanding</div>
                        <div style="font-size: 18px; font-weight: 600; color: #3498db;">${formatCurrency(data.total_outstanding || 0)}</div>
                    </div>
                </div>
            </div>
            <div style="margin-bottom: 10px; color: #7f8c8d; font-size: 14px;">
                As on: ${data.as_on_date || 'N/A'}
            </div>
            <div style="overflow-x: auto;">
                <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
                    <thead>
                        <tr style="background: #34495e; color: white;">
                            <th style="padding: 12px; text-align: left; border: 1px solid #2c3e50;">Party Name</th>
                            <th style="padding: 12px; text-align: right; border: 1px solid #2c3e50;">Debit</th>
                            <th style="padding: 12px; text-align: right; border: 1px solid #2c3e50;">Credit</th>
                            <th style="padding: 12px; text-align: right; border: 1px solid #2c3e50;">Balance</th>
                            <th style="padding: 12px; text-align: center; border: 1px solid #2c3e50;">Transactions</th>
                            <th style="padding: 12px; text-align: center; border: 1px solid #2c3e50;">Last Transaction</th>
                        </tr>
                    </thead>
                    <tbody>
    `;
    
    // Check if parties array exists
    if (data.parties && Array.isArray(data.parties)) {
        data.parties.forEach(party => {
            const balanceClass = party.balance > 0 ? 'color: #27ae60;' : party.balance < 0 ? 'color: #e74c3c;' : '';
            html += `
                <tr style="border-bottom: 1px solid #ecf0f1;">
                    <td style="padding: 10px; font-weight: 600;">${party.party_name || '-'}</td>
                    <td style="padding: 10px; text-align: right; color: #27ae60;">${formatCurrency(party.debit || 0)}</td>
                    <td style="padding: 10px; text-align: right; color: #e74c3c;">${formatCurrency(party.credit || 0)}</td>
                    <td style="padding: 10px; text-align: right; font-weight: 600; ${balanceClass}">${formatCurrency(Math.abs(party.balance || 0))}</td>
                    <td style="padding: 10px; text-align: center;">${party.transaction_count || 0}</td>
                    <td style="padding: 10px; text-align: center; font-size: 12px; color: #7f8c8d;">${party.last_transaction || '-'}</td>
                </tr>
            `;
        });
    } else {
        html += `
            <tr>
                <td colspan="6" style="text-align: center; padding: 20px; color: #7f8c8d;">No parties found</td>
            </tr>
        `;
    }
    
    html += `
                    </tbody>
                </table>
            </div>
        </div>
    `;
    
    contentDiv.innerHTML = html;
}

