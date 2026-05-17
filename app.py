# ============================================================
# Study Reminder Pro - Main Application Entry Point
# File: app.py
#
# Run this file to start the application.
# Tech: Python 3.10+ · CustomTkinter · Tkinter · JSON storage
# ============================================================

import tkinter as tk
import customtkinter as ctk
import sys
import os
import random
from datetime import date, datetime

# ── Local imports ────────────────────────────────────────────
from core.database import Database
from core.theme import THEMES, FONTS, MOTIVATIONAL_QUOTES
from ui.widgets import SidebarButton, ToastNotification
from ui.dashboard import DashboardView
from ui.subjects import SubjectsView
from ui.pomodoro import PomodoroView
from ui.roadmap import RoadmapView
from ui.analytics import AnalyticsView
from ui.settings import SettingsView
from ui.tasks import TasksView
from themes.theme_manager import ThemeManager
from services.settings_service import SettingsService
from services.scheduler_service import SchedulerService
from services.notification_service import NotificationService
from focus.focus_controller import FocusController
from utils.event_bus import EventBus


# ════════════════════════════════════════════════════════════
#  Splash Screen
# ════════════════════════════════════════════════════════════
class SplashScreen(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.overrideredirect(True)
        self.attributes("-topmost", True)

        w, h = 480, 320
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
        self.configure(bg="#0D0F1A")

        # Logo area
        canvas = tk.Canvas(self, width=w, height=h,
                           bg="#0D0F1A", highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        # Decorative gradient circles
        for i, (r_size, color) in enumerate([(200, "#1A1D2E"), (140, "#2A2E45"), (90, "#3A3E5C")]):
            canvas.create_oval(w//2 - r_size, h//2 - r_size,
                               w//2 + r_size, h//2 + r_size,
                               fill="", outline=color, width=2)

        canvas.create_text(w//2, h//2 - 40, text="📖",
                           font=("Segoe UI", 54), fill="#7C6EFA")
        canvas.create_text(w//2, h//2 + 30, text="Study Reminder Pro",
                           font=("Segoe UI", 22, "bold"), fill="#F0F1FF")
        canvas.create_text(w//2, h//2 + 62, text="Your smart academic companion",
                           font=("Segoe UI", 11), fill="#8B8FA8")

        # Progress bar simulation
        self._bar = canvas.create_rectangle(w//2 - 120, h - 50,
                                            w//2 - 120, h - 36,
                                            fill="#7C6EFA", outline="")
        canvas.create_rectangle(w//2 - 120, h - 50,
                                w//2 + 120, h - 36,
                                fill="#1C2033", outline="")
        self._bar = canvas.create_rectangle(w//2 - 120, h - 50,
                                            w//2 - 120, h - 36,
                                            fill="#7C6EFA", outline="")
        self._canvas = canvas
        self.width = w
        self.height = h
        self._progress = 0
        self._animate_bar()

    def _animate_bar(self):
        if self._progress < 100:
            self._progress += 3
            x2 = (self.width // 2 - 120) + int(240 * self._progress / 100)
            self._canvas.coords(self._bar,
                                self.width//2 - 120, self.height - 50,
                                x2, self.height - 36)
            self.after(30, self._animate_bar)
        else:
            self.after(200, self.destroy)


# ════════════════════════════════════════════════════════════
#  Main Application Window
# ════════════════════════════════════════════════════════════
class StudyReminderApp(ctk.CTk):

    # Nav items: (key, icon, label)
    NAV_ITEMS = [
        ("dashboard",  "🏠", "Dashboard"),
        ("roadmap",    "🗺️", "Roadmap"),
        ("tasks",      "📝", "Tasks"),
        ("subjects",   "📚", "Subjects"),
        ("pomodoro",   "🍅", "Pomodoro"),
        ("analytics",  "📊", "Analytics"),
        ("settings",   "⚙️", "Settings"),
    ]

    def __init__(self):
        with open("debug_log.txt", "a") as log:
            log.write(f"[{datetime.now()}] Init started\n")
        super().__init__()

        # ── Database & Services ──
        with open("debug_log.txt", "a") as log:
            log.write(f"[{datetime.now()}] Initializing Database & Services\n")
            
        self.events = EventBus()
        self.db = Database()
        self.theme_manager = ThemeManager()
        self.settings = SettingsService(self.db._settings_db, self.theme_manager)
        
        self.scheduler = SchedulerService()
        self.scheduler.start()
        self.notifier = NotificationService()
        
        self.focus_controller = FocusController(self)

        # ── Theme setup ──
        try:
            mode = self.db.settings.get("theme", "dark")
            if self.db.settings.get("glassmorphism"): mode = "glass"
            accent = self.db.settings.get("accent_color")
            
            self.theme_manager.set_theme(mode, accent_hex=accent)
            self._theme_name = self.theme_manager.current_mode
            self.colors = self.theme_manager.colors
            self.settings.add_listener("theme", self._on_theme_changed)
        except Exception:
            self._theme_name = "dark"
            self.colors = THEMES["dark"]

        # ── Window ──
        with open("debug_log.txt", "a") as log:
            log.write(f"[{datetime.now()}] Configuring window\n")
        self.title("Study Reminder Pro")
        self.geometry("1200x760")
        self.minsize(900, 620)
        self.configure(fg_color=self.colors["bg_primary"])
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # ── Icon ──
        try:
            ico = os.path.join(os.path.dirname(__file__), "assets", "icon.ico")
            if os.path.exists(ico):
                self.iconbitmap(ico)
        except Exception:
            pass

        # ── Desktop Widget ──
        self.mini_panel = None
        if self.db.settings.get("show_widget"):
            self._toggle_mini_panel(True)

        # ── Layout ──
        with open("debug_log.txt", "a") as log:
            log.write(f"[{datetime.now()}] Building layout\n")
        self._build_layout()
        self._active_page = None
        self._page_widgets = {}
        self._nav_btns = {}

        with open("debug_log.txt", "a") as log:
            log.write(f"[{datetime.now()}] Building sidebar and content\n")
        self._build_sidebar()
        self._build_content_area()

        # Force update to resolve dimensions
        self.update()

        # Defer non-critical startup tasks
        self.after(200, self._deferred_init)

    def _deferred_init(self):
        """Heavy lifting deferred after initial frame render."""
        with open("debug_log.txt", "a") as log:
            log.write(f"[{datetime.now()}] Running deferred init\n")
            
        # Navigate to dashboard
        self.navigate("dashboard")

        # Start periodic checks
        self._check_reminders()
        
        with open("debug_log.txt", "a") as log:
            log.write(f"[{datetime.now()}] Deferred init complete\n")

    # ── Layout skeleton ───────────────────────────────────────
    def _build_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._sidebar = ctk.CTkFrame(self,
                                     fg_color=self.colors["bg_sidebar"],
                                     width=220, corner_radius=0)
        self._sidebar.grid(row=0, column=0, sticky="nsew")
        self._sidebar.grid_propagate(False)

        self._content = ctk.CTkFrame(self,
                                     fg_color=self.colors["bg_primary"],
                                     corner_radius=0)
        self._content.grid(row=0, column=1, sticky="nsew")
        self._content.grid_rowconfigure(0, weight=1)
        self._content.grid_columnconfigure(0, weight=1)

    # ── Sidebar ───────────────────────────────────────────────
    def _build_sidebar(self):
        c = self.colors
        sb = self._sidebar

        # Logo
        logo_frame = ctk.CTkFrame(sb, fg_color="transparent")
        logo_frame.pack(fill="x", padx=16, pady=(30, 20))
        ctk.CTkLabel(logo_frame, text="📖", font=("Segoe UI", 30)).pack(side="left")
        name_col = ctk.CTkFrame(logo_frame, fg_color="transparent")
        name_col.pack(side="left", padx=8)
        ctk.CTkLabel(name_col, text="Study", font=("Segoe UI", 15, "bold"),
                     text_color=c["accent"]).pack(anchor="w")
        ctk.CTkLabel(name_col, text="Reminder Pro", font=("Segoe UI", 11),
                     text_color=c["text_secondary"]).pack(anchor="w")

        # Divider
        ctk.CTkFrame(sb, height=1, fg_color=c["border"]).pack(fill="x", padx=16, pady=8)

        # Scrollable Nav container
        self._nav_scroll = ctk.CTkScrollableFrame(sb, fg_color="transparent", corner_radius=0)
        self._nav_scroll.pack(fill="both", expand=True, padx=4)

        # Nav buttons
        for key, icon, label in self.NAV_ITEMS:
            try:
                btn = SidebarButton(self._nav_scroll, label, icon,
                                    command=lambda k=key: self.navigate(k),
                                    active=False, colors=c)
                btn.pack(fill="x", padx=8, pady=2)
                self._nav_btns[key] = btn
            except Exception as e:
                with open("sidebar_debug.txt", "a") as log:
                    log.write(f"ERROR creating button {key}: {e}\n")

        # Bottom section
        footer = ctk.CTkFrame(sb, fg_color="transparent")
        footer.pack(side="bottom", fill="x", padx=16, pady=16)
        
        ctk.CTkFrame(footer, height=1, fg_color=c["border"]).pack(fill="x", pady=(0, 16))
        
        self._streak_badge = ctk.CTkFrame(footer, fg_color=c["bg_card"],
                                          corner_radius=12, border_width=1,
                                          border_color=c["border"])
        self._streak_badge.pack(fill="x")

        streak = self.db.streaks["current"]
        self._streak_label = ctk.CTkLabel(self._streak_badge,
                     text=f"🔥  {streak}-day streak",
                     font=FONTS["small"],
                     text_color=c["warning"])
        self._streak_label.pack(padx=12, pady=8)

    def update_sidebar_streak(self):
        if hasattr(self, '_streak_label') and self._streak_label.winfo_exists():
            streak = self.db.streaks["current"]
            self._streak_label.configure(text=f"🔥  {streak}-day streak")

    # ── Content area ──────────────────────────────────────────
    def _build_content_area(self):
        """Top bar + page container."""
        c = self.colors

        # Top bar
        topbar = ctk.CTkFrame(self._content, fg_color=c["bg_secondary"],
                               height=52, corner_radius=0)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)

        self._page_title_var = tk.StringVar(value="Dashboard")
        ctk.CTkLabel(topbar, textvariable=self._page_title_var,
                     font=FONTS["subheading"],
                     text_color=c["text_primary"]).pack(side="left", padx=24)

        # Quick theme toggle in topbar
        theme_btn = ctk.CTkButton(topbar, text="🌙" if self._theme_name == "dark" else "☀️",
                                  width=38, height=32, corner_radius=10,
                                  fg_color=c["bg_card"],
                                  hover_color=c["border"],
                                  text_color=c["text_primary"],
                                  font=("Segoe UI", 14),
                                  command=self._quick_theme_toggle)
        theme_btn.pack(side="right", padx=12)
        self._topbar_theme_btn = theme_btn

        today = date.today().strftime("%a, %b %d")
        ctk.CTkLabel(topbar, text=today, font=FONTS["small"],
                     text_color=c["text_muted"]).pack(side="right", padx=8)

        # Page container
        self._page_container = ctk.CTkFrame(self._content,
                                            fg_color=c["bg_primary"],
                                            corner_radius=0)
        self._page_container.pack(fill="both", expand=True)
        self._page_container.grid_rowconfigure(0, weight=1)
        self._page_container.grid_columnconfigure(0, weight=1)

    # ── Navigation ────────────────────────────────────────────
    def navigate(self, page_key):
        if hasattr(self, 'update_sidebar_streak'):
            self.update_sidebar_streak()
            
        if self._active_page == page_key:
            # Refresh current page
            if page_key in self._page_widgets:
                w = self._page_widgets[page_key]
                if hasattr(w, "refresh"):
                    w.refresh()
            return

        # Hide old page
        if self._active_page and self._active_page in self._page_widgets:
            self._page_widgets[self._active_page].grid_remove()
            self._nav_btns[self._active_page].set_active(False)

        self._active_page = page_key

        # Build page if not cached
        if page_key not in self._page_widgets:
            self._page_widgets[page_key] = self._build_page(page_key)

        widget = self._page_widgets[page_key]
        if hasattr(widget, "refresh"):
            widget.refresh()
        widget.grid(row=0, column=0, sticky="nsew")

        # Update nav + title
        self._nav_btns[page_key].set_active(True)
        title_map = {k: l for k, _, l in self.NAV_ITEMS}
        self._page_title_var.set(title_map.get(page_key, page_key.title()))

    def _build_page(self, key):
        c = self.colors
        p = self._page_container

        if key == "dashboard":
            return DashboardView(p, self.db, c, self.toast, self.events)
        elif key == "roadmap":
            return RoadmapView(p, self.db, c)
        elif key == "tasks":
            return TasksView(p, self.db, c, self.toast)
        elif key == "subjects":
            return SubjectsView(p, self.db, c, self.toast)
        elif key == "pomodoro":
            return PomodoroView(p, self.db, c, self.toast)
        elif key == "analytics":
            return AnalyticsView(p, self.db, c, self.toast)
        elif key == "settings":
            return SettingsView(p, self.db, c, self.toast,
                                theme_switch_fn=self.switch_theme)
        else:
            return ctk.CTkLabel(p, text="Page not found")

    # ── Toast notifications ───────────────────────────────────
    def toast(self, message, kind="info"):
        ToastNotification(self, message, kind, self.colors)

    # ── Theme switching ──
    def switch_theme(self, mode, accent_hex=None):
        # Update manager state
        self.theme_manager.set_theme(mode, accent_hex=accent_hex)
        self._on_theme_changed(mode)

    def _on_theme_changed(self, mode):
        """Called automatically when the theme setting changes."""
        self._theme_name = mode
        self.colors = self.theme_manager.colors

        # Rebuild all cached pages so they use new colors
        for w in self._page_widgets.values():
            if hasattr(w, "cleanup"):
                w.cleanup()
            w.destroy()
        self._page_widgets.clear()
        self._nav_btns.clear()

        # Rebuild sidebar and content
        self._sidebar.destroy()
        self._content.destroy()
        self.configure(fg_color=self.colors["bg_primary"])

        self._sidebar = ctk.CTkFrame(self,
                                     fg_color=self.colors["bg_sidebar"],
                                     width=220, corner_radius=0)
        self._sidebar.grid(row=0, column=0, sticky="nsew")
        self._sidebar.grid_propagate(False)

        self._content = ctk.CTkFrame(self,
                                     fg_color=self.colors["bg_primary"],
                                     corner_radius=0)
        self._content.grid(row=0, column=1, sticky="nsew")
        self._content.grid_rowconfigure(0, weight=1)
        self._content.grid_columnconfigure(0, weight=1)

        self._build_sidebar()
        self._build_content_area()
        self._active_page = None
        self.navigate("dashboard")

        icon = "☀️" if mode == "dark" else "🌙"
        self._topbar_theme_btn.configure(text=icon)

    def _quick_theme_toggle(self):
        new_mode = "light" if self._theme_name == "dark" else "dark"
        self.switch_theme(new_mode)

    # ── Periodic reminders ────────────────────────────────────
    def _check_reminders(self):
        """Check for upcoming exams and show warnings."""
        for s in self.db.subjects:
            days = self.db.days_until_exam(s)
            if days is not None:
                if days == 0:
                    self.toast(f"🚨  {s['name']} exam is TODAY!", "error")
                elif days == 1:
                    self.toast(f"⚠️  {s['name']} exam is TOMORROW!", "warning")
                elif days == 3:
                    self.toast(f"📅  {s['name']} exam in 3 days.", "info")
        # Re-check every 2 hours
        self.after(7_200_000, self._check_reminders)

    def _toggle_mini_panel(self, show):
        if show:
            if not self.mini_panel:
                from ui.mini_panel import MiniPanel
                self.mini_panel = MiniPanel(self, self.db, self.colors, self._show_main_window, focus_ctrl=self.focus_controller)
            else:
                self.mini_panel.deiconify()
        else:
            if self.mini_panel:
                self.mini_panel.withdraw()

    def _show_main_window(self):
        self.deiconify()
        self.focus_force()

    def on_closing(self):
        """Handle window close event."""
        # Cleanup background services
        if hasattr(self, 'scheduler'):
            self.scheduler.stop()
            
        if hasattr(self, 'db') and hasattr(self.db, 'settings'):
            if self.db.settings.get("minimize_to_tray", False):
                self.withdraw()
                return
                
        self.quit()


# ════════════════════════════════════════════════════════════
#  Entry Point
# ════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import traceback
    try:
        app = StudyReminderApp()
        app.mainloop()
    except Exception:
        with open("crash_log.txt", "w") as f:
            traceback.print_exc(file=f)
        traceback.print_exc()
