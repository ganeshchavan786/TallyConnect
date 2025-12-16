# Migration Plan: Backend/Frontend Structure

## Overview
Restructure project to use `backend/` and `frontend/` folders for professional separation.

## Current Structure
```
TallyConnect/
├── config/              → Move to backend/config/
├── database/            → Move to backend/database/
├── reports/
│   ├── portal/          → Move to frontend/portal/
│   ├── static/          → Move to frontend/static/
│   └── templates/       → Move to frontend/templates/
├── TallyConnect.py      → Move to backend/app.py
├── portal_server.py     → Move to backend/portal_server.py
└── portal_launcher.py   → Move to backend/portal_launcher.py
```

## New Structure
```
TallyConnect/
├── backend/
│   ├── config/
│   ├── database/
│   ├── services/        (Phase 3)
│   ├── ui/              (Phase 4)
│   ├── app.py
│   ├── portal_server.py
│   └── portal_launcher.py
├── frontend/
│   ├── portal/
│   ├── static/
│   └── templates/
└── tests/
```

## Migration Steps

### Phase 1: Create Structure
1. Create `backend/` and `frontend/` directories
2. Create subdirectories

### Phase 2: Move Files
1. Move Python files to `backend/`
2. Move HTML/CSS/JS to `frontend/`
3. Keep `tests/` at root

### Phase 3: Update Imports
1. Update all Python imports
2. Update relative paths
3. Update portal server paths

### Phase 4: Update Build Configs
1. Update PyInstaller specs
2. Update build scripts
3. Test EXE builds

### Phase 5: Testing
1. Run all tests
2. Test application
3. Test portal server
4. Test EXE builds

## Path Updates Needed

### portal_server.py
- `reports/portal` → `frontend/portal`
- Update `PORTAL_DIR` path

### PyInstaller Specs
- Update `datas` paths
- `('reports', 'reports')` → `('frontend', 'frontend')`

### Import Updates
- `from config import ...` → `from backend.config import ...`
- Or use relative imports: `from .config import ...`

## Benefits
✅ Professional structure
✅ Clear separation
✅ Industry standard
✅ Easy to scale
✅ Better organization

