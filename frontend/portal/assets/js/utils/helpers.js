/* ============================================
   Helpers - Utility Functions
   ============================================ */

/**
 * Format currency amount in Indian format
 * @param {number} amount - Amount to format
 * @returns {string} Formatted currency string
 */
function formatCurrency(amount) {
    if (amount < 0) return `-₹ ${Math.abs(amount).toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
    return `₹ ${amount.toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
}

/**
 * Format date from YYYY-MM-DD to DD-MMM-YY (Tally style)
 * @param {string} dateStr - Date string in YYYY-MM-DD format
 * @returns {string} Formatted date string
 */
function formatDateTally(dateStr) {
    try {
        const date = new Date(dateStr);
        const day = String(date.getDate()).padStart(2, '0');
        const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        const month = months[date.getMonth()];
        const year = String(date.getFullYear()).slice(-2);
        return `${day}-${month}-${year}`;
    } catch {
        return dateStr;
    }
}

/**
 * Get report URL based on environment
 * @param {string} relativePath - Relative path to report
 * @returns {string} Full URL or relative path
 */
function getReportUrl(relativePath) {
    // If running through server (localhost:8000), use full URL
    // Server will generate report on-demand from database
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        return `${window.location.protocol}//${window.location.host}/${relativePath}`;
    }
    // File protocol - use relative (for static testing)
    return relativePath;
}

