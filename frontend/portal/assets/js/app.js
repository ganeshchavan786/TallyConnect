/* ============================================
   App - Main Application Initialization
   ============================================ */

// Embedded companies data (fallback for file protocol)
const COMPANIES_DATA = [];

// Global state
let selectedCompany = null;
let selectedLedger = null;
let navigationHistory = [];
let companiesData = [];

// Ledger management state
let allLedgers = [];
let filteredLedgers = [];
let currentPage = 1;
let itemsPerPage = 20;
let currentSort = 'name-asc';
let currentFilter = 'all';
let currentSearch = '';

/**
 * Initialize application on page load
 */
window.onload = function() {
    // Don't load companies on standalone pages (ledger-report.html, etc.)
    const isStandalonePage = window.location.pathname.includes('ledger-report.html') ||
                             window.location.pathname.includes('outstanding-report.html') ||
                             window.location.pathname.includes('dashboard.html');
    
    if (isStandalonePage) {
        // Standalone pages handle their own initialization
        return;
    }
    
    // If running through server, always fetch from API (reads from database)
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        loadCompanies(); // Server reads from database
    } else if (typeof COMPANIES_DATA !== 'undefined' && COMPANIES_DATA.length > 0) {
        // File protocol - use embedded data
        companiesData = COMPANIES_DATA;
        displayCompanies(companiesData);
    } else {
        // Fallback: try to fetch
        loadCompanies();
    }
};

/**
 * Show page by ID
 * @param {string} pageId - Page ID to show
 */
function showPage(pageId) {
    // Hide all pages
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    
    // Show selected page (only if element exists)
    const pageElement = document.getElementById(pageId);
    if (pageElement) {
        pageElement.classList.add('active');
    } else {
        console.warn(`Page element with id '${pageId}' not found. This is normal for standalone pages.`);
    }
    
    // Update nav links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    
    // Update sidebar navigation
    if (pageId === 'companies') {
        document.querySelectorAll('.nav-link')[0].classList.add('active');
        document.getElementById('reportsLink').style.display = 'none';
        document.getElementById('ledgersLink').style.display = 'none';
    } else if (pageId === 'reports') {
        document.querySelectorAll('.nav-link')[1].classList.add('active');
        document.getElementById('reportsLink').style.display = 'block';
    } else if (pageId === 'ledgers') {
        document.querySelectorAll('.nav-link')[2].classList.add('active');
        document.getElementById('ledgersLink').style.display = 'block';
    }
}

/**
 * Show outstanding report
 */
function showOutstandingReport() {
    if (!selectedCompany) return;
    
    // Call API to get outstanding data (no file generation)
    const safeGuid = selectedCompany.guid.replace(/-/g, '_').replace(/\./g, '_');
    const safeAlterid = String(selectedCompany.alterid).replace(/\./g, '_');
    const apiUrl = `api/outstanding-data/${safeGuid}_${safeAlterid}`;
    loadOutstandingReport(apiUrl, 'reports');
}

/**
 * Show dashboard
 */
function showDashboard() {
    if (!selectedCompany) return;
    
    // Call API to get dashboard data (no file generation)
    const safeGuid = selectedCompany.guid.replace(/-/g, '_').replace(/\./g, '_');
    const safeAlterid = String(selectedCompany.alterid).replace(/\./g, '_');
    const apiUrl = `api/dashboard-data/${safeGuid}_${safeAlterid}`;
    loadDashboardReport(apiUrl, 'reports');
}

/**
 * Go back to previous page
 */
function goBack() {
    const previousPage = navigationHistory.pop() || 'reports';
    showPage(previousPage);
}

