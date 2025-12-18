/* ============================================
   Date Filters - Common Filter Utility
   ============================================
   Reusable date range and year filter components
   for Dashboard and other reports.
*/

/**
 * DateFilterManager - Manages date range and year filters
 */
class DateFilterManager {
    constructor(options = {}) {
        this.containerId = options.containerId || 'filterContainer';
        this.onFilterChange = options.onFilterChange || null;
        this.selectedDateRange = options.defaultDateRange || 'last_30_days';
        this.selectedYear = options.defaultYear || null;
        this.customStartDate = null;
        this.customEndDate = null;
        this.availableYears = [];
        
        // Financial year calculation (April 1 to March 31)
        this.fyStartMonth = 4; // April
    }
    
    /**
     * Calculate Financial Year dates
     * @param {Date} date - Reference date (default: today)
     * @returns {Object} {start: Date, end: Date, label: string}
     */
    getFinancialYear(date = new Date()) {
        const year = date.getFullYear();
        const month = date.getMonth() + 1; // 1-12
        
        let fyStart, fyEnd, fyLabel;
        
        if (month >= this.fyStartMonth) {
            // April to December - current FY
            fyStart = new Date(year, this.fyStartMonth - 1, 1);
            // FY ends on last day of month before FY start month (Apr-start FY => Mar 31 next year)
            const endMonthIndex = this.fyStartMonth - 2; // Apr(4) -> Mar index 2
            const endYear = year + 1;
            fyEnd = new Date(endYear, endMonthIndex, this.getLastDayOfMonth(endYear, endMonthIndex));
            fyLabel = `${year}-${String(year + 1).slice(-2)}`;
        } else {
            // January to March - previous FY
            fyStart = new Date(year - 1, this.fyStartMonth - 1, 1);
            const endMonthIndex = this.fyStartMonth - 2; // Mar index 2
            const endYear = year;
            fyEnd = new Date(endYear, endMonthIndex, this.getLastDayOfMonth(endYear, endMonthIndex));
            fyLabel = `${year - 1}-${String(year).slice(-2)}`;
        }
        
        return { start: fyStart, end: fyEnd, label: fyLabel };
    }
    
    /**
     * Get last day of month
     */
    getLastDayOfMonth(year, month) {
        // monthIndex is 0-11; last day = new Date(year, monthIndex + 1, 0)
        const monthIndex = month;
        return new Date(year, monthIndex + 1, 0).getDate();
    }
    
    /**
     * Get date range based on selected option
     * @param {string} rangeType - Date range type
     * @returns {Object} {start: Date, end: Date}
     */
    getDateRange(rangeType) {
        const today = new Date();
        today.setHours(23, 59, 59, 999);
        
        let start, end;
        
        switch(rangeType) {
            case 'current_month': {
                // Current calendar month (1st -> last day)
                const y = today.getFullYear();
                const m = today.getMonth(); // 0-11
                start = new Date(y, m, 1);
                start.setHours(0, 0, 0, 0);
                end = new Date(y, m, this.getLastDayOfMonth(y, m));
                end.setHours(23, 59, 59, 999);
                break;
            }

            case 'last_7_days': {
                // Rolling last 7 days (including today)
                start = new Date(today);
                start.setDate(start.getDate() - 6);
                start.setHours(0, 0, 0, 0);
                end = new Date(today);
                break;
            }

            case 'previous_week': {
                // Previous week (Mon-Sun) in local time
                // Convert JS day (Sun=0..Sat=6) to Monday-based index (Mon=0..Sun=6)
                const mondayIndex = (today.getDay() + 6) % 7;
                const thisMonday = new Date(today);
                thisMonday.setDate(thisMonday.getDate() - mondayIndex);
                thisMonday.setHours(0, 0, 0, 0);

                start = new Date(thisMonday);
                start.setDate(start.getDate() - 7);
                start.setHours(0, 0, 0, 0);

                end = new Date(start);
                end.setDate(end.getDate() + 6);
                end.setHours(23, 59, 59, 999);
                break;
            }

            case 'today':
                start = new Date(today);
                start.setHours(0, 0, 0, 0);
                end = new Date(today);
                break;
                
            case 'last_30_days':
                start = new Date(today);
                start.setDate(start.getDate() - 30);
                start.setHours(0, 0, 0, 0);
                end = new Date(today);
                break;
                
            case 'last_60_days':
                start = new Date(today);
                start.setDate(start.getDate() - 60);
                start.setHours(0, 0, 0, 0);
                end = new Date(today);
                break;
                
            case 'last_90_days':
                start = new Date(today);
                start.setDate(start.getDate() - 90);
                start.setHours(0, 0, 0, 0);
                end = new Date(today);
                break;
                
            case 'last_year':
                start = new Date(today);
                start.setFullYear(start.getFullYear() - 1);
                start.setHours(0, 0, 0, 0);
                end = new Date(today);
                break;
                
            case 'current_financial_year':
                const fy = this.getFinancialYear();
                start = fy.start;
                end = fy.end;
                break;
                
            case 'previous_financial_year':
                const currentFY = this.getFinancialYear();
                const prevFYStart = new Date(currentFY.start);
                prevFYStart.setFullYear(prevFYStart.getFullYear() - 1);
                const prevFYEnd = new Date(currentFY.end);
                prevFYEnd.setFullYear(prevFYEnd.getFullYear() - 1);
                start = prevFYStart;
                end = prevFYEnd;
                break;
                
            case 'all_time':
                start = new Date(2000, 0, 1); // Very old date
                end = new Date(today);
                break;
                
            case 'custom':
                if (this.customStartDate && this.customEndDate) {
                    start = new Date(this.customStartDate);
                    end = new Date(this.customEndDate);
                } else {
                    // Default to last 30 days if custom dates not set
                    start = new Date(today);
                    start.setDate(start.getDate() - 30);
                    end = new Date(today);
                }
                break;
                
            default:
                // Default to last 30 days
                start = new Date(today);
                start.setDate(start.getDate() - 30);
                end = new Date(today);
        }
        
        return { start, end };
    }

    /**
     * Format date to "DD-MMM-YYYY" for UI display
     */
    formatDateForDisplay(date) {
        const d = new Date(date);
        const dd = String(d.getDate()).padStart(2, '0');
        const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
        const mmm = months[d.getMonth()] || '';
        const yyyy = d.getFullYear();
        return `${dd}-${mmm}-${yyyy}`;
    }
    
    /**
     * Get date range for a specific financial year
     * @param {number} year - Start year of financial year (e.g., 2024 for FY 2024-25)
     * @returns {Object} {start: Date, end: Date}
     */
    getFinancialYearRange(year) {
        const start = new Date(year, this.fyStartMonth - 1, 1);
        const endMonthIndex = this.fyStartMonth - 2; // Apr-start FY => Mar index 2
        const endYear = year + 1;
        const end = new Date(endYear, endMonthIndex, this.getLastDayOfMonth(endYear, endMonthIndex));
        return { start, end };
    }
    
    /**
     * Format date to YYYY-MM-DD
     */
    formatDateForAPI(date) {
        const d = new Date(date);
        const year = d.getFullYear();
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }
    
    /**
     * Get current filter values as API parameters
     * @returns {Object} {start_date, end_date, financial_year}
     */
    getFilterParams() {
        let start, end;
        
        if (this.selectedYear) {
            // Year filter selected - use financial year
            const year = parseInt(this.selectedYear);
            const range = this.getFinancialYearRange(year);
            start = this.formatDateForAPI(range.start);
            end = this.formatDateForAPI(range.end);
        } else {
            // Date range filter selected
            const range = this.getDateRange(this.selectedDateRange);
            start = this.formatDateForAPI(range.start);
            end = this.formatDateForAPI(range.end);
        }
        
        return {
            start_date: start,
            end_date: end,
            financial_year: this.selectedYear ? `${this.selectedYear}-${String(parseInt(this.selectedYear) + 1).slice(-2)}` : null
        };
    }
    
    /**
     * Render date range filter dropdown
     */
    renderDateRangeFilter() {
        const dateRangeOptions = [
            { value: 'current_month', label: 'Current Month (1st–last day)' },
            { value: 'last_7_days', label: 'Last 7 days (rolling)' },
            { value: 'previous_week', label: 'Previous Week (Mon–Sun)' },
            { value: 'today', label: 'Today' },
            { value: 'last_30_days', label: 'Last 30 days' },
            { value: 'last_60_days', label: 'Last 60 days' },
            { value: 'last_90_days', label: 'Last 90 days' },
            { value: 'last_year', label: 'Last year' },
            { value: 'current_financial_year', label: 'Current Financial Year' },
            { value: 'previous_financial_year', label: 'Previous Financial Year' },
            { value: 'all_time', label: 'All time' },
            { value: 'custom', label: 'Custom date' }
        ];
        
        // If year is selected, show "Year Selected" instead of date range
        let currentLabel;
        if (this.selectedYear) {
            currentLabel = 'Year Selected';
        } else {
            currentLabel = dateRangeOptions.find(opt => opt.value === this.selectedDateRange)?.label || 'Last 30 days';
        }
        
        return `
            <div class="date-range-filter" style="position: relative; display: inline-block;">
                <button type="button" class="date-range-button" id="dateRangeButton" 
                        style="padding: 8px 16px; border: 1px solid #ddd; border-radius: 4px; 
                               background: white; cursor: pointer; display: flex; align-items: center; gap: 8px;
                               font-size: 14px; min-width: 180px; justify-content: space-between;
                               ${this.selectedYear ? 'opacity: 0.6;' : ''}">
                    <span style="display: flex; align-items: center; gap: 6px;">
                        <span>🕐</span>
                        <span>${currentLabel}</span>
                    </span>
                    <span>▼</span>
                </button>
                <div class="date-range-dropdown" id="dateRangeDropdown" 
                     style="display: none; position: absolute; top: 100%; left: 0; margin-top: 4px;
                            background: white; border: 1px solid #ddd; border-radius: 4px;
                            box-shadow: 0 4px 6px rgba(0,0,0,0.1); z-index: 1000; min-width: 200px;
                            padding: 8px 0;">
                    ${dateRangeOptions.map(opt => `
                        <label style="display: flex; align-items: center; padding: 8px 16px; cursor: pointer;
                                     ${opt.value === this.selectedDateRange ? 'background: #f0f0f0;' : ''}
                                     hover:background: #f5f5f5;">
                            <input type="radio" name="dateRange" value="${opt.value}" 
                                   ${opt.value === this.selectedDateRange ? 'checked' : ''}
                                   style="margin-right: 8px;">
                            <span>${opt.label}</span>
                        </label>
                    `).join('')}
                    ${this.selectedDateRange === 'custom' ? `
                        <div style="padding: 16px; border-top: 1px solid #eee;">
                            <div style="margin-bottom: 12px;">
                                <label style="display: block; margin-bottom: 4px; font-size: 12px; color: #666;">Start Date:</label>
                                <input type="date" id="customStartDate" value="${this.customStartDate || ''}" 
                                       style="width: 100%; padding: 6px; border: 1px solid #ddd; border-radius: 4px;">
                            </div>
                            <div>
                                <label style="display: block; margin-bottom: 4px; font-size: 12px; color: #666;">End Date:</label>
                                <input type="date" id="customEndDate" value="${this.customEndDate || ''}" 
                                       style="width: 100%; padding: 6px; border: 1px solid #ddd; border-radius: 4px;">
                            </div>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }
    
    /**
     * Render year filter dropdown
     */
    renderYearFilter() {
        // Generate years from 2017 to current year + 1
        const currentYear = new Date().getFullYear();
        const years = [];
        for (let y = 2017; y <= currentYear + 1; y++) {
            years.push(y);
        }
        years.reverse(); // Most recent first
        
        this.availableYears = years;
        
        const currentLabel = this.selectedYear ? `FY ${this.selectedYear}-${String(parseInt(this.selectedYear) + 1).slice(-2)}` : '- Any -';
        
        return `
            <div class="year-filter" style="position: relative; display: inline-block;">
                <button type="button" class="year-filter-button" id="yearFilterButton" 
                        style="padding: 8px 16px; border: 1px solid #ddd; border-radius: 4px; 
                               background: white; cursor: pointer; display: flex; align-items: center; gap: 8px;
                               font-size: 14px; min-width: 150px; justify-content: space-between;">
                    <span>${currentLabel}</span>
                    <span>▼</span>
                </button>
                <div class="year-filter-dropdown" id="yearFilterDropdown" 
                     style="display: none; position: absolute; top: 100%; left: 0; margin-top: 4px;
                            background: white; border: 1px solid #ddd; border-radius: 4px;
                            box-shadow: 0 4px 6px rgba(0,0,0,0.1); z-index: 1000; min-width: 200px;
                            max-height: 300px; overflow-y: auto;">
                    <div style="padding: 8px; border-bottom: 1px solid #eee;">
                        <input type="text" id="yearSearchInput" placeholder="Search" 
                               style="width: 100%; padding: 6px; border: 1px solid #ddd; border-radius: 4px;
                                      font-size: 14px;">
                    </div>
                    <label class="year-filter-option" data-year="" 
                           style="display: flex; align-items: center; padding: 8px 16px; cursor: pointer;
                                  ${!this.selectedYear ? 'background: #0066cc; color: white;' : 'hover:background: #f5f5f5;'}
                                  border-bottom: 1px solid #eee;">
                        <span style="margin-right: 8px;">○</span>
                        <span>- Any -</span>
                    </label>
                    ${years.map(year => `
                        <label class="year-filter-option" data-year="${year}" 
                               style="display: flex; align-items: center; padding: 8px 16px; cursor: pointer;
                                      ${this.selectedYear == year ? 'background: #0066cc; color: white;' : 'hover:background: #f5f5f5;'}
                                      border-bottom: 1px solid #eee;">
                            <span style="margin-right: 8px;">${this.selectedYear == year ? '●' : '○'}</span>
                            <span>FY ${year}-${String(year + 1).slice(-2)}</span>
                        </label>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    /**
     * Render filter container
     */
    render() {
        const container = document.getElementById(this.containerId);
        if (!container) {
            console.error(`Container #${this.containerId} not found`);
            return;
        }

        // Period summary (always show exact From–To so users understand what "current month/week" means)
        let periodStart = null;
        let periodEnd = null;
        let periodLabel = '';
        try {
            const params = this.getFilterParams();
            periodStart = params.start_date;
            periodEnd = params.end_date;
            if (this.selectedYear) {
                periodLabel = `FY ${this.selectedYear}-${String(parseInt(this.selectedYear) + 1).slice(-2)}`;
            } else {
                const options = [
                    { value: 'current_month', label: 'Current Month' },
                    { value: 'last_7_days', label: 'Last 7 days' },
                    { value: 'previous_week', label: 'Previous Week' },
                    { value: 'today', label: 'Today' },
                    { value: 'last_30_days', label: 'Last 30 days' },
                    { value: 'last_60_days', label: 'Last 60 days' },
                    { value: 'last_90_days', label: 'Last 90 days' },
                    { value: 'last_year', label: 'Last year' },
                    { value: 'current_financial_year', label: 'Current FY' },
                    { value: 'previous_financial_year', label: 'Previous FY' },
                    { value: 'all_time', label: 'All time' },
                    { value: 'custom', label: 'Custom' },
                ];
                periodLabel = options.find(o => o.value === this.selectedDateRange)?.label || 'Period';
            }
        } catch (e) {
            // ignore
        }
        
        container.innerHTML = `
            <div style="display: flex; gap: 12px; align-items: center; margin-bottom: 20px; flex-wrap: wrap;">
                <div style="font-weight: 600; color: #2c3e50;">Filters:</div>
                ${this.renderDateRangeFilter()}
                ${this.renderYearFilter()}
            </div>
            <div id="periodSummary" style="margin-top: -10px; margin-bottom: 12px; font-size: 12px; color: #6c757d;">
                <strong style="color:#2c3e50;">Period:</strong>
                ${periodLabel ? `${periodLabel} • ` : ''}
                ${periodStart && periodEnd ? `${periodStart} → ${periodEnd}` : ''}
            </div>
        `;
        
        this.attachEventListeners();
    }
    
    /**
     * Attach event listeners
     */
    attachEventListeners() {
        // Date range filter
        const dateRangeButton = document.getElementById('dateRangeButton');
        const dateRangeDropdown = document.getElementById('dateRangeDropdown');
        
        if (dateRangeButton && dateRangeDropdown) {
            dateRangeButton.addEventListener('click', (e) => {
                e.stopPropagation();
                const isVisible = dateRangeDropdown.style.display !== 'none';
                dateRangeDropdown.style.display = isVisible ? 'none' : 'block';
                
                // Close year filter if open
                const yearFilterDropdown = document.getElementById('yearFilterDropdown');
                if (yearFilterDropdown) {
                    yearFilterDropdown.style.display = 'none';
                }
            });
            
            // Date range radio buttons
            const dateRangeRadios = document.querySelectorAll('input[name="dateRange"]');
            dateRangeRadios.forEach(radio => {
                radio.addEventListener('change', (e) => {
                    this.selectedDateRange = e.target.value;
                    this.selectedYear = null; // Clear year filter when date range selected
                    if (e.target.value !== 'custom') {
                        this.customStartDate = null;
                        this.customEndDate = null;
                    }
                    this.render();
                    this.notifyFilterChange();
                });
            });
            
            // Custom date inputs
            const customStartDate = document.getElementById('customStartDate');
            const customEndDate = document.getElementById('customEndDate');
            
            if (customStartDate) {
                customStartDate.addEventListener('change', (e) => {
                    this.customStartDate = e.target.value;
                    this.notifyFilterChange();
                });
            }
            
            if (customEndDate) {
                customEndDate.addEventListener('change', (e) => {
                    this.customEndDate = e.target.value;
                    this.notifyFilterChange();
                });
            }
        }
        
        // Year filter
        const yearFilterButton = document.getElementById('yearFilterButton');
        const yearFilterDropdown = document.getElementById('yearFilterDropdown');
        
        if (yearFilterButton && yearFilterDropdown) {
            yearFilterButton.addEventListener('click', (e) => {
                e.stopPropagation();
                const isVisible = yearFilterDropdown.style.display !== 'none';
                yearFilterDropdown.style.display = isVisible ? 'none' : 'block';
                
                // Close date range filter if open
                if (dateRangeDropdown) {
                    dateRangeDropdown.style.display = 'none';
                }
            });
            
            // Year filter options
            const yearOptions = document.querySelectorAll('.year-filter-option');
            yearOptions.forEach(option => {
                option.addEventListener('click', (e) => {
                    const year = option.getAttribute('data-year');
                    this.selectedYear = year || null;
                    this.selectedDateRange = null; // Clear date range when year selected
                    this.customStartDate = null;
                    this.customEndDate = null;
                    this.render();
                    this.notifyFilterChange();
                });
            });
            
            // Year search
            const yearSearchInput = document.getElementById('yearSearchInput');
            if (yearSearchInput) {
                yearSearchInput.addEventListener('input', (e) => {
                    const searchTerm = e.target.value.toLowerCase();
                    yearOptions.forEach(option => {
                        const year = option.getAttribute('data-year');
                        const label = option.textContent.trim();
                        if (year && (year.includes(searchTerm) || label.toLowerCase().includes(searchTerm))) {
                            option.style.display = 'flex';
                        } else if (!year && searchTerm === '') {
                            option.style.display = 'flex'; // Show "- Any -" when search is empty
                        } else {
                            option.style.display = 'none';
                        }
                    });
                });
            }
        }
        
        // Close dropdowns when clicking outside
        document.addEventListener('click', (e) => {
            if (dateRangeDropdown && !dateRangeButton.contains(e.target) && !dateRangeDropdown.contains(e.target)) {
                dateRangeDropdown.style.display = 'none';
            }
            if (yearFilterDropdown && !yearFilterButton.contains(e.target) && !yearFilterDropdown.contains(e.target)) {
                yearFilterDropdown.style.display = 'none';
            }
        });
    }
    
    /**
     * Notify filter change callback
     */
    notifyFilterChange() {
        if (this.onFilterChange && typeof this.onFilterChange === 'function') {
            const params = this.getFilterParams();
            this.onFilterChange(params);
        }
    }
}

