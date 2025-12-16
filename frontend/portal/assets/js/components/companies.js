/* ============================================
   Companies Component - Company Selection
   ============================================ */

/**
 * Display companies in grid
 * @param {Array} companies - Array of company objects
 */
function displayCompanies(companies) {
    const grid = document.getElementById('companyGrid');
    if (!grid) {
        console.warn('companyGrid element not found. This is normal for standalone pages.');
        return;
    }
    grid.innerHTML = '';
    
    // Debug logging
    console.log(`[Portal] Displaying ${companies.length} companies`);
    
    if (companies.length === 0) {
        grid.innerHTML = '<div class="loading">No companies found.<br><small>Please sync companies in TallyConnect app first.</small></div>';
        return;
    }
    
    companies.forEach((company, index) => {
        console.log(`[Portal] Company ${index + 1}: ${company.name} (GUID: ${company.guid.substring(0, 20)}...)`);
        const card = document.createElement('div');
        card.className = 'company-card';
        card.innerHTML = `
            <div class="company-name">${company.name}</div>
            <div class="company-info">
                Records: ${company.total_records || 0}<br>
                Status: ${company.status || 'Unknown'}
            </div>
        `;
        card.onclick = () => selectCompany(company);
        grid.appendChild(card);
    });
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

