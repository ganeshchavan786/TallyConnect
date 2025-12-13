/*
 * TallyConnect - Export Utilities
 * Export reports to PDF/Excel
 */

/**
 * Export table to CSV
 * @param {string} tableId - ID of table to export
 * @param {string} filename - Output filename
 */
function exportToCSV(tableId, filename = 'report.csv') {
    const table = document.getElementById(tableId);
    let csv = [];
    
    // Get headers
    const headers = [];
    table.querySelectorAll('thead th').forEach(th => {
        headers.push(th.textContent.trim());
    });
    csv.push(headers.join(','));
    
    // Get rows
    table.querySelectorAll('tbody tr').forEach(tr => {
        const row = [];
        tr.querySelectorAll('td').forEach(td => {
            // Escape commas and quotes
            let cell = td.textContent.trim();
            cell = cell.replace(/"/g, '""');
            if (cell.includes(',')) {
                cell = `"${cell}"`;
            }
            row.push(cell);
        });
        csv.push(row.join(','));
    });
    
    // Download
    const csvContent = csv.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.click();
}

/**
 * Export to PDF (uses browser print functionality)
 */
function exportToPDF() {
    window.print();
}

/**
 * Export table to Excel (basic implementation)
 * @param {string} tableId - ID of table to export
 * @param {string} filename - Output filename
 */
function exportToExcel(tableId, filename = 'report.xlsx') {
    // Basic implementation - exports as Excel-compatible HTML
    const table = document.getElementById(tableId);
    const html = table.outerHTML;
    
    const blob = new Blob([html], {
        type: 'application/vnd.ms-excel'
    });
    
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.click();
}

/**
 * Copy table to clipboard
 * @param {string} tableId - ID of table to copy
 */
function copyTableToClipboard(tableId) {
    const table = document.getElementById(tableId);
    const range = document.createRange();
    range.selectNode(table);
    window.getSelection().removeAllRanges();
    window.getSelection().addRange(range);
    
    try {
        document.execCommand('copy');
        alert('Table copied to clipboard!');
    } catch (err) {
        alert('Failed to copy table');
    }
    
    window.getSelection().removeAllRanges();
}

/**
 * Print specific section of report
 * @param {string} sectionId - ID of section to print
 */
function printSection(sectionId) {
    const section = document.getElementById(sectionId);
    const printWindow = window.open('', '', 'height=600,width=800');
    
    printWindow.document.write('<html><head><title>Print</title>');
    printWindow.document.write('<link rel="stylesheet" href="../static/css/main.css">');
    printWindow.document.write('</head><body>');
    printWindow.document.write(section.outerHTML);
    printWindow.document.write('</body></html>');
    
    printWindow.document.close();
    printWindow.print();
}

