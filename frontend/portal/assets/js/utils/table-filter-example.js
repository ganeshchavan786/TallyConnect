/* ============================================
   Example: How to use TableFilterManager for Reports
   ============================================ */

/**
 * Example: Sales Register Voucher List with Filter, Sort, Pagination
 * 
 * This shows how to use the common TableFilterManager class
 * for any report that needs filtering, sorting, and pagination.
 */

// Step 1: Create a global variable for the filter manager
let salesRegisterFilterManager = null;

// Step 2: Initialize filter manager when rendering the report
function renderSalesRegisterVouchersWithFilters(data) {
    const contentDiv = document.getElementById('reportContent');
    
    // Create HTML with filter controls
    let html = `
        <div style="padding: 20px;">
            <h2>Sales Register - Voucher List</h2>
            
            <!-- Filter Controls -->
            <div id="salesRegisterControls" style="margin-bottom: 20px; padding: 15px; background: #f8f9fa; border-radius: 8px;">
                <div style="display: flex; gap: 15px; align-items: center; flex-wrap: wrap;">
                    <input type="text" id="salesRegisterSearch" placeholder="🔍 Search..." style="flex: 1; padding: 10px; border: 2px solid #dee2e6; border-radius: 6px;">
                    <select id="salesRegisterSort" style="padding: 10px; border: 2px solid #dee2e6; border-radius: 6px;">
                        <option value="date-desc">Date (Newest First)</option>
                        <option value="date-asc">Date (Oldest First)</option>
                        <option value="particulars-asc">Particulars (A-Z)</option>
                        <option value="debit-desc">Amount (High-Low)</option>
                    </select>
                    <button onclick="if (salesRegisterFilterManager) salesRegisterFilterManager.clearFilters()">Clear</button>
                </div>
                <div id="salesRegisterContext" style="margin-top: 10px; color: #495057;"></div>
            </div>
            
            <!-- Table -->
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Particulars</th>
                        <th>Vch No</th>
                        <th>Debit</th>
                    </tr>
                </thead>
                <tbody id="salesRegisterTableBody">
                    <!-- Data rendered by filter manager -->
                </tbody>
            </table>
            
            <!-- Pagination -->
            <div id="salesRegisterPagination" style="margin-top: 20px;"></div>
        </div>
    `;
    
    contentDiv.innerHTML = html;
    
    // Step 3: Initialize TableFilterManager
    salesRegisterFilterManager = new TableFilterManager({
        itemsPerPage: 20,
        defaultSort: 'date-desc',
        searchInputId: 'salesRegisterSearch',
        sortSelectId: 'salesRegisterSort',
        paginationId: 'salesRegisterPagination',
        contextId: 'salesRegisterContext',
        storageKey: 'sales_register_preferences',
        
        // Fields to search in
        searchFields: ['particulars', 'voucher_number', 'date'],
        
        // Custom sort functions
        sortColumns: {
            'date-asc': (a, b) => new Date(a.date) - new Date(b.date),
            'date-desc': (a, b) => new Date(b.date) - new Date(a.date),
            'particulars-asc': (a, b) => (a.particulars || '').localeCompare(b.particulars || ''),
            'debit-desc': (a, b) => (b.debit || 0) - (a.debit || 0)
        },
        
        // Render function - called when data needs to be displayed
        onRender: function(paginatedData, info) {
            const tbody = document.getElementById('salesRegisterTableBody');
            if (!tbody) return;
            
            tbody.innerHTML = '';
            
            if (paginatedData.length === 0) {
                tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; padding: 20px;">No vouchers found.</td></tr>';
                return;
            }
            
            paginatedData.forEach(vch => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${formatDateTally(vch.date)}</td>
                    <td>${vch.particulars || '-'}</td>
                    <td>${vch.voucher_number || '-'}</td>
                    <td>${formatCurrency(vch.debit || 0)}</td>
                `;
                tbody.appendChild(row);
            });
        },
        
        // Update context display
        onUpdateContext: function(info) {
            const contextEl = document.getElementById('salesRegisterContext');
            if (!contextEl) return;
            
            let text = `<strong>${info.filtered}</strong> of <strong>${info.total}</strong> vouchers`;
            if (info.searchTerm) {
                text += ` matching "<strong>${info.searchTerm}</strong>"`;
            }
            if (info.filtered > 0) {
                text += ` | Showing <strong>${info.startIndex}-${info.endIndex}</strong> on page <strong>${info.currentPage}</strong>`;
            }
            contextEl.innerHTML = text;
        },
        
        // Save preferences
        onSavePreferences: function() {
            try {
                localStorage.setItem('sales_register_preferences', JSON.stringify({
                    sort: this.config.sortBy,
                    search: this.config.searchTerm,
                    page: this.config.currentPage
                }));
            } catch (e) {
                console.warn('Could not save preferences:', e);
            }
        },
        
        // Load preferences
        onLoadPreferences: function() {
            try {
                const saved = localStorage.getItem('sales_register_preferences');
                if (saved) {
                    const prefs = JSON.parse(saved);
                    this.config.sortBy = prefs.sort || 'date-desc';
                    this.config.searchTerm = prefs.search || '';
                    this.config.currentPage = prefs.page || 1;
                    
                    // Update UI
                    const searchInput = document.getElementById('salesRegisterSearch');
                    const sortSelect = document.getElementById('salesRegisterSort');
                    if (searchInput) searchInput.value = this.config.searchTerm;
                    if (sortSelect) sortSelect.value = this.config.sortBy;
                }
            } catch (e) {
                console.warn('Could not load preferences:', e);
            }
        }
    });
    
    // Step 4: Set data and render
    salesRegisterFilterManager.setData(data.vouchers || []);
}

/**
 * Example: Ledger Report with Filters
 */
let ledgerReportFilterManager = null;

function renderLedgerReportWithFilters(data) {
    // Similar setup as above, but for ledger transactions
    ledgerReportFilterManager = new TableFilterManager({
        itemsPerPage: 50,
        defaultSort: 'date-desc',
        searchInputId: 'ledgerReportSearch',
        sortSelectId: 'ledgerReportSort',
        paginationId: 'ledgerReportPagination',
        contextId: 'ledgerReportContext',
        storageKey: 'ledger_report_preferences',
        searchFields: ['particulars', 'voucher_number', 'narration'],
        sortColumns: {
            'date-asc': (a, b) => new Date(a.date) - new Date(b.date),
            'date-desc': (a, b) => new Date(b.date) - new Date(a.date),
            'debit-desc': (a, b) => (b.debit || 0) - (a.debit || 0),
            'credit-desc': (a, b) => (b.credit || 0) - (a.credit || 0)
        },
        onRender: function(paginatedData, info) {
            // Render ledger transactions
            const tbody = document.getElementById('ledgerReportTableBody');
            // ... render logic
        },
        onUpdateContext: function(info) {
            // Update context
        },
        onSavePreferences: function() {
            // Save preferences
        },
        onLoadPreferences: function() {
            // Load preferences
        }
    });
    
    ledgerReportFilterManager.setData(data.transactions || []);
}

