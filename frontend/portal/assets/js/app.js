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

// Branding: set logo source depending on how portal is opened (server vs file protocol)
document.addEventListener('DOMContentLoaded', function () {
    try {
        const isFile = window.location.protocol === 'file:';
        const logoSrc = isFile ? '../../Logo.png' : '/logo.png';
        document.querySelectorAll('img.brand-logo').forEach(img => {
            // Avoid resetting if page provided a different logo explicitly
            img.src = logoSrc;
        });
    } catch (e) {
        // ignore
    }
});

// Build stamp: show exact build version/time in sidebar to avoid confusion
document.addEventListener('DOMContentLoaded', function () {
    try {
        const sidebar = document.querySelector('.sidebar');
        if (!sidebar) return;

        let el = document.getElementById('buildInfo');
        if (!el) {
            el = document.createElement('div');
            el.id = 'buildInfo';
            el.style.marginTop = 'auto';
            el.style.padding = '12px 10px';
            el.style.fontSize = '11px';
            el.style.opacity = '0.85';
            el.style.color = 'rgba(255,255,255,0.75)';
            el.style.borderTop = '1px solid rgba(255,255,255,0.12)';
            el.innerText = '';
            sidebar.appendChild(el);
        }

        const isServer = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
        if (!isServer) {
            el.style.display = 'none';
            return;
        }

        fetch('/api/build-info')
            .then(r => r.ok ? r.json() : null)
            .then(info => {
                if (!info) return;
                const tag = info.git_tag || 'dev';
                const commit = info.git_commit || 'dev';
                const at = info.generated_at || '';
                el.innerText = `Build: ${tag} (${commit})${at ? ` • ${at}` : ''}`;
            })
            .catch(() => { /* ignore */ });
    } catch (e) {
        // ignore
    }
});

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

