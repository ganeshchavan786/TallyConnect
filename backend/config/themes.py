"""
TallyConnect Themes
==================

Theme definitions for the application UI.
"""

THEMES = {
    "Modern Blue": {
        "primary": "#3498db", "success": "#27ae60", "danger": "#e74c3c",
        "warning": "#f39c12", "info": "#16a085", "dark": "#2c3e50",
        "light": "#ecf0f1", "bg": "#f8f9fa", "text": "#34495e",
        "accent": "#3498db", "header": "#2c3e50", "border": "#bdc3c7",
        "tree_header_bg": "#2c3e50", "tree_header_fg": "white",
        "tree_even": "#ffffff", "tree_odd": "#f8fbfc"
    },
    "Dark Professional": {
        "primary": "#1e88e5", "success": "#43a047", "danger": "#e53935",
        "warning": "#fb8c00", "info": "#00acc1", "dark": "#212121",
        "light": "#424242", "bg": "#303030", "text": "#e0e0e0",
        "accent": "#1e88e5", "header": "#212121", "border": "#616161",
        "tree_header_bg": "#424242", "tree_header_fg": "#e0e0e0",
        "tree_even": "#303030", "tree_odd": "#383838"
    },
    "Light Professional": {
        "primary": "#1976d2", "success": "#388e3c", "danger": "#d32f2f",
        "warning": "#f57c00", "info": "#0097a7", "dark": "#37474f",
        "light": "#eceff1", "bg": "#fafafa", "text": "#263238",
        "accent": "#1976d2", "header": "#37474f", "border": "#cfd8dc",
        "tree_header_bg": "#546e7a", "tree_header_fg": "white",
        "tree_even": "#ffffff", "tree_odd": "#f5f5f5"
    },
    "Fresh Green": {
        "primary": "#66bb6a", "success": "#4caf50", "danger": "#ef5350",
        "warning": "#ffa726", "info": "#26a69a", "dark": "#2e7d32",
        "light": "#e8f5e9", "bg": "#f1f8f4", "text": "#1b5e20",
        "accent": "#66bb6a", "header": "#2e7d32", "border": "#a5d6a7",
        "tree_header_bg": "#388e3c", "tree_header_fg": "white",
        "tree_even": "#ffffff", "tree_odd": "#e8f5e9"
    },
    "Purple Elegant": {
        "primary": "#9c27b0", "success": "#66bb6a", "danger": "#ef5350",
        "warning": "#ffa726", "info": "#26c6da", "dark": "#4a148c",
        "light": "#f3e5f5", "bg": "#faf5ff", "text": "#4a148c",
        "accent": "#9c27b0", "header": "#6a1b9a", "border": "#ce93d8",
        "tree_header_bg": "#7b1fa2", "tree_header_fg": "white",
        "tree_even": "#ffffff", "tree_odd": "#f3e5f5"
    }
}

DEFAULT_THEME = "Modern Blue"

def get_theme(theme_name=None):
    """Get theme by name, returns default if not found."""
    if theme_name is None:
        theme_name = DEFAULT_THEME
    return THEMES.get(theme_name, THEMES[DEFAULT_THEME])

def get_theme_names():
    """Get list of available theme names."""
    return list(THEMES.keys())

