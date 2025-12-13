# 📊 TallyConnect v5.6

[![Version](https://img.shields.io/badge/version-5.6-blue.svg)](https://github.com/ganeshchavan786/TallyConnect)
[![Python](https://img.shields.io/badge/python-3.13-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Proprietary-red.svg)](./LICENSE.txt)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)

**Modern Tally Sync Platform** - Professional tool for synchronizing Tally data with local database

🌟 **[Live Demo](#) | [Download Latest Release](https://github.com/ganeshchavan786/TallyConnect/releases) | [Report Bug](https://github.com/ganeshchavan786/TallyConnect/issues)**

---

## 🌟 Features

### Core Functionality
- ✅ **Multi-Company Sync** - Sync multiple Tally companies simultaneously
- ✅ **Smart Batch Processing** - Optimized batch sync with configurable size
- ✅ **Date Slicing** - Split large date ranges for better performance
- ✅ **Auto-Sync** - Automatic scheduled synchronization
- ✅ **Resume Sync** - Continue interrupted syncs automatically

### User Interface
- 🎨 **5 Professional Themes** - Modern Blue, Dark Professional, Light Professional, Fresh Green, Purple Elegant
- 🎯 **Color-Coded Buttons** - Blue, Green, Teal, Orange, Red for different actions
- 📱 **Responsive Design** - Clean, modern interface with proper spacing
- 🔄 **Live Progress Tracking** - Real-time sync progress and status

### Data Management
- 💾 **SQLite Local Database** - Fast local storage
- 📝 **Company Notes** - Add notes for each synced company
- 📋 **Sync Logs** - Detailed logs of all sync operations
- 🔍 **DSN Auto-Detection** - Automatically detect Tally ODBC connections

---

## 🚀 Quick Start

### Prerequisites
- Windows 10 or later (64-bit)
- Tally with ODBC enabled
- ODBC Driver configured for Tally

### Installation

#### Option 1: Installer (Recommended)
1. Download `TallyConnectSetup_v5.6.exe`
2. Run the installer
3. Follow installation wizard
4. Launch TallyConnect from Desktop or Start Menu

#### Option 2: Portable
1. Extract `TallyConnect.exe` to any folder
2. Double-click to run
3. Database will be created in the same folder

---

## 📖 Usage Guide

### First Time Setup

1. **Configure DSN**
   - Click "🔍 Auto Detect" to find Tally ODBC connections
   - Or manually enter DSN name

2. **Load Companies**
   - Click "➕ Add Company" in toolbar
   - Click "📥 Load Companies" button
   - Select company from list

3. **Configure Sync Settings**
   - Click "⚙️ Sync Settings"
   - Set Date Range (From - To)
   - Configure Batch Size (default: 100)
   - Enable Date Slicing if needed

4. **Start Sync**
   - Select company from Available Companies
   - Click "▶ Sync" button in the company row
   - OR double-click company name
   - Monitor progress in footer

### Views

#### 🏢 Synced Companies View
- Shows all companies that have been synced
- Columns: Name, Status, Sync, Remove, Next Sync, AlterID, Records
- Click "▶ Sync" to re-sync a company
- Click "🗑 Remove" to delete company and data

#### ➕ Add Company View
- Shows available companies from Tally (not yet synced)
- Load companies list from Tally
- Double-click to start sync

#### ⚙️ Sync Settings View
- Configure DSN connection
- Set date range for sync
- Adjust batch size and slicing
- Enable/disable auto-sync

---

## 🎨 Themes

Choose from 5 professional themes via dropdown in toolbar:

1. **Modern Blue** (Default) - Clean professional blue
2. **Dark Professional** - Eye-friendly dark theme
3. **Light Professional** - Bright, crisp interface
4. **Fresh Green** - Nature-inspired green palette
5. **Purple Elegant** - Sophisticated purple accent

---

## 🔧 Advanced Features

### Auto-Sync
- Enable in Sync Settings panel
- Set interval in minutes (1-60)
- Automatically syncs all synced companies
- Shows countdown to next sync

### Batch Processing
- Configure batch size (50-1000)
- Optimizes memory usage
- Better performance for large datasets

### Date Slicing
- Enable "Slice by Days"
- Set slice size (1-30 days)
- Breaks large date ranges into smaller chunks
- Prevents timeout on huge datasets

### Company Notes
- Add notes for each company
- Saved locally in `notes/` folder
- Select company and use Notes panel

---

## 🛠️ Building from Source

### Requirements
```bash
pip install -r requirements.txt
```

### Build Executable
```bash
pyinstaller TallyConnect.spec
```

Output: `dist/TallyConnect.exe`

### Create Installer
1. Build executable first
2. Install [Inno Setup](https://jrsoftware.org/isinfo.php)
3. Compile `TallyConnectInstaller.iss`
4. Output: `dist/TallyConnectSetup_v5.6.exe`

---

## 📁 Project Structure

```
TallyConnect/
├── C2.py                       # Main application
├── TallyConnect.spec           # PyInstaller config
├── TallyConnectInstaller.iss   # Inno Setup installer
├── requirements.txt            # Python dependencies
├── TalllyData.db              # SQLite database
├── notes/                     # Company notes folder
├── dist/                      # Built executables
└── build/                     # Build artifacts
```

---

## 🐛 Troubleshooting

### Sync Fails
- Check Tally is running and ODBC is enabled
- Verify DSN name is correct
- Check date format (DD-MM-YYYY)
- Try smaller batch size

### ODBC Error
- Install/reinstall Tally ODBC driver
- Configure DSN in Windows ODBC Data Sources
- Test connection from ODBC Administrator

### Database Locked
- Close other instances of TallyConnect
- Check antivirus isn't blocking database file

---

## 📝 Version History

### v5.6 (Current)
- Rebranded to TallyConnect
- 5 professional themes
- Color-coded buttons
- Improved UI/UX
- Better performance

---

## 📞 Support

For support and inquiries:
- **Company:** Katara Dental
- **Website:** https://kataradental.com
- **Support:** https://kataradental.com/support

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

© 2025 Katara Dental. All rights reserved.

## 🌟 Star History

If you find this project useful, please consider giving it a ⭐!

[![Star History Chart](https://api.star-history.com/svg?repos=ganeshchavan786/TallyConnect&type=Date)](https://star-history.com/#ganeshchavan786/TallyConnect&Date)

---

## 🙏 Acknowledgments

Built with:
- Python 3.x
- Tkinter (GUI)
- PyODBC (Tally connection)
- SQLite3 (Local storage)
- PyInstaller (Executable)
- Inno Setup (Installer)

---

**Made with ❤️ by Katara Dental**

