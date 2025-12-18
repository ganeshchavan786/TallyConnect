# Changelog

All notable changes to this project will be documented in this file.

## [1.5.1] - 2025-12-18

### Fixed
- **Sync logs UI reliability**
  - Fixed `/api/sync-logs/` auto-restore overwriting requested filters (company/level/status)
  - `created_at` is now stored in local time to match UI/date-based filtering (fixes “today logs not showing” in some cases)
  - Ignored runtime SQLite artifacts (`*.db-wal`, `*.db-shm`) and `sync_logs_backup.jsonl` via `.gitignore`

## [1.5.0] - 2025-12-17

### Fixed
- **EXE Hang Issue**
  - Fixed application hanging on startup with "Not Responding" message
  - Portal server startup moved to background thread (non-blocking)
  - Database initialization with timeout protection
  - UI initialization deferred to prevent blocking
  - Application now starts in <1 second

- **Sync Logs JavaScript Errors**
  - Fixed `currentPage` duplicate declaration error
  - Fixed `itemsPerPage` duplicate declaration error
  - Renamed variables to avoid conflicts with app.js
  - Sync logs page now loads without errors

- **Sync Logs Functionality**
  - Complete sync logs documentation created
  - Test cases written and passing (15 tests)
  - Diagnostic script for checking sync logs status
  - All sync operations now properly log to database

### Added
- **Sync Logs System**
  - Complete sync logs implementation with database storage
  - Portal API endpoint for sync logs (`/api/sync-logs/`)
  - Frontend sync logs page with filters and pagination
  - Comprehensive test suite (15 tests, all passing)
  - Diagnostic tools and documentation

- **Documentation**
  - `SYNC_LOGS_DOCUMENTATION.md` - Complete implementation guide
  - `SYNC_LOGS_TEST_RESULTS.md` - Test results and coverage
  - `SYNC_LOGS_ISSUE_FIX.md` - Issue diagnosis and fixes
  - `EXE_HANG_FIX.md` - EXE hang issue resolution
  - `SYNC_LOGS_JS_FIX.md` - JavaScript error fixes

### Changed
- **Performance Improvements**
  - Non-blocking portal server startup
  - Deferred UI initialization
  - Background tree refresh
  - Database connection timeout protection

### Technical Details
- Portal server starts in daemon thread
- UI initialization uses `root.after()` for deferred loading
- Database initialization has 5-second timeout
- All JavaScript variable conflicts resolved
- Sync logs use UTC timestamps for consistency

## [1.1.0-alpha] - 2025-12-16

### Added
- **Sales Register ReportService Integration**
  - Sales Register voucher list now uses ReportService for filtering, sorting, pagination, and export
  - Custom sort functions for date, customer, amount
  - Export functionality (CSV, Excel, PDF)
  - Context display showing filtered/total records

### Changed
- **Navigation Flow Improvements**
  - Auto-redirect from index.html to companies.html on startup
  - Company selection now redirects to Dashboard (instead of Reports)
  - Improved user flow: Companies → Dashboard

- **Sidebar Menu Updates**
  - Added menu items to all pages: Outstanding, Ledger, Sales Register
  - Consistent navigation across all report pages
  - Active page highlighting

- **Ledger List Fixes**
  - Search term no longer persists from localStorage
  - Default view shows all ledgers (no search filter applied)
  - Improved pagination behavior

### Technical Details
- Sales Register uses ReportService with custom render callbacks
- Sidebar menu structure standardized across all HTML pages
- Navigation flow optimized for better UX

## [1.0.0-alpha] - 2025-12-15

### Added
- **Portal System**
  - Web-based report portal with modular frontend structure
  - Company selection page
  - Ledger selection with search, filter, and pagination
  - Multiple report types: Ledger Report, Outstanding Report, Dashboard, Sales Register

- **Ledger Report**
  - Tally-style ledger report display
  - One line per voucher (grouped by vch_mst_id)
  - Counter ledger in Particulars column
  - Running balance calculation
  - Date range filtering
  - Period selection

- **Sales Register Report**
  - Monthly summary view
  - Voucher list view with drill-down
  - Tally-style display (sales amount in Debit column)
  - Period selection (From Date / To Date)
  - One line per voucher with total invoice amount (Sales + GST)

- **Common Features**
  - Filter, Sort, Pagination (TableFilterManager class)
  - Export functionality (CSV, Excel, PDF)
  - Responsive design (mobile and desktop)
  - Loading indicators
  - Persistent preferences (localStorage)
  - Data context display

- **Reusable Services**
  - `TableFilterManager` - Core filtering/sorting/pagination
  - `ReportService` - Complete report solution wrapper
  - Common export functions
  - Utility helpers

- **Backend**
  - Portal server with API endpoints
  - Database queries optimized for Tally-style reports
  - Voucher grouping by vch_mst_id
  - Sales ledger identification and amount calculation

### Technical Details
- **Frontend:** Modular HTML/CSS/JS structure
- **Backend:** Python with SQLite database
- **API:** RESTful endpoints for data fetching
- **Database:** TallyConnectDb.db (SQLite)

### Files Structure
```
frontend/portal/
  ├── assets/
  │   ├── css/ (main.css, layout.css, components.css, utilities.css)
  │   └── js/
  │       ├── utils/ (filters.js, export.js, report-service.js, helpers.js)
  │       └── components/ (ledgers.js, ledger-report.js, sales-register.js, etc.)
  ├── *.html (companies.html, reports.html, ledgers.html, etc.)
backend/
  ├── portal_server.py (Portal API server)
  ├── database/queries.py (SQL queries)
  └── utils/ (portal_starter.py, helpers)
```

### Known Issues
- Sales Register export buttons need integration
- Some reports need TableFilterManager integration
- Purchase Register report pending

### Next Steps
- Integrate ReportService in all reports
- Add Purchase Register report
- Enhance export functionality
- Add more filter options

