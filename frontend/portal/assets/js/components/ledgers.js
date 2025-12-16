/* ============================================
   Ledgers Component - Ledger List & Selection
   ============================================ */

/**
 * Display ledgers with filters and pagination
 * @param {Array} ledgers - Array of ledger objects
 */
function displayLedgers(ledgers) {
    // Store all ledgers
    allLedgers = ledgers || [];
    
    // Load saved preferences
    loadLedgerPreferences();
    
    // Apply filters and sorting
    applyFiltersAndSort();
    
    // Update data context
    updateDataContext();
    
    // Render paginated list
    renderLedgerList();
}

/**
 * Render ledger list with pagination
 */
function renderLedgerList() {
    const list = document.getElementById('ledgerList');
    list.innerHTML = '';
    
    if (filteredLedgers.length === 0) {
        list.innerHTML = '<div class="loading">No ledgers found matching your criteria.</div>';
        document.getElementById('pagination').style.display = 'none';
        return;
    }
    
    // Calculate pagination
    const totalPages = Math.ceil(filteredLedgers.length / itemsPerPage);
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = Math.min(startIndex + itemsPerPage, filteredLedgers.length);
    const pageLedgers = filteredLedgers.slice(startIndex, endIndex);
    
    // Render ledger items
    pageLedgers.forEach(ledger => {
        const item = document.createElement('div');
        item.className = 'ledger-item';
        item.innerHTML = `
            <div class="ledger-info">
                <div class="ledger-name">${ledger.name}</div>
                <div class="ledger-count">Transactions: ${ledger.count || 0}</div>
            </div>
        `;
        item.setAttribute('data-ledger-name', ledger.name);
        item.onclick = () => selectLedger(ledger);
        list.appendChild(item);
    });
    
    // Render pagination
    renderPagination(totalPages);
}

/**
 * Render pagination controls
 * @param {number} totalPages - Total number of pages
 */
function renderPagination(totalPages) {
    const pagination = document.getElementById('pagination');
    
    if (totalPages <= 1) {
        pagination.style.display = 'none';
        return;
    }
    
    pagination.style.display = 'flex';
    pagination.innerHTML = '';
    
    // Previous button
    const prevBtn = document.createElement('button');
    prevBtn.textContent = '← Previous';
    prevBtn.disabled = currentPage === 1;
    prevBtn.onclick = () => {
        if (currentPage > 1) {
            currentPage--;
            renderLedgerList();
            updateDataContext();
            saveLedgerPreferences();
        }
    };
    pagination.appendChild(prevBtn);
    
    // Page numbers
    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(totalPages, currentPage + 2);
    
    if (startPage > 1) {
        const firstBtn = document.createElement('button');
        firstBtn.textContent = '1';
        firstBtn.onclick = () => {
            currentPage = 1;
            renderLedgerList();
            updateDataContext();
            saveLedgerPreferences();
        };
        pagination.appendChild(firstBtn);
        
        if (startPage > 2) {
            const ellipsis = document.createElement('span');
            ellipsis.textContent = '...';
            ellipsis.className = 'pagination-info';
            pagination.appendChild(ellipsis);
        }
    }
    
    for (let i = startPage; i <= endPage; i++) {
        const pageBtn = document.createElement('button');
        pageBtn.textContent = i;
        pageBtn.className = i === currentPage ? 'active' : '';
        pageBtn.onclick = () => {
            currentPage = i;
            renderLedgerList();
            updateDataContext();
            saveLedgerPreferences();
        };
        pagination.appendChild(pageBtn);
    }
    
    if (endPage < totalPages) {
        if (endPage < totalPages - 1) {
            const ellipsis = document.createElement('span');
            ellipsis.textContent = '...';
            ellipsis.className = 'pagination-info';
            pagination.appendChild(ellipsis);
        }
        
        const lastBtn = document.createElement('button');
        lastBtn.textContent = totalPages;
        lastBtn.onclick = () => {
            currentPage = totalPages;
            renderLedgerList();
            updateDataContext();
            saveLedgerPreferences();
        };
        pagination.appendChild(lastBtn);
    }
    
    // Next button
    const nextBtn = document.createElement('button');
    nextBtn.textContent = 'Next →';
    nextBtn.disabled = currentPage === totalPages;
    nextBtn.onclick = () => {
        if (currentPage < totalPages) {
            currentPage++;
            renderLedgerList();
            updateDataContext();
            saveLedgerPreferences();
        }
    };
    pagination.appendChild(nextBtn);
    
    // Page info
    const info = document.createElement('span');
    info.className = 'pagination-info';
    const startIndex = (currentPage - 1) * itemsPerPage + 1;
    const endIndex = Math.min(currentPage * itemsPerPage, filteredLedgers.length);
    info.textContent = `Showing ${startIndex}-${endIndex} of ${filteredLedgers.length}`;
    pagination.appendChild(info);
}

/**
 * Handle ledger selection
 * @param {object} ledger - Selected ledger object
 */
function selectLedger(ledger) {
    selectedLedger = ledger;
    
    // Highlight selected
    document.querySelectorAll('.ledger-item').forEach(item => {
        item.classList.remove('selected');
    });
    event.currentTarget.classList.add('selected');
    
    // Use original ledger name
    const originalLedgerName = ledger.name;
    
    // Sanitize guid and alterid for URL
    const safeGuid = selectedCompany.guid.replace(/-/g, '_').replace(/\./g, '_');
    const safeAlterid = String(selectedCompany.alterid).replace(/\./g, '_');
    
    // Call API to get ledger data (no file generation)
    const apiUrl = `api/ledger-data/${safeGuid}_${safeAlterid}/${encodeURIComponent(originalLedgerName)}?from=01-04-2024&to=31-12-2025`;
    loadLedgerReport(apiUrl, 'ledgers');
}

/**
 * Show ledger selection page
 */
function showLedgerSelection() {
    if (!selectedCompany) return;
    
    // Load ledgers for selected company
    loadLedgers();
    showPage('ledgers');
}

