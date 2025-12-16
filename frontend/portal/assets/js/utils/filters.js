/* ============================================
   Filters - Filter, Sort, Pagination Logic
   ============================================ */

/**
 * Common Table Filter and Pagination Manager
 * Can be used for any report (Sales Register, Ledger Report, etc.)
 */
class TableFilterManager {
    constructor(config) {
        this.config = {
            // Data
            allData: [],
            filteredData: [],
            
            // Pagination
            currentPage: 1,
            itemsPerPage: config.itemsPerPage || 20,
            
            // Filters
            searchTerm: '',
            sortBy: config.defaultSort || 'date-desc',
            customFilter: null, // Custom filter function
            
            // Column configuration for sorting
            sortColumns: config.sortColumns || {},
            
            // Search configuration
            searchFields: config.searchFields || [], // Fields to search in
            
            // Callbacks
            onRender: config.onRender || null, // Function to render filtered data
            onUpdateContext: config.onUpdateContext || null, // Function to update data context
            onSavePreferences: config.onSavePreferences || null, // Function to save preferences
            onLoadPreferences: config.onLoadPreferences || null, // Function to load preferences
            
            // Storage key for preferences
            storageKey: config.storageKey || 'table_preferences',
            
            // Element IDs
            searchInputId: config.searchInputId || null,
            sortSelectId: config.sortSelectId || null,
            paginationId: config.paginationId || null,
            contextId: config.contextId || null,
            
            ...config
        };
        
        this.init();
    }
    
    init() {
        // Load preferences if available
        if (this.config.onLoadPreferences) {
            this.config.onLoadPreferences.call(this);
        }
        
        // Attach event listeners
        if (this.config.searchInputId) {
            const searchInput = document.getElementById(this.config.searchInputId);
            if (searchInput) {
                searchInput.addEventListener('input', () => this.handleSearch());
            }
        }
        
        if (this.config.sortSelectId) {
            const sortSelect = document.getElementById(this.config.sortSelectId);
            if (sortSelect) {
                sortSelect.addEventListener('change', () => this.handleSort());
            }
        }
    }
    
    /**
     * Set data and apply filters
     */
    setData(data) {
        this.config.allData = Array.isArray(data) ? [...data] : [];
        this.applyFilters();
    }
    
    /**
     * Apply all filters, sorting, and pagination
     */
    applyFilters() {
        // Start with all data
        this.config.filteredData = [...this.config.allData];
        
        // Apply search filter
        if (this.config.searchTerm) {
            const searchLower = this.config.searchTerm.toLowerCase();
            this.config.filteredData = this.config.filteredData.filter(item => {
                if (this.config.searchFields.length > 0) {
                    // Search in specified fields
                    return this.config.searchFields.some(field => {
                        const value = this.getNestedValue(item, field);
                        return value && String(value).toLowerCase().includes(searchLower);
                    });
                } else {
                    // Search in all string fields
                    return Object.values(item).some(val => 
                        val && String(val).toLowerCase().includes(searchLower)
                    );
                }
            });
        }
        
        // Apply custom filter if provided
        if (this.config.customFilter && typeof this.config.customFilter === 'function') {
            this.config.filteredData = this.config.filteredData.filter(this.config.customFilter);
        }
        
        // Apply sorting
        this.applySorting();
        
        // Reset to first page
        this.config.currentPage = 1;
        
        // Render
        this.render();
    }
    
    /**
     * Apply sorting based on current sortBy value
     */
    applySorting() {
        if (!this.config.sortBy) return;
        
        this.config.filteredData.sort((a, b) => {
            // Use custom sort function if provided for this sort type
            if (this.config.sortColumns[this.config.sortBy]) {
                const sortFn = this.config.sortColumns[this.config.sortBy];
                return sortFn(a, b);
            }
            
            // Default sorting logic
            const [field, direction] = this.config.sortBy.split('-');
            const aVal = this.getNestedValue(a, field);
            const bVal = this.getNestedValue(b, field);
            
            let comparison = 0;
            if (aVal === null || aVal === undefined) comparison = 1;
            else if (bVal === null || bVal === undefined) comparison = -1;
            else if (typeof aVal === 'number' && typeof bVal === 'number') {
                comparison = aVal - bVal;
            } else {
                comparison = String(aVal).localeCompare(String(bVal));
            }
            
            return direction === 'desc' ? -comparison : comparison;
        });
    }
    
    /**
     * Get nested value from object (e.g., 'user.name')
     */
    getNestedValue(obj, path) {
        return path.split('.').reduce((current, prop) => current?.[prop], obj);
    }
    
    /**
     * Handle search input
     */
    handleSearch() {
        if (this.config.searchInputId) {
            this.config.searchTerm = document.getElementById(this.config.searchInputId).value;
            this.applyFilters();
        }
    }
    
    /**
     * Handle sort change
     */
    handleSort() {
        if (this.config.sortSelectId) {
            this.config.sortBy = document.getElementById(this.config.sortSelectId).value;
            this.applyFilters();
        }
    }
    
    /**
     * Get paginated data
     */
    getPaginatedData() {
        const startIndex = (this.config.currentPage - 1) * this.config.itemsPerPage;
        const endIndex = startIndex + this.config.itemsPerPage;
        return this.config.filteredData.slice(startIndex, endIndex);
    }
    
    /**
     * Get total pages
     */
    getTotalPages() {
        return Math.ceil(this.config.filteredData.length / this.config.itemsPerPage);
    }
    
    /**
     * Go to specific page
     */
    goToPage(page) {
        const totalPages = this.getTotalPages();
        if (page >= 1 && page <= totalPages) {
            this.config.currentPage = page;
            this.render();
        }
    }
    
    /**
     * Render pagination controls
     */
    renderPagination() {
        if (!this.config.paginationId) return;
        
        const paginationEl = document.getElementById(this.config.paginationId);
        if (!paginationEl) return;
        
        const totalPages = this.getTotalPages();
        
        if (totalPages <= 1) {
            paginationEl.style.display = 'none';
            return;
        }
        
        paginationEl.style.display = 'flex';
        paginationEl.innerHTML = '';
        
        // Previous button
        const prevBtn = document.createElement('button');
        prevBtn.textContent = '← Previous';
        prevBtn.disabled = this.config.currentPage === 1;
        prevBtn.onclick = () => this.goToPage(this.config.currentPage - 1);
        paginationEl.appendChild(prevBtn);
        
        // Page numbers
        const startPage = Math.max(1, this.config.currentPage - 2);
        const endPage = Math.min(totalPages, this.config.currentPage + 2);
        
        if (startPage > 1) {
            const firstBtn = document.createElement('button');
            firstBtn.textContent = '1';
            firstBtn.onclick = () => this.goToPage(1);
            paginationEl.appendChild(firstBtn);
            
            if (startPage > 2) {
                const ellipsis = document.createElement('span');
                ellipsis.textContent = '...';
                ellipsis.className = 'pagination-info';
                paginationEl.appendChild(ellipsis);
            }
        }
        
        for (let i = startPage; i <= endPage; i++) {
            const pageBtn = document.createElement('button');
            pageBtn.textContent = i;
            pageBtn.className = i === this.config.currentPage ? 'active' : '';
            pageBtn.onclick = () => this.goToPage(i);
            paginationEl.appendChild(pageBtn);
        }
        
        if (endPage < totalPages) {
            if (endPage < totalPages - 1) {
                const ellipsis = document.createElement('span');
                ellipsis.textContent = '...';
                ellipsis.className = 'pagination-info';
                paginationEl.appendChild(ellipsis);
            }
            
            const lastBtn = document.createElement('button');
            lastBtn.textContent = totalPages;
            lastBtn.onclick = () => this.goToPage(totalPages);
            paginationEl.appendChild(lastBtn);
        }
        
        // Next button
        const nextBtn = document.createElement('button');
        nextBtn.textContent = 'Next →';
        nextBtn.disabled = this.config.currentPage === totalPages;
        nextBtn.onclick = () => this.goToPage(this.config.currentPage + 1);
        paginationEl.appendChild(nextBtn);
        
        // Page info
        const info = document.createElement('span');
        info.className = 'pagination-info';
        const startIndex = (this.config.currentPage - 1) * this.config.itemsPerPage + 1;
        const endIndex = Math.min(this.config.currentPage * this.config.itemsPerPage, this.config.filteredData.length);
        info.textContent = `Showing ${startIndex}-${endIndex} of ${this.config.filteredData.length}`;
        paginationEl.appendChild(info);
    }
    
    /**
     * Update data context display
     */
    updateContext() {
        if (!this.config.contextId || !this.config.onUpdateContext) return;
        
        const contextEl = document.getElementById(this.config.contextId);
        if (!contextEl) return;
        
        const total = this.config.allData.length;
        const filtered = this.config.filteredData.length;
        const startIndex = (this.config.currentPage - 1) * this.config.itemsPerPage + 1;
        const endIndex = Math.min(this.config.currentPage * this.config.itemsPerPage, filtered);
        
        if (this.config.onUpdateContext) {
            this.config.onUpdateContext.call(this, {
                total,
                filtered,
                startIndex,
                endIndex,
                currentPage: this.config.currentPage,
                searchTerm: this.config.searchTerm
            });
        }
    }
    
    /**
     * Render filtered and paginated data
     */
    render() {
        // Render pagination
        this.renderPagination();
        
        // Update context
        this.updateContext();
        
        // Call custom render function
        if (this.config.onRender) {
            const paginatedData = this.getPaginatedData();
            this.config.onRender.call(this, paginatedData, {
                total: this.config.allData.length,
                filtered: this.config.filteredData.length,
                currentPage: this.config.currentPage,
                totalPages: this.getTotalPages()
            });
        }
        
        // Save preferences
        if (this.config.onSavePreferences) {
            this.config.onSavePreferences.call(this);
        }
    }
    
    /**
     * Clear all filters
     */
    clearFilters() {
        this.config.searchTerm = '';
        this.config.sortBy = this.config.defaultSort || 'date-desc';
        this.config.currentPage = 1;
        
        if (this.config.searchInputId) {
            const searchInput = document.getElementById(this.config.searchInputId);
            if (searchInput) searchInput.value = '';
        }
        
        if (this.config.sortSelectId) {
            const sortSelect = document.getElementById(this.config.sortSelectId);
            if (sortSelect) sortSelect.value = this.config.sortBy;
        }
        
        this.applyFilters();
    }
}

/**
 * Apply filters and sorting to ledger list (Legacy - for backward compatibility)
 */
function applyFiltersAndSort() {
    // Start with all ledgers
    filteredLedgers = [...allLedgers];
    
    // Apply search filter
    if (currentSearch) {
        const searchLower = currentSearch.toLowerCase();
        filteredLedgers = filteredLedgers.filter(ledger => 
            ledger.name.toLowerCase().includes(searchLower)
        );
    }
    
    // Apply count filter
    if (currentFilter !== 'all') {
        filteredLedgers = filteredLedgers.filter(ledger => {
            const count = ledger.count || 0;
            switch(currentFilter) {
                case '0-10': return count >= 0 && count <= 10;
                case '11-50': return count >= 11 && count <= 50;
                case '51-100': return count >= 51 && count <= 100;
                case '100+': return count > 100;
                default: return true;
            }
        });
    }
    
    // Apply sorting
    filteredLedgers.sort((a, b) => {
        switch(currentSort) {
            case 'name-asc':
                return (a.name || '').localeCompare(b.name || '');
            case 'name-desc':
                return (b.name || '').localeCompare(a.name || '');
            case 'count-asc':
                return (a.count || 0) - (b.count || 0);
            case 'count-desc':
                return (b.count || 0) - (a.count || 0);
            default:
                return 0;
        }
    });
    
    // Reset to first page
    currentPage = 1;
}

/**
 * Filter ledgers based on search and filter inputs
 */
function filterLedgers() {
    currentSearch = document.getElementById('ledgerSearch').value;
    currentFilter = document.getElementById('filterCount').value;
    applyFiltersAndSort();
    renderLedgerList();
    updateDataContext();
    saveLedgerPreferences();
}

/**
 * Sort ledgers based on selected sort option
 */
function sortLedgers() {
    currentSort = document.getElementById('sortBy').value;
    applyFiltersAndSort();
    renderLedgerList();
    updateDataContext();
    saveLedgerPreferences();
}

/**
 * Clear all filters and reset to default
 */
function clearFilters() {
    document.getElementById('ledgerSearch').value = '';
    document.getElementById('filterCount').value = 'all';
    document.getElementById('sortBy').value = 'name-asc';
    currentSearch = '';
    currentFilter = 'all';
    currentSort = 'name-asc';
    applyFiltersAndSort();
    renderLedgerList();
    updateDataContext();
    saveLedgerPreferences();
}

/**
 * Update data context display
 */
function updateDataContext() {
    const context = document.getElementById('dataContext');
    const total = allLedgers.length;
    const filtered = filteredLedgers.length;
    const startIndex = (currentPage - 1) * itemsPerPage + 1;
    const endIndex = Math.min(currentPage * itemsPerPage, filteredLedgers.length);
    
    let contextText = `<strong>${filtered}</strong> of <strong>${total}</strong> ledgers`;
    if (currentSearch) {
        contextText += ` matching "<strong>${currentSearch}</strong>"`;
    }
    if (currentFilter !== 'all') {
        contextText += ` with <strong>${currentFilter}</strong> transactions`;
    }
    if (filtered > 0) {
        contextText += ` | Showing <strong>${startIndex}-${endIndex}</strong> on page <strong>${currentPage}</strong>`;
    }
    
    context.innerHTML = contextText;
}

/**
 * Save ledger preferences to localStorage
 */
function saveLedgerPreferences() {
    try {
        localStorage.setItem('ledger_preferences', JSON.stringify({
            sort: currentSort,
            filter: currentFilter,
            search: currentSearch,
            itemsPerPage: itemsPerPage,
            page: currentPage
        }));
    } catch (e) {
        console.warn('Could not save preferences:', e);
    }
}

/**
 * Load ledger preferences from localStorage
 */
function loadLedgerPreferences() {
    try {
        const saved = localStorage.getItem('ledger_preferences');
        if (saved) {
            const prefs = JSON.parse(saved);
            currentSort = prefs.sort || 'name-asc';
            currentFilter = prefs.filter || 'all';
            // Don't restore search term - always start with empty search to show all ledgers
            currentSearch = '';
            itemsPerPage = prefs.itemsPerPage || 20;
            currentPage = 1; // Always start at page 1
            
            // Apply to UI
            document.getElementById('sortBy').value = currentSort;
            document.getElementById('filterCount').value = currentFilter;
            document.getElementById('ledgerSearch').value = ''; // Clear search input
        } else {
            // Default values if no preferences saved
            currentSort = 'name-asc';
            currentFilter = 'all';
            currentSearch = '';
            itemsPerPage = 20;
            currentPage = 1;
        }
    } catch (e) {
        console.warn('Could not load preferences:', e);
        // Default values on error
        currentSort = 'name-asc';
        currentFilter = 'all';
        currentSearch = '';
        itemsPerPage = 20;
        currentPage = 1;
    }
}

