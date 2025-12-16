/* ============================================
   Report Service - Common Reusable Functions
   ============================================
   
   This service provides common functionality for all reports:
   - Filter, Sort, Pagination (via TableFilterManager)
   - Export (CSV, Excel, PDF)
   - Loading States
   - Data Context Display
   
   Usage:
   const reportService = new ReportService(config);
   reportService.init(data);
*/

/**
 * Report Service - Main class for report functionality
 */
class ReportService {
    constructor(config) {
        this.config = {
            // Report identification
            reportName: config.reportName || 'report',
            reportType: config.reportType || 'table', // 'table' or 'list'
            
            // Element IDs
            containerId: config.containerId || 'reportContent',
            tableId: config.tableId || null,
            searchInputId: config.searchInputId || null,
            sortSelectId: config.sortSelectId || null,
            filterSelectId: config.filterSelectId || null,
            paginationId: config.paginationId || null,
            contextId: config.contextId || null,
            exportButtonsId: config.exportButtonsId || null,
            
            // Data configuration
            dataField: config.dataField || 'transactions', // Field name in data object
            searchFields: config.searchFields || [], // Fields to search in
            sortColumns: config.sortColumns || {}, // Custom sort functions
            defaultSort: config.defaultSort || 'date-desc',
            itemsPerPage: config.itemsPerPage || 20,
            
            // Export configuration
            exportFileName: config.exportFileName || null, // Function to generate filename
            exportColumns: config.exportColumns || [], // Columns to export
            
            // Storage
            storageKey: config.storageKey || 'report_preferences',
            
            // Callbacks
            onRender: config.onRender || null, // Custom render function
            onRowClick: config.onRowClick || null, // Row click handler
            onDataLoad: config.onDataLoad || null, // Data load callback
            
            // UI Configuration
            showSearch: config.showSearch !== false,
            showSort: config.showSort !== false,
            showFilter: config.showFilter !== false,
            showPagination: config.showPagination !== false,
            showExport: config.showExport !== false,
            showContext: config.showContext !== false,
            
            ...config
        };
        
        this.filterManager = null;
        this.currentData = null;
        this.originalData = null;
    }
    
    /**
     * Initialize the report service
     * @param {object} data - Report data object
     */
    init(data) {
        this.originalData = data;
        this.currentData = data[this.config.dataField] || data || [];
        
        // Create filter manager if needed
        if (this.config.showSearch || this.config.showSort || this.config.showPagination) {
            this.initFilterManager();
        }
        
        // Render UI
        this.renderControls();
        this.renderData();
        
        // Setup export if enabled
        if (this.config.showExport) {
            this.setupExport();
        }
    }
    
    /**
     * Initialize TableFilterManager
     */
    initFilterManager() {
        if (typeof TableFilterManager === 'undefined') {
            console.warn('TableFilterManager not loaded. Loading filters.js...');
            return;
        }
        
        this.filterManager = new TableFilterManager({
            itemsPerPage: this.config.itemsPerPage,
            defaultSort: this.config.defaultSort,
            searchInputId: this.config.searchInputId,
            sortSelectId: this.config.sortSelectId,
            paginationId: this.config.paginationId,
            contextId: this.config.contextId,
            storageKey: this.config.storageKey,
            searchFields: this.config.searchFields,
            sortColumns: this.config.sortColumns,
            onRender: (paginatedData, info) => {
                this.renderTable(paginatedData, info);
            },
            onUpdateContext: (info) => {
                this.updateContext(info);
            },
            onSavePreferences: () => {
                this.savePreferences();
            },
            onLoadPreferences: () => {
                this.loadPreferences();
            }
        });
        
        // Set data
        this.filterManager.setData(Array.isArray(this.currentData) ? this.currentData : []);
    }
    
    /**
     * Render filter controls
     */
    renderControls() {
        const container = document.getElementById(this.config.containerId);
        if (!container) return;
        
        let controlsHtml = '';
        
        // Controls container
        if (this.config.showSearch || this.config.showSort || this.config.showFilter) {
            controlsHtml += `
                <div id="${this.config.reportName}Controls" class="report-controls" style="margin-bottom: 20px; padding: 15px; background: #f8f9fa; border-radius: 8px; border: 1px solid #dee2e6;">
                    <div style="display: flex; gap: 15px; align-items: center; flex-wrap: wrap;">
            `;
            
            // Search input
            if (this.config.showSearch && this.config.searchInputId) {
                controlsHtml += `
                    <div style="flex: 1; min-width: 200px;">
                        <input type="text" id="${this.config.searchInputId}" 
                               class="search-input" 
                               placeholder="🔍 Search..." 
                               style="width: 100%; padding: 10px; border: 2px solid #dee2e6; border-radius: 6px; font-size: 14px;">
                    </div>
                `;
            }
            
            // Sort select
            if (this.config.showSort && this.config.sortSelectId) {
                controlsHtml += `
                    <div>
                        <select id="${this.config.sortSelectId}" 
                                class="filter-select" 
                                style="padding: 10px; border: 2px solid #dee2e6; border-radius: 6px; font-size: 14px;">
                            <option value="date-desc">Date (Newest First)</option>
                            <option value="date-asc">Date (Oldest First)</option>
                            <option value="name-asc">Name (A-Z)</option>
                            <option value="name-desc">Name (Z-A)</option>
                            <option value="amount-desc">Amount (High-Low)</option>
                            <option value="amount-asc">Amount (Low-High)</option>
                        </select>
                    </div>
                `;
            }
            
            // Filter select (if custom filter needed)
            if (this.config.showFilter && this.config.filterSelectId) {
                controlsHtml += `
                    <div>
                        <select id="${this.config.filterSelectId}" 
                                class="filter-select" 
                                style="padding: 10px; border: 2px solid #dee2e6; border-radius: 6px; font-size: 14px;">
                            <option value="all">All</option>
                        </select>
                    </div>
                `;
            }
            
            // Clear filters button
            if (this.config.showSearch || this.config.showSort) {
                controlsHtml += `
                    <div>
                        <button onclick="if (window.${this.config.reportName}Service) window.${this.config.reportName}Service.clearFilters()" 
                                style="padding: 10px 20px; background: #95a5a6; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 14px;">
                            Clear Filters
                        </button>
                    </div>
                `;
            }
            
            // Export buttons
            if (this.config.showExport && this.config.exportButtonsId) {
                controlsHtml += `
                    <div>
                        <button onclick="if (window.${this.config.reportName}Service) window.${this.config.reportName}Service.export('csv')" 
                                style="padding: 10px 15px; background: #27ae60; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 14px; margin-right: 5px;">
                            📥 CSV
                        </button>
                        <button onclick="if (window.${this.config.reportName}Service) window.${this.config.reportName}Service.export('excel')" 
                                style="padding: 10px 15px; background: #3498db; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 14px; margin-right: 5px;">
                            📊 Excel
                        </button>
                        <button onclick="if (window.${this.config.reportName}Service) window.${this.config.reportName}Service.export('pdf')" 
                                style="padding: 10px 15px; background: #e74c3c; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 14px;">
                            📄 PDF
                        </button>
                    </div>
                `;
            }
            
            controlsHtml += `
                    </div>
            `;
            
            // Context display
            if (this.config.showContext && this.config.contextId) {
                controlsHtml += `
                    <div id="${this.config.contextId}" style="margin-top: 10px; color: #495057; font-size: 14px;"></div>
                `;
            }
            
            controlsHtml += `</div>`;
        }
        
        // Insert controls at the beginning of container
        if (controlsHtml) {
            container.insertAdjacentHTML('afterbegin', controlsHtml);
        }
    }
    
    /**
     * Render table/data
     */
    renderData() {
        if (this.filterManager) {
            // Filter manager will call renderTable via onRender callback
            return;
        }
        
        // Fallback: render without filters
        this.renderTable(this.currentData, {
            total: this.currentData.length,
            filtered: this.currentData.length,
            currentPage: 1,
            totalPages: 1
        });
    }
    
    /**
     * Render table rows
     */
    renderTable(data, info) {
        if (this.config.onRender) {
            // Use custom render function
            this.config.onRender.call(this, data, info, this.originalData);
            return;
        }
        
        // Default table rendering
        const tableId = this.config.tableId || `${this.config.reportName}Table`;
        let table = document.getElementById(tableId);
        
        if (!table) {
            // Create table if doesn't exist
            const container = document.getElementById(this.config.containerId);
            if (!container) return;
            
            container.insertAdjacentHTML('beforeend', `
                <table id="${tableId}" style="width: 100%; border-collapse: collapse; margin-top: 20px;">
                    <thead id="${tableId}Head"></thead>
                    <tbody id="${tableId}Body"></tbody>
                </table>
            `);
            table = document.getElementById(tableId);
        }
        
        const tbody = document.getElementById(`${tableId}Body`);
        if (!tbody) return;
        
        tbody.innerHTML = '';
        
        if (!data || data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="10" style="text-align: center; padding: 20px; color: #7f8c8d;">No data found.</td></tr>';
            return;
        }
        
        // Render rows (default implementation - should be overridden)
        data.forEach((row, index) => {
            const tr = document.createElement('tr');
            tr.innerHTML = this.renderRow(row, index);
            if (this.config.onRowClick) {
                tr.style.cursor = 'pointer';
                tr.onclick = () => this.config.onRowClick(row, index);
            }
            tbody.appendChild(tr);
        });
    }
    
    /**
     * Render a single row (override in config)
     */
    renderRow(row, index) {
        // Default implementation - should be customized
        return `<td>${JSON.stringify(row)}</td>`;
    }
    
    /**
     * Update context display
     */
    updateContext(info) {
        if (!this.config.contextId) return;
        
        const contextEl = document.getElementById(this.config.contextId);
        if (!contextEl) return;
        
        let text = `<strong>${info.filtered}</strong> of <strong>${info.total}</strong> records`;
        if (info.searchTerm) {
            text += ` matching "<strong>${info.searchTerm}</strong>"`;
        }
        if (info.filtered > 0) {
            text += ` | Showing <strong>${info.startIndex}-${info.endIndex}</strong> on page <strong>${info.currentPage}</strong>`;
        }
        contextEl.innerHTML = text;
    }
    
    /**
     * Clear all filters
     */
    clearFilters() {
        if (this.filterManager) {
            this.filterManager.clearFilters();
        } else {
            // Reset manually
            if (this.config.searchInputId) {
                const searchInput = document.getElementById(this.config.searchInputId);
                if (searchInput) searchInput.value = '';
            }
            if (this.config.sortSelectId) {
                const sortSelect = document.getElementById(this.config.sortSelectId);
                if (sortSelect) sortSelect.value = this.config.defaultSort;
            }
            this.renderData();
        }
    }
    
    /**
     * Setup export functionality
     */
    setupExport() {
        // Export functions are in export.js
        // They will be called via export() method
    }
    
    /**
     * Export data in specified format
     * @param {string} format - 'csv', 'excel', or 'pdf'
     */
    export(format) {
        const dataToExport = this.filterManager 
            ? this.filterManager.config.filteredData 
            : this.currentData;
        
        if (!dataToExport || dataToExport.length === 0) {
            alert('No data to export');
            return;
        }
        
        // Generate filename
        const fileName = this.config.exportFileName 
            ? this.config.exportFileName(this.originalData, format)
            : `${this.config.reportName}_${new Date().toISOString().split('T')[0]}`;
        
        // Export based on format
        switch(format) {
            case 'csv':
                this.exportToCSV(dataToExport, fileName);
                break;
            case 'excel':
                this.exportToExcel(dataToExport, fileName);
                break;
            case 'pdf':
                this.exportToPDF(dataToExport, fileName);
                break;
            default:
                alert('Invalid export format');
        }
    }
    
    /**
     * Export to CSV
     */
    exportToCSV(data, fileName) {
        if (typeof exportToCSV === 'function') {
            // Use existing export function if available
            const tableId = this.config.tableId || `${this.config.reportName}Table`;
            exportToCSV(tableId, `${fileName}.csv`);
            return;
        }
        
        // Fallback: manual CSV generation
        const columns = this.config.exportColumns || Object.keys(data[0] || {});
        let csv = columns.join(',') + '\n';
        
        data.forEach(row => {
            const values = columns.map(col => {
                const value = this.getNestedValue(row, col) || '';
                return `"${String(value).replace(/"/g, '""')}"`;
            });
            csv += values.join(',') + '\n';
        });
        
        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = `${fileName}.csv`;
        link.click();
    }
    
    /**
     * Export to Excel
     */
    exportToExcel(data, fileName) {
        if (typeof exportToExcel === 'function') {
            const tableId = this.config.tableId || `${this.config.reportName}Table`;
            exportToExcel(tableId, `${fileName}.xls`);
            return;
        }
        
        // Fallback implementation
        const tableId = this.config.tableId || `${this.config.reportName}Table`;
        const table = document.getElementById(tableId);
        if (table) {
            const html = table.outerHTML;
            const blob = new Blob([html], { type: 'application/vnd.ms-excel' });
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = `${fileName}.xls`;
            link.click();
        }
    }
    
    /**
     * Export to PDF
     */
    exportToPDF(data, fileName) {
        if (typeof exportToPDF === 'function') {
            exportToPDF();
            return;
        }
        
        // Fallback: use window.print()
        window.print();
    }
    
    /**
     * Get nested value from object
     */
    getNestedValue(obj, path) {
        return path.split('.').reduce((current, prop) => current?.[prop], obj);
    }
    
    /**
     * Save preferences
     */
    savePreferences() {
        try {
            const prefs = {
                sort: this.filterManager ? this.filterManager.config.sortBy : this.config.defaultSort,
                search: this.filterManager ? this.filterManager.config.searchTerm : '',
                page: this.filterManager ? this.filterManager.config.currentPage : 1,
                itemsPerPage: this.config.itemsPerPage
            };
            localStorage.setItem(this.config.storageKey, JSON.stringify(prefs));
        } catch (e) {
            console.warn('Could not save preferences:', e);
        }
    }
    
    /**
     * Load preferences
     */
    loadPreferences() {
        try {
            const saved = localStorage.getItem(this.config.storageKey);
            if (saved) {
                const prefs = JSON.parse(saved);
                if (this.filterManager) {
                    this.filterManager.config.sortBy = prefs.sort || this.config.defaultSort;
                    this.filterManager.config.searchTerm = prefs.search || '';
                    this.filterManager.config.currentPage = prefs.page || 1;
                }
            }
        } catch (e) {
            console.warn('Could not load preferences:', e);
        }
    }
    
    /**
     * Show loading state
     */
    showLoading() {
        const container = document.getElementById(this.config.containerId);
        if (!container) return;
        
        container.innerHTML = `
            <div style="text-align: center; padding: 50px;">
                <div class="spinner" style="margin: 20px auto;"></div>
                <div style="color: #3498db; font-size: 18px; margin: 20px 0;">Loading ${this.config.reportName}...</div>
            </div>
        `;
    }
    
    /**
     * Show error state
     */
    showError(message) {
        const container = document.getElementById(this.config.containerId);
        if (!container) return;
        
        container.innerHTML = `
            <div style="text-align: center; padding: 50px; color: #e74c3c;">
                <div style="font-size: 48px; margin-bottom: 20px;">⚠️</div>
                <div style="font-size: 18px; font-weight: 600; margin-bottom: 10px;">Error loading ${this.config.reportName}</div>
                <div style="font-size: 14px; color: #7f8c8d;">${message || 'An error occurred'}</div>
            </div>
        `;
    }
    
    /**
     * Update data
     */
    updateData(data) {
        this.originalData = data;
        this.currentData = data[this.config.dataField] || data || [];
        
        if (this.filterManager) {
            this.filterManager.setData(Array.isArray(this.currentData) ? this.currentData : []);
        } else {
            this.renderData();
        }
    }
}

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ReportService;
}

