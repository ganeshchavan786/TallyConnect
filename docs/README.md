# TallyConnect - Modern Tally Sync Platform

## Overview

TallyConnect is a professional application for syncing Tally data and generating comprehensive reports through a modern web portal interface.

## Features

- 🔄 **Tally Data Sync** - Sync multiple companies from Tally
- 📊 **Web Portal Reports** - Beautiful HTML reports via web interface
- 🎨 **Modern UI** - Clean and intuitive user interface
- 🔒 **System Tray** - Run in background with system tray support
- 🚀 **Auto-Start** - Portal can start automatically on Windows boot

## Installation

1. Run `TallyConnectSetup_v5.6.exe` installer
2. Follow the installation wizard
3. Desktop shortcuts will be created automatically

## Quick Start

### Main Application (Recommended)
- Double-click `TallyConnect.exe` or use desktop shortcut
- **Portal automatically starts with the main app**
- Browser opens automatically at `http://localhost:8000`
- Click "➕ Add Company" to sync Tally companies
- View synced companies in the main window
- View reports, ledgers, and dashboard in the portal

### Portal Server (Standalone)
- Double-click `TallyConnectPortal.exe` or use desktop shortcut
- Portal opens automatically in your browser at `http://localhost:8000`
- View reports, ledgers, and dashboard

## Project Structure

```
Project Root/
├── backend/          # Python backend code
│   ├── app.py        # Main TallyConnect GUI application
│   ├── portal_server.py
│   ├── config/       # Configuration settings
│   ├── database/     # Database operations
│   └── ...
├── frontend/         # Web frontend assets
│   ├── portal/       # Portal HTML
│   ├── static/       # CSS, JS, images
│   └── templates/    # HTML templates
├── tests/            # Unit tests
├── docs/             # Documentation
└── dist/             # Built executables
```

## Development

### Requirements
- Python 3.8+
- PyInstaller (for building EXEs)
- pyodbc (for Tally connection)

### Setup
```bash
pip install -r requirements.txt
```

### Run from Source
```bash
# Main application (includes portal automatically)
python main.py

# Portal server only (standalone)
python -m backend.portal_launcher
```

### Build EXEs
```bash
build.bat
```

## Documentation

All documentation is available in the `docs/` folder:

- `MIGRATION_STATUS.md` - Backend/Frontend migration details
- `CLEANUP_SUMMARY.md` - Project cleanup summary
- `BUILD_STATUS.md` - EXE build results
- `PROJECT_STRUCTURE.md` - Detailed project structure
- `MIGRATION_PLAN.md` - Migration plan documentation
- `REFACTORING_PROGRESS.md` - Refactoring progress tracking

## Support

Made with ❤️ by **Vrushali Infotech Pvt Ltd, Pune, Maharashtra**

© 2025 Vrushali Infotech Pvt Ltd, Pune, Maharashtra

## License

See `LICENSE.txt` for details.
