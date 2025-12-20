/* ============================================
   Companies Component - Company Selection
   ============================================ */

// Global variables for filtering
let allCompanies = [];
let filteredCompanies = [];

/**
 * Display companies in grid with modern design
 * @param {Array} companies - Array of company objects
 */
function displayCompanies(companies) {
    const grid = document.getElementById('companyGrid');
    if (!grid) {
        console.warn('companyGrid element not found. This is normal for standalone pages.');
        return;
    }
    
    // Store all companies
    allCompanies = companies || [];
    
    // Debug logging
    console.log(`[Portal] Displaying ${allCompanies.length} companies`);
    
    // Apply filters and render
    applyCompanyFiltersAndSort();
    
    // Setup event listeners if not already set
    setupCompanyFilters();
}

/**
 * Apply filters and sorting for companies
 */
function applyCompanyFiltersAndSort() {
    const grid = document.getElementById('companyGrid');
    const emptyState = document.getElementById('emptyState');
    if (!grid) return;
    
    // Get filter values
    const searchTerm = (document.getElementById('companySearch')?.value || '').toLowerCase().trim();
    const sortBy = document.getElementById('sortFilter')?.value || 'name';
    
    // Filter companies
    filteredCompanies = allCompanies.filter(company => {
        const matchesSearch = !searchTerm || company.name.toLowerCase().includes(searchTerm);
        return matchesSearch;
    });
    
    // Sort companies
    filteredCompanies.sort((a, b) => {
        switch(sortBy) {
            case 'records':
                return (parseInt(b.total_records) || 0) - (parseInt(a.total_records) || 0);
            case 'name':
            default:
                return (a.name || '').localeCompare(b.name || '');
        }
    });
    
    // Render filtered companies
    renderCompanyGrid();
    
    // Show/hide empty state
    if (filteredCompanies.length === 0) {
        grid.style.display = 'none';
        if (emptyState) emptyState.style.display = 'block';
    } else {
        grid.style.display = 'grid';
        if (emptyState) emptyState.style.display = 'none';
    }
}

/**
 * Render company grid with modern cards
 */
function renderCompanyGrid() {
    const grid = document.getElementById('companyGrid');
    if (!grid) return;
    
    grid.innerHTML = '';
    
    filteredCompanies.forEach((company, index) => {
        const card = document.createElement('div');
        card.className = 'company-card';
        
        const records = parseInt(company.total_records) || 0;
        const status = (company.status || 'Unknown').toLowerCase();
        const statusClass = status === 'active' ? 'tc-badge--success' : 
                          status === 'inactive' ? 'tc-badge--danger' : 
                          'tc-badge--muted';
        const statusText = status.charAt(0).toUpperCase() + status.slice(1);
        
        // Gradient colors based on index
        const gradients = [
            'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
            'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
            'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
            'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
            'linear-gradient(135deg, #30cfd0 0%, #330867 100%)'
        ];
        const gradient = gradients[index % gradients.length];
        
        card.innerHTML = `
            <div class="company-card__header" style="background: ${gradient};">
                <div class="company-card__icon">🏢</div>
            </div>
            <div class="company-card__body">
                <div class="company-card__name">${company.name || 'Unknown Company'}</div>
                <div class="company-card__meta">
                    <div class="company-card__meta-item">
                        <span class="company-card__meta-label">Transaction Records</span>
                        <span class="company-card__meta-value">${records.toLocaleString()}</span>
                    </div>
                </div>
            </div>
        `;
        
        card.onclick = () => selectCompany(company);
        grid.appendChild(card);
    });
}

/**
 * Setup filter event listeners
 */
function setupCompanyFilters() {
    // Remove existing listeners to avoid duplicates
    const searchInput = document.getElementById('companySearch');
    const statusFilter = document.getElementById('statusFilter');
    const sortFilter = document.getElementById('sortFilter');
    
    if (searchInput && !searchInput.hasAttribute('data-listener')) {
        searchInput.addEventListener('input', applyCompanyFiltersAndSort);
        searchInput.setAttribute('data-listener', 'true');
    }
    
    if (sortFilter && !sortFilter.hasAttribute('data-listener')) {
        sortFilter.addEventListener('change', applyCompanyFiltersAndSort);
        sortFilter.setAttribute('data-listener', 'true');
    }
}

/**
 * Handle company selection
 * @param {object} company - Selected company object
 */
function selectCompany(company) {
    selectedCompany = company;
    
    // Highlight selected
    document.querySelectorAll('.company-card').forEach(card => {
        card.classList.remove('selected');
    });
    event.currentTarget.classList.add('selected');
    
    // Show reports page
    setTimeout(() => {
        showPage('reports');
        document.getElementById('reportsLink').style.display = 'block';
    }, 300);
}

