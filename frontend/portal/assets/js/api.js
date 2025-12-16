/* ============================================
   API - API Call Functions
   ============================================ */

/**
 * Load companies from API
 */
function loadCompanies() {
    // If running through server, use API endpoint (reads from database)
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        fetch('api/companies.json')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                return response.json();
            })
            .then(companies => {
                console.log(`[Portal] Loaded ${companies.length} companies from API`);
                companiesData = companies;
                const companyGrid = document.getElementById('companyGrid');
                if (companyGrid) {
                    displayCompanies(companies);
                }
            })
            .catch(error => {
                console.error('Error loading companies:', error);
                const companyGrid = document.getElementById('companyGrid');
                if (companyGrid) {
                    companyGrid.innerHTML = 
                        `<div class="loading">Error loading companies: ${error.message}<br><small>Make sure server is running and database exists</small></div>`;
                }
            });
        return;
    }
    // Try to fetch from API (for HTTP server)
    if (window.location.protocol === 'file:') {
        // File protocol - use embedded data
        if (companiesData.length > 0) {
            displayCompanies(companiesData);
        } else {
            document.getElementById('companyGrid').innerHTML = 
                '<div class="loading">Please run: start_portal_server.bat<br><small>Or: python generate_portal.py</small></div>';
        }
    } else {
        // HTTP protocol - fetch from server (auto-generates on-demand)
        fetch('api/companies.json')
            .then(response => response.json())
            .then(companies => {
                displayCompanies(companies);
            })
            .catch(() => {
                if (companiesData.length > 0) {
                    displayCompanies(companiesData);
                } else {
                    document.getElementById('companyGrid').innerHTML = 
                        '<div class="loading">Connecting to server...<br><small>If this persists, run: start_portal_server.bat</small></div>';
                }
            });
    }
}

/**
 * Load ledgers for selected company
 */
function loadLedgers() {
    if (!selectedCompany) return;
    
    // Show loading indicator
    document.getElementById('ledgerLoading').style.display = 'flex';
    
    // Try to get ledgers from embedded data
    if (selectedCompany.ledgers && selectedCompany.ledgers.length > 0) {
        setTimeout(() => {
            displayLedgers(selectedCompany.ledgers);
            document.getElementById('ledgerLoading').style.display = 'none';
        }, 300);
    } else if (window.location.protocol === 'file:') {
        // File protocol - try embedded data
        const company = companiesData.find(c => c.guid === selectedCompany.guid);
        if (company && company.ledgers) {
            setTimeout(() => {
                displayLedgers(company.ledgers);
                document.getElementById('ledgerLoading').style.display = 'none';
            }, 300);
        } else {
            document.getElementById('ledgerList').innerHTML = 
                '<div class="loading">No ledgers found.<br><small>Use start_portal_server.bat for auto-generation</small></div>';
            document.getElementById('ledgerLoading').style.display = 'none';
        }
    } else {
        // HTTP protocol - fetch from server (auto-generates on-demand)
        const safeGuid = selectedCompany.guid.replace(/-/g, '_');
        const safeAlterid = String(selectedCompany.alterid).replace(/\./g, '_');
        fetch(`api/ledgers/${safeGuid}_${safeAlterid}.json`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                return response.json();
            })
            .then(ledgers => {
                if (ledgers && ledgers.length > 0) {
                    displayLedgers(ledgers);
                } else {
                    document.getElementById('ledgerList').innerHTML = 
                        '<div class="loading">No ledgers found for this company.</div>';
                    updateDataContext();
                }
                document.getElementById('ledgerLoading').style.display = 'none';
            })
            .catch(error => {
                console.error('Error loading ledgers:', error);
                document.getElementById('ledgerList').innerHTML = 
                    `<div class="loading">Error loading ledgers: ${error.message}<br><small>Check server console for details</small></div>`;
                document.getElementById('ledgerLoading').style.display = 'none';
            });
    }
}

/**
 * Load ledger report from API
 * @param {string} apiUrl - API URL for ledger data
 * @param {string} fromPage - Page to return to
 */
function loadLedgerReport(apiUrl, fromPage) {
    // Don't call showPage if we're on a standalone page (ledger-report.html)
    const isStandalonePage = window.location.pathname.includes('ledger-report.html');
    if (!isStandalonePage) {
        navigationHistory.push(fromPage);
        showPage('viewer');
    }
    
    const contentDiv = document.getElementById('reportContent');
    if (!contentDiv) {
        console.error('reportContent element not found');
        return;
    }
    contentDiv.innerHTML = `
        <div style="text-align: center; padding: 50px;">
            <div class="spinner" style="border: 4px solid #f3f3f3; border-top: 4px solid #3498db; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 20px auto;"></div>
            <div style="color: #3498db; font-size: 18px; margin: 20px 0;">Loading ledger report...</div>
        </div>
    `;
    
    fetch(apiUrl)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            renderLedgerReport(data);
        })
        .catch(error => {
            console.error('Error loading ledger report:', error);
            contentDiv.innerHTML = `
                <div style="text-align: center; padding: 50px; color: #e74c3c;">
                    <div style="font-size: 48px; margin-bottom: 20px;">⚠️</div>
                    <div style="font-size: 20px; font-weight: 600; margin: 20px 0;">Error loading ledger report</div>
                    <div style="color: #7f8c8d; font-size: 14px;">${error.message}</div>
                </div>
            `;
        });
}

/**
 * Load outstanding report from API
 * @param {string} apiUrl - API URL for outstanding data
 * @param {string} fromPage - Page to return to
 */
function loadOutstandingReport(apiUrl, fromPage) {
    // Don't call showPage if we're on a standalone page
    const isStandalonePage = window.location.pathname.includes('outstanding-report.html');
    if (!isStandalonePage) {
        navigationHistory.push(fromPage);
        showPage('viewer');
    }
    
    const contentDiv = document.getElementById('reportContent');
    if (!contentDiv) {
        console.error('reportContent element not found');
        return;
    }
    contentDiv.innerHTML = `
        <div style="text-align: center; padding: 50px;">
            <div class="spinner" style="border: 4px solid #f3f3f3; border-top: 4px solid #3498db; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 20px auto;"></div>
            <div style="color: #3498db; font-size: 18px; margin: 20px 0;">Loading outstanding report...</div>
        </div>
    `;
    
    fetch(apiUrl)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            renderOutstandingReport(data);
        })
        .catch(error => {
            console.error('Error loading outstanding report:', error);
            contentDiv.innerHTML = `
                <div style="text-align: center; padding: 50px; color: #e74c3c;">
                    <div style="font-size: 48px; margin-bottom: 20px;">⚠️</div>
                    <div style="font-size: 20px; font-weight: 600; margin: 20px 0;">Error loading outstanding report</div>
                    <div style="color: #7f8c8d; font-size: 14px;">${error.message}</div>
                </div>
            `;
        });
}

/**
 * Load dashboard report from API
 * @param {string} apiUrl - API URL for dashboard data
 * @param {string} fromPage - Page to return to
 */
function loadDashboardReport(apiUrl, fromPage) {
    // Don't call showPage if we're on a standalone page
    const isStandalonePage = window.location.pathname.includes('dashboard.html');
    if (!isStandalonePage) {
        navigationHistory.push(fromPage);
        showPage('viewer');
    }
    
    const contentDiv = document.getElementById('reportContent');
    if (!contentDiv) {
        console.error('reportContent element not found');
        return;
    }
    contentDiv.innerHTML = `
        <div style="text-align: center; padding: 50px;">
            <div class="spinner" style="border: 4px solid #f3f3f3; border-top: 4px solid #3498db; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 20px auto;"></div>
            <div style="color: #3498db; font-size: 18px; margin: 20px 0;">Loading dashboard...</div>
        </div>
    `;
    
    fetch(apiUrl)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            renderDashboardReport(data);
        })
        .catch(error => {
            console.error('Error loading dashboard:', error);
            contentDiv.innerHTML = `
                <div style="text-align: center; padding: 50px; color: #e74c3c;">
                    <div style="font-size: 48px; margin-bottom: 20px;">⚠️</div>
                    <div style="font-size: 20px; font-weight: 600; margin: 20px 0;">Error loading dashboard</div>
                    <div style="color: #7f8c8d; font-size: 14px;">${error.message}</div>
                </div>
            `;
        });
}

/**
 * Load Sales Register report from API
 */
function loadSalesRegister(apiUrl, fromPage) {
    const isStandalonePage = window.location.pathname.includes('sales-register.html');
    if (!isStandalonePage) {
        navigationHistory.push(fromPage);
        showPage('viewer');
    }
    
    const contentDiv = document.getElementById('reportContent');
    if (!contentDiv) {
        console.error('reportContent element not found');
        return;
    }
    
    contentDiv.innerHTML = `<div style="text-align: center; padding: 50px;"><div class="spinner" style="border: 4px solid #f3f3f3; border-top: 4px solid #3498db; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 20px auto;"></div><div style="color: #3498db; font-size: 18px; margin: 20px 0;">Loading sales register...</div></div>`;
    
    fetch(apiUrl)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            if (typeof window !== 'undefined') {
                window.salesRegisterData = data;
            }
            const currentView = window.currentView || 'monthly';
            renderSalesRegister(data, currentView);
        })
        .catch(error => {
            console.error('Error loading sales register:', error);
            contentDiv.innerHTML = `<div style="text-align: center; padding: 50px; color: #e74c3c;"><div style="font-size: 48px; margin-bottom: 20px;">⚠️</div><div style="font-size: 20px; font-weight: 600; margin: 20px 0;">Error loading sales register</div><div style="color: #7f8c8d; font-size: 14px;">${error.message}</div></div>`;
        });
}

