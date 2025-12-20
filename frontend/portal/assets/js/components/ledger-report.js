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
    
    // Hide loading and empty states
    const loadingMessage = document.getElementById('loadingMessage');
    const emptyMessage = document.getElementById('emptyMessage');
    if (loadingMessage) loadingMessage.style.display = 'none';
    if (emptyMessage) emptyMessage.style.display = 'none';
    
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
    
    // Check if data is empty
    if (!data || !data.transactions || data.transactions.length === 0) {
        if (emptyMessage) emptyMessage.style.display = 'block';
        contentDiv.innerHTML = '';
        return;
    }
    
    // Build HTML - Class-based (no inline styles)
    let html = `
        <div class="tc-panel tc-report" id="ledgerReportContent">
            <!-- Header with Export Buttons -->
            <div class="tc-header-row tc-mb-16">
                <div>
                    <h2 class="tc-title-xl">${data.company_name}</h2>
                    <h3 class="tc-title-lg">Ledger: ${data.ledger_name}</h3>
                </div>
                <div class="tc-actions">
                    <button onclick="exportLedgerReport('csv')" class="tc-btn tc-btn--success">
                        📄 CSV
                    </button>
                    <button onclick="exportLedgerReport('excel')" class="tc-btn tc-btn--primary">
                        📊 Excel
                    </button>
                    <button onclick="exportLedgerReport('pdf')" class="tc-btn tc-btn--danger">
                        📑 PDF
                    </button>
                </div>
            </div>
            
            <!-- Summary Box - Tally Style -->
            <div class="tc-grid tc-grid--4 tc-mb-16">
                <div class="tc-metric tc-metric--slate tc-metric--compact">
                    <div class="tc-metric__label">Opening Balance</div>
                    <div class="tc-metric__value tc-metric__value--xl">${formatCurrency(data.opening_balance)}</div>
                </div>
                <div class="tc-metric tc-metric--green tc-metric--compact">
                    <div class="tc-metric__label">Total Debit</div>
                    <div class="tc-metric__value tc-metric__value--xl">${formatCurrency(data.total_debit)}</div>
                </div>
                <div class="tc-metric tc-metric--red tc-metric--compact">
                    <div class="tc-metric__label">Total Credit</div>
                    <div class="tc-metric__value tc-metric__value--xl">${formatCurrency(data.total_credit)}</div>
                </div>
                <div class="tc-metric tc-metric--blue tc-metric--compact">
                    <div class="tc-metric__label">Closing Balance</div>
                    <div class="tc-metric__value tc-metric__value--xl">${formatCurrency(data.closing_balance)}</div>
                </div>
            </div>
            
            <!-- Period Info -->
            <div class="tc-period-bar">
                <strong>Period:</strong> ${data.from_date} to ${data.to_date} | <strong>Transactions:</strong> ${data.total_transactions}
            </div>
            
            <!-- Transaction Table - Tally Style -->
            <div class="tc-table-wrap">
                <table class="tc-table" id="ledgerTable">
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Particulars</th>
                            <th>Vch Type</th>
                            <th>Vch No.</th>
                            <th class="tc-right">Debit</th>
                            <th class="tc-right">Credit</th>
                            <th class="tc-right">Balance</th>
                        </tr>
                    </thead>
                    <tbody>
    `;
    
    data.transactions.forEach(trans => {
        const isSpecial = trans.isSpecial || false;
        const dateFormatted = trans.date ? formatDateTally(trans.date) : '';
        const balanceValue = trans.balance !== null && trans.balance !== undefined ? Math.abs(trans.balance) : null;
        const balanceCssClass = trans.balance > 0 ? 'tc-text-success' : trans.balance < 0 ? 'tc-text-danger' : 'tc-text-primary';
        
        // Tally style: Show only debit OR credit, not both
        // For special rows (Current Total), always show even if 0
        let debitDisplay = '';
        let creditDisplay = '';
        
        if (isSpecial && trans.particulars === 'Current Total') {
            // Current Total: Always show amounts (even if 0.00)
            debitDisplay = trans.debit !== null && trans.debit !== undefined ? formatCurrency(trans.debit) : '0.00';
            creditDisplay = trans.credit !== null && trans.credit !== undefined ? formatCurrency(trans.credit) : '0.00';
        } else if (isSpecial && trans.particulars === 'Closing Balance') {
            // Closing Balance: Show 0.00 in Credit if balance is zero (Tally style)
            if (trans.debit !== null && trans.debit !== undefined && trans.debit > 0) {
                debitDisplay = formatCurrency(trans.debit);
            }
            if (trans.credit !== null && trans.credit !== undefined) {
                creditDisplay = formatCurrency(trans.credit);  // Shows 0.00 if balance is zero
            }
        } else {
            // Regular transactions: Show only if > 0
            debitDisplay = trans.debit !== null && trans.debit !== undefined && trans.debit > 0 ? formatCurrency(trans.debit) : '';
            creditDisplay = trans.credit !== null && trans.credit !== undefined && trans.credit > 0 ? formatCurrency(trans.credit) : '';
        }
        
        // Use particulars if available, otherwise narration
        const particulars = (trans.particulars || trans.narration || '').substring(0, 60);
        
        // Special row styling
        const rowClass = isSpecial ? 'special-row' : '';
        const rowStyle = isSpecial ? 'background: rgba(15, 23, 42, 0.04); font-weight: 700;' : '';
        
        html += `
            <tr class="${rowClass}" style="${rowStyle}">
                <td>${dateFormatted}</td>
                <td><strong>${particulars || '-'}</strong></td>
                <td>${trans.voucher_type || '-'}</td>
                <td>${trans.voucher_number || '-'}</td>
                <td class="tc-right tc-text-success ${trans.debit > 0 ? 'tc-fw-600' : ''}">${debitDisplay || '-'}</td>
                <td class="tc-right tc-text-danger ${trans.credit > 0 ? 'tc-fw-600' : ''}">${creditDisplay || '-'}</td>
                <td class="tc-right tc-fw-600 ${balanceCssClass}">${balanceValue !== null ? formatCurrency(balanceValue) : '-'}</td>
            </tr>
        `;
    });
    
    // No separate tfoot needed - Current Total comes from UNION ALL query
    html += `
                    </tbody>
                </table>
                </table>
            </div>
        </div>
    `;
    
    contentDiv.innerHTML = html;
}
