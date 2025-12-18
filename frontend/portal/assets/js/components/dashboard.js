/* ============================================
   Dashboard Component
   ============================================ */

/**
 * Render dashboard report
 * @param {object} data - Dashboard report data
 */
function renderDashboardReport(data) {
    const contentDiv = document.getElementById('reportContent');
    if (!contentDiv) {
        console.error('reportContent element not found');
        return;
    }

    function _num(val) {
        const n = Number(val);
        return Number.isFinite(n) ? n : 0;
    }

    function _monthLabel(item) {
        if (!item) return '-';
        if (item.month_name) return String(item.month_name);
        const mk = item.month_key ? String(item.month_key) : '';
        // month_key format: YYYY-MM
        const m = mk.match(/^(\d{4})-(\d{2})$/);
        if (m) {
            const year = m[1];
            const mm = m[2];
            const map = {
                '01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr', '05': 'May', '06': 'Jun',
                '07': 'Jul', '08': 'Aug', '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec'
            };
            return `${map[mm] || mm} ${year}`;
        }
        return mk || '-';
    }

    function renderMonthlySalesTrendFallback(trend) {
        const canvas = document.getElementById('monthlySalesChart');
        if (!canvas) return;
        const container = canvas.parentElement;
        if (!container) return;

        const items = Array.isArray(trend) ? trend : [];
        const values = items.map(i => _num(i && i.sales_amount));
        const max = Math.max(1, ...values);

        const rows = items.map((item) => {
            const month = _monthLabel(item);
            const amount = _num(item && item.sales_amount);
            const pct = Math.max(0, Math.min(100, (amount / max) * 100));
            return `
                <div class="tc-bar-row">
                    <div class="tc-bar-label">${month}</div>
                    <div class="tc-bar-track">
                        <div class="tc-bar-fill" style="width:${pct}%;"></div>
                    </div>
                    <div class="tc-bar-value">${formatCurrency(amount)}</div>
                </div>
            `;
        }).join('');

        container.innerHTML = `
            <div class="tc-section__hint">Chart library not available — showing sales trend as bars.</div>
            <div class="tc-bars">${rows || '<div class="tc-muted">No monthly trend data</div>'}</div>
        `;
    }

    function _parseYMD(ymd) {
        // Parse "YYYY-MM-DD" safely in local time (avoid UTC parsing quirks)
        const s = String(ymd || '');
        const m = s.match(/^(\d{4})-(\d{2})-(\d{2})$/);
        if (!m) return null;
        const y = parseInt(m[1], 10);
        const mo = parseInt(m[2], 10) - 1;
        const d = parseInt(m[3], 10);
        return new Date(y, mo, d, 0, 0, 0, 0);
    }

    function _monthKeyFromDate(dt) {
        const y = dt.getFullYear();
        const m = String(dt.getMonth() + 1).padStart(2, '0');
        return `${y}-${m}`;
    }

    function _weekdayKey(dt) {
        return dt.getDay(); // 0=Sun..6=Sat
    }

    function _weekdayName(key) {
        const order = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
        return order[key] || 'NA';
    }
    
    let html = `
        <div class="tc-panel tc-report">
            <h2 class="tc-title-xl">${data.company_name || 'Company'} - Dashboard</h2>
            ${data.sales && data.sales.period_start && data.sales.period_end ? `
            <div class="tc-subtitle tc-mb-16">
                Showing data for: <strong>${data.sales.period_start}</strong> → <strong>${data.sales.period_end}</strong>
                ${data.sales.financial_year ? ` (FY ${data.sales.financial_year})` : ``}
            </div>
            ` : `<div class="tc-mb-16"></div>`}

            <div class="tc-tabs" id="dashboardTabs">
                <button type="button" class="tc-tab tc-tab--active" data-tab="overview">Overview</button>
                <button type="button" class="tc-tab" data-tab="trends">Trends</button>
                <button type="button" class="tc-tab" data-tab="customers">Customers</button>
                <button type="button" class="tc-tab" data-tab="returns">Returns</button>
                <button type="button" class="tc-tab" data-tab="accounts">Accounts</button>
            </div>

            <div class="tc-tab-panels">
                <div class="tc-tab-panel tc-tab-panel--active" id="tab-overview">
            
            <!-- KPI Strip (pastel tiles, reference-like) -->
            <div class="tc-kpi-grid">
                <div class="tc-kpi tc-kpi--mint">
                    <div class="tc-kpi__top">
                        <div class="tc-kpi__label">Sales</div>
                        <div class="tc-kpi__icon">💰</div>
                    </div>
                    <div class="tc-kpi__value">${formatCurrency((data.sales && data.sales.total_sales_amount) ? data.sales.total_sales_amount : 0)}</div>
                    <div class="tc-kpi__sub">Sales + GST</div>
                </div>

                <div class="tc-kpi tc-kpi--teal">
                    <div class="tc-kpi__top">
                        <div class="tc-kpi__label">Net Sales</div>
                        <div class="tc-kpi__icon">✅</div>
                    </div>
                    <div class="tc-kpi__value">${formatCurrency((data.sales && data.sales.net_sales_amount) ? data.sales.net_sales_amount : 0)}</div>
                    <div class="tc-kpi__sub">Sales − Returns</div>
                </div>

                <div class="tc-kpi tc-kpi--rose">
                    <div class="tc-kpi__top">
                        <div class="tc-kpi__label">Returns</div>
                        <div class="tc-kpi__icon">↩️</div>
                    </div>
                    <div class="tc-kpi__value">${formatCurrency((data.sales && data.sales.returns_amount) ? data.sales.returns_amount : 0)}</div>
                    <div class="tc-kpi__sub">${(data.sales && data.sales.returns_percent) ? (data.sales.returns_percent).toFixed(2) : '0.00'}% of sales</div>
                </div>

                <div class="tc-kpi tc-kpi--sky">
                    <div class="tc-kpi__top">
                        <div class="tc-kpi__label">Invoices</div>
                        <div class="tc-kpi__icon">🧾</div>
                    </div>
                    <div class="tc-kpi__value">${(data.sales && data.sales.total_sales_count) ? (data.sales.total_sales_count).toLocaleString() : '0'}</div>
                    <div class="tc-kpi__sub">Sales count</div>
                </div>

                <div class="tc-kpi tc-kpi--violet">
                    <div class="tc-kpi__top">
                        <div class="tc-kpi__label">Avg / Invoice</div>
                        <div class="tc-kpi__icon">📊</div>
                    </div>
                    <div class="tc-kpi__value">${formatCurrency((data.sales && data.sales.avg_sales_per_transaction) ? data.sales.avg_sales_per_transaction : 0)}</div>
                    <div class="tc-kpi__sub">Ticket size</div>
                </div>

                <div class="tc-kpi tc-kpi--amber">
                    <div class="tc-kpi__top">
                        <div class="tc-kpi__label">Growth</div>
                        <div class="tc-kpi__icon">📈</div>
                    </div>
                    <div class="tc-kpi__value">${Math.abs((data.sales && data.sales.sales_growth_percent) ? data.sales.sales_growth_percent : 0).toFixed(1)}%</div>
                    <div class="tc-kpi__sub">
                        <span class="tc-kpi__badge ${(data.sales && (data.sales.sales_growth_percent || 0) >= 0) ? 'tc-kpi__badge--up' : 'tc-kpi__badge--down'}">
                            ${(data.sales && (data.sales.sales_growth_percent || 0) >= 0) ? '↑' : '↓'} vs Prev FY
                        </span>
                    </div>
                </div>
            </div>

            <div class="tc-kpi-grid" style="grid-template-columns: repeat(6, minmax(0, 1fr)); margin-top: 0;">
                <div class="tc-kpi tc-kpi--sky">
                    <div class="tc-kpi__top">
                        <div class="tc-kpi__label">Transactions</div>
                        <div class="tc-kpi__icon">🔁</div>
                    </div>
                    <div class="tc-kpi__value">${(data.stats && data.stats.total_transactions) ? data.stats.total_transactions.toLocaleString() : 0}</div>
                    <div class="tc-kpi__sub">All vouchers</div>
                </div>
                <div class="tc-kpi tc-kpi--mint">
                    <div class="tc-kpi__top">
                        <div class="tc-kpi__label">Parties</div>
                        <div class="tc-kpi__icon">👥</div>
                    </div>
                    <div class="tc-kpi__value">${(data.stats && data.stats.total_parties) ? data.stats.total_parties.toLocaleString() : 0}</div>
                    <div class="tc-kpi__sub">Unique ledgers</div>
                </div>
                <div class="tc-kpi tc-kpi--teal">
                    <div class="tc-kpi__top">
                        <div class="tc-kpi__label">Net Balance</div>
                        <div class="tc-kpi__icon">⚖️</div>
                    </div>
                    <div class="tc-kpi__value">${formatCurrency((data.stats && data.stats.net_balance) ? data.stats.net_balance : 0)}</div>
                    <div class="tc-kpi__sub">Overall</div>
                </div>
                <div class="tc-kpi tc-kpi--violet">
                    <div class="tc-kpi__top">
                        <div class="tc-kpi__label">Best Month</div>
                        <div class="tc-kpi__icon">⭐</div>
                    </div>
                    <div id="bestMonthBox" class="tc-kpi__value">-</div>
                    <div id="bestMonthAmt" class="tc-kpi__sub">-</div>
                </div>
                <div class="tc-kpi tc-kpi--rose">
                    <div class="tc-kpi__top">
                        <div class="tc-kpi__label">MoM Change</div>
                        <div class="tc-kpi__icon">🧭</div>
                    </div>
                    <div id="momChangeBox" class="tc-kpi__value">-</div>
                    <div id="momChangeAmt" class="tc-kpi__sub">-</div>
                </div>
                <div class="tc-kpi tc-kpi--amber">
                    <div class="tc-kpi__top">
                        <div class="tc-kpi__label">FY</div>
                        <div class="tc-kpi__icon">📅</div>
                    </div>
                    <div class="tc-kpi__value">${(data.sales && data.sales.financial_year) ? data.sales.financial_year : '-'}</div>
                    <div class="tc-kpi__sub">${(data.sales && data.sales.period_start && data.sales.period_end) ? `${data.sales.period_start} → ${data.sales.period_end}` : ''}</div>
                </div>
            </div>

                </div>
                <div class="tc-tab-panel tc-tab-panel--active" id="tab-trends">
            
            <!-- Monthly Sales Trend Chart -->
            ${data.sales && data.monthly_sales_trend && data.monthly_sales_trend.length > 0 ? `
            <div class="tc-section">
                <h3 class="tc-section__title">📈 Monthly Sales Trend</h3>
                <div class="tc-chart">
                    <canvas id="monthlySalesChart"></canvas>
                </div>
            </div>
            ` : ''}

            <!-- New: Daily Sales Trend -->
            ${data.daily_sales_trend && data.daily_sales_trend.length > 0 ? `
            <div class="tc-section">
                <h3 class="tc-section__title">📅 Daily Sales Trend</h3>
                <div class="tc-section__hint">(Shows sales amount per day for selected period)</div>
                <div id="salesSlicers" class="tc-mb-12"></div>
                <div class="tc-chart tc-chart--h360">
                    <canvas id="dailySalesChart"></canvas>
                </div>
            </div>
            ` : ''}

            <!-- Sales by Weekday -->
            ${data.sales_by_weekday && data.sales_by_weekday.length > 0 ? `
            <div class="tc-section">
                <h3 class="tc-section__title">🗓️ Sales by Weekday</h3>
                <div class="tc-section__hint">(Pattern: which day of week has highest sales)</div>
                <div class="tc-chart tc-chart--h320">
                    <canvas id="weekdaySalesChart"></canvas>
                </div>
            </div>
            ` : ''}

                </div>
                <div class="tc-tab-panel tc-tab-panel--active" id="tab-customers">
            
            <!-- Top Sales Customers Table -->
            ${data.top_sales_customers && data.top_sales_customers.length > 0 ? `
            <div class="tc-section">
                <h3 class="tc-section__title">🏆 Top 10 Sales Customers</h3>
                <div class="tc-table-wrap">
                    <table class="tc-table">
                        <thead>
                            <tr>
                                <th class="tc-center">Rank</th>
                                <th>Customer Name</th>
                                <th class="tc-right">Total Sales</th>
                                <th class="tc-center">Invoices</th>
                                <th class="tc-right">Avg Invoice</th>
                                <th class="tc-right">% of Total</th>
                            </tr>
                        </thead>
                        <tbody>
            ${data.top_sales_customers.map((customer, idx) => {
                const percentOfTotal = data.sales && data.sales.total_sales_amount > 0 
                    ? ((customer.total_sales / data.sales.total_sales_amount) * 100).toFixed(1)
                    : '0.0';
                return `
                            <tr>
                                <td class="tc-center tc-fw-600 tc-text-primary">${idx + 1}</td>
                                <td class="tc-fw-600">${customer.customer_name || '-'}</td>
                                <td class="tc-right tc-fw-600 tc-text-success">${formatCurrency(customer.total_sales || 0)}</td>
                                <td class="tc-center">${(customer.invoice_count || 0).toLocaleString()}</td>
                                <td class="tc-right tc-muted">${formatCurrency(customer.avg_invoice_value || 0)}</td>
                                <td class="tc-right tc-fw-600 tc-text-primary">${percentOfTotal}%</td>
                            </tr>
                `;
            }).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
            ` : ''}
            
            <!-- Additional Charts: Sales by Customer and Sales Distribution -->
            ${data.top_sales_customers && data.top_sales_customers.length > 0 && data.sales ? `
            <div class="tc-grid tc-grid--2 tc-mb-16">
                <div class="tc-section">
                    <h3 class="tc-section__title">📊 Sales by Customer (Top 10)</h3>
                    <div class="tc-chart tc-chart--h360">
                        <canvas id="salesByCustomerChart"></canvas>
                    </div>
                </div>
                <div class="tc-section">
                    <h3 class="tc-section__title">🥧 Sales Distribution</h3>
                    <div class="tc-chart tc-chart--h360">
                        <canvas id="salesDistributionChart"></canvas>
                    </div>
                </div>
            </div>
            ` : ''}

                </div>
                <div class="tc-tab-panel tc-tab-panel--active" id="tab-returns">

            ${data.monthly_sales_returns_trend && data.monthly_sales_returns_trend.length > 0 ? `
            <div class="tc-section">
                <h3 class="tc-section__title">↩️ Monthly Returns / Credit Notes Trend</h3>
                <div class="tc-section__hint">(Credit Notes / Sales Returns amount by month)</div>
                <div class="tc-chart tc-chart--h320">
                    <canvas id="monthlyReturnsChart"></canvas>
                </div>
            </div>
            ` : ''}

                </div>

                <div class="tc-tab-panel tc-tab-panel--active" id="tab-accounts">

            <!-- Top Debtors and Creditors -->
            <div class="tc-grid tc-grid--2 tc-mb-16">
                <div class="tc-section">
                    <h3 class="tc-section__title">Top 10 Debtors</h3>
                    <div class="tc-table-wrap">
                        <table class="tc-table">
                            <thead>
                                <tr>
                                    <th>Party</th>
                                    <th class="tc-right">Balance</th>
                                </tr>
                            </thead>
                            <tbody>
    `;
    
    // Check if top_debtors array exists
    if (data.top_debtors && Array.isArray(data.top_debtors)) {
        data.top_debtors.forEach((debtor, idx) => {
            html += `
                <tr>
                    <td class="tc-fw-600">${idx + 1}. ${debtor.party_name || '-'}</td>
                    <td class="tc-right tc-text-success tc-fw-600">${formatCurrency(debtor.balance || 0)}</td>
                </tr>
            `;
        });
    } else {
        html += `
            <tr>
                <td colspan="2" class="tc-center tc-muted">No debtors found</td>
            </tr>
        `;
    }
    
    html += `
                            </tbody>
                        </table>
                    </div>
                </div>
                <div class="tc-section">
                    <h3 class="tc-section__title">Top 10 Creditors</h3>
                    <div class="tc-table-wrap">
                        <table class="tc-table">
                            <thead>
                                <tr>
                                    <th>Party</th>
                                    <th class="tc-right">Balance</th>
                                </tr>
                            </thead>
                            <tbody>
    `;
    
    // Check if top_creditors array exists
    if (data.top_creditors && Array.isArray(data.top_creditors)) {
        data.top_creditors.forEach((creditor, idx) => {
            html += `
                <tr>
                    <td class="tc-fw-600">${idx + 1}. ${creditor.party_name || '-'}</td>
                    <td class="tc-right tc-text-danger tc-fw-600">${formatCurrency(creditor.balance || 0)}</td>
                </tr>
            `;
        });
    } else {
        html += `
            <tr>
                <td colspan="2" class="tc-center tc-muted">No creditors found</td>
            </tr>
        `;
    }
    
    html += `
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            
            <!-- Voucher Type Summary -->
            <div class="tc-section">
                <h3 class="tc-section__title">Voucher Type Summary</h3>
                <div class="tc-table-wrap">
                    <table class="tc-table">
                        <thead>
                            <tr>
                                <th>Voucher Type</th>
                                <th class="tc-right">Count</th>
                                <th class="tc-right">Total Debit</th>
                                <th class="tc-right">Total Credit</th>
                            </tr>
                        </thead>
                        <tbody>
    `;
    
    // Check if voucher_types array exists
    if (data.voucher_types && Array.isArray(data.voucher_types)) {
        data.voucher_types.forEach(vt => {
            html += `
                <tr>
                    <td class="tc-fw-600">${vt.type || '-'}</td>
                    <td class="tc-right">${vt.count || 0}</td>
                    <td class="tc-right tc-text-success">${formatCurrency(vt.debit || 0)}</td>
                    <td class="tc-right tc-text-danger">${formatCurrency(vt.credit || 0)}</td>
                </tr>
            `;
        });
    } else {
        html += `
            <tr>
                <td colspan="4" class="tc-center tc-muted">No voucher types found</td>
            </tr>
        `;
    }
    
    html += `
                        </tbody>
                    </table>
                </div>
            </div>

                </div>
            </div>
        </div>
    `;
    
    contentDiv.innerHTML = html;

    // Tabs behavior + chart resize when switching tabs
    try {
        window.__tcDashCharts = window.__tcDashCharts || {};
        const tabs = document.getElementById('dashboardTabs');
        const panels = {
            overview: document.getElementById('tab-overview'),
            trends: document.getElementById('tab-trends'),
            customers: document.getElementById('tab-customers'),
            returns: document.getElementById('tab-returns'),
            accounts: document.getElementById('tab-accounts'),
        };

        function setActiveTab(tabKey) {
            if (tabs) {
                tabs.querySelectorAll('.tc-tab').forEach(b => b.classList.remove('tc-tab--active'));
                const btn = tabs.querySelector(`.tc-tab[data-tab="${tabKey}"]`);
                if (btn) btn.classList.add('tc-tab--active');
            }
            Object.values(panels).forEach(p => p && p.classList.remove('tc-tab-panel--active'));
            if (panels[tabKey]) panels[tabKey].classList.add('tc-tab-panel--active');

            // Resize charts after panel becomes visible
            setTimeout(() => {
                try { window.dispatchEvent(new Event('resize')); } catch (e) {}
                try {
                    const charts = window.__tcDashCharts || {};
                    Object.values(charts).forEach(ch => ch && ch.resize && ch.resize());
                } catch (e) {}
            }, 0);
        }

        // Make sure charts can measure size at least once (all panels start as active),
        // then switch to Overview as default.
        setTimeout(() => setActiveTab('overview'), 0);

        if (tabs) {
            tabs.addEventListener('click', (e) => {
                const btn = e.target && e.target.closest ? e.target.closest('button.tc-tab') : null;
                if (!btn) return;
                const tabKey = btn.getAttribute('data-tab');
                if (!tabKey) return;
                setActiveTab(tabKey);
            });
        }
    } catch (e) {
        // ignore
    }

    // ----- Excel-like slicers (Simple) for Daily Sales + Weekday pattern -----
    const _slicerState = {
        selectedMonths: new Set(),   // month_key e.g. "2025-04"
        selectedWeekdays: new Set(), // 0..6
    };

    function _renderSalesSlicers(fullDaily) {
        const container = document.getElementById('salesSlicers');
        if (!container) return;

        // Build available months from daily data
        const monthSet = new Set();
        const parsedDaily = (Array.isArray(fullDaily) ? fullDaily : []).map(r => {
            const dt = _parseYMD(r && r.day);
            if (!dt) return null;
            const mk = _monthKeyFromDate(dt);
            monthSet.add(mk);
            return {
                day: String(r.day || ''),
                dt,
                month_key: mk,
                weekday_key: _weekdayKey(dt),
                sales_amount: _num(r && r.sales_amount),
                sales_count: r && r.sales_count ? Number(r.sales_count) : 0,
            };
        }).filter(Boolean);

        const months = Array.from(monthSet).sort(); // chronological
        const monthChips = months.map(mk => {
            const label = _monthLabel({ month_key: mk });
            const active = _slicerState.selectedMonths.has(mk);
            return `<button data-kind="month" data-value="${mk}" class="tc-chip ${active ? 'tc-chip--active-primary' : ''}">${label}</button>`;
        }).join('');

        const weekdayOrder = [
            { key: 1, label: 'Mon' },
            { key: 2, label: 'Tue' },
            { key: 3, label: 'Wed' },
            { key: 4, label: 'Thu' },
            { key: 5, label: 'Fri' },
            { key: 6, label: 'Sat' },
            { key: 0, label: 'Sun' },
        ];

        const weekdayChips = weekdayOrder.map(w => {
            const active = _slicerState.selectedWeekdays.has(w.key);
            return `<button data-kind="weekday" data-value="${w.key}" class="tc-chip ${active ? 'tc-chip--active-success' : ''}">${w.label}</button>`;
        }).join('');

        const hasFilters = _slicerState.selectedMonths.size > 0 || _slicerState.selectedWeekdays.size > 0;
        const summaryParts = [];
        if (_slicerState.selectedMonths.size > 0) {
            const labels = Array.from(_slicerState.selectedMonths).sort().map(mk => _monthLabel({ month_key: mk }));
            summaryParts.push(`Months: ${labels.join(', ')}`);
        }
        if (_slicerState.selectedWeekdays.size > 0) {
            const labels = Array.from(_slicerState.selectedWeekdays).sort().map(k => _weekdayName(k));
            summaryParts.push(`Weekdays: ${labels.join(', ')}`);
        }

        container.innerHTML = `
            <div class="tc-slicers">
                <div class="tc-chip-label">Slicers:</div>
                <div class="tc-chip-row">
                    <div class="tc-chip-label">Month</div>
                    ${monthChips || '<span class="tc-muted" style="font-size:12px;">No months</span>'}
                </div>
                <div class="tc-chip-row">
                    <div class="tc-chip-label">Weekday</div>
                    ${weekdayChips}
                </div>
                <button data-kind="clear" class="tc-btn tc-btn--ghost tc-btn--warning" style="margin-left:auto;">Clear</button>
            </div>
            <div class="tc-chip-summary">
                ${hasFilters ? summaryParts.join(' • ') : 'No slicers selected (showing all).'}
            </div>
        `;

        // Event delegation
        container.onclick = (ev) => {
            const btn = ev.target && ev.target.closest ? ev.target.closest('button') : null;
            if (!btn) return;
            const kind = btn.getAttribute('data-kind');
            const val = btn.getAttribute('data-value');
            if (kind === 'clear') {
                _slicerState.selectedMonths.clear();
                _slicerState.selectedWeekdays.clear();
                _applySlicerFilters(parsedDaily);
                _renderSalesSlicers(fullDaily);
                return;
            }
            if (kind === 'month' && val) {
                if (_slicerState.selectedMonths.has(val)) _slicerState.selectedMonths.delete(val);
                else _slicerState.selectedMonths.add(val);
                _applySlicerFilters(parsedDaily);
                _renderSalesSlicers(fullDaily);
                return;
            }
            if (kind === 'weekday' && val !== null && val !== undefined) {
                const k = Number(val);
                if (_slicerState.selectedWeekdays.has(k)) _slicerState.selectedWeekdays.delete(k);
                else _slicerState.selectedWeekdays.add(k);
                _applySlicerFilters(parsedDaily);
                _renderSalesSlicers(fullDaily);
                return;
            }
        };
    }

    function _aggregateWeekdayFromDaily(dailyRows) {
        const agg = new Map(); // weekday_key -> {weekday_key, weekday_name, sales_amount, sales_count}
        (dailyRows || []).forEach(r => {
            const k = r.weekday_key;
            const prev = agg.get(k) || { weekday_key: k, weekday_name: _weekdayName(k), sales_amount: 0, sales_count: 0 };
            prev.sales_amount += _num(r.sales_amount);
            prev.sales_count += Number(r.sales_count || 0);
            agg.set(k, prev);
        });
        // Ensure all 7 present
        for (let k = 0; k <= 6; k++) {
            if (!agg.has(k)) agg.set(k, { weekday_key: k, weekday_name: _weekdayName(k), sales_amount: 0, sales_count: 0 });
        }
        return Array.from(agg.values()).sort((a, b) => a.weekday_key - b.weekday_key);
    }

    function _drawDailySales(series) {
        const ctxDaily = document.getElementById('dailySalesChart');
        if (!ctxDaily) return;
        // Reuse existing rendering logic by temporarily replacing data.daily_sales_trend
        const original = data.daily_sales_trend;
        data.daily_sales_trend = series.map(r => ({ day: r.day, sales_amount: r.sales_amount, sales_count: r.sales_count }));
        // The existing renderer block below will run after this setup only once per page load,
        // so for slicer interactions we re-render here by recreating the parent content.
        const parent = ctxDaily.parentElement;
        if (!parent) return;
        parent.innerHTML = `<canvas id="dailySalesChart"></canvas>`;
        // Call the existing renderer by falling through to our dedicated function below
        _renderDailySalesChart(data.daily_sales_trend);
        data.daily_sales_trend = original;
    }

    function _drawWeekday(weekdayAgg) {
        const ctxWd = document.getElementById('weekdaySalesChart');
        if (!ctxWd) return;
        const parent = ctxWd.parentElement;
        if (!parent) return;
        parent.innerHTML = `<canvas id="weekdaySalesChart"></canvas>`;
        _renderWeekdayChart(weekdayAgg);
    }

    function _applySlicerFilters(parsedDaily) {
        // Filter daily by selected months + weekdays
        let rows = parsedDaily.slice();
        if (_slicerState.selectedMonths.size > 0) {
            rows = rows.filter(r => _slicerState.selectedMonths.has(r.month_key));
        }
        if (_slicerState.selectedWeekdays.size > 0) {
            rows = rows.filter(r => _slicerState.selectedWeekdays.has(r.weekday_key));
        }

        // Recompute weekday aggregation from filtered daily rows
        const weekdayAgg = _aggregateWeekdayFromDaily(rows);

        _drawDailySales(rows);
        _drawWeekday(weekdayAgg);
    }

    // Compute Best Month + MoM Change from monthly_sales_trend (client-side, consistent with filtered trend)
    try {
        if (data.monthly_sales_trend && Array.isArray(data.monthly_sales_trend) && data.monthly_sales_trend.length > 0) {
            const trend = data.monthly_sales_trend.map(it => ({
                label: _monthLabel(it),
                month_key: it && it.month_key ? String(it.month_key) : '',
                amount: _num(it && it.sales_amount),
            }));
            // Best month
            const best = trend.reduce((a, b) => (b.amount > a.amount ? b : a), trend[0]);
            const bestEl = document.getElementById('bestMonthBox');
            const bestAmtEl = document.getElementById('bestMonthAmt');
            if (bestEl) bestEl.innerText = best.label;
            if (bestAmtEl) bestAmtEl.innerText = formatCurrency(best.amount);

            // MoM change: last two months in the trend (already ordered by month_key)
            if (trend.length >= 2) {
                const prev = trend[trend.length - 2];
                const last = trend[trend.length - 1];
                const delta = last.amount - prev.amount;
                const pct = prev.amount > 0 ? (delta / prev.amount) * 100 : (last.amount > 0 ? 100 : 0);
                const momEl = document.getElementById('momChangeBox');
                const momAmtEl = document.getElementById('momChangeAmt');
                if (momEl) momEl.innerText = `${pct >= 0 ? '↑' : '↓'} ${Math.abs(pct).toFixed(1)}%`;
                if (momAmtEl) momAmtEl.innerText = `${prev.label} → ${last.label} • ${formatCurrency(delta)}`;
            }
        }
    } catch (e) {
        // ignore
    }
    
    // Render Monthly Sales Trend Chart using Chart.js
    if (data.sales && data.monthly_sales_trend && data.monthly_sales_trend.length > 0) {
        if (typeof Chart === 'undefined') {
            renderMonthlySalesTrendFallback(data.monthly_sales_trend);
        } else {
            const ctx = document.getElementById('monthlySalesChart');
            if (ctx) {
                try {
                    const labels = data.monthly_sales_trend.map(item => _monthLabel(item));
                    const salesData = data.monthly_sales_trend.map(item => _num(item && item.sales_amount));
                    
                    window.__tcDashCharts = window.__tcDashCharts || {};
                    window.__tcDashCharts.monthlySales = new Chart(ctx, {
                        type: 'line',
                        data: {
                            labels: labels,
                            datasets: [{
                                label: 'Sales Amount',
                                data: salesData,
                                borderColor: 'rgb(39, 174, 96)',
                                backgroundColor: 'rgba(39, 174, 96, 0.1)',
                                borderWidth: 3,
                                fill: true,
                                tension: 0.4,
                                pointRadius: 5,
                                pointHoverRadius: 7,
                                pointBackgroundColor: 'rgb(39, 174, 96)',
                                pointBorderColor: '#fff',
                                pointBorderWidth: 2
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: {
                                    display: true,
                                    position: 'top',
                                    labels: {
                                        font: {
                                            size: 14,
                                            weight: 'bold'
                                        },
                                        color: '#2c3e50'
                                    }
                                },
                                tooltip: {
                                    mode: 'index',
                                    intersect: false,
                                    callbacks: {
                                        label: function(context) {
                                            return 'Sales: ' + formatCurrency(context.parsed.y);
                                        }
                                    }
                                }
                            },
                            scales: {
                                y: {
                                    beginAtZero: true,
                                    ticks: {
                                        callback: function(value) {
                                            if (value >= 1000000) {
                                                return '₹' + (value / 1000000).toFixed(1) + 'M';
                                            } else if (value >= 1000) {
                                                return '₹' + (value / 1000).toFixed(1) + 'K';
                                            }
                                            return '₹' + value;
                                        },
                                        font: {
                                            size: 12
                                        },
                                        color: '#7f8c8d'
                                    },
                                    grid: {
                                        color: 'rgba(0,0,0,0.1)'
                                    }
                                },
                                x: {
                                    ticks: {
                                        font: {
                                            size: 12
                                        },
                                        color: '#7f8c8d'
                                    },
                                    grid: {
                                        display: false
                                    }
                                }
                            },
                            interaction: {
                                mode: 'nearest',
                                axis: 'x',
                                intersect: false
                            }
                        }
                    });
                } catch (e) {
                    console.warn('Monthly sales chart failed, using fallback:', e);
                    renderMonthlySalesTrendFallback(data.monthly_sales_trend);
                }
            }
        }
    }
    
    // Render Sales by Customer Bar Chart
    if (data.top_sales_customers && data.top_sales_customers.length > 0 && typeof Chart !== 'undefined') {
        const ctxBar = document.getElementById('salesByCustomerChart');
        if (ctxBar) {
            // Show top 10 customers
            const topCustomers = data.top_sales_customers.slice(0, 10);
            const customerLabels = topCustomers.map(c => {
                // Truncate long names
                const name = c.customer_name || 'Unknown';
                return name.length > 20 ? name.substring(0, 20) + '...' : name;
            });
            const customerSales = topCustomers.map(c => c.total_sales);
            
            window.__tcDashCharts = window.__tcDashCharts || {};
            window.__tcDashCharts.salesByCustomer = new Chart(ctxBar, {
                type: 'bar',
                data: {
                    labels: customerLabels,
                    datasets: [{
                        label: 'Sales Amount',
                        data: customerSales,
                        backgroundColor: [
                            'rgba(39, 174, 96, 0.8)',
                            'rgba(52, 152, 219, 0.8)',
                            'rgba(155, 89, 182, 0.8)',
                            'rgba(241, 196, 15, 0.8)',
                            'rgba(230, 126, 34, 0.8)',
                            'rgba(231, 76, 60, 0.8)',
                            'rgba(46, 204, 113, 0.8)',
                            'rgba(26, 188, 156, 0.8)',
                            'rgba(52, 73, 94, 0.8)',
                            'rgba(149, 165, 166, 0.8)'
                        ],
                        borderColor: [
                            'rgb(39, 174, 96)',
                            'rgb(52, 152, 219)',
                            'rgb(155, 89, 182)',
                            'rgb(241, 196, 15)',
                            'rgb(230, 126, 34)',
                            'rgb(231, 76, 60)',
                            'rgb(46, 204, 113)',
                            'rgb(26, 188, 156)',
                            'rgb(52, 73, 94)',
                            'rgb(149, 165, 166)'
                        ],
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    indexAxis: 'y', // Horizontal bar chart
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return 'Sales: ' + formatCurrency(context.parsed.x);
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    if (value >= 1000000) {
                                        return '₹' + (value / 1000000).toFixed(1) + 'M';
                                    } else if (value >= 1000) {
                                        return '₹' + (value / 1000).toFixed(1) + 'K';
                                    }
                                    return '₹' + value;
                                },
                                font: {
                                    size: 11
                                },
                                color: '#7f8c8d'
                            },
                            grid: {
                                color: 'rgba(0,0,0,0.1)'
                            }
                        },
                        y: {
                            ticks: {
                                font: {
                                    size: 11
                                },
                                color: '#7f8c8d'
                            },
                            grid: {
                                display: false
                            }
                        }
                    }
                }
            });
        }
    }

    // Render Daily Sales Trend
    function _renderDailySalesChart(series) {
        const ctxDaily = document.getElementById('dailySalesChart');
        if (!ctxDaily) return;
        if (typeof Chart === 'undefined') {
            const parent = ctxDaily.parentElement;
            if (parent) {
                const rows = (series || []).slice(-60).map(r => {
                    const d = r.day || '-';
                    const amt = _num(r.sales_amount);
                    const cnt = r.sales_count || 0;
                    return `<tr><td style="padding:8px;">${d}</td><td style="padding:8px; text-align:right;">${formatCurrency(amt)}</td><td style="padding:8px; text-align:right;">${cnt}</td></tr>`;
                }).join('');
                parent.innerHTML = `
                    <div style="font-size:12px; color:#7f8c8d; margin-bottom:8px;">Chart library not available — showing last 60 days as table</div>
                    <div style="overflow:auto; max-height:320px; border:1px solid #eee; border-radius:8px; background:#fff;">
                        <table style="width:100%; border-collapse:collapse;">
                            <thead><tr style="background:#f1f3f5;"><th style="padding:8px; text-align:left;">Date</th><th style="padding:8px; text-align:right;">Sales</th><th style="padding:8px; text-align:right;">Invoices</th></tr></thead>
                            <tbody>${rows}</tbody>
                        </table>
                    </div>
                `;
            }
        } else {
            try {
                const maxPoints = 120;
                const sliced = (series || []).length > maxPoints ? (series || []).slice((series || []).length - maxPoints) : (series || []);
                const labels = sliced.map(r => String(r.day || '-'));
                const amounts = sliced.map(r => _num(r.sales_amount));
                window.__tcDashCharts = window.__tcDashCharts || {};
                window.__tcDashCharts.dailySales = new Chart(ctxDaily, {
                    type: 'line',
                    data: {
                        labels,
                        datasets: [{
                            label: 'Daily Sales',
                            data: amounts,
                            borderColor: 'rgb(52, 152, 219)',
                            backgroundColor: 'rgba(52, 152, 219, 0.12)',
                            borderWidth: 2,
                            fill: true,
                            tension: 0.25,
                            pointRadius: 0,
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { display: true },
                            tooltip: {
                                callbacks: {
                                    label: function (context) {
                                        return 'Sales: ' + formatCurrency(context.parsed.y);
                                    }
                                }
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                ticks: {
                                    callback: function (value) {
                                        if (value >= 1000000) return '₹' + (value / 1000000).toFixed(1) + 'M';
                                        if (value >= 1000) return '₹' + (value / 1000).toFixed(1) + 'K';
                                        return '₹' + value;
                                    }
                                }
                            },
                            x: { ticks: { maxRotation: 0, autoSkip: true, maxTicksLimit: 12 } }
                        }
                    }
                });
            } catch (e) {
                // ignore
            }
        }
    }

    if (data.daily_sales_trend && Array.isArray(data.daily_sales_trend) && data.daily_sales_trend.length > 0) {
        _renderDailySalesChart(data.daily_sales_trend);
        // initialize slicers (months + weekdays) and wire to charts
        try {
            _renderSalesSlicers(data.daily_sales_trend);
            // Initial: no filter => use full daily and recompute weekday from daily (so slicers affect both)
            const parsedDaily = (Array.isArray(data.daily_sales_trend) ? data.daily_sales_trend : []).map(r => {
                const dt = _parseYMD(r && r.day);
                if (!dt) return null;
                return {
                    day: String(r.day || ''),
                    dt,
                    month_key: _monthKeyFromDate(dt),
                    weekday_key: _weekdayKey(dt),
                    sales_amount: _num(r && r.sales_amount),
                    sales_count: r && r.sales_count ? Number(r.sales_count) : 0,
                };
            }).filter(Boolean);
            // override helpers for slicer redraw to use the already-defined renderers
            _applySlicerFilters(parsedDaily);
        } catch (e) {
            // ignore
        }
    }

    function _renderWeekdayChart(seriesAgg) {
        const ctxWd = document.getElementById('weekdaySalesChart');
        if (!ctxWd) return;
        const parent = ctxWd.parentElement;
        const order = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
        const map = {};
        (seriesAgg || []).forEach(r => { map[String(r.weekday_name)] = _num(r.sales_amount); });
        const labels = order;
        const amounts = order.map(d => _num(map[d]));

        if (typeof Chart === 'undefined') {
            if (parent) {
                const rows = labels.map((d, i) => `<tr><td style="padding:8px;">${d}</td><td style="padding:8px; text-align:right;">${formatCurrency(amounts[i])}</td></tr>`).join('');
                parent.innerHTML = `
                    <div style="font-size:12px; color:#7f8c8d; margin-bottom:8px;">Chart library not available — showing weekday totals as table</div>
                    <table style="width:100%; border-collapse:collapse; background:#fff; border:1px solid #eee; border-radius:8px; overflow:hidden;">
                        <thead><tr style="background:#f1f3f5;"><th style="padding:8px; text-align:left;">Weekday</th><th style="padding:8px; text-align:right;">Sales</th></tr></thead>
                        <tbody>${rows}</tbody>
                    </table>
                `;
            }
        } else {
            try {
                window.__tcDashCharts = window.__tcDashCharts || {};
                window.__tcDashCharts.weekdaySales = new Chart(ctxWd, {
                    type: 'bar',
                    data: {
                        labels,
                        datasets: [{
                            label: 'Sales Amount',
                            data: amounts,
                            backgroundColor: 'rgba(46, 204, 113, 0.65)',
                            borderColor: 'rgb(39, 174, 96)',
                            borderWidth: 1,
                            borderRadius: 6,
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { display: true },
                            tooltip: {
                                callbacks: {
                                    label: function (context) {
                                        return 'Sales: ' + formatCurrency(context.parsed.y);
                                    }
                                }
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                ticks: {
                                    callback: function (value) {
                                        if (value >= 1000000) return '₹' + (value / 1000000).toFixed(1) + 'M';
                                        if (value >= 1000) return '₹' + (value / 1000).toFixed(1) + 'K';
                                        return '₹' + value;
                                    }
                                }
                            }
                        }
                    }
                });
            } catch (e) {
                // ignore
            }
        }
    }

    if (data.sales_by_weekday && Array.isArray(data.sales_by_weekday) && data.sales_by_weekday.length > 0) {
        _renderWeekdayChart(data.sales_by_weekday);
    }
    
    // Render Sales Distribution Pie Chart
    if (data.top_sales_customers && data.top_sales_customers.length > 0 && data.sales && typeof Chart !== 'undefined') {
        const ctxPie = document.getElementById('salesDistributionChart');
        if (ctxPie) {
            // Top 5 customers + Others
            const top5 = data.top_sales_customers.slice(0, 5);
            const top5Total = top5.reduce((sum, c) => sum + (c.total_sales || 0), 0);
            const othersTotal = (data.sales.total_sales_amount || 0) - top5Total;
            
            const pieLabels = [...top5.map(c => {
                const name = c.customer_name || 'Unknown';
                return name.length > 15 ? name.substring(0, 15) + '...' : name;
            }), 'Others'];
            const pieData = [...top5.map(c => c.total_sales || 0), othersTotal];
            
            window.__tcDashCharts = window.__tcDashCharts || {};
            window.__tcDashCharts.salesDistribution = new Chart(ctxPie, {
                type: 'pie',
                data: {
                    labels: pieLabels,
                    datasets: [{
                        data: pieData,
                        backgroundColor: [
                            'rgba(39, 174, 96, 0.8)',
                            'rgba(52, 152, 219, 0.8)',
                            'rgba(155, 89, 182, 0.8)',
                            'rgba(241, 196, 15, 0.8)',
                            'rgba(230, 126, 34, 0.8)',
                            'rgba(149, 165, 166, 0.8)'
                        ],
                        borderColor: [
                            'rgb(39, 174, 96)',
                            'rgb(52, 152, 219)',
                            'rgb(155, 89, 182)',
                            'rgb(241, 196, 15)',
                            'rgb(230, 126, 34)',
                            'rgb(149, 165, 166)'
                        ],
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'right',
                            labels: {
                                font: {
                                    size: 12
                                },
                                color: '#2c3e50',
                                padding: 15,
                                generateLabels: function(chart) {
                                    const data = chart.data;
                                    if (data.labels.length && data.datasets.length) {
                                        return data.labels.map((label, i) => {
                                            const value = data.datasets[0].data[i];
                                            const total = data.datasets[0].data.reduce((a, b) => a + b, 0);
                                            const percentage = ((value / total) * 100).toFixed(1);
                                            return {
                                                text: `${label} (${percentage}%)`,
                                                fillStyle: data.datasets[0].backgroundColor[i],
                                                strokeStyle: data.datasets[0].borderColor[i],
                                                lineWidth: data.datasets[0].borderWidth,
                                                hidden: false,
                                                index: i
                                            };
                                        });
                                    }
                                    return [];
                                }
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const label = context.label || '';
                                    const value = context.parsed || 0;
                                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                    const percentage = ((value / total) * 100).toFixed(1);
                                    return `${label}: ${formatCurrency(value)} (${percentage}%)`;
                                }
                            }
                        }
                    }
                }
            });
        }
    }

    // Render Monthly Returns Trend Chart (Returns tab)
    if (data.monthly_sales_returns_trend && Array.isArray(data.monthly_sales_returns_trend) && data.monthly_sales_returns_trend.length > 0 && typeof Chart !== 'undefined') {
        const ctxR = document.getElementById('monthlyReturnsChart');
        if (ctxR) {
            try {
                const labels = data.monthly_sales_returns_trend.map(it => it.month_name || it.month_key);
                const values = data.monthly_sales_returns_trend.map(it => _num(it.returns_amount));
                window.__tcDashCharts = window.__tcDashCharts || {};
                window.__tcDashCharts.monthlyReturns = new Chart(ctxR, {
                    type: 'bar',
                    data: {
                        labels,
                        datasets: [{
                            label: 'Returns / Credit Notes',
                            data: values,
                            backgroundColor: 'rgba(220, 38, 38, 0.55)',
                            borderColor: 'rgb(220, 38, 38)',
                            borderWidth: 1,
                            borderRadius: 8,
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { display: true },
                            tooltip: {
                                callbacks: {
                                    label: (context) => 'Returns: ' + formatCurrency(context.parsed.y)
                                }
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                ticks: {
                                    callback: function (value) {
                                        if (value >= 1000000) return '₹' + (value / 1000000).toFixed(1) + 'M';
                                        if (value >= 1000) return '₹' + (value / 1000).toFixed(1) + 'K';
                                        return '₹' + value;
                                    }
                                }
                            }
                        }
                    }
                });
            } catch (e) {
                // ignore
            }
        }
    }
}

