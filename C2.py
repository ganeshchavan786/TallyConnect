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
try:
    import pystray
    from PIL import Image, ImageDraw
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False

# ---------- Configuration ----------
DB_FILE = "TallyConnectDb.db"
BATCH_SIZE = 100  # Reduced from 500 (Tally returns in smaller chunks)
COMMON_PORTS = [9000, 9001, 9999, 9002]
DSN_PREFIX = "TallyODBC64_"
TALLY_COMPANY_QUERY = 'SELECT $Name, $GUID, $AlterID FROM Company'

VOUCHER_QUERY_TEMPLATE = """
SELECT $OwnerCompany, $OwnerGUID, $OnwerAlterID, $VchDate, $VchType, $VchNo, $VchLedName,
       $VchLedAmount, $VchDrCr, $VchLedDrAmt, $VchLedCrAmt, $VchPartyName, $VchLedParent,
       $VchNarration, $VchGstin, $VchLedGstin, $VchLedBillRef, $VchLedBillType, $VchLedPrimaryGrp,
       $VchLedNature, $VchLedBSGrp, $VchLedBSGrpNature, $VchIsOptional, $VchMstID, $VchledbillCount
FROM TallyVchLedCollectionCMP
WHERE $OwnerGUID = '{guid}'
  AND $VchDate >= $$Date:"{from_date}"
  AND $VchDate <= $$Date:"{to_date}"
"""

# ---------- DB Helpers ----------
def init_db(db_path=DB_FILE):
    conn = sqlite3.connect(db_path, check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS companies (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      guid TEXT NOT NULL,
      alterid TEXT NOT NULL,
      dsn TEXT,
      status TEXT DEFAULT 'new',
      total_records INTEGER DEFAULT 0,
      last_sync TEXT,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP,
      UNIQUE(guid, alterid)
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS vouchers (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      company_guid TEXT NOT NULL,
      company_alterid TEXT NOT NULL,
      company_name TEXT,
      vch_date TEXT,
      vch_type TEXT,
      vch_no TEXT,
      vch_mst_id TEXT,
      led_name TEXT,
      led_amount REAL,
      vch_dr_cr TEXT,
      vch_dr_amt REAL,
      vch_cr_amt REAL,
      vch_party_name TEXT,
      vch_led_parent TEXT,
      vch_narration TEXT,
      vch_gstin TEXT,
      vch_led_gstin TEXT,
      vch_led_bill_ref TEXT,
      vch_led_bill_type TEXT,
      vch_led_primary_grp TEXT,
      vch_led_nature TEXT,
      vch_led_bs_grp TEXT,
      vch_led_bs_grp_nature TEXT,
      vch_is_optional TEXT,
      vch_led_bill_count INTEGER,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP,
      UNIQUE(company_guid, company_alterid, vch_mst_id, led_name)
    )
    """)
    conn.commit()
    return conn

def try_connect_dsn(dsn_name, timeout=5):
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
        
        # Theme System
        self.themes = {
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
        
        self.current_theme = tk.StringVar(value="Modern Blue")
        self.colors = self.themes[self.current_theme.get()].copy()
        
        self.db_conn = init_db()
        self.db_lock = threading.Lock()
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
        try:
            self.auto_detect_dsn(silent=True)
        except Exception:
            pass
        self._start_status_thread()
        self._mark_interrupted_syncs()
        self._refresh_tree()

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
        self.title_label = tk.Label(self.title_frame, text="📊 TALLYCONNECT", fg="white", bg=self.colors["header"],
                 font=("Segoe UI", 22, "bold"))
        self.title_label.pack(anchor="w")
        self.subtitle_label = tk.Label(self.title_frame, text="Modern Tally Sync Platform", fg="#95a5a6", bg=self.colors["header"],
                 font=("Segoe UI", 10))
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
        self.theme_dropdown = ttk.Combobox(toolbar_content, textvariable=self.current_theme, 
                                          values=list(self.themes.keys()),
                                          state="readonly", width=18, font=("Segoe UI", 9))
        self.theme_dropdown.pack(side=tk.RIGHT, padx=4)
        self.theme_dropdown.bind("<<ComboboxSelected>>", lambda e: self.apply_theme())
        
        tk.Label(toolbar_content, text="v5.6 Pro", bg="white", fg="#95a5a6", 
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

        cols = ("Name", "Reports", "Status", "Sync", "Remove", "Next Sync", "AlterID", "Records")
        self.tree = ttk.Treeview(left_body, columns=cols, show="headings", height=18, style="Custom.Treeview")
        for c in cols:
            self.tree.heading(c, text=c)
            if c == "Name":
                self.tree.column(c, width=180, minwidth=150, stretch=True, anchor="w")
            elif c == "Reports":
                self.tree.column(c, width=110, minwidth=100, stretch=False, anchor="center")
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
        self.from_var = tk.StringVar(value="01-01-2024")
        self.entry_from = ttk.Entry(date_row, textvariable=self.from_var, width=15)
        self.entry_from.pack(side=tk.LEFT, padx=4)
        tk.Label(date_row, text="To:", bg="white").pack(side=tk.LEFT, padx=(12, 4))
        self.to_var = tk.StringVar(value=datetime.now().strftime("%d-%m-%Y"))
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
        
        self.progress = ttk.Progressbar(prog_frame, orient="horizontal", length=500, mode="determinate", 
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
            self.colors = self.themes[theme_name].copy()
            
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
            name, alterid = vals[0], vals[6]  # Updated: AlterID is now at index 6
            with self.db_lock:
                cur = self.db_conn.cursor()
                cur.execute("SELECT guid FROM companies WHERE name=? AND alterid=?", (name, alterid))
                row = cur.fetchone()
            if row:
                self.load_notes(row[0])
        except Exception:
            pass

    def _on_tree_click(self, event):
        """Handle clicks on Reports/Sync/Remove columns inside the tree."""
        try:
            region = self.tree.identify("region", event.x, event.y)
            if region != "cell":
                return
            row_id = self.tree.identify_row(event.y)
            col_id = self.tree.identify_column(event.x)
            if not row_id or not col_id:
                return
            col_index = int(col_id.replace("#", ""))  # 1-based
            if col_index == 2:  # Reports column
                self.tree.selection_set(row_id)
                self.show_report_menu()
                return "break"
            if col_index == 4:  # Sync column
                self.tree.selection_set(row_id)
                self.manual_sync_all()
                return "break"
            if col_index == 5:  # Remove column
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

    def show_report_menu(self):
        """Show report selection menu."""
        try:
            sel = self.tree.selection()
            if not sel:
                messagebox.showwarning("No Selection", "Please select a company first")
                return
            
            vals = self.tree.item(sel[0], "values")
            company_name = vals[0]
            alterid = vals[6]
            
            # Get GUID from database
            with self.db_lock:
                cur = self.db_conn.cursor()
                cur.execute("SELECT guid FROM companies WHERE name=? AND alterid=?", (company_name, alterid))
                row = cur.fetchone()
            
            if not row:
                messagebox.showerror("Error", "Company not found in database")
                return
            
            guid = row[0]
            
            # Create popup menu
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="📊 Outstanding Report", 
                           command=lambda: self.generate_outstanding_report(company_name, guid, alterid))
            menu.add_command(label="📗 Ledger Report", 
                           command=lambda: self.show_ledger_dialog(company_name, guid, alterid))
            menu.add_command(label="📈 Dashboard", 
                           command=lambda: self.generate_dashboard(company_name, guid, alterid))
            
            # Show menu at mouse position
            try:
                menu.tk_popup(self.root.winfo_pointerx(), self.root.winfo_pointery())
            finally:
                menu.grab_release()
                
        except Exception as e:
            self.log(f"✗ Report menu error: {e}")
            messagebox.showerror("Error", f"Failed to show report menu: {e}")

    def generate_outstanding_report(self, company_name, guid, alterid):
        """Generate outstanding report."""
        try:
            self.log(f"🔄 Generating outstanding report for {company_name}...")
            from reports import ReportGenerator
            
            generator = ReportGenerator(DB_FILE)
            report_path = generator.generate_outstanding_report(company_name, guid, alterid)
            
            self.log(f"✓ Outstanding report generated: {os.path.basename(report_path)}")
            messagebox.showinfo("Success", f"Outstanding report generated successfully!\n\n{os.path.basename(report_path)}")
            
        except Exception as e:
            self.log(f"✗ Outstanding report error: {e}")
            messagebox.showerror("Error", f"Failed to generate outstanding report:\n{e}")

    def show_ledger_dialog(self, company_name, guid, alterid):
        """Show dialog to select ledger and date range."""
        try:
            # Create dialog window
            dialog = tk.Toplevel(self.root)
            dialog.title(f"Ledger Report - {company_name}")
            dialog.geometry("450x280")
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Get available parties/ledgers
            with self.db_lock:
                cur = self.db_conn.cursor()
                cur.execute("""
                    SELECT DISTINCT vch_party_name 
                    FROM vouchers 
                    WHERE company_guid=? AND company_alterid=? 
                    AND vch_party_name IS NOT NULL AND vch_party_name != ''
                    ORDER BY vch_party_name
                """, (guid, str(alterid)))
                parties = [row[0] for row in cur.fetchall()]
            
            # Ledger selection
            tk.Label(dialog, text="Select Party/Ledger:", font=("Segoe UI", 10, "bold")).pack(pady=(15, 5))
            ledger_var = tk.StringVar()
            ledger_combo = ttk.Combobox(dialog, textvariable=ledger_var, values=parties, width=40, state="readonly")
            ledger_combo.pack(pady=5)
            if parties:
                ledger_combo.current(0)
            
            # Date range
            tk.Label(dialog, text="Date Range:", font=("Segoe UI", 10, "bold")).pack(pady=(15, 5))
            date_frame = tk.Frame(dialog)
            date_frame.pack(pady=5)
            
            tk.Label(date_frame, text="From:").pack(side=tk.LEFT, padx=5)
            from_var = tk.StringVar(value="01-04-2024")
            tk.Entry(date_frame, textvariable=from_var, width=15).pack(side=tk.LEFT, padx=5)
            
            tk.Label(date_frame, text="To:").pack(side=tk.LEFT, padx=5)
            to_var = tk.StringVar(value=datetime.now().strftime("%d-%m-%Y"))
            tk.Entry(date_frame, textvariable=to_var, width=15).pack(side=tk.LEFT, padx=5)
            
            # Buttons
            btn_frame = tk.Frame(dialog)
            btn_frame.pack(pady=20)
            
            def generate():
                ledger = ledger_var.get()
                if not ledger:
                    messagebox.showwarning("No Selection", "Please select a party/ledger")
                    return
                
                dialog.destroy()
                self.generate_ledger_report(company_name, guid, alterid, ledger, from_var.get(), to_var.get())
            
            ttk.Button(btn_frame, text="📊 Generate Report", command=generate, style="Success.TButton").pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text="❌ Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
            
        except Exception as e:
            self.log(f"✗ Ledger dialog error: {e}")
            messagebox.showerror("Error", f"Failed to show ledger dialog:\n{e}")

    def generate_ledger_report(self, company_name, guid, alterid, ledger_name, from_date, to_date):
        """Generate ledger report."""
        try:
            self.log(f"🔄 Generating ledger report for {ledger_name}...")
            from reports import ReportGenerator
            
            generator = ReportGenerator(DB_FILE)
            report_path = generator.generate_ledger_report(company_name, guid, alterid, ledger_name, from_date, to_date)
            
            self.log(f"✓ Ledger report generated: {os.path.basename(report_path)}")
            messagebox.showinfo("Success", f"Ledger report generated successfully!\n\n{os.path.basename(report_path)}")
            
        except Exception as e:
            self.log(f"✗ Ledger report error: {e}")
            messagebox.showerror("Error", f"Failed to generate ledger report:\n{e}")

    def generate_dashboard(self, company_name, guid, alterid):
        """Generate dashboard report."""
        try:
            self.log(f"🔄 Generating dashboard for {company_name}...")
            from reports import ReportGenerator
            
            generator = ReportGenerator(DB_FILE)
            report_path = generator.generate_dashboard(company_name, guid, alterid)
            
            self.log(f"✓ Dashboard generated: {os.path.basename(report_path)}")
            messagebox.showinfo("Success", f"Dashboard generated successfully!\n\n{os.path.basename(report_path)}")
            
        except Exception as e:
            self.log(f"✗ Dashboard error: {e}")
            messagebox.showerror("Error", f"Failed to generate dashboard:\n{e}")

    def save_notes(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a company to save notes")
            return
        vals = self.tree.item(sel[0], "values")
        name, alterid = vals[0], vals[5]
        with self.db_lock:
            cur = self.db_conn.cursor()
            cur.execute("SELECT guid FROM companies WHERE name=? AND alterid=?", (name, alterid))
            row = cur.fetchone()
        if not row:
            messagebox.showwarning("No company", "Selected company not found in DB")
            return
        guid = row[0]
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
                messagebox.showerror("Error", "Could not detect Tally DSN")

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
            conn = pyodbc.connect(f"DSN={dsn};", timeout=10)
            cur = conn.cursor()
            cur.execute(TALLY_COMPANY_QUERY)
            companies = cur.fetchall()
            cur.close()
            conn.close()
            
            local_status = {}
            try:
                with self.db_lock:
                    c = self.db_conn.cursor()
                    c.execute("SELECT guid, alterid, status FROM companies")
                    for g, a, s in c.fetchall():
                        key = (str(g) if g is not None else None, str(a) if a is not None else 'None')
                        local_status[key] = s
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
            self.log(f"✗ Error loading companies: {e}")
            messagebox.showerror("Error", f"Could not load companies:\n{e}")
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
        if not dsn:
            messagebox.showwarning("DSN Required", "Enter or detect DSN first")
            return
        key = f"{guid}|{alterid}"

        lock = self.sync_locks.setdefault(key, threading.Lock())
        acquired = lock.acquire(blocking=False)
        if not acquired:
            messagebox.showinfo("Sync", "Sync already running for this company")
            return

        with self.db_lock:
            cur = self.db_conn.cursor()
            cur.execute("SELECT id, status FROM companies WHERE guid=? AND alterid=?", (guid, alterid))
            r = cur.fetchone()
            if r:
                cur.execute("UPDATE companies SET status='syncing', dsn=? WHERE guid=? AND alterid=?", (dsn, guid, alterid))
                self.db_conn.commit()
            else:
                cur.execute("INSERT OR IGNORE INTO companies (name, guid, alterid, dsn, status) VALUES (?, ?, ?, ?, 'syncing')", (name, guid, alterid, dsn))
                self.db_conn.commit()
        
        # Remove from available list (optimistic UI)
        self.avail_listbox.delete(sel[0])
        avail_count = self.avail_listbox.size()
        try:
            self.avail_count_label.config(text=f"{avail_count} available")
        except:
            pass
        
        t = threading.Thread(target=self._sync_worker, args=(name, guid, alterid, dsn, from_date, to_date, lock), daemon=True)
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
        
        try:
            conn = pyodbc.connect(f"DSN={dsn};", timeout=30)
            cur = conn.cursor()

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

            def _execute_window(f_d, t_d):
                nonlocal approx_inserted, batch_count, estimated_batches
                
                q = VOUCHER_QUERY_TEMPLATE.format(guid=guid, from_date=f_d, to_date=t_d)
                self.log(f"[{name}] 📤 Query: {f_d} → {t_d}")
                try:
                    cur.execute(q)
                except Exception as exq:
                    self.log(f"[{name}] ❌ Query error: {exq}")
                    return

                batch_no = 0
                while True:
                    rows = cur.fetchmany(batch_size)
                    if not rows:
                        break
                    batch_no += 1
                    batch_count += 1
                    params = []
                    
                    # FIXED: params list built inside row loop
                    for r in rows:
                        try:
                            vch_date = str(r[3]) if len(r) > 3 else None
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

                        params.append((
                            guid, alterid, name, vch_date, vch_type, vch_no, vch_mst_id,
                            led_name, led_amount, vch_dr_cr, vch_dr_amt, vch_cr_amt, vch_party_name, vch_led_parent,
                            vch_narration, vch_gstin, vch_led_gstin, vch_led_bill_ref, vch_led_bill_type,
                            vch_led_primary_grp, vch_led_nature, vch_led_bs_grp, vch_led_bs_grp_nature,
                            vch_is_optional, vch_led_bill_count
                        ))
                    
                    # OPTIMIZED: SQLite bulk insert with PRAGMA settings
                    if params:
                        with self.db_lock:
                            db_cur = self.db_conn.cursor()
                            
                            # Enable faster inserts (only once per sync)
                            if batch_no == 1:
                                db_cur.execute("PRAGMA synchronous = NORMAL")
                                db_cur.execute("PRAGMA temp_store = MEMORY")
                                db_cur.execute("PRAGMA cache_size = 10000")
                            
                            db_cur.executemany("""
                            INSERT OR IGNORE INTO vouchers
                            (company_guid, company_alterid, company_name, vch_date, vch_type, vch_no, vch_mst_id,
                             led_name, led_amount, vch_dr_cr, vch_dr_amt, vch_cr_amt, vch_party_name, vch_led_parent,
                             vch_narration, vch_gstin, vch_led_gstin, vch_led_bill_ref, vch_led_bill_type,
                             vch_led_primary_grp, vch_led_nature, vch_led_bs_grp, vch_led_bs_grp_nature,
                             vch_is_optional, vch_led_bill_count)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, params)
                            self.db_conn.commit()
                            approx_inserted += len(params)

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
                    time.sleep(0.01)

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
                        _execute_window(f_d, t_d)
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

            # Restore PRAGMA and update company status
            with self.db_lock:
                db_cur = self.db_conn.cursor()
                db_cur.execute("PRAGMA synchronous = FULL")
                db_cur.execute("""
                UPDATE companies SET total_records=?, last_sync=?, status='synced' WHERE guid=? AND alterid=?
                """, (approx_inserted, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), guid, alterid))
                self.db_conn.commit()

            self._update_progress(100)
            self.log(f"✅ COMPLETE: {name} | {approx_inserted} vouchers synced in {batch_count} batches!")
            self._refresh_tree()

        except Exception as e:
            self.log(f"❌ Sync error for {name}: {e}")
            with self.db_lock:
                c = self.db_conn.cursor()
                c.execute("UPDATE companies SET status='failed' WHERE guid=? AND alterid=?", (guid, alterid))
                self.db_conn.commit()

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
            self.progress['value'] = p
            self.progress_label.config(text=f"{p}%")
            self.root.update_idletasks()
        except:
            pass

    def _refresh_tree(self):
        with self.db_lock:
            cur = self.db_conn.cursor()
            cur.execute("SELECT name, alterid, status, total_records, guid FROM companies WHERE status='synced' ORDER BY name")
            rows = cur.fetchall()
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
            reports_label = "📊 Reports"
            sync_label = "▶ Sync"
            remove_label = "🗑 Remove"
            self.tree.insert(
                "",
                "end",
                values=(
                    name,
                    reports_label,
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
        with self.db_lock:
            cur = self.db_conn.cursor()
            cur.execute("SELECT name, guid, alterid FROM companies WHERE status='syncing'")
            rows = cur.fetchall()
            for name, guid, alterid in rows:
                cur.execute("UPDATE companies SET status='incomplete' WHERE guid=? AND alterid=?", (guid, alterid))
            self.db_conn.commit()
        if rows:
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
            with self.db_lock:
                cur = self.db_conn.cursor()
                cur.execute("SELECT guid FROM companies WHERE name=? AND alterid=?", (name, alterid))
                row = cur.fetchone()
                if row:
                    guid = row[0]
                    cur.execute("DELETE FROM vouchers WHERE company_guid=? AND company_alterid=?", (guid, alterid))
                    cur.execute("DELETE FROM companies WHERE guid=? AND alterid=?", (guid, alterid))
                    self.db_conn.commit()
            self.log(f"✓ Removed {name}")
            self._refresh_tree()
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

        with self.db_lock:
            cur = self.db_conn.cursor()
            cur.execute("SELECT guid FROM companies WHERE name=? AND alterid=?", (name, alterid))
            row = cur.fetchone()

        if not row:
            messagebox.showinfo("Sync", "Company not found in database")
            return

        guid = row[0]
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
                with self.db_lock:
                    cur = self.db_conn.cursor()
                    cur.execute("SELECT name, guid, alterid FROM companies WHERE status='synced' ORDER BY name")
                    companies = cur.fetchall()
                
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
        
        def create_icon():
            # Create a 64x64 image with blue background
            image = Image.new('RGB', (64, 64), color='#3498db')
            draw = ImageDraw.Draw(image)
            # Draw a simple "T" for TallyConnect
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
            self.root.destroy()

def main():
    root = tk.Tk()
    app = BizAnalystApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()

if __name__ == "__main__":
    main()