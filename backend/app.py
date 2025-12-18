#!/usr/bin/env python3
"""
v5.6_optimized.py

OPTIMIZATIONS:
 ✅ Removed COUNT query (Tally doesn't support it properly)
 ✅ Simulated progress (10, 20, 50, 100%)
 ✅ SQLite PRAGMA optimization (faster inserts)
 ✅ Auto-hide synced companies from available list
 ✅ Connection reuse for Tally
 ✅ Better timeout & error handling
 ✅ Progress estimation based on batch size
"""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import pyodbc
import sqlite3
import time
from datetime import datetime, timedelta
import traceback
import os
import re
import sys
try:
    import pystray
    from PIL import Image, ImageDraw
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False

# ---------- Configuration ----------
from backend.config import (
    DB_FILE, BATCH_SIZE, COMMON_PORTS, DSN_PREFIX,
    TALLY_COMPANY_QUERY, VOUCHER_QUERY_TEMPLATE
)
from backend.config.themes import THEMES, DEFAULT_THEME, get_theme

# ---------- Database ----------
from backend.database.connection import init_db
from backend.database.company_dao import CompanyDAO

# ---------- Utilities ----------
from backend.utils.error_handler import get_user_friendly_error
from backend.utils.sync_logger import get_sync_logger
from backend.utils.validators import (
    validate_sync_params, CompanyValidator, DateValidator, ValidationError
)

def _load_build_info():
    """Load build_info.json if present (generated during build)."""
    try:
        base_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        candidates = [
            os.path.join(base_dir, "build_info.json"),
        ]
        # In PyInstaller, additional data can be under _MEIPASS; try there too.
        try:
            candidates.append(os.path.join(sys._MEIPASS, "build_info.json"))  # type: ignore[attr-defined]
        except Exception:
            pass
        for p in candidates:
            if p and os.path.exists(p):
                import json
                with open(p, "r", encoding="utf-8") as f:
                    return json.load(f)
    except Exception:
        pass
    return {"generated_at": "unknown", "git_tag": "dev", "git_commit": "dev"}

def try_connect_dsn(dsn_name, timeout=5):
    """Try to connect to Tally DSN."""
    try:
        conn = pyodbc.connect(f"DSN={dsn_name};", timeout=timeout)
        cur = conn.cursor()
        cur.execute(TALLY_COMPANY_QUERY)
        _ = cur.fetchone()
        cur.close()
        conn.close()
        return True, None
    except Exception as e:
        return False, str(e)

# ---------- Application ----------
class BizAnalystApp:
    def __init__(self, root):
        self.root = root
        try:
            self.root.state('zoomed')
        except:
            pass
        try:
            self.root.minsize(1200, 750)
        except:
            pass
        self.root.title("TallyConnect v5.6 — Modern Tally Sync Platform")
        self.root.geometry("1200x750")

        # Apply window icon/logo (uses Logo.png if present)
        try:
            self._apply_window_logo()
        except Exception:
            pass
        
        # Theme System - Using config module
        self.themes = THEMES
        self.current_theme = tk.StringVar(value=DEFAULT_THEME)
        self.colors = get_theme(self.current_theme.get()).copy()
        
        # Initialize database (with timeout protection)
        try:
            self.db_conn = init_db()
        except Exception as e:
            print(f"[ERROR] Database initialization failed: {e}")
            # Create minimal connection as fallback
            import sqlite3
            from backend.config.settings import DB_FILE
            self.db_conn = sqlite3.connect(DB_FILE, check_same_thread=False, timeout=5.0)
        
        self.db_lock = threading.Lock()
        # Initialize CompanyDAO for database operations
        self.company_dao = CompanyDAO(self.db_conn, self.db_lock)
        self.sync_threads = {}
        self.sync_locks = {}
        # auto-sync feature
        self.auto_sync_enabled = tk.BooleanVar(value=False)
        self.auto_sync_interval_var = tk.IntVar(value=5)  # minutes
        self.auto_sync_timers = {}  # key -> {next_sync_time, countdown}
        self.auto_sync_stop_event = threading.Event()
        self.company_map = {}
        self.company_map = {}
        self._last_load_time = 0.0
        self._last_tree_refresh = 0.0
        
        self.batch_size_var = tk.IntVar(value=BATCH_SIZE)
        self.slice_var = tk.BooleanVar(value=False)
        self.slice_days_var = tk.IntVar(value=7)
        
        # System tray support
        self.tray_icon = None
        self.tray_thread = None
        if TRAY_AVAILABLE:
            self._setup_tray()
        
        self._build_ui()
        try:
            self.root.bind('<Control-r>', lambda e: self._refresh_tree())
            self.root.bind('<Control-l>', lambda e: self.load_companies())
            self.root.bind('<Control-s>', lambda e: self.sync_selected())
        except:
            pass
        try:
            self._build_menu()
        except:
            pass
        # Start UI update in background to prevent blocking
        self.root.after(100, self._initialize_after_ui)
    
    def _initialize_after_ui(self):
        """Initialize non-critical components after UI is shown."""
        try:
            self.auto_detect_dsn(silent=True)
        except Exception:
            pass
        self._start_status_thread()
        self._mark_interrupted_syncs()
        # Refresh tree in background to prevent blocking
        self.root.after(200, self._refresh_tree)

    def _build_ui(self):
        self._create_styles()
        self.root.config(bg=self.colors["bg"])

        # ========== MODERN HEADER ==========
        self.header = tk.Frame(self.root, bg=self.colors["header"], height=80)
        self.header.pack(fill=tk.X)
        self.header.pack_propagate(False)
        
        # Add subtle shadow effect with a thin line
        self.shadow_line = tk.Frame(self.root, bg="#34495e", height=2)
        self.shadow_line.pack(fill=tk.X)
        
        self.title_frame = tk.Frame(self.header, bg=self.colors["header"])
        self.title_frame.pack(side=tk.LEFT, padx=24, pady=12)

        # Header brand row (Logo.png + text). Fallback to text-only if image not available.
        brand_row = tk.Frame(self.title_frame, bg=self.colors["header"])
        brand_row.pack(anchor="w")

        header_logo_img = None
        try:
            header_logo_img = self._load_brand_image(size=(52, 52))
        except Exception:
            header_logo_img = None

        if header_logo_img is not None:
            self._header_logo_image = header_logo_img  # keep reference
            self.header_logo_label = tk.Label(
                brand_row,
                image=self._header_logo_image,
                bg=self.colors["header"],
                bd=0,
                highlightthickness=0,
            )
            self.header_logo_label.pack(side=tk.LEFT, padx=(0, 12))

            text_col = tk.Frame(brand_row, bg=self.colors["header"])
            text_col.pack(side=tk.LEFT)
            self.title_label = tk.Label(
                text_col,
                text="TALLYCONNECT",
                fg="white",
                bg=self.colors["header"],
                font=("Segoe UI", 22, "bold"),
            )
            self.title_label.pack(anchor="w")
            self.subtitle_label = tk.Label(
                text_col,
                text="Modern Tally Sync Platform",
                fg="#95a5a6",
                bg=self.colors["header"],
                font=("Segoe UI", 10),
            )
            self.subtitle_label.pack(anchor="w")
        else:
            # Text-only fallback
            self.title_label = tk.Label(
                brand_row,
                text="📊 TALLYCONNECT",
                fg="white",
                bg=self.colors["header"],
                font=("Segoe UI", 22, "bold"),
            )
            self.title_label.pack(anchor="w")
            self.subtitle_label = tk.Label(
                self.title_frame,
                text="Modern Tally Sync Platform",
                fg="#95a5a6",
                bg=self.colors["header"],
                font=("Segoe UI", 10),
            )
            self.subtitle_label.pack(anchor="w")
        
        self.status_frame = tk.Frame(self.header, bg=self.colors["header"])
        self.status_frame.pack(side=tk.RIGHT, padx=24, pady=12)
        self.status_canvas = tk.Canvas(self.status_frame, width=18, height=18, bg=self.colors["header"], 
                                       highlightthickness=0)
        self.status_canvas.pack(side=tk.LEFT, padx=(0, 10))
        self._draw_status_circle("gray")
        self.status_label = tk.Label(self.status_frame, text="Initializing...", fg="#2ecc71", bg=self.colors["header"],
                                     font=("Segoe UI", 11, "bold"))
        self.status_label.pack(side=tk.LEFT)

        # ========== MODERN TOOLBAR ==========
        toolbar = tk.Frame(self.root, bg="#ffffff", height=60)
        toolbar.pack(fill=tk.X, padx=0, pady=0)
        toolbar.pack_propagate(False)
        
        # Add top border to toolbar
        toolbar_border = tk.Frame(toolbar, bg="#e0e0e0", height=1)
        toolbar_border.pack(fill=tk.X)
        
        toolbar_content = tk.Frame(toolbar, bg="#ffffff")
        toolbar_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tk.Label(toolbar_content, text="Quick Actions:", bg="white", fg=self.colors["text"],
                font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Button(toolbar_content, text="🏢 Synced Companies", command=self.show_synced_companies, 
                  style="Info.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar_content, text="➕ Add Company", command=self.show_add_company,
                  style="Success.TButton").pack(side=tk.LEFT, padx=5)
        self.toolbar_sync_btn = ttk.Button(toolbar_content, text="⚙️ Sync Settings", command=self.show_sync_settings, 
                                          style="Accent.TButton")
        self.toolbar_sync_btn.pack(side=tk.LEFT, padx=5)
        
        # Theme Selector
        tk.Label(toolbar_content, text="Theme:", bg="white", fg=self.colors["text"],
                font=("Segoe UI", 9)).pack(side=tk.RIGHT, padx=(12, 4))
        from backend.config.themes import get_theme_names
        self.theme_dropdown = ttk.Combobox(toolbar_content, textvariable=self.current_theme, 
                                          values=get_theme_names(),
                                          state="readonly", width=18, font=("Segoe UI", 9))
        self.theme_dropdown.pack(side=tk.RIGHT, padx=4)
        self.theme_dropdown.bind("<<ComboboxSelected>>", lambda e: self.apply_theme())
        
        # Build stamp (helps identify exactly which EXE is running)
        try:
            bi = _load_build_info()
            build_text = f"{bi.get('git_tag','dev')} ({bi.get('git_commit','dev')})"
            if bi.get("generated_at"):
                build_text += f" • {bi.get('generated_at')}"
        except Exception:
            build_text = "dev"

        tk.Label(toolbar_content, text=f"v5.6 Pro • {build_text}", bg="white", fg="#95a5a6",
                font=("Segoe UI", 9, "italic")).pack(side=tk.RIGHT, padx=12)

        # ========== MAIN CONTENT AREA ==========
        self.paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # === LEFT: Companies Tree ===
        self.left_frame = tk.Frame(self.paned, bg="white", width=350)
        self.paned.add(self.left_frame, weight=1)
        self.left_frame.pack_propagate(False)
        
        self.left_header = tk.Frame(self.left_frame, bg=self.colors["primary"], height=48)
        self.left_header.pack(fill=tk.X)
        self.left_header.pack_propagate(False)
        
        self.header_left = tk.Frame(self.left_header, bg=self.colors["primary"])
        self.header_left.pack(side=tk.LEFT, anchor="w", padx=16, pady=10)
        self.left_header_label = tk.Label(self.header_left, text="📋 Synced Companies", bg=self.colors["primary"], fg="white",
                 font=("Segoe UI", 13, "bold"))
        self.left_header_label.pack(side=tk.LEFT)
        
        # Modern count badge
        count_frame = tk.Frame(self.left_frame, bg="#f8f9fa")
        count_frame.pack(fill=tk.X, padx=12, pady=8)
        self.company_count = tk.Label(count_frame, text="0 synced", bg="#f8f9fa", fg=self.colors["text"], 
                                      font=("Segoe UI", 10, "bold"))
        self.company_count.pack(anchor="w", padx=8, pady=4)

        # Body container to keep tree and actions visible together
        left_body = tk.Frame(self.left_frame, bg="white")
        left_body.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        left_body.grid_rowconfigure(0, weight=1)
        left_body.grid_columnconfigure(0, weight=1)

        cols = ("Name", "Status", "Sync", "Remove", "Next Sync", "AlterID", "Records")
        self.tree = ttk.Treeview(left_body, columns=cols, show="headings", height=18, style="Custom.Treeview")
        for c in cols:
            self.tree.heading(c, text=c)
            if c == "Name":
                self.tree.column(c, width=180, minwidth=150, stretch=True, anchor="w")
            elif c == "Next Sync":
                self.tree.column(c, width=100, minwidth=90, stretch=False, anchor="center")
            elif c in ("Sync", "Remove"):
                self.tree.column(c, width=100 if c == "Sync" else 100, minwidth=90, stretch=False, anchor="center")
            elif c == "AlterID":
                self.tree.column(c, width=85, minwidth=70, stretch=False, anchor="center")
            else:  # Status, Records
                self.tree.column(c, width=80, minwidth=70, stretch=False, anchor="center")
        self.tree.grid(row=0, column=0, sticky="nsew", pady=(0, 6))

        # Inline actions are available via Sync / Remove columns; no separate action bar needed

        # === MIDDLE: Controls & Available Companies ===
        self.mid_frame = tk.Frame(self.paned, bg="white")
        self.paned.add(self.mid_frame, weight=2)

        self.ctrl_frame = tk.LabelFrame(self.mid_frame, text="⚙️ Sync Settings", bg="white", font=("Segoe UI", 10, "bold"))
        self.ctrl_frame_pack_kwargs = dict(fill=tk.X, padx=12, pady=10)
        self.sync_settings_visible = False  # hidden until toggled
        
        dsn_row = tk.Frame(self.ctrl_frame, bg="white")
        dsn_row.pack(fill=tk.X, padx=10, pady=6)
        tk.Label(dsn_row, text="DSN:", bg="white", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 8))
        self.dsn_var = tk.StringVar()
        self.entry_dsn = ttk.Entry(dsn_row, textvariable=self.dsn_var, width=35)
        self.entry_dsn.pack(side=tk.LEFT, padx=6)
        ttk.Button(dsn_row, text="🔍 Auto Detect", command=self.auto_detect_dsn, 
                  style="Info.TButton").pack(side=tk.LEFT, padx=4)
        
        date_row = tk.Frame(self.ctrl_frame, bg="white")
        date_row.pack(fill=tk.X, padx=10, pady=6)
        tk.Label(date_row, text="Date Range:", bg="white", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)
        tk.Label(date_row, text="From:", bg="white").pack(side=tk.LEFT, padx=(16, 4))
        
        # Calculate current financial year (April 1 to March 31)
        now = datetime.now()
        current_year = now.year
        current_month = now.month
        
        # Financial year: April to March
        # If current month is April or later, FY starts this year
        # If current month is Jan-Mar, FY started last year
        if current_month >= 4:
            # FY 2025-26: 01-04-2025 to 31-03-2026
            fy_start_date = f"01-04-{current_year}"
            fy_end_date = f"31-03-{current_year + 1}"
        else:
            # FY 2024-25: 01-04-2024 to 31-03-2025
            fy_start_date = f"01-04-{current_year - 1}"
            fy_end_date = f"31-03-{current_year}"
        
        self.from_var = tk.StringVar(value=fy_start_date)
        self.entry_from = ttk.Entry(date_row, textvariable=self.from_var, width=15)
        self.entry_from.pack(side=tk.LEFT, padx=4)
        tk.Label(date_row, text="To:", bg="white").pack(side=tk.LEFT, padx=(12, 4))
        self.to_var = tk.StringVar(value=fy_end_date)
        self.entry_to = ttk.Entry(date_row, textvariable=self.to_var, width=15)
        self.entry_to.pack(side=tk.LEFT, padx=4)
        
        adv_row = tk.Frame(self.ctrl_frame, bg="white")
        adv_row.pack(fill=tk.X, padx=10, pady=6)
        tk.Label(adv_row, text="Batch Size:", bg="white").pack(side=tk.LEFT)
        self.entry_batch = ttk.Entry(adv_row, textvariable=self.batch_size_var, width=8)
        self.entry_batch.pack(side=tk.LEFT, padx=6)
        
        tk.Label(adv_row, text="", bg="white").pack(side=tk.LEFT, padx=12)
        self.chk_slice = ttk.Checkbutton(adv_row, text="Slice by Days:", variable=self.slice_var)
        self.chk_slice.pack(side=tk.LEFT)
        self.spin_slice = ttk.Entry(adv_row, textvariable=self.slice_days_var, width=6)
        self.spin_slice.pack(side=tk.LEFT, padx=4)

        # === AUTO-SYNC SETTINGS ===
        auto_sync_frame = tk.Frame(self.ctrl_frame, bg="white")
        auto_sync_frame.pack(fill=tk.X, padx=10, pady=8)
        tk.Label(auto_sync_frame, text="Auto-Sync:", bg="white", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)
        ttk.Checkbutton(auto_sync_frame, text="Enable", variable=self.auto_sync_enabled, 
                       command=self._on_toggle_auto_sync).pack(side=tk.LEFT, padx=6)
        self.auto_sync_status = tk.Label(auto_sync_frame, text="● Disabled", bg="white", fg="gray", 
                                        font=("Segoe UI", 9, "bold"))
        self.auto_sync_status.pack(side=tk.LEFT, padx=4)
        tk.Label(auto_sync_frame, text="Interval (min):", bg="white").pack(side=tk.LEFT, padx=(12, 4))
        ttk.Spinbox(auto_sync_frame, from_=1, to=60, textvariable=self.auto_sync_interval_var, 
                   width=4).pack(side=tk.LEFT, padx=2)
        ttk.Button(auto_sync_frame, text="⚡ Update", 
                  command=self._on_update_auto_sync_timer, style="Warning.TButton").pack(side=tk.LEFT, padx=4)
        
        self.avail_header = tk.Frame(self.mid_frame, bg=self.colors["info"], height=42)
        self.avail_header_pack_kwargs = dict(fill=tk.X, padx=12, pady=(12, 0))
        self.avail_header.pack(**self.avail_header_pack_kwargs)
        self.avail_header.pack_propagate(False)
        tk.Label(self.avail_header, text="🏢 Available Companies", bg=self.colors["info"], 
                 fg="white", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=16, pady=10)
        
        self.avail_ctrl = tk.Frame(self.mid_frame, bg="white")
        self.avail_ctrl_pack_kwargs = dict(fill=tk.X, padx=12, pady=4)
        self.avail_ctrl.pack(**self.avail_ctrl_pack_kwargs)
        
        self.avail_count_label = tk.Label(self.avail_ctrl, text="0 available", bg="white", fg="#666", 
                                         font=("Segoe UI", 9, "bold"))
        self.avail_count_label.pack(side=tk.LEFT)
        
        self.avail_skipped_label = tk.Label(self.avail_ctrl, text="", bg="white", fg="#c00", 
                                           font=("Segoe UI", 8, "bold"))
        self.avail_skipped_label.pack(side=tk.RIGHT)
        
        self.avail_listbox = tk.Listbox(self.mid_frame, height=7, bg="#f8f9fa", font=("Segoe UI", 10), 
                                       selectmode=tk.SINGLE, relief=tk.FLAT, bd=0,
                                       highlightthickness=1, highlightbackground="#e0e0e0",
                                       selectbackground=self.colors["primary"], selectforeground="white")
        self.avail_listbox_pack_kwargs = dict(fill=tk.BOTH, expand=True, padx=12, pady=(0, 10))
        self.avail_listbox.pack(**self.avail_listbox_pack_kwargs)
        
        self.avail_scrollbar = ttk.Scrollbar(self.mid_frame, orient=tk.VERTICAL, command=self.avail_listbox.yview)
        self.avail_scrollbar_pack_kwargs = dict(side=tk.RIGHT, fill=tk.Y, padx=(0, 12))
        self.avail_scrollbar.pack(**self.avail_scrollbar_pack_kwargs)
        self.avail_listbox.config(yscrollcommand=self.avail_scrollbar.set)
        
        self.btnrow = tk.Frame(self.mid_frame, bg="white")
        self.btnrow_pack_kwargs = dict(fill=tk.X, padx=12, pady=(0, 12))
        self.btnrow.pack(**self.btnrow_pack_kwargs)
        self.btn_load = ttk.Button(self.btnrow, text="📥 Load Companies", command=self.load_companies,
                                  style="Success.TButton")
        self.btn_load.pack(side=tk.LEFT, padx=4)
        self.btn_sync = ttk.Button(self.btnrow, text="⚙️ Sync Settings", command=self.show_sync_settings, 
                                  style="Warning.TButton")
        self.btn_sync.pack(side=tk.LEFT, padx=4)

        # === RIGHT: Notes + Log ===
        self.right_frame = tk.Frame(self.paned, bg="white", width=380)
        self.paned.add(self.right_frame, weight=1)
        self.right_frame.pack_propagate(False)
        
        self.notes_header = tk.Frame(self.right_frame, bg=self.colors["warning"], height=42)
        self.notes_header.pack(fill=tk.X)
        self.notes_header.pack_propagate(False)
        self.notes_header_label = tk.Label(self.notes_header, text="📝 Notes", bg=self.colors["warning"], fg="white",
                 font=("Segoe UI", 12, "bold"))
        self.notes_header_label.pack(anchor="w", padx=16, pady=10)
        
        self.notes_text = tk.Text(self.right_frame, height=6, bg="#fffef8", font=("Segoe UI", 10), 
                                 relief=tk.FLAT, bd=1, padx=8, pady=8)
        self.notes_text.pack(fill=tk.X, padx=12, pady=10)
        
        notes_row = tk.Frame(self.right_frame, bg="white")
        notes_row.pack(fill=tk.X, padx=12, pady=(0, 10))
        ttk.Button(notes_row, text="💾 Save", command=self.save_notes, style="Success.TButton").pack(side=tk.LEFT, padx=4)
        ttk.Button(notes_row, text="✕ Clear", command=lambda: self.notes_text.delete("1.0", "end"),
                  style="Danger.TButton").pack(side=tk.LEFT, padx=4)
        
        self.log_header = tk.Frame(self.right_frame, bg=self.colors["success"], height=42)
        self.log_header.pack(fill=tk.X, pady=(8, 0))
        self.log_header.pack_propagate(False)
        self.log_header_label = tk.Label(self.log_header, text="📋 Sync Log", bg=self.colors["success"], fg="white",
                 font=("Segoe UI", 12, "bold"))
        self.log_header_label.pack(anchor="w", padx=16, pady=10)
        
        self.log_text = tk.Text(self.right_frame, height=10, bg="#f8f9fa", font=("Consolas", 9), 
                               relief=tk.FLAT, bd=1, padx=8, pady=8)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 10))

        # ========== MODERN FOOTER ==========
        self.footer = tk.Frame(self.root, bg="#ffffff", height=80)
        self.footer_pack_kwargs = dict(fill=tk.X, side=tk.BOTTOM)
        self.footer.pack(**self.footer_pack_kwargs)
        self.footer.pack_propagate(False)
        
        # Top border for footer
        tk.Frame(self.footer, bg="#e0e0e0", height=1).pack(fill=tk.X)
        
        prog_frame = tk.Frame(self.footer, bg="#ffffff")
        prog_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(prog_frame, text="Progress:", bg="#ffffff", fg=self.colors["text"],
                font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        
        # Circular progress indicator (larger for better visibility)
        from backend.ui.circular_progress import CircularProgress
        self.circular_progress = CircularProgress(
            prog_frame, 
            size=65, 
            line_width=6,
            bg_color="#e0e0e0",
            progress_color=self.colors["primary"],
            text_color=self.colors["text"]
        )
        self.circular_progress.pack(side=tk.LEFT, padx=8)
        # Initialize at 0%
        self.circular_progress.set_progress(0)
        
        # Horizontal progress bar (kept for compatibility)
        self.progress = ttk.Progressbar(prog_frame, orient="horizontal", length=450, mode="determinate", 
                                       style='Custom.Horizontal.TProgressbar')
        self.progress.pack(side=tk.LEFT, padx=8, fill=tk.X, expand=True)
        self.progress_label = tk.Label(prog_frame, text="0%", bg="#ffffff", fg=self.colors["success"],
                                      font=("Segoe UI", 11, "bold"), width=5)
        self.progress_label.pack(side=tk.LEFT, padx=6)
        
        info_frame = tk.Frame(self.footer, bg="#ffffff")
        info_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        self.batch_info_label = tk.Label(info_frame, text="✓ Ready", bg="#ffffff", fg=self.colors["text"],
                                        font=("Segoe UI", 9))
        self.batch_info_label.pack(side=tk.LEFT, padx=6)
        self.db_info = tk.Label(info_frame, text=f"📊 DB: {os.path.basename(DB_FILE)}", bg="#ffffff", 
                               fg="#95a5a6", font=("Segoe UI", 9))
        self.db_info.pack(side=tk.RIGHT, padx=6)

        self.statusbar = tk.Label(self.root, text="✓ Ready", anchor="w", relief=tk.FLAT, 
                                 bg="#f8f9fa", fg=self.colors["text"], font=("Segoe UI", 9), padx=20, pady=8)
        self.statusbar_pack_kwargs = dict(fill=tk.X, side=tk.BOTTOM)
        self.statusbar.pack(**self.statusbar_pack_kwargs)

        try:
            self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)
            self.tree.bind("<Button-1>", self._on_tree_click)
        except:
            pass
        try:
            self.avail_listbox.bind("<Double-Button-1>", lambda e: self.sync_selected())
        except:
            pass
        try:
            self.avail_listbox.bind("<<ListboxSelect>>", self._on_avail_select)
        except:
            pass

        # Start in Synced Companies view
        self.show_synced_companies()

    def show_sync_settings(self):
        """Show only Sync Settings panel."""
        try:
            if not self.sync_settings_visible:
                self.ctrl_frame.pack(**self.ctrl_frame_pack_kwargs)
            self.sync_settings_visible = True
            self._set_minimal_view(sync_only=True)
        except Exception as e:
            self.log(f"✗ Show Sync Settings error: {e}")

    def show_synced_companies(self):
        """Show only Synced Companies panel."""
        try:
            self.ctrl_frame.pack_forget()
            self.sync_settings_visible = False
            self._set_synced_only()
        except Exception as e:
            self.log(f"✗ Show Synced Companies error: {e}")

    def show_add_company(self):
        """Show Add Company view (available companies, notes, log, progress)."""
        try:
            self.ctrl_frame.pack_forget()
            self.sync_settings_visible = False
            self._set_add_company_view()
        except Exception as e:
            self.log(f"✗ Show Add Company error: {e}")

    def _set_minimal_view(self, sync_only: bool):
        """When Sync Settings is open, hide other panels so only settings show."""
        try:
            panes = self.paned.panes()
            if sync_only:
                # Ensure mid frame is present for settings
                if str(self.mid_frame) not in panes:
                    self.paned.add(self.mid_frame, weight=2)
                # Remove side panes
                if str(self.left_frame) in panes:
                    self.paned.forget(self.left_frame)
                if str(self.right_frame) in panes:
                    self.paned.forget(self.right_frame)
                # Hide available list and controls
                for w in (self.avail_header, self.avail_ctrl, self.avail_listbox, self.avail_scrollbar, self.btnrow):
                    try:
                        w.pack_forget()
                    except Exception:
                        pass
                # Hide footer & status bar
                try:
                    self.footer.pack_forget()
                except Exception:
                    pass
                try:
                    self.statusbar.pack_forget()
                except Exception:
                    pass
            else:
                # Re-add panes if missing (full view)
                panes = self.paned.panes()
                if str(self.left_frame) not in panes:
                    self.paned.insert(0, self.left_frame)
                if str(self.mid_frame) not in panes:
                    self.paned.add(self.mid_frame, weight=2)
                if str(self.right_frame) not in panes:
                    self.paned.add(self.right_frame, weight=1)
                # Restore available list and controls
                for widget, kwargs in (
                    (self.avail_header, self.avail_header_pack_kwargs),
                    (self.avail_ctrl, self.avail_ctrl_pack_kwargs),
                    (self.avail_listbox, self.avail_listbox_pack_kwargs),
                    (self.avail_scrollbar, self.avail_scrollbar_pack_kwargs),
                    (self.btnrow, self.btnrow_pack_kwargs),
                ):
                    try:
                        widget.pack(**kwargs)
                    except Exception:
                        pass
                # Restore footer & status bar
                try:
                    self.footer.pack(**self.footer_pack_kwargs)
                except Exception:
                    pass
                try:
                    self.statusbar.pack(**self.statusbar_pack_kwargs)
                except Exception:
                    pass
        except Exception as e:
            self.log(f"✗ Minimal view toggle error: {e}")

    def _set_synced_only(self):
        """Show only the Synced Companies list."""
        try:
            panes = self.paned.panes()
            # Ensure left pane is visible
            if str(self.left_frame) not in panes:
                self.paned.insert(0, self.left_frame)
            # Hide mid and right panes
            if str(self.mid_frame) in panes:
                self.paned.forget(self.mid_frame)
            if str(self.right_frame) in panes:
                self.paned.forget(self.right_frame)
            # Hide footer & status bar
            try:
                self.footer.pack_forget()
            except Exception:
                pass
            try:
                self.statusbar.pack_forget()
            except Exception:
                pass
        except Exception as e:
            self.log(f"✗ Synced-only view error: {e}")

    def _set_add_company_view(self):
        """Show available companies + notes/log + progress; hide synced list."""
        try:
            panes = self.paned.panes()
            # Hide left pane, ensure mid/right are visible
            if str(self.left_frame) in panes:
                self.paned.forget(self.left_frame)
            if str(self.mid_frame) not in panes:
                self.paned.add(self.mid_frame, weight=2)
            if str(self.right_frame) not in panes:
                self.paned.add(self.right_frame, weight=1)

            # Restore available list and controls
            for widget, kwargs in (
                (self.avail_header, self.avail_header_pack_kwargs),
                (self.avail_ctrl, self.avail_ctrl_pack_kwargs),
                (self.avail_listbox, self.avail_listbox_pack_kwargs),
                (self.avail_scrollbar, self.avail_scrollbar_pack_kwargs),
                (self.btnrow, self.btnrow_pack_kwargs),
            ):
                try:
                    widget.pack(**kwargs)
                except Exception:
                    pass

            # Hide sync settings frame if visible
            try:
                self.ctrl_frame.pack_forget()
            except Exception:
                pass

            # Restore footer & status bar
            try:
                self.footer.pack(**self.footer_pack_kwargs)
            except Exception:
                pass
            try:
                self.statusbar.pack(**self.statusbar_pack_kwargs)
            except Exception:
                pass
        except Exception as e:
            self.log(f"✗ Add company view error: {e}")

    def apply_theme(self):
        """Apply selected theme to all UI elements"""
        try:
            theme_name = self.current_theme.get()
            self.colors = get_theme(theme_name).copy()
            
            # Recreate styles with new colors
            self._create_styles()
            
            # Update all UI elements
            try:
                self.root.config(bg=self.colors["bg"])
            except: pass
            
            # Header
            for widget in [getattr(self, w, None) for w in ['header', 'title_frame', 'status_frame']]:
                if widget:
                    try: widget.config(bg=self.colors["header"])
                    except: pass
            
            # Update all frames and labels recursively
            self._update_widget_colors(self.root)
            
            # Refresh tree with new colors
            self._refresh_tree()
            
            self.log(f"✓ Theme changed to: {theme_name}")
        except Exception as e:
            self.log(f"✗ Theme apply error: {e}")
    
    def _update_widget_colors(self, widget):
        """Recursively update widget colors"""
        try:
            widget_class = widget.winfo_class()
            
            # Update based on widget type
            if widget_class == 'Frame':
                current_bg = str(widget.cget('bg'))
                # Update specific frame types
                if current_bg in ['#2c3e50', '#2b3e50', '#212121', '#37474f', '#2e7d32', '#4a148c', '#6a1b9a']:
                    widget.config(bg=self.colors["header"])
                elif current_bg in ['#3498db', '#1e88e5', '#1976d2', '#66bb6a', '#9c27b0']:
                    widget.config(bg=self.colors["primary"])
                elif current_bg in ['#27ae60', '#43a047', '#388e3c', '#4caf50']:
                    widget.config(bg=self.colors["success"])
                elif current_bg in ['#f39c12', '#fb8c00', '#f57c00', '#ffa726']:
                    widget.config(bg=self.colors["warning"])
                elif current_bg in ['#16a085', '#00acc1', '#0097a7', '#26a69a', '#26c6da']:
                    widget.config(bg=self.colors["info"])
            
            elif widget_class == 'Label':
                current_bg = str(widget.cget('bg'))
                if current_bg in ['#2c3e50', '#212121', '#37474f', '#2e7d32', '#4a148c', '#6a1b9a']:
                    widget.config(bg=self.colors["header"], fg="white")
                elif current_bg in ['#3498db', '#1e88e5', '#1976d2', '#66bb6a', '#9c27b0']:
                    widget.config(bg=self.colors["primary"], fg="white")
            
            # Process children
            for child in widget.winfo_children():
                self._update_widget_colors(child)
        except:
            pass
    
    def _create_styles(self):
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except:
            try:
                style.theme_use('default')
            except:
                pass

        # Modern Treeview with theme colors
        style.configure("Custom.Treeview", 
                       rowheight=32, 
                       font=("Segoe UI", 10), 
                       borderwidth=0, 
                       relief=tk.FLAT,
                       background=self.colors.get("tree_even", "white"),
                       fieldbackground=self.colors.get("tree_even", "white"))
        
        style.configure("Treeview.Heading", 
                       font=("Segoe UI", 11, "bold"), 
                       background=self.colors.get("tree_header_bg", "#2c3e50"),
                       foreground=self.colors.get("tree_header_fg", "white"),
                       relief=tk.FLAT,
                       borderwidth=1)
        
        style.map("Treeview.Heading", 
                 background=[('active', self.colors.get("dark", "#34495e"))],
                 foreground=[('active', self.colors.get("tree_header_fg", "white"))])

        # Uniform button size for all buttons
        button_padding = (14, 8)
        button_font = ("Segoe UI", 10, "bold")
        
        # PRIMARY BLUE - Main Action Buttons (Accent) 🔵
        style.configure("Accent.TButton", 
                       foreground="white", 
                       background=self.colors.get("accent", "#3498db"),
                       font=button_font,
                       borderwidth=0,
                       relief=tk.FLAT,
                       padding=button_padding)
        
        style.map("Accent.TButton",
                  foreground=[('active', 'white'), ('pressed', 'white')],
                  background=[('active', self.colors.get("primary", "#2980b9")), 
                            ('pressed', self.colors.get("dark", "#21618c"))])

        # SUCCESS GREEN - Positive Actions (Save, Load, Sync) 🟢
        style.configure("Success.TButton", 
                       foreground="white", 
                       background=self.colors.get("success", "#27ae60"),
                       font=button_font,
                       borderwidth=0,
                       relief=tk.FLAT,
                       padding=button_padding)
        
        style.map("Success.TButton",
                  foreground=[('active', 'white'), ('pressed', 'white')],
                  background=[('active', "#229954"), ('pressed', "#1e8449")])

        # INFO TEAL - Secondary Actions (Auto Detect, Update) 🟦
        style.configure("Info.TButton", 
                       foreground="white", 
                       background=self.colors.get("info", "#16a085"),
                       font=button_font,
                       borderwidth=0,
                       relief=tk.FLAT,
                       padding=button_padding)
        
        style.map("Info.TButton",
                  foreground=[('active', 'white'), ('pressed', 'white')],
                  background=[('active', "#138d75"), ('pressed', "#117a65")])

        # WARNING ORANGE - Caution Actions (Settings) 🟠
        style.configure("Warning.TButton", 
                       foreground="white", 
                       background=self.colors.get("warning", "#f39c12"),
                       font=button_font,
                       borderwidth=0,
                       relief=tk.FLAT,
                       padding=button_padding)
        
        style.map("Warning.TButton",
                  foreground=[('active', 'white'), ('pressed', 'white')],
                  background=[('active', "#e67e22"), ('pressed', "#d35400")])

        # DANGER RED - Delete/Remove Actions 🔴
        style.configure("Danger.TButton", 
                       foreground="white", 
                       background=self.colors.get("danger", "#e74c3c"),
                       font=button_font,
                       borderwidth=0,
                       relief=tk.FLAT,
                       padding=button_padding)
        
        style.map("Danger.TButton",
                  foreground=[('active', 'white'), ('pressed', 'white')],
                  background=[('active', "#c0392b"), ('pressed', "#a93226")])

        # DEFAULT LIGHT - Neutral Actions ⚪
        style.configure("TButton", 
                       padding=button_padding,
                       font=button_font,
                       relief=tk.FLAT,
                       borderwidth=0,
                       background="#ecf0f1",
                       foreground="#34495e")
        
        style.map("TButton",
                 background=[('active', '#bdc3c7'), ('pressed', '#95a5a6')],
                 foreground=[('active', '#2c3e50')],
                 relief=[('pressed', tk.FLAT)])

        # Theme-based Progress Bar
        try:
            style.configure('Custom.Horizontal.TProgressbar', 
                          troughcolor=self.colors.get("light", "#ecf0f1"), 
                          background=self.colors.get("success", "#27ae60"),
                          thickness=18,
                          borderwidth=0)
            style.map('Custom.Horizontal.TProgressbar', 
                     background=[('selected', self.colors.get("success", "#27ae60"))])
        except:
            pass

    def _on_tree_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        try:
            vals = self.tree.item(sel[0], "values")
            name, alterid = vals[0], vals[5]  # AlterID is at index 5 (after removing Reports column)
            guid = self.company_dao.get_guid_by_name_alterid(name, alterid)
            if guid:
                self.load_notes(guid)
        except Exception:
            pass

    def _on_tree_click(self, event):
        """Handle clicks on Sync/Remove columns inside the tree."""
        try:
            region = self.tree.identify("region", event.x, event.y)
            if region != "cell":
                return
            row_id = self.tree.identify_row(event.y)
            col_id = self.tree.identify_column(event.x)
            if not row_id or not col_id:
                return
            col_index = int(col_id.replace("#", ""))  # 1-based
            # Column order: Name(1), Status(2), Sync(3), Remove(4), Next Sync(5), AlterID(6), Records(7)
            if col_index == 3:  # Sync column
                self.tree.selection_set(row_id)
                self.manual_sync_all()
                return "break"
            if col_index == 4:  # Remove column
                self.tree.selection_set(row_id)
                self.remove_company()
                return "break"
        except Exception as e:
            self.log(f"✗ Tree click error: {e}")

    def _on_avail_select(self, event):
        try:
            sel = self.avail_listbox.curselection()
            if not sel:
                return
            raw = self.avail_listbox.get(sel[0])
            name = raw.split(" | ")[0].strip()
            meta = self.company_map.get(name)
            if not meta:
                self.notes_text.delete("1.0", "end")
                return
            guid = meta.get("guid")
            if not guid:
                self.notes_text.delete("1.0", "end")
                return
            self.load_notes(guid)
        except Exception:
            pass


    def save_notes(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a company to save notes")
            return
        vals = self.tree.item(sel[0], "values")
        name, alterid = vals[0], vals[5]
        guid = self.company_dao.get_guid_by_name_alterid(name, alterid)
        if not guid:
            messagebox.showwarning("No company", "Selected company not found in DB")
            return
        notes_dir = os.path.join(os.path.dirname(__file__), "notes")
        os.makedirs(notes_dir, exist_ok=True)
        path = os.path.join(notes_dir, f"{guid}.txt")
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.notes_text.get("1.0", "end").strip())
            self.log(f"✓ Notes saved for {name}")
        except Exception as e:
            self.log(f"✗ Could not save notes: {e}")

    def load_notes(self, guid):
        notes_dir = os.path.join(os.path.dirname(__file__), "notes")
        path = os.path.join(notes_dir, f"{guid}.txt")
        self.notes_text.delete("1.0", "end")
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self.notes_text.insert("1.0", f.read())
            except:
                pass

    def log(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] {msg}\n"
        try:
            self.log_text.insert("end", line)
            self.log_text.see("end")
        except:
            pass
        print(line.strip())
        self.statusbar.config(text=msg)

    def set_status(self, text, color="white"):
        try:
            color_map = {"lightgreen": "green", "tomato": "red", "white": "gray"}
            circle = color_map.get(color, color)
            self._draw_status_circle(circle)
            self.status_label.config(text=text, fg="white")
        except:
            pass

    def _build_menu(self):
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self._show_about)
        help_menu.add_command(label="Help", command=self._show_help)
        menubar.add_cascade(label="Help", menu=help_menu)

        try:
            self.root.config(menu=menubar)
        except:
            pass

    def _show_about(self):
        messagebox.showinfo("About Biz Analyst", "Biz Analyst v5.6\nOptimized Tally Sync Tool\n\n© Internal")

    def _show_help(self):
        help_text = """BIZ ANALYST v5.6 - Quick Start Guide

1. SETUP:
   • Click "🔍 Auto Detect" to find Tally DSN
   • Or enter DSN manually

2. LOAD COMPANIES:
   • Click "📥 Load Companies"
   • Synced companies automatically hidden
   • Select from "Available Companies"

3. CONFIGURE SYNC:
   • Set Date Range (DD-MM-YYYY)
   • Adjust Batch Size if needed
   • Enable "Slice by Days" for large ranges

4. SYNC:
   • Click "⚙️ Sync Settings"
   • Monitor progress (10%, 20%, 50%, 100%)
   • Check Sync Log for details

5. AFTER SYNC:
   • Company moves to "Synced Companies" list
   • Auto-hidden from "Available Companies"
   • Add notes per company

Keyboard Shortcuts:
  Ctrl+R = Refresh
  Ctrl+L = Load Companies
  Ctrl+S = Sync Settings
"""
        messagebox.showinfo("Help", help_text)

    def _draw_status_circle(self, color):
        try:
            self.status_canvas.delete("all")
            self.status_canvas.create_oval(2, 2, 14, 14, fill=color, outline=color)
        except:
            pass

    def auto_detect_dsn(self, silent: bool = False):
        self.log("🔍 Detecting DSN...")
        candidates = [f"{DSN_PREFIX}{p}" for p in COMMON_PORTS]
        found = False
        for d in candidates:
            ok, err = try_connect_dsn(d)
            if ok:
                self.dsn_var.set(d)
                self.set_status(f"Connected: {d}", "lightgreen")
                self.log(f"✓ Detected DSN: {d}")
                found = True
                break
        if not found:
            self.set_status("DSN not found", "tomato")
            self.log("✗ Could not detect DSN")
            if not silent:
                messagebox.showerror("Tally Connection Error", "⚠️ Could not detect Tally DSN.\n\nPlease ensure:\n1. Tally is running\n2. Tally ODBC is configured\n3. Try entering DSN manually")

    def load_companies(self):
        dsn = self.dsn_var.get().strip()
        if not dsn:
            messagebox.showwarning("DSN Required", "Enter or detect DSN first")
            return
        now = time.time()
        if now - self._last_load_time < 5:
            self.log("Load companies called too recently — skipping repeat call")
            return
        self._last_load_time = now
        self.btn_load.config(state=tk.DISABLED)
        try:
            self.log(f"📥 Loading companies from DSN: {dsn} ...")
            try:
                conn = pyodbc.connect(f"DSN={dsn};", timeout=10)
            except Exception as conn_error:
                error_msg = get_user_friendly_error(str(conn_error))
                self.log(f"✗ Connection error: {conn_error}")
                messagebox.showerror("Tally Connection Error", error_msg)
                return
            cur = conn.cursor()
            cur.execute(TALLY_COMPANY_QUERY)
            companies = cur.fetchall()
            cur.close()
            conn.close()
            
            # Get company statuses using CompanyDAO
            try:
                local_status = self.company_dao.get_all_status()
            except Exception:
                local_status = {}

            self.avail_listbox.delete(0, tk.END)
            self.company_map.clear()
            skipped_counts = {"synced": 0, "syncing": 0, "incomplete": 0}
            for row in companies:
                try:
                    name, guid, alter = row[0], row[1], row[2]
                except Exception:
                    name = row[0] if len(row) > 0 else "Unknown"
                    guid = row[1] if len(row) > 1 else None
                    alter = row[2] if len(row) > 2 else None
                alter_str = str(alter) if alter is not None else "None"
                guid_str = str(guid) if guid is not None else None

                local_key = (guid_str, alter_str)
                st = local_status.get(local_key)
                if st in ('synced', 'syncing', 'incomplete'):
                    if st in skipped_counts:
                        skipped_counts[st] += 1
                    else:
                        skipped_counts['synced'] += 1
                    continue

                display = f"{name} | AlterID: {alter_str}"
                self.avail_listbox.insert(tk.END, display)
                self.company_map[name] = {"guid": guid_str, "alterid": alter_str}
            
            # Update available count
            avail_count = self.avail_listbox.size()
            try:
                self.avail_count_label.config(text=f"{avail_count} available")
            except:
                pass
            
            self.log(f"✓ Loaded {len(companies)} companies from Tally")
            total_skipped = sum(skipped_counts.values())
            if total_skipped:
                msg = f"Skipped {total_skipped}: synced={skipped_counts['synced']}, syncing={skipped_counts['syncing']}, incomplete={skipped_counts['incomplete']}"
                self.log(f"⚑ {msg}")
                try:
                    self.avail_skipped_label.config(text=msg)
                except:
                    pass
            else:
                try:
                    self.avail_skipped_label.config(text="")
                except:
                    pass
        except Exception as e:
            error_msg = get_user_friendly_error(str(e))
            self.log(f"✗ Error loading companies: {e}")
            messagebox.showerror("Tally Connection Error", error_msg)
        finally:
            self.btn_load.config(state=tk.NORMAL)

    def sync_selected(self):
        sel = self.avail_listbox.curselection()
        if not sel:
            messagebox.showwarning("Select", "Choose a company to sync")
            return
        raw = self.avail_listbox.get(sel[0])
        name = raw.split(" | ")[0].strip()
        meta = self.company_map.get(name)
        if not meta:
            messagebox.showerror("Error", "Company metadata missing")
            return
        guid = meta["guid"]
        alterid = meta["alterid"]
        dsn = self.dsn_var.get().strip()
        from_date = self.from_var.get().strip()
        to_date = self.to_var.get().strip()
        
        # Phase 5: Validate inputs
        if not dsn:
            messagebox.showwarning("DSN Required", "Enter or detect DSN first")
            return
        
        # Validate DSN
        is_valid, error = CompanyValidator.validate_dsn(dsn)
        if not is_valid:
            messagebox.showerror("Invalid DSN", f"DSN validation failed: {error}")
            return
        
        # Validate sync parameters
        try:
            is_valid, error = validate_sync_params(guid, alterid, from_date, to_date)
            if not is_valid:
                messagebox.showerror("Validation Error", f"Sync parameters invalid: {error}")
                return
        except ValidationError as ve:
            from backend.utils.error_handler import handle_validation_error
            error_msg = handle_validation_error(ve)
            messagebox.showerror("Validation Error", error_msg)
            return
        
        key = f"{guid}|{alterid}"

        lock = self.sync_locks.setdefault(key, threading.Lock())
        acquired = lock.acquire(blocking=False)
        if not acquired:
            messagebox.showinfo("Sync", "Sync already running for this company")
            return

        # Use CompanyDAO for insert/update
        # CRITICAL: Convert alterid to string to ensure proper matching
        alterid_str = str(alterid) if alterid is not None else ""
        self.company_dao.insert_or_update(name, guid, alterid_str, dsn, 'syncing')
        
        # Show and reset progress indicators
        self._update_progress(0)
        
        # Remove from available list (optimistic UI)
        self.avail_listbox.delete(sel[0])
        avail_count = self.avail_listbox.size()
        try:
            self.avail_count_label.config(text=f"{avail_count} available")
        except:
            pass
        
        t = threading.Thread(target=self._sync_worker, args=(name, guid, alterid_str, dsn, from_date, to_date, lock), daemon=True)
        self.sync_threads[key] = t
        self.btn_sync.config(state=tk.DISABLED)
        t.start()
        self.log(f"▶️ Started sync thread for {name}")

    def _sync_worker(self, name, guid, alterid, dsn, from_date, to_date, lock):
        """OPTIMIZED: No COUNT, simulated progress, PRAGMA optimizations"""
        key = f"{guid}|{alterid}"
        approx_inserted = 0
        stage_reported = set()
        batch_count = 0
        estimated_batches = 0  # We'll estimate based on date range
        
        # Initialize sync logger (with error handling to prevent hang)
        # Use None for db_lock to allow logger to use its own connection without lock conflicts
        # Logger has its own connection and WAL mode, so it can write independently
        sync_logger = None
        try:
            # Don't pass db_lock - logger will use its own connection with WAL mode
            # This allows logging even when main sync is holding locks
            sync_logger = get_sync_logger(db_path=DB_FILE, db_lock=None)
            print(f"[DEBUG] Sync logger initialized successfully (independent connection)")
        except Exception as logger_err:
            print(f"[WARNING] Failed to initialize sync logger: {logger_err}")
            import traceback
            traceback.print_exc()
            sync_logger = None
        
        sync_start_time = time.time()
        
        # Log sync start (non-blocking, after connection to avoid blocking)
        # CRITICAL: Convert alterid to string for logging
        alterid_str_log = str(alterid) if alterid is not None else ""
        if sync_logger:
            try:
                print(f"[DEBUG] Attempting to log sync start: {name}, GUID: {guid}, AlterID: {alterid_str_log}")
                log_id = sync_logger.sync_started(guid, alterid_str_log, name, details=f"Date range: {from_date} to {to_date}")
                print(f"[DEBUG] Sync start logged successfully, Log ID: {log_id}")
            except Exception as log_err:
                print(f"[WARNING] Failed to log sync start: {log_err}")
                import traceback
                traceback.print_exc()
        else:
            print(f"[WARNING] Sync logger is None - cannot log sync start")
        
        try:
            try:
                self.log(f"[{name}] 🔌 Connecting to Tally...")
                # Increase connection timeout for large queries
                conn = pyodbc.connect(f"DSN={dsn};", timeout=60)
                self.log(f"[{name}] ✅ Connected to Tally successfully")
            except Exception as conn_error:
                error_msg = get_user_friendly_error(str(conn_error))
                self.log(f"❌ Connection error for {name}: {conn_error}")
                messagebox.showerror("Tally Connection Error", f"Cannot connect to Tally for {name}:\n\n{error_msg}")
                raise
            cur = conn.cursor()
            self.log(f"[{name}] ✅ Cursor created, ready to execute queries")

            try:
                batch_size = int(self.batch_size_var.get())
                if batch_size < 50:
                    batch_size = 50
            except Exception:
                batch_size = BATCH_SIZE

            try:
                use_slicing = bool(self.slice_var.get())
                slice_days = int(self.slice_days_var.get()) if self.slice_days_var.get() else 7
                if slice_days < 1:
                    slice_days = 1
            except Exception:
                use_slicing = False
                slice_days = 7
            
            # Auto-enable slicing for large date ranges (>365 days) to prevent hangs
            try:
                from_dt = datetime.strptime(from_date, "%d-%m-%Y")
                to_dt = datetime.strptime(to_date, "%d-%m-%Y")
                # Calculate total days: (end_date - start_date).days + 1
                # +1 because we include both start and end dates
                # Example: 01-01-2024 to 03-01-2024 = 3 days (01, 02, 03)
                total_days = (to_dt - from_dt).days + 1
                if total_days > 365 and not use_slicing:
                    self.log(f"[{name}] ⚠️ Large date range detected ({total_days} days from {from_date} to {to_date}). Auto-enabling date slicing to prevent hangs...")
                    use_slicing = True
                    # Optimize slice size based on range (based on performance test results):
                    # - >2 years: Use financial year slices (365 days) - Best for large ranges
                    # - 1-2 years: Use monthly slices (30 days) - Best progress tracking
                    # - <1 year: Use 30-day slices
                    if total_days > 730:  # More than 2 years
                        slice_days = 365  # Financial year slices (fastest per query)
                        self.log(f"[{name}] 📅 Using financial year slices (365 days) for optimal performance")
                    elif total_days > 365:  # 1-2 years
                        slice_days = 30  # Monthly slices (best progress)
                        self.log(f"[{name}] 📅 Using monthly slices (30 days) for better progress tracking")
                    else:
                        slice_days = min(30, max(7, total_days // 12))  # Divide into ~12 chunks
                        self.log(f"[{name}] 📅 Using {slice_days}-day slices for faster sync")
            except Exception as e:
                self.log(f"[{name}] ⚠️ Error calculating date range: {e}")
                pass  # If date parsing fails, continue with original settings

            def _execute_window(f_d, t_d):
                nonlocal approx_inserted, batch_count, estimated_batches
                
                # Calculate date range in days
                try:
                    from_dt = datetime.strptime(f_d, "%d-%m-%Y")
                    to_dt = datetime.strptime(t_d, "%d-%m-%Y")
                    days_diff = (to_dt - from_dt).days + 1
                except:
                    days_diff = 0
                
                q = VOUCHER_QUERY_TEMPLATE.format(guid=guid, from_date=f_d, to_date=t_d)
                self.log(f"[{name}] 📤 Query: {f_d} → {t_d} ({days_diff} days)")
                
                # Warn if date range is very large
                if days_diff > 365:
                    self.log(f"[{name}] ⚠️ WARNING: Large date range ({days_diff} days). This may take 2-5 minutes. Consider using 'Slice by Days' for faster sync.")
                
                self.log(f"[{name}] ⏳ Executing query... (Please wait, Tally is processing data)")
                
                query_start_time = time.time()
                last_log_time = query_start_time
                try:
                    # Execute query - this may take time for large date ranges
                    # Note: We can't add timeout here as pyodbc doesn't support query timeout
                    # The query will complete when Tally finishes processing
                    cur.execute(q)
                    query_duration = time.time() - query_start_time
                    self.log(f"[{name}] ✅ Query executed in {query_duration:.1f} seconds, fetching results...")
                except Exception as exq:
                    error_msg = str(exq)
                    query_duration = time.time() - query_start_time
                    self.log(f"[{name}] ❌ Query error after {query_duration:.1f} seconds: {error_msg}")
                    # Log error to sync logger if available
                    if sync_logger:
                        try:
                            sync_logger.error(guid, alterid_str_log, name, 
                                            f"Query execution failed for date range {f_d} to {t_d}: {error_msg}",
                                            error_code="QUERY_ERROR",
                                            error_message=error_msg)
                        except:
                            pass
                    # Re-raise to be caught by outer exception handler
                    raise Exception(f"Query execution failed: {error_msg}")

                batch_no = 0
                fetch_start_time = time.time()
                self.log(f"[{name}] 📥 Starting to fetch results in batches of {batch_size}...")
                self.log(f"[{name}] ⚠️ NOTE: First batch fetch may take 2-5 minutes for large queries. Please wait...")
                
                # Use smaller batch size for first fetch to reduce initial wait time
                first_batch_size = min(50, batch_size)
                
                while True:
                    # Add timeout protection and progress logging for fetchmany
                    fetch_batch_start = time.time()
                    current_batch_size = first_batch_size if batch_no == 0 else batch_size
                    
                    try:
                        if batch_no == 0:
                            self.log(f"[{name}] ⏳ Fetching first batch ({current_batch_size} rows)...")
                            self.log(f"[{name}] ⚠️ IMPORTANT: First fetch may take 2-5 minutes for large queries. Tally is processing data. Please DO NOT close the app.")
                        else:
                            self.log(f"[{name}] ⏳ Fetching batch {batch_no + 1} ({current_batch_size} rows)...")
                        
                        # Note: fetchmany() is blocking - we cannot interrupt it
                        # Tally will return results when ready, which may take several minutes
                        rows = cur.fetchmany(current_batch_size)
                        fetch_duration = time.time() - fetch_batch_start
                        
                        if not rows:
                            total_fetch_time = time.time() - fetch_start_time
                            self.log(f"[{name}] ✅ Finished fetching all results in {total_fetch_time:.1f} seconds")
                            break
                        
                        self.log(f"[{name}] ✅ Fetched batch {batch_no + 1}: {len(rows)} rows (took {fetch_duration:.1f}s)")
                    except Exception as fetch_err:
                        fetch_duration = time.time() - fetch_batch_start
                        error_msg = str(fetch_err)
                        self.log(f"[{name}] ❌ Error fetching batch {batch_no + 1} after {fetch_duration:.1f}s: {error_msg}")
                        if sync_logger:
                            try:
                                sync_logger.error(guid, alterid_str_log, name,
                                                f"Error fetching batch {batch_no + 1}: {error_msg}",
                                                error_code="FETCH_ERROR",
                                                error_message=error_msg)
                            except:
                                pass
                        raise Exception(f"Failed to fetch batch {batch_no + 1}: {error_msg}")
                    
                    batch_no += 1
                    batch_count += 1
                    params = []
                    
                    # FIXED: params list built inside row loop
                    # CRITICAL: Filter rows to only include those matching the target AlterID
                    # Tally query returns vouchers for ALL AlterIDs with the same GUID
                    # We need to only process rows where the AlterID from Tally matches our target
                    alterid_str_target = str(alterid) if alterid is not None else ""
                    for r in rows:
                        try:
                            # Extract AlterID from Tally result (column index 2: $OnwerAlterID)
                            tally_alterid = r[2] if len(r) > 2 else None
                            tally_alterid_str = str(tally_alterid) if tally_alterid is not None else ""
                            
                            # Skip rows that don't match our target AlterID
                            if tally_alterid_str != alterid_str_target:
                                continue  # Skip this row - it belongs to a different AlterID
                            
                            # Extract date - handle None, empty string, and format conversion
                            vch_date_raw = r[3] if len(r) > 3 else None
                            if vch_date_raw is None or vch_date_raw == '':
                                vch_date = None
                            else:
                                # Convert to string and ensure proper format
                                vch_date = str(vch_date_raw).strip()
                                if vch_date == '' or vch_date.lower() == 'none':
                                    vch_date = None
                            
                            # Debug first row date extraction
                            if batch_count == 1 and len(params) == 0:
                                print(f"[DEBUG] First row date extraction: raw={repr(vch_date_raw)}, final={repr(vch_date)}, row_len={len(r)}")
                            vch_type = str(r[4]) if len(r) > 4 else None
                            vch_no = str(r[5]) if len(r) > 5 else None
                            led_name = str(r[6]) if len(r) > 6 else None
                            led_amount = float(r[7]) if len(r) > 7 and r[7] is not None else None
                            vch_dr_cr = str(r[8]) if len(r) > 8 else None
                            vch_dr_amt = float(r[9]) if len(r) > 9 and r[9] is not None else None
                            vch_cr_amt = float(r[10]) if len(r) > 10 and r[10] is not None else None
                            vch_party_name = str(r[11]) if len(r) > 11 else None
                            vch_led_parent = str(r[12]) if len(r) > 12 else None
                            vch_narration = str(r[13]) if len(r) > 13 else None
                            vch_gstin = str(r[14]) if len(r) > 14 else None
                            vch_led_gstin = str(r[15]) if len(r) > 15 else None
                            vch_led_bill_ref = str(r[16]) if len(r) > 16 else None
                            vch_led_bill_type = str(r[17]) if len(r) > 17 else None
                            vch_led_primary_grp = str(r[18]) if len(r) > 18 else None
                            vch_led_nature = str(r[19]) if len(r) > 19 else None
                            vch_led_bs_grp = str(r[20]) if len(r) > 20 else None
                            vch_led_bs_grp_nature = str(r[21]) if len(r) > 21 else None
                            vch_is_optional = str(r[22]) if len(r) > 22 else None
                            vch_mst_id = str(r[23]) if len(r) > 23 else None
                            vch_led_bill_count = int(r[24]) if len(r) > 24 and r[24] is not None else 0
                        except Exception as ex_row:
                            self.log(f"[{name}] Row parse error: {ex_row}")
                            continue

                        # CRITICAL: Convert alterid to string for consistent storage
                        alterid_str_insert = str(alterid) if alterid is not None else ""
                        params.append((
                            guid, alterid_str_insert, name, vch_date, vch_type, vch_no, vch_mst_id,
                            led_name, led_amount, vch_dr_cr, vch_dr_amt, vch_cr_amt, vch_party_name, vch_led_parent,
                            vch_narration, vch_gstin, vch_led_gstin, vch_led_bill_ref, vch_led_bill_type,
                            vch_led_primary_grp, vch_led_nature, vch_led_bs_grp, vch_led_bs_grp_nature,
                            vch_is_optional, vch_led_bill_count
                        ))
                    
                    # OPTIMIZED: SQLite bulk insert with PRAGMA settings
                    # CRITICAL: Keep lock time minimal to prevent UI freeze
                    if params:
                        insert_start = time.time()
                        print(f"[DEBUG] Preparing to insert batch {batch_count}: {len(params)} rows, AlterID={alterid_str_insert}")
                        
                        # DEBUG: Check first param to verify AlterID format
                        if params and batch_count == 1:
                            first_param = params[0]
                            print(f"[DEBUG] First param AlterID: {repr(first_param[1])} (type: {type(first_param[1]).__name__})")
                            print(f"[DEBUG] First param GUID: {repr(first_param[0])}")
                            print(f"[DEBUG] First param vch_mst_id: {repr(first_param[6])}")
                            print(f"[DEBUG] First param led_name: {repr(first_param[7])}")
                        
                        try:
                            # Acquire lock with timeout to prevent deadlock
                            lock_acquired = False
                            try:
                                lock_acquired = self.db_lock.acquire(timeout=1.0)  # 1 second timeout
                                if not lock_acquired:
                                    self.log(f"[{name}] ⚠️ Database lock timeout, retrying...")
                                    time.sleep(0.1)
                                    lock_acquired = self.db_lock.acquire(timeout=5.0)  # Retry with longer timeout
                                
                                if lock_acquired:
                                    db_cur = self.db_conn.cursor()
                                    
                                    # CRITICAL: PRAGMA commands must be executed BEFORE starting a transaction
                                    # SQLite doesn't allow PRAGMA changes inside a transaction
                                    # Apply PRAGMA settings only once, before any inserts, and commit first
                                    if batch_no == 1:
                                        # Commit any existing transaction first to ensure we're outside a transaction
                                        self.db_conn.commit()
                                        # Now apply PRAGMA settings (outside transaction)
                                        db_cur.execute("PRAGMA synchronous = NORMAL")  # Changed from OFF to NORMAL for stability
                                        db_cur.execute("PRAGMA temp_store = MEMORY")
                                        db_cur.execute("PRAGMA cache_size = 10000")
                                        # Removed WAL mode - can cause issues on some systems
                                        # Commit PRAGMA changes (though PRAGMA changes are immediate, this ensures clean state)
                                        self.db_conn.commit()
                                        print(f"[DEBUG] PRAGMA settings applied for batch 1 (outside transaction)")
                                    
                                    # Use INSERT OR REPLACE to handle duplicates
                                    # This ensures vouchers are inserted even if there are duplicates
                                    try:
                                        print(f"[DEBUG] Executing INSERT for {len(params)} rows...")
                                        # Use INSERT with error handling instead of INSERT OR IGNORE
                                        # INSERT OR IGNORE silently ignores ALL duplicates, which can hide issues
                                        # UNIQUE constraint: (company_guid, company_alterid, vch_mst_id, led_name)
                                        try:
                                            db_cur.executemany("""
                                            INSERT INTO vouchers
                                        (company_guid, company_alterid, company_name, vch_date, vch_type, vch_no, vch_mst_id,
                                         led_name, led_amount, vch_dr_cr, vch_dr_amt, vch_cr_amt, vch_party_name, vch_led_parent,
                                         vch_narration, vch_gstin, vch_led_gstin, vch_led_bill_ref, vch_led_bill_type,
                                         vch_led_primary_grp, vch_led_nature, vch_led_bs_grp, vch_led_bs_grp_nature,
                                         vch_is_optional, vch_led_bill_count)
                                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                        """, params)
                                        except sqlite3.IntegrityError as integrity_err:
                                            # UNIQUE constraint violation - some rows are duplicates
                                            # SQLite's INSERT OR REPLACE only works with PRIMARY KEY, not UNIQUE constraints
                                            # So we need to use INSERT OR IGNORE, but this means duplicates are silently ignored
                                            # For now, we'll use INSERT OR IGNORE and log a warning
                                            print(f"[WARNING] Integrity error (duplicates): {integrity_err}")
                                            print(f"[DEBUG] Using INSERT OR IGNORE for {len(params)} rows (duplicates will be ignored)...")
                                            db_cur.executemany("""
                                            INSERT OR IGNORE INTO vouchers
                                            (company_guid, company_alterid, company_name, vch_date, vch_type, vch_no, vch_mst_id,
                                             led_name, led_amount, vch_dr_cr, vch_dr_amt, vch_cr_amt, vch_party_name, vch_led_parent,
                                             vch_narration, vch_gstin, vch_led_gstin, vch_led_bill_ref, vch_led_bill_type,
                                             vch_led_primary_grp, vch_led_nature, vch_led_bs_grp, vch_led_bs_grp_nature,
                                             vch_is_optional, vch_led_bill_count)
                                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                            """, params)
                                        
                                        print(f"[DEBUG] INSERT executed, committing...")
                                        # Commit every batch
                                        self.db_conn.commit()
                                        rows_inserted = len(params)
                                        print(f"[DEBUG] Committed {rows_inserted} rows")
                                        
                                        # Debug: Verify inserts for first batch
                                        if batch_count == 1:
                                            # Force commit and verify with fresh cursor
                                            # CRITICAL: Use a NEW connection to verify, not the same one
                                            # This ensures we're reading from disk, not from uncommitted transaction cache
                                            # Use the same database path as the main connection (self.db_conn)
                                            # CRITICAL: We need the absolute path to the actual database file
                                            # Method 1: Try PRAGMA database_list first
                                            import os
                                            from backend.config.settings import DB_FILE
                                            main_db_path = None
                                            
                                            try:
                                                verify_cur_temp = self.db_conn.cursor()
                                                verify_cur_temp.execute("PRAGMA database_list")
                                                db_list = verify_cur_temp.fetchall()
                                                verify_cur_temp.close()
                                                
                                                # PRAGMA database_list returns: (seq, name, file)
                                                # The main database is usually the first one with name='main'
                                                for db_entry in db_list:
                                                    if len(db_entry) >= 3 and db_entry[1] == 'main':
                                                        db_file = db_entry[2]
                                                        # If PRAGMA returns a path, make it absolute
                                                        if db_file and db_file != '':
                                                            # If it's already absolute, use it; otherwise resolve it
                                                            if os.path.isabs(db_file):
                                                                main_db_path = db_file
                                                            else:
                                                                # Relative path - resolve from current working directory
                                                                main_db_path = os.path.abspath(db_file)
                                                            break
                                            except Exception as pragma_err:
                                                print(f"[DEBUG] PRAGMA database_list failed: {pragma_err}")
                                            
                                            # Fallback: Use DB_FILE from project root (same as init_db uses)
                                            if not main_db_path or main_db_path == '' or not os.path.exists(main_db_path):
                                                # Get project root (where main.py is located)
                                                # This file is in backend/app.py, so go up two levels
                                                current_file = os.path.abspath(__file__)
                                                project_root = os.path.dirname(os.path.dirname(current_file))
                                                main_db_path = os.path.join(project_root, DB_FILE)
                                                # Ensure it's absolute
                                                main_db_path = os.path.abspath(main_db_path)
                                            
                                            verify_conn = sqlite3.connect(main_db_path, check_same_thread=False)
                                            verify_cur = verify_conn.cursor()
                                            print(f"[DEBUG] Verification using database: {main_db_path}")
                                            print(f"[DEBUG] Database file exists: {os.path.exists(main_db_path)}")
                                            print(f"[DEBUG] Database file size: {os.path.getsize(main_db_path) if os.path.exists(main_db_path) else 0} bytes")
                                            
                                            # Try multiple query formats to find the issue
                                            print(f"[DEBUG] Verifying insert with AlterID: '{alterid_str_insert}' (type: {type(alterid_str_insert).__name__})")
                                            
                                            # Query 1: Exact match
                                            verify_cur.execute("SELECT COUNT(*) FROM vouchers WHERE company_guid=? AND company_alterid=?", 
                                                              (guid, alterid_str_insert))
                                            verify_count = verify_cur.fetchone()[0]
                                            
                                            # Query 2: Cast to string
                                            verify_cur.execute("SELECT COUNT(*) FROM vouchers WHERE company_guid=? AND CAST(company_alterid AS TEXT)=?", 
                                                              (guid, alterid_str_insert))
                                            verify_count2 = verify_cur.fetchone()[0]
                                            
                                            # Query 3: Total for this GUID
                                            verify_cur.execute("SELECT COUNT(*) FROM vouchers WHERE company_guid=?", (guid,))
                                            total_for_guid = verify_cur.fetchone()[0]
                                            
                                            # Query 4: Check what AlterIDs actually exist for this GUID
                                            verify_cur.execute("SELECT DISTINCT company_alterid, COUNT(*) FROM vouchers WHERE company_guid=? GROUP BY company_alterid", (guid,))
                                            existing_alterids = verify_cur.fetchall()
                                            
                                            print(f"[DEBUG] ✅ After batch 1: Inserted {rows_inserted} rows")
                                            print(f"[DEBUG]   Query 1 (exact): {verify_count} vouchers for AlterID '{alterid_str_insert}'")
                                            print(f"[DEBUG]   Query 2 (CAST): {verify_count2} vouchers for AlterID '{alterid_str_insert}'")
                                            print(f"[DEBUG]   Total vouchers for GUID: {total_for_guid}")
                                            print(f"[DEBUG]   Existing AlterIDs for this GUID:")
                                            for alt_id, cnt in existing_alterids:
                                                print(f"      - AlterID '{alt_id}' (type: {type(alt_id).__name__}): {cnt} vouchers")
                                                if str(alt_id) == alterid_str_insert:
                                                    print(f"        ✅ MATCHES inserted AlterID!")
                                                else:
                                                    print(f"        ❌ Does NOT match inserted AlterID '{alterid_str_insert}'")
                                            
                                            if verify_count == 0 and verify_count2 == 0:
                                                print(f"[ERROR] ❌ CRITICAL: No vouchers found after insert! GUID={guid}, AlterID={alterid_str_insert}")
                                                # Check what's in the first param
                                                if params:
                                                    first_param = params[0]
                                                    print(f"[DEBUG] First param: GUID={first_param[0]}, AlterID={first_param[1]} (type: {type(first_param[1]).__name__})")
                                                # Check all AlterIDs in database
                                                verify_cur.execute("SELECT DISTINCT company_alterid, COUNT(*) FROM vouchers WHERE company_guid=? GROUP BY company_alterid", (guid,))
                                                all_alterids = verify_cur.fetchall()
                                                print(f"[DEBUG] All AlterIDs in DB for this GUID:")
                                                for a in all_alterids:
                                                    print(f"  - '{a[0]}' (type: {type(a[0]).__name__}, repr: {repr(a[0])}) | Count: {a[1]}")
                                            verify_cur.close()
                                            verify_conn.close()
                                    except Exception as insert_err:
                                        print(f"[ERROR] ❌ Voucher insert failed: {insert_err}")
                                        import traceback
                                        traceback.print_exc()
                                        raise
                                    approx_inserted += rows_inserted
                                else:
                                    raise Exception("Failed to acquire database lock")
                            finally:
                                if lock_acquired:
                                    self.db_lock.release()
                            
                            insert_duration = time.time() - insert_start
                            
                            # Log insertion progress (non-blocking)
                            if batch_count % 10 == 0 or batch_count == 1:
                                self.log(f"[{name}] 💾 Inserted batch {batch_count}: {rows_inserted} rows in {insert_duration:.2f}s (Total: {approx_inserted:,})")
                            
                            if sync_logger and (batch_count % 10 == 0 or batch_count == 1):
                                try:
                                    sync_logger.sync_progress(
                                        guid, alterid_str_log, name, 
                                        records_synced=approx_inserted,
                                        message=f"Batch {batch_count}: {rows_inserted} vouchers inserted",
                                        details=f"Total inserted so far: {approx_inserted} vouchers"
                                    )
                                except Exception as log_err:
                                    print(f"[WARNING] Failed to log progress: {log_err}")
                        except Exception as insert_err:
                            insert_duration = time.time() - insert_start
                            self.log(f"[{name}] ❌ Database insert error after {insert_duration:.2f}s: {insert_err}")
                            # Don't raise - continue with next batch to prevent complete failure
                            self.log(f"[{name}] ⚠️ Skipping batch {batch_count} due to insert error, continuing...")

                    # SIMULATED PROGRESS (no COUNT needed)
                    estimated_batches = max(estimated_batches, batch_count + 5)
                    progress_pct = int((batch_count / max(estimated_batches, 1)) * 100)
                    progress_pct = min(progress_pct, 99)
                    self._update_progress(progress_pct)
                    
                    # Staged logging
                    for threshold in (10, 20, 50, 100):
                        if progress_pct >= threshold and threshold not in stage_reported:
                            self.log(f"[{name}] ⏳ Progress: {threshold}%")
                            stage_reported.add(threshold)

                    try:
                        self.batch_info_label.config(text=f"Batch {batch_count}: {len(params)} rows | Total: {approx_inserted}")
                    except Exception:
                        pass

                    self.log(f"[{name}] Batch {batch_no}: {len(params)} rows (≈{approx_inserted} total)")
                    
                    # CRITICAL: Allow UI to update and prevent "Not Responding"
                    # Small sleep allows other threads (including UI) to run
                    time.sleep(0.05)  # Increased from 0.01 to 0.05 for better UI responsiveness
                    
                    # Force UI update to prevent "Not Responding" status
                    try:
                        self.root.update_idletasks()  # Process pending UI events
                    except:
                        pass  # Ignore if root is destroyed

            # Process date windows
            if use_slicing:
                try:
                    from_dt = datetime.strptime(from_date, "%d-%m-%Y")
                except Exception:
                    try:
                        from_dt = datetime.strptime(from_date, "%Y-%m-%d")
                    except Exception:
                        from_dt = None
                try:
                    to_dt = datetime.strptime(to_date, "%d-%m-%Y")
                except Exception:
                    try:
                        to_dt = datetime.strptime(to_date, "%Y-%m-%d")
                    except Exception:
                        to_dt = None

                if from_dt and to_dt and from_dt <= to_dt:
                    cur_start = from_dt
                    while cur_start <= to_dt:
                        cur_end = cur_start + timedelta(days=slice_days - 1)
                        if cur_end > to_dt:
                            cur_end = to_dt
                        f_d = cur_start.strftime("%d-%m-%Y")
                        t_d = cur_end.strftime("%d-%m-%Y")
                        try:
                            _execute_window(f_d, t_d)
                        except Exception as window_err:
                            # If one window fails, log and continue to next window
                            self.log(f"[{name}] ⚠️ Window {f_d} to {t_d} failed: {window_err}")
                            if sync_logger:
                                try:
                                    sync_logger.warning(guid, alterid_str_log, name,
                                                       f"Date window sync failed: {f_d} to {t_d}",
                                                       details=str(window_err),
                                                       sync_status='in_progress')
                                except:
                                    pass
                            # Continue to next window instead of failing entire sync
                        cur_start = cur_end + timedelta(days=1)
                else:
                    _execute_window(from_date, to_date)
            else:
                _execute_window(from_date, to_date)

            try:
                cur.close()
                conn.close()
            except:
                pass

            # Restore PRAGMA and update company status using CompanyDAO
            with self.db_lock:
                db_cur = self.db_conn.cursor()
                db_cur.execute("PRAGMA synchronous = FULL")
            
            # Verify actual vouchers inserted
            # CRITICAL: Use string alterid for verification to match insert format
            alterid_str_verify = str(alterid) if alterid is not None else ""
            db_cur.execute("SELECT COUNT(*) as count FROM vouchers WHERE company_guid = ? AND company_alterid = ?", 
                         (guid, alterid_str_verify))
            actual_vouchers = db_cur.fetchone()[0]
            
            # Log voucher count verification (non-blocking)
            if sync_logger:
                try:
                    if actual_vouchers != approx_inserted:
                        sync_logger.warning(
                            guid, alterid_str_log, name,
                            f"Voucher count mismatch: Expected {approx_inserted}, Actual in DB: {actual_vouchers}",
                            details=f"Sync reported {approx_inserted} vouchers but database has {actual_vouchers} vouchers",
                            sync_status='completed'
                        )
                    else:
                        sync_logger.info(
                            guid, alterid_str_log, name,
                            f"Voucher insertion verified: {actual_vouchers} vouchers in database",
                            details=f"All {approx_inserted} vouchers successfully inserted",
                            sync_status='completed'
                        )
                except Exception as log_err:
                    print(f"[WARNING] Failed to log verification: {log_err}")
            
            # Update company status with logger
            # CRITICAL: Convert alterid to string to ensure proper matching
            alterid_str = str(alterid) if alterid is not None else ""
            self.log(f"[{name}] 💾 Updating company in database: GUID={guid}, AlterID={alterid_str}, Records={actual_vouchers}")
            try:
                self.company_dao.update_sync_complete(guid, alterid_str, actual_vouchers, name, logger=sync_logger)
                self.log(f"[{name}] ✅ Company updated in database successfully")
            except Exception as update_err:
                self.log(f"[{name}] ❌ Error updating company in database: {update_err}")
                # Try to insert manually if update failed
                try:
                    self.company_dao.insert_or_update(name, guid, alterid_str, self.dsn_var.get().strip(), 'synced')
                    self.log(f"[{name}] ✅ Company inserted manually")
                except Exception as insert_err:
                    self.log(f"[{name}] ❌ Error inserting company: {insert_err}")
            
            # Calculate duration
            sync_duration = time.time() - sync_start_time
            
            # Log sync completion (non-blocking)
            if sync_logger:
                try:
                    print(f"[DEBUG] Attempting to log sync completion: {name}, Records: {actual_vouchers}, Duration: {sync_duration:.2f}s")
                    log_id = sync_logger.sync_completed(
                        guid, alterid_str_log, name,
                        records_synced=actual_vouchers,
                        duration_seconds=sync_duration,
                        details=f"Sync completed in {batch_count} batches. Duration: {sync_duration:.2f} seconds"
                    )
                    print(f"[DEBUG] Sync completion logged successfully, Log ID: {log_id}")
                except Exception as log_err:
                    print(f"[WARNING] Failed to log completion: {log_err}")
                    import traceback
                    traceback.print_exc()
            else:
                print(f"[WARNING] Sync logger is None - cannot log sync completion")

            self._update_progress(100)
            
            # Phase 1: Critical Fixes - Create backup after successful sync
            try:
                from backend.utils.backup import backup_database
                success, message = backup_database(DB_FILE)
                if success:
                    self.log(f"[{name}] 💾 {message}")
                else:
                    self.log(f"[{name}] ⚠️ Backup warning: {message}")
            except Exception as backup_err:
                self.log(f"[{name}] ⚠️ Backup failed (non-critical): {backup_err}")
            
            # Only show COMPLETE if batches were actually processed
            if batch_count > 0:
                self.log(f"✅ COMPLETE: {name} | {actual_vouchers} vouchers synced in {batch_count} batches!")
            else:
                self.log(f"⚠️ WARNING: {name} | Sync completed but no batches were processed (0 vouchers)")
                if sync_logger:
                    try:
                        sync_logger.warning(guid, alterid_str_log, name,
                                          "Sync completed with 0 batches - no data was synced",
                                          details="Check query execution and date range",
                                          sync_status='completed')
                    except:
                        pass
            # Phase 4: Invalidate cache after sync completes
            try:
                from backend.utils.cache import get_cache
                cache = get_cache()
                # Invalidate company list cache
                cache.delete_pattern("companies_all_synced")
                # Invalidate dashboard cache for this company
                cache.delete_pattern(f"dashboard_data:{guid}")
                # Invalidate sales register cache for this company
                cache.delete_pattern(f"sales_register_data:{guid}")
                # Invalidate ledger data cache for this company
                cache.delete_pattern(f"ledger_data:{guid}")
                # Invalidate outstanding data cache for this company
                cache.delete_pattern(f"outstanding_data:{guid}")
                self.log(f"[{name}] 🗑️ Cache invalidated after sync")
            except Exception as cache_err:
                # Non-critical - log but don't fail
                print(f"[WARNING] Cache invalidation failed: {cache_err}")
            
            self._refresh_tree()
            # Keep progress at 100% for 2 seconds, then reset to 0
            self.root.after(2000, lambda: self._update_progress(0))
            # Keep progress at 100% for 2 seconds, then reset
            self.root.after(2000, lambda: self._update_progress(0))

        except Exception as e:
            error_msg = get_user_friendly_error(str(e))
            sync_duration = time.time() - sync_start_time if 'sync_start_time' in locals() else 0
            
            # Log sync failure (non-blocking)
            if sync_logger:
                try:
                    sync_logger.sync_failed(
                        guid, alterid_str_log, name,
                        error_message=str(e),
                        error_code="SYNC_ERROR",
                        details=f"Sync failed after {sync_duration:.2f} seconds. Error: {error_msg}",
                        records_synced=approx_inserted
                    )
                except Exception as log_err:
                    print(f"[WARNING] Failed to log failure: {log_err}")
            
            self.log(f"❌ Sync error for {name}: {e}")
            self.log(f"   User message: {error_msg}")
            # Show user-friendly error message
            try:
                messagebox.showerror("Sync Failed", f"Failed to sync {name}:\n\n{error_msg}")
            except:
                pass
            self.company_dao.update_status(guid, alterid, 'failed')

        finally:
            try:
                lock.release()
            except Exception:
                pass
            try:
                self.btn_sync.config(state=tk.NORMAL)
            except Exception:
                pass

    def _on_toggle_show_hidden(self):
        try:
            self.load_companies()
        except Exception:
            pass

    def _update_progress(self, percent):
        try:
            try:
                p = int(percent)
            except Exception:
                p = 0
            if p < 0:
                p = 0
            if p > 100:
                p = 100
            
            # Update horizontal progress bar
            self.progress['value'] = p
            self.progress_label.config(text=f"{p}%")
            
            # Update circular progress indicator
            try:
                if hasattr(self, 'circular_progress'):
                    self.circular_progress.set_progress(p)
            except:
                pass
            
            self.root.update_idletasks()
        except:
            pass

    def _refresh_tree(self):
        # Use CompanyDAO to get synced companies
        rows = self.company_dao.get_all_synced()
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        for idx, r in enumerate(rows):
            name, alterid, status, total, guid = r[0], r[1], r[2], r[3], r[4]
            
            # Get countdown for Next Sync column
            countdown = ""
            if self.auto_sync_enabled.get():
                key = f"{guid}|{alterid}"
                if key in self.auto_sync_timers:
                    next_time = self.auto_sync_timers[key]['next_sync']
                    delta = next_time - datetime.now()
                    if delta.total_seconds() > 0:
                        mins, secs = divmod(int(delta.total_seconds()), 60)
                        countdown = f"{mins}m {secs}s"
                    else:
                        countdown = "Syncing..."
                else:
                    interval = self.auto_sync_interval_var.get()
                    countdown = f"{interval}m 0s"
            
            tag = 'even' if idx % 2 == 0 else 'odd'
            try:
                self.tree.tag_configure('even', background=self.colors.get("tree_even", "#ffffff"))
                self.tree.tag_configure('odd', background=self.colors.get("tree_odd", "#f8fbfc"))
            except:
                pass
            sync_label = "▶ Sync"
            remove_label = "🗑 Remove"
            self.tree.insert(
                "",
                "end",
                values=(
                    name,
                    status or '',
                    sync_label,
                    remove_label,
                    countdown,
                    alterid or '',
                    total or 0,
                ),
                tags=(tag,),
            )
        try:
            self.company_count.config(text=f"{len(rows)} synced")
        except:
            pass

    def _mark_interrupted_syncs(self):
        # Use CompanyDAO to mark interrupted syncs
        rows = self.company_dao.get_syncing_companies()
        count = self.company_dao.mark_interrupted_syncs()
        if count > 0:
            for name, guid, alterid in rows:
                if messagebox.askyesno("Resume interrupted sync", f"Resume sync for '{name}' (AlterID: {alterid})?"):
                    key = f"{guid}|{alterid}"
                    lock = self.sync_locks.setdefault(key, threading.Lock())
                    acquired = lock.acquire(blocking=False)
                    if not acquired:
                        continue
                    t = threading.Thread(target=self._sync_worker, args=(name, guid, alterid, self.dsn_var.get().strip(), self.from_var.get().strip(), self.to_var.get().strip(), lock), daemon=True)
                    self.sync_threads[key] = t
                    self.btn_sync.config(state=tk.DISABLED)
                    t.start()

    def remove_company(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Choose a company to remove")
            return
        vals = self.tree.item(sel[0], "values")
        name, alterid = vals[0], vals[5]
        if not messagebox.askyesno("Confirm", f"Remove '{name}' (AlterID: {alterid})? This will delete all vouchers for that company."):
            return
        try:
            # Get GUID first
            guid = self.company_dao.get_guid_by_name_alterid(name, alterid)
            if guid:
                # Use CompanyDAO to delete company (also deletes vouchers)
                self.company_dao.delete_company(guid, alterid)
                self.log(f"✓ Removed {name}")
                self._refresh_tree()
            else:
                messagebox.showerror("Error", "Company not found")
        except Exception as e:
            self.log(f"✗ Error removing company: {e}")
            messagebox.showerror("Error", f"Could not remove: {e}")

    def manual_sync_all(self):
        """Sync only the selected company from the Synced Companies list."""
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Sync", "Select a company to sync")
            return
        vals = self.tree.item(sel[0], "values")
        try:
            name, alterid = vals[0], vals[5]
        except Exception:
            messagebox.showinfo("Sync", "Select a valid company to sync")
            return

        guid = self.company_dao.get_guid_by_name_alterid(name, alterid)
        if not guid:
            messagebox.showinfo("Sync", "Company not found in database")
            return
        
        # Show and reset progress indicators
        self._update_progress(0)
        
        self.log(f"🔄 Manual Sync started for {name}")
        self._auto_sync_company(name, guid, alterid)

    def _start_status_thread(self):
        t = threading.Thread(target=self._status_worker, daemon=True)
        t.start()
        # Start auto-sync worker
        self._start_auto_sync_worker()

    def _start_auto_sync_worker(self):
        """Start background auto-sync countdown worker"""
        t = threading.Thread(target=self._auto_sync_worker, daemon=True)
        t.start()

    def _auto_sync_worker(self):
        """Background worker for auto-sync countdowns"""
        while not self.auto_sync_stop_event.is_set():
            try:
                if not self.auto_sync_enabled.get():
                    time.sleep(1)
                    continue
                
                now = datetime.now()
                # Use CompanyDAO to get synced companies
                companies = self.company_dao.get_all_synced()
                # Convert to (name, guid, alterid) format
                companies = [(row[0], row[4], row[1]) for row in companies]
                
                for name, guid, alterid in companies:
                    key = f"{guid}|{alterid}"
                    if key not in self.auto_sync_timers:
                        self.auto_sync_timers[key] = {
                            'next_sync': now + timedelta(minutes=self.auto_sync_interval_var.get()),
                            'name': name
                        }
                    
                    timer_info = self.auto_sync_timers[key]
                    next_time = timer_info['next_sync']
                    
                    if now >= next_time:
                        # Trigger auto-sync
                        self._auto_sync_company(name, guid, alterid)
                        # Reset timer
                        self.auto_sync_timers[key]['next_sync'] = datetime.now() + timedelta(minutes=self.auto_sync_interval_var.get())
                    
                self._refresh_tree()
                time.sleep(1)
            except Exception as e:
                self.log(f"Auto-sync worker error: {e}")
                time.sleep(5)

    def _auto_sync_company(self, name, guid, alterid):
        """Trigger sync for company without user interaction"""
        key = f"{guid}|{alterid}"
        lock = self.sync_locks.setdefault(key, threading.Lock())
        acquired = lock.acquire(blocking=False)
        if not acquired:
            return
        
        # Show progress indicator when sync starts
        self._update_progress(0)
        
        self.log(f"⏱️ Auto-syncing {name}...")
        t = threading.Thread(target=self._sync_worker, args=(name, guid, alterid, self.dsn_var.get().strip(), 
                                                            self.from_var.get().strip(), self.to_var.get().strip(), lock), daemon=True)
        self.sync_threads[key] = t
        t.start()

    def _on_toggle_auto_sync(self):
        """Handle auto-sync enable/disable toggle"""
        if self.auto_sync_enabled.get():
            self.auto_sync_status.config(text="● Enabled", fg="green")
            self.log("✓ Auto-Sync enabled")
        else:
            self.auto_sync_status.config(text="● Disabled", fg="gray")
            self.log("✗ Auto-Sync disabled")

    def _on_update_auto_sync_timer(self):
        """Update auto-sync interval"""
        interval = self.auto_sync_interval_var.get()
        self.log(f"⚡ Auto-Sync interval updated to {interval} minute(s)")
        # Reset all timers
        self.auto_sync_timers.clear()

    def _status_worker(self):
        while True:
            try:
                dsn = self.dsn_var.get().strip()
                if dsn:
                    ok, _ = try_connect_dsn(dsn, timeout=3)
                    if ok:
                        self.set_status(f"Connected: {dsn}", "lightgreen")
                    else:
                        self.set_status("DSN Offline", "tomato")
                now = time.time()
                active_syncs = len([t for t in self.sync_threads.values() if t.is_alive()])
                if active_syncs == 0 and (now - self._last_tree_refresh) > 10:
                    self._refresh_tree()
                    self._last_tree_refresh = now
                elif active_syncs > 0 and (now - self._last_tree_refresh) > 30:
                    self._refresh_tree()
                    self._last_tree_refresh = now
            except Exception:
                pass
            time.sleep(5)

    def _setup_tray(self):
        """Setup system tray icon."""
        if not TRAY_AVAILABLE:
            return

        def _get_base_dir():
            if getattr(sys, 'frozen', False):
                return os.path.dirname(sys.executable)
            return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        def _get_resource_dir():
            if getattr(sys, 'frozen', False):
                try:
                    return sys._MEIPASS
                except Exception:
                    return os.path.dirname(sys.executable)
            return _get_base_dir()
        
        def create_icon():
            # Prefer Logo.png (supports transparency). Fallback to generated icon.
            try:
                logo_candidates = [
                    os.path.join(_get_base_dir(), "Logo.png"),
                    os.path.join(_get_resource_dir(), "Logo.png"),
                ]
                for p in logo_candidates:
                    if os.path.exists(p):
                        img = Image.open(p).convert("RGBA")
                        # center-crop to square then resize to tray size
                        w, h = img.size
                        side = min(w, h)
                        left = (w - side) // 2
                        top = (h - side) // 2
                        img = img.crop((left, top, left + side, top + side))
                        img = img.resize((64, 64))
                        return img
            except Exception:
                pass

            image = Image.new('RGB', (64, 64), color='#3498db')
            draw = ImageDraw.Draw(image)
            draw.text((32, 32), "T", fill='white', anchor="mm")
            return image
        
        def show_window(icon=None, item=None):
            """Show main window."""
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force()
        
        def hide_window():
            """Hide window to tray."""
            self.root.withdraw()
        
        def quit_app(icon=None, item=None):
            """Quit application."""
            if self.tray_icon:
                self.tray_icon.stop()
            try:
                self.auto_sync_stop_event.set()
            except:
                pass
            try:
                self.db_conn.close()
            except:
                pass
            self.root.quit()
            self.root.destroy()
        
        # Menu items
        menu = pystray.Menu(
            pystray.MenuItem("Show TallyConnect", show_window),
            pystray.MenuItem("Hide to Tray", hide_window),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit", quit_app)
        )
        
        # Create icon
        self.tray_icon = pystray.Icon("TallyConnect", create_icon(), "TallyConnect - Modern Tally Sync Platform", menu)
        
        # Start tray icon in separate thread
        def run_tray():
            self.tray_icon.run()
        
        self.tray_thread = threading.Thread(target=run_tray, daemon=True)
        self.tray_thread.start()

    def _apply_window_logo(self):
        """Set the Tk window icon from Logo.png (works in script + EXE)."""
        try:
            from PIL import Image, ImageTk
        except Exception:
            return

        def _get_base_dir():
            if getattr(sys, 'frozen', False):
                return os.path.dirname(sys.executable)
            return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        def _get_resource_dir():
            if getattr(sys, 'frozen', False):
                try:
                    return sys._MEIPASS
                except Exception:
                    return os.path.dirname(sys.executable)
            return _get_base_dir()

        # Prefer .ico for Windows taskbar/titlebar where supported
        ico_candidates = [
            os.path.join(_get_base_dir(), "TallyConnect.ico"),
            os.path.join(_get_base_dir(), "build-config", "TallyConnect.ico"),
        ]
        ico_path = next((p for p in ico_candidates if os.path.exists(p)), None)
        if ico_path:
            try:
                self.root.iconbitmap(ico_path)
            except Exception:
                pass

        logo_candidates = [
            os.path.join(_get_base_dir(), "Logo.png"),
            os.path.join(_get_resource_dir(), "Logo.png"),
        ]
        logo_path = next((p for p in logo_candidates if os.path.exists(p)), None)
        if not logo_path:
            return

        img = Image.open(logo_path).convert("RGBA")
        # Use a small size for window icon
        img = img.resize((64, 64))
        self._tk_logo_image = ImageTk.PhotoImage(img)  # keep reference
        try:
            self.root.iconphoto(True, self._tk_logo_image)
        except Exception:
            pass

    def _load_brand_image(self, size=(52, 52)):
        """Load Logo.png as a Tk PhotoImage (scaled square)."""
        from PIL import Image, ImageTk

        def _get_base_dir():
            if getattr(sys, 'frozen', False):
                return os.path.dirname(sys.executable)
            return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        def _get_resource_dir():
            if getattr(sys, 'frozen', False):
                try:
                    return sys._MEIPASS
                except Exception:
                    return os.path.dirname(sys.executable)
            return _get_base_dir()

        logo_candidates = [
            os.path.join(_get_base_dir(), "Logo.png"),
            os.path.join(_get_resource_dir(), "Logo.png"),
        ]
        logo_path = next((p for p in logo_candidates if os.path.exists(p)), None)
        if not logo_path:
            return None

        img = Image.open(logo_path).convert("RGBA")
        w, h = img.size
        side = min(w, h)
        left = (w - side) // 2
        top = (h - side) // 2
        img = img.crop((left, top, left + side, top + side))
        img = img.resize(size)
        return ImageTk.PhotoImage(img)
    
    def on_close(self):
        """Handle window close - minimize to tray instead of closing."""
        if TRAY_AVAILABLE and self.tray_icon:
            # Hide window to tray
            self.root.withdraw()
        else:
            # No tray available, close normally
            try:
                self.auto_sync_stop_event.set()
            except:
                pass
            try:
                self.db_conn.close()
            except:
                pass
            # Portal will be shut down by main.py's finally block
            self.root.destroy()

def main():
    root = tk.Tk()
    app = BizAnalystApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()

if __name__ == "__main__":
    main()