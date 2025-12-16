/*
 * TallyConnect - Filters & Search
 * Interactive filtering for reports
 */

/**
 * Search/filter table rows
 * @param {string} inputId - ID of search input element
 * @param {string} tableId - ID of table element
 */
function searchTable(inputId, tableId) {
    const input = document.getElementById(inputId);
    const filter = input.value.toUpperCase();
    const table = document.getElementById(tableId);
    const tr = table.getElementsByTagName('tr');
    
    // Start from 1 to skip header row
    for (let i = 1; i < tr.length; i++) {
        const txtValue = tr[i].textContent || tr[i].innerText;
        if (txtValue.toUpperCase().indexOf(filter) > -1) {
            tr[i].style.display = '';
        } else {
            tr[i].style.display = 'none';
        }
    }
}

/**
 * Sort table by column
 * @param {number} columnIndex - Column index to sort by
 * @param {string} tableId - ID of table element
 */
function sortTable(columnIndex, tableId) {
    const table = document.getElementById(tableId);
    const tbody = table.getElementsByTagName('tbody')[0];
    const rows = Array.from(tbody.getElementsByTagName('tr'));
    
    // Determine sort direction
    const currentDirection = table.getAttribute('data-sort-direction') || 'asc';
    const newDirection = currentDirection === 'asc' ? 'desc' : 'asc';
    
    // Sort rows
    rows.sort((a, b) => {
        const aValue = a.getElementsByTagName('td')[columnIndex].textContent.trim();
        const bValue = b.getElementsByTagName('td')[columnIndex].textContent.trim();
        
        // Try numeric sort first
        const aNum = parseFloat(aValue.replace(/[^0-9.-]/g, ''));
        const bNum = parseFloat(bValue.replace(/[^0-9.-]/g, ''));
        
        if (!isNaN(aNum) && !isNaN(bNum)) {
            return newDirection === 'asc' ? aNum - bNum : bNum - aNum;
        }
        
        // String sort
        return newDirection === 'asc' 
            ? aValue.localeCompare(bValue) 
            : bValue.localeCompare(aValue);
    });
    
    // Reattach sorted rows
    rows.forEach(row => tbody.appendChild(row));
    
    // Update sort direction
    table.setAttribute('data-sort-direction', newDirection);
}

/**
 * Filter table by date range
 * @param {string} fromDateId - ID of from date input
 * @param {string} toDateId - ID of to date input
 * @param {string} tableId - ID of table element
 * @param {number} dateColumnIndex - Column index containing dates
 */
function filterByDateRange(fromDateId, toDateId, tableId, dateColumnIndex) {
    const fromDate = document.getElementById(fromDateId).value;
    const toDate = document.getElementById(toDateId).value;
    const table = document.getElementById(tableId);
    const rows = table.getElementsByTagName('tr');
    
    for (let i = 1; i < rows.length; i++) {
        const dateCell = rows[i].getElementsByTagName('td')[dateColumnIndex];
        const dateValue = dateCell.textContent.trim();
        
        // Convert to comparable format (assuming DD-MM-YYYY)
        const [day, month, year] = dateValue.split('-');
        const rowDate = new Date(year, month - 1, day);
        
        const from = fromDate ? new Date(fromDate) : new Date('1900-01-01');
        const to = toDate ? new Date(toDate) : new Date('2100-12-31');
        
        if (rowDate >= from && rowDate <= to) {
            rows[i].style.display = '';
        } else {
            rows[i].style.display = 'none';
        }
    }
}

/**
 * Highlight text in search results
 * @param {string} text - Text to highlight
 * @param {string} search - Search term
 */
function highlightText(text, search) {
    if (!search) return text;
    const regex = new RegExp(`(${search})`, 'gi');
    return text.replace(regex, '<mark>$1</mark>');
}

// Auto-attach event listeners when DOM loads
document.addEventListener('DOMContentLoaded', function() {
    // Attach search functionality to all .search-input elements
    document.querySelectorAll('.search-input').forEach(input => {
        input.addEventListener('keyup', function() {
            const tableId = this.getAttribute('data-table');
            searchTable(this.id, tableId);
        });
    });
    
    // Make table headers clickable for sorting
    document.querySelectorAll('th[data-sortable="true"]').forEach((header, index) => {
        header.style.cursor = 'pointer';
        header.addEventListener('click', function() {
            const table = this.closest('table');
            sortTable(index, table.id);
        });
    });
});

