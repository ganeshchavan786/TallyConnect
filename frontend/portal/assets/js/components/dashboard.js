/* ============================================
   Dashboard Component
   ============================================ */

/**
 * Render dashboard report
 * @param {object} data - Dashboard report data
 */
function renderDashboardReport(data) {
    const contentDiv = document.getElementById('reportContent');
    if (!contentDiv) {
        console.error('reportContent element not found');
        return;
    }
    
    let html = `
        <div style="padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h2 style="color: #2c3e50; margin-bottom: 20px;">${data.company_name || 'Company'} - Dashboard</h2>
            
            <!-- Summary Stats -->
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 30px;">
                <div style="padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 8px;">
                    <div style="font-size: 14px; opacity: 0.9;">Total Transactions</div>
                    <div style="font-size: 32px; font-weight: 600; margin-top: 10px;">${(data.stats && data.stats.total_transactions) ? data.stats.total_transactions.toLocaleString() : 0}</div>
                </div>
                <div style="padding: 20px; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; border-radius: 8px;">
                    <div style="font-size: 14px; opacity: 0.9;">Total Parties</div>
                    <div style="font-size: 32px; font-weight: 600; margin-top: 10px;">${(data.stats && data.stats.total_parties) ? data.stats.total_parties.toLocaleString() : 0}</div>
                </div>
                <div style="padding: 20px; background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; border-radius: 8px;">
                    <div style="font-size: 14px; opacity: 0.9;">Net Balance</div>
                    <div style="font-size: 32px; font-weight: 600; margin-top: 10px;">${formatCurrency((data.stats && data.stats.net_balance) ? data.stats.net_balance : 0)}</div>
                </div>
            </div>
            
            <!-- Top Debtors and Creditors -->
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px;">
                <div style="padding: 20px; background: #ecf0f1; border-radius: 8px;">
                    <h3 style="color: #2c3e50; margin-bottom: 15px;">Top 10 Debtors</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <thead>
                            <tr style="background: #34495e; color: white;">
                                <th style="padding: 8px; text-align: left;">Party</th>
                                <th style="padding: 8px; text-align: right;">Balance</th>
                            </tr>
                        </thead>
                        <tbody>
    `;
    
    // Check if top_debtors array exists
    if (data.top_debtors && Array.isArray(data.top_debtors)) {
        data.top_debtors.forEach((debtor, idx) => {
            html += `
                <tr style="border-bottom: 1px solid #bdc3c7;">
                    <td style="padding: 8px;">${idx + 1}. ${debtor.party_name || '-'}</td>
                    <td style="padding: 8px; text-align: right; color: #27ae60; font-weight: 600;">${formatCurrency(debtor.balance || 0)}</td>
                </tr>
            `;
        });
    } else {
        html += `
            <tr>
                <td colspan="2" style="text-align: center; padding: 10px; color: #7f8c8d;">No debtors found</td>
            </tr>
        `;
    }
    
    html += `
                        </tbody>
                    </table>
                </div>
                <div style="padding: 20px; background: #ecf0f1; border-radius: 8px;">
                    <h3 style="color: #2c3e50; margin-bottom: 15px;">Top 10 Creditors</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <thead>
                            <tr style="background: #34495e; color: white;">
                                <th style="padding: 8px; text-align: left;">Party</th>
                                <th style="padding: 8px; text-align: right;">Balance</th>
                            </tr>
                        </thead>
                        <tbody>
    `;
    
    // Check if top_creditors array exists
    if (data.top_creditors && Array.isArray(data.top_creditors)) {
        data.top_creditors.forEach((creditor, idx) => {
            html += `
                <tr style="border-bottom: 1px solid #bdc3c7;">
                    <td style="padding: 8px;">${idx + 1}. ${creditor.party_name || '-'}</td>
                    <td style="padding: 8px; text-align: right; color: #e74c3c; font-weight: 600;">${formatCurrency(creditor.balance || 0)}</td>
                </tr>
            `;
        });
    } else {
        html += `
            <tr>
                <td colspan="2" style="text-align: center; padding: 10px; color: #7f8c8d;">No creditors found</td>
            </tr>
        `;
    }
    
    html += `
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- Voucher Type Summary -->
            <div style="margin-bottom: 30px;">
                <h3 style="color: #2c3e50; margin-bottom: 15px;">Voucher Type Summary</h3>
                <div style="overflow-x: auto;">
                    <table style="width: 100%; border-collapse: collapse;">
                        <thead>
                            <tr style="background: #34495e; color: white;">
                                <th style="padding: 12px; text-align: left;">Voucher Type</th>
                                <th style="padding: 12px; text-align: right;">Count</th>
                                <th style="padding: 12px; text-align: right;">Total Debit</th>
                                <th style="padding: 12px; text-align: right;">Total Credit</th>
                            </tr>
                        </thead>
                        <tbody>
    `;
    
    // Check if voucher_types array exists
    if (data.voucher_types && Array.isArray(data.voucher_types)) {
        data.voucher_types.forEach(vt => {
            html += `
                <tr style="border-bottom: 1px solid #ecf0f1;">
                    <td style="padding: 10px;">${vt.type || '-'}</td>
                    <td style="padding: 10px; text-align: right;">${vt.count || 0}</td>
                    <td style="padding: 10px; text-align: right; color: #27ae60;">${formatCurrency(vt.debit || 0)}</td>
                    <td style="padding: 10px; text-align: right; color: #e74c3c;">${formatCurrency(vt.credit || 0)}</td>
                </tr>
            `;
        });
    } else {
        html += `
            <tr>
                <td colspan="4" style="text-align: center; padding: 10px; color: #7f8c8d;">No voucher types found</td>
            </tr>
        `;
    }
    
    html += `
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    `;
    
    contentDiv.innerHTML = html;
}

