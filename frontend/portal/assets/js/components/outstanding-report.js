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
        <div class="tc-section">
            <div class="tc-header-row">
                <div>
                    <h2 class="tc-title-xl">${data.company_name}</h2>
                    <h3 class="tc-title-lg">Outstanding Report</h3>
                    <div class="tc-subtitle">As on: ${data.as_on_date || 'N/A'}</div>
                </div>
                <div class="tc-actions">
                    <button onclick="exportOutstandingReport('csv')" class="tc-btn tc-btn--success">
                        📄 CSV
                    </button>
                    <button onclick="exportOutstandingReport('excel')" class="tc-btn tc-btn--primary">
                        📊 Excel
                    </button>
                    <button onclick="exportOutstandingReport('pdf')" class="tc-btn tc-btn--danger">
                        📑 PDF
                    </button>
                </div>
            </div>
            
            <!-- KPI Cards -->
            <div class="tc-kpi-grid">
                <div class="tc-kpi tc-kpi--mint">
                    <div class="tc-kpi__top">
                        <div class="tc-kpi__label">Total Parties</div>
                        <div class="tc-kpi__icon">👥</div>
                    </div>
                    <div class="tc-kpi__value">${data.total_parties || 0}</div>
                    <div class="tc-kpi__sub">Parties</div>
                </div>
                <div class="tc-kpi tc-kpi--sky">
                    <div class="tc-kpi__top">
                        <div class="tc-kpi__label">Total Debit</div>
                        <div class="tc-kpi__icon">📈</div>
                    </div>
                    <div class="tc-kpi__value">${formatCurrency(data.total_debit || 0)}</div>
                    <div class="tc-kpi__sub">Debit Amount</div>
                </div>
                <div class="tc-kpi tc-kpi--rose">
                    <div class="tc-kpi__top">
                        <div class="tc-kpi__label">Total Credit</div>
                        <div class="tc-kpi__icon">📉</div>
                    </div>
                    <div class="tc-kpi__value">${formatCurrency(data.total_credit || 0)}</div>
                    <div class="tc-kpi__sub">Credit Amount</div>
                </div>
                <div class="tc-kpi tc-kpi--violet">
                    <div class="tc-kpi__top">
                        <div class="tc-kpi__label">Total Outstanding</div>
                        <div class="tc-kpi__icon">💰</div>
                    </div>
                    <div class="tc-kpi__value">${formatCurrency(data.total_outstanding || 0)}</div>
                    <div class="tc-kpi__sub">Net Balance</div>
                </div>
            </div>
        </div>
        
        <!-- Parties Table -->
        <div class="tc-section">
            <h3 class="tc-section__title">📋 Party Details</h3>
            <div class="tc-section__hint">Outstanding balances for all parties</div>
            <div class="tc-table-wrap">
                <table class="tc-table">
                    <thead>
                        <tr>
                            <th>Party Name</th>
                            <th class="tc-right">Debit</th>
                            <th class="tc-right">Credit</th>
                            <th class="tc-right">Balance</th>
                            <th class="tc-center">Transactions</th>
                            <th class="tc-center">Last Transaction</th>
                        </tr>
                    </thead>
                    <tbody>
    `;
    
    // Check if parties array exists
    if (data.parties && Array.isArray(data.parties)) {
        data.parties.forEach(party => {
            const balanceClass = party.balance > 0 ? 'tc-text-success' : party.balance < 0 ? 'tc-text-danger' : '';
            html += `
                        <tr>
                            <td class="tc-fw-600">${party.party_name || '-'}</td>
                            <td class="tc-right tc-text-success">${formatCurrency(party.debit || 0)}</td>
                            <td class="tc-right tc-text-danger">${formatCurrency(party.credit || 0)}</td>
                            <td class="tc-right tc-fw-600 ${balanceClass}">${formatCurrency(Math.abs(party.balance || 0))}</td>
                            <td class="tc-center">${party.transaction_count || 0}</td>
                            <td class="tc-center tc-muted">${party.last_transaction || '-'}</td>
                        </tr>
            `;
        });
    } else {
        html += `
                        <tr>
                            <td colspan="6" class="tc-center tc-muted" style="padding: 40px;">No parties found</td>
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
    
    // Store data for export
    if (typeof window !== 'undefined') {
        window.currentOutstandingData = data;
    }
}

/**
 * Export outstanding report
 * @param {string} format - Export format ('csv', 'excel', 'pdf')
 */
function exportOutstandingReport(format) {
    if (!window.currentOutstandingData) {
        alert('No data available to export');
        return;
    }
    
    const data = window.currentOutstandingData;
    const parties = data.parties || [];
    
    if (format === 'csv') {
        let csv = 'Party Name,Debit,Credit,Balance,Transactions,Last Transaction\n';
        parties.forEach(party => {
            csv += `"${party.party_name || ''}",${party.debit || 0},${party.credit || 0},${party.balance || 0},${party.transaction_count || 0},"${party.last_transaction || ''}"\n`;
        });
        
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `outstanding-report-${data.company_name || 'report'}-${new Date().toISOString().split('T')[0]}.csv`;
        a.click();
        window.URL.revokeObjectURL(url);
    } else if (format === 'excel') {
        // For Excel, use CSV format (browsers will open in Excel)
        exportOutstandingReport('csv');
    } else if (format === 'pdf') {
        alert('PDF export coming soon!');
    }
}

