# ============================================================
# Study Reminder Pro - Dashboard View
# File: ui/dashboard.py
# ============================================================

import tkinter as tk
import customtkinter as ctk
import random
from datetime import date, datetime
from core.theme import FONTS, MOTIVATIONAL_QUOTES, STUDY_TIPS
from ui.widgets import (AnimatedProgressBar, LinearProgressBar,
                        GlassCard, ExamCountdownBadge, LiveCountdown)
from analytics.goals_engine import GoalsEngine
from analytics.forecast_engine import ForecastEngine
from analytics.analytics_engine import AnalyticsEngine

from ui.dashboard_widgets.productivity_widget import ProductivityWidget
from ui.dashboard_widgets.burnout_widget import BurnoutWidget
from ui.dashboard_widgets.goals_widget import GoalsWidget
from ui.dashboard_widgets.forecast_widget import ForecastWidget
from ui.dashboard_widgets.pressure_widget import PressureWidget
from ui.dashboard_widgets.heatmap_widget import HeatmapWidget
from ui.dashboard_widgets.level_widget import LevelWidget
from analytics.gamification_engine import GamificationEngine

class DashboardView(ctk.CTkScrollableFrame):
    """Main dashboard showing overview, stats, and alerts."""

    def __init__(self, master, db, colors, toast_fn, events, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.db = db
        self.colors = colors
        self.toast = toast_fn
        self.events = events
        
        self.analytics_engine = AnalyticsEngine(self.db)
        self.goals_engine = GoalsEngine(self.db)
        self.forecast_engine = ForecastEngine(self.db, self.analytics_engine)
        self.gamification_engine = GamificationEngine(self.db)
        
        self._widgets = []
        self._build()
        
        # Subscribe to relevant events
        self.events.subscribe("TASK_COMPLETED", self._on_data_changed)
        self.events.subscribe("LECTURE_COMPLETED", self._on_data_changed)

    def _on_data_changed(self, _data=None):
        self._perform_data_refresh()
        if hasattr(self, '_refresh_subjects'):
            self._refresh_subjects()
            
    def _perform_data_refresh(self):
        if not self.winfo_exists():
            return
        try:
            self.goals_widget.refresh()
            self.prod_widget.refresh()
            self.pressure_widget.refresh()
            self.forecast_widget.refresh()
            self.burnout_widget.refresh()
            self.heatmap_widget.refresh()
        except Exception:
            pass

    def cleanup(self):
        """Unsubscribe from events to prevent memory leaks."""
        if self.events:
            self.events.unsubscribe("LECTURE_COMPLETED", self._on_data_changed)
            self.events.unsubscribe("TASK_COMPLETED", self._on_data_changed)

    def _build(self):
        c = self.colors
        
        # ── Motivational Header ───────────────────────────────
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(20, 10))
        self._widgets.append(header)

        hour = datetime.now().hour
        greeting = "Good Morning" if hour < 12 else ("Good Afternoon" if hour < 17 else "Good Evening")
        name = self.db.settings.get("student_name", "Student")

        ctk.CTkLabel(header, text=f"{greeting}, {name}! 👋",
                     font=FONTS["heading"], text_color=c["text_primary"],
                     anchor="w").pack(side="left")

        self.quote_label = ctk.CTkLabel(header, text=f"✨ {random.choice(MOTIVATIONAL_QUOTES)}", 
                                        font=("Segoe UI", 13, "italic"), text_color=c["accent_light"])
        self.quote_label.pack(side="left", padx=20)
        
        # Level Widget in Header
        self.lvl_widget = LevelWidget(header, self.db, self.colors, self.gamification_engine)
        self.lvl_widget.pack(side="right")
        
        # ── Modular Grid System ──────────────────────────────
        grid = ctk.CTkFrame(self, fg_color="transparent")
        grid.pack(fill="x", padx=24, pady=10)
        self._widgets.append(grid)
        grid.grid_columnconfigure((0, 1), weight=1, uniform="col")
        
        # Row 0: Goals & Productivity
        self.goals_widget = GoalsWidget(grid, self.db, self.colors, self.goals_engine)
        self.goals_widget.grid(row=0, column=0, sticky="nsew", padx=(0, 12), pady=(0, 24))
        
        self.prod_widget = ProductivityWidget(grid, self.db, self.colors, self.analytics_engine)
        self.prod_widget.grid(row=0, column=1, sticky="nsew", padx=(12, 0), pady=(0, 24))
        
        # Row 1: Exam Pressure & Forecasts
        self.pressure_widget = PressureWidget(grid, self.db, self.colors)
        self.pressure_widget.grid(row=1, column=0, sticky="nsew", padx=(0, 12), pady=(0, 24))
        
        self.forecast_widget = ForecastWidget(grid, self.db, self.colors, self.forecast_engine)
        self.forecast_widget.grid(row=1, column=1, sticky="nsew", padx=(12, 0), pady=(0, 24))
        
        # Row 2: Burnout Insights (Spans 2 columns)
        self.burnout_widget = BurnoutWidget(grid, self.db, self.colors, self.goals_engine, self.analytics_engine)
        self.burnout_widget.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=(0, 24))
        
        # Row 3: Heatmap (Spans 2 columns)
        self.heatmap_widget = HeatmapWidget(grid, self.db, self.colors, self.analytics_engine)
        self.heatmap_widget.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=(0, 24))
        
        # ── Subject Progress Overview ────────────────────────
        lbl = ctk.CTkLabel(self, text="📋 Subject Overview",
                     font=FONTS["subheading"], text_color=c["text_primary"],
                     anchor="w")
        lbl.pack(fill="x", padx=24, pady=(10, 6))
        self._widgets.append(lbl)

        self.subjects_container = ctk.CTkFrame(self, fg_color="transparent")
        self.subjects_container.pack(fill="x", padx=0, pady=0)
        self._widgets.append(self.subjects_container)
        self._refresh_subjects()

    def _refresh_subjects(self):
        c = self.colors
        
        # Clear existing subject widgets
        for widget in self.subjects_container.winfo_children():
            widget.destroy()

        active_subjects = []
        archived_subjects = []
        for s in self.db.subjects:
            days = self.db.days_until_exam(s)
            if days is None or days >= 0:
                active_subjects.append(s)
            else:
                archived_subjects.append(s)

        if not active_subjects:
            empty = ctk.CTkFrame(self.subjects_container, fg_color=c["bg_card"], corner_radius=16)
            empty.pack(fill="x", padx=24, pady=4)
            ctk.CTkLabel(empty, text="No active upcoming exams! Relax or add a new subject 📝",
                         font=FONTS["body"], text_color=c["text_secondary"]).pack(pady=40)
        else:
            subj_grid = ctk.CTkFrame(self.subjects_container, fg_color="transparent")
            subj_grid.pack(fill="x", padx=24)
            subj_grid.grid_columnconfigure((0, 1), weight=1, uniform="subj")
            for i, subj in enumerate(active_subjects):
                row, col = divmod(i, 2)
                self._subject_mini_card(subj_grid, subj, row, col)
                
        if archived_subjects:
            self._dashboard_archive_btn = ctk.CTkButton(self.subjects_container, text="▶ Archived Exams",
                         font=FONTS["subheading"], fg_color="transparent", text_color=c["text_secondary"],
                         hover_color=c["bg_secondary"], anchor="w",
                         command=self._toggle_dashboard_archive)
            self._dashboard_archive_btn.pack(fill="x", padx=24, pady=(20, 6))
            
            self._dashboard_archive_container = ctk.CTkFrame(self.subjects_container, fg_color="transparent")
            self._dashboard_archive_container.pack(fill="x", padx=24)
            self._dashboard_archive_container.pack_forget()
            self._dashboard_archive_visible = False
            
            self._dashboard_archive_container.grid_columnconfigure((0, 1), weight=1, uniform="subj")
            for i, subj in enumerate(archived_subjects):
                row, col = divmod(i, 2)
                self._subject_mini_card(self._dashboard_archive_container, subj, row, col, is_archived=True)

    def _toggle_dashboard_archive(self):
        if self._dashboard_archive_visible:
            self._dashboard_archive_container.pack_forget()
            self._dashboard_archive_btn.configure(text="▶ Archived Exams")
            self._dashboard_archive_visible = False
        else:
            self._dashboard_archive_container.pack(fill="x", padx=24)
            self._dashboard_archive_btn.configure(text="▼ Archived Exams")
            self._dashboard_archive_visible = True

    def _subject_mini_card(self, parent, subj, row, col, is_archived=False):
        c = self.colors
        pct = self.db.progress_pct(subj)
        
        card = ctk.CTkFrame(parent, fg_color=c["bg_card"], corner_radius=16,
                            border_width=1, border_color=c["border"])
        card.grid(row=row, column=col, sticky="nsew",
                  padx=(0 if col == 0 else 12, 0), pady=8)

        # Header row
        h_row = ctk.CTkFrame(card, fg_color="transparent")
        h_row.pack(fill="x", padx=14, pady=(12, 4))

        icon_bg = ctk.CTkFrame(h_row, width=36, height=36, corner_radius=10, fg_color=subj["color"])
        icon_bg.pack(side="left")
        icon_bg.pack_propagate(False)
        ctk.CTkLabel(icon_bg, text=subj["icon"], font=("Segoe UI", 16)).pack(expand=True)

        ctk.CTkLabel(h_row, text=subj["name"], font=FONTS["title"], text_color=c["text_primary"]).pack(side="left", padx=10)
        
        # Start Focus Button
        ctk.CTkButton(h_row, text="🔥", width=32, height=32, corner_radius=16,
                      fg_color=c["bg_secondary"], hover_color=c["accent"],
                      text_color=c["accent"], command=lambda s=subj: self._start_focus(s)).pack(side="right", padx=6)

        if not is_archived:
            LiveCountdown(h_row, self.db, subj, c).pack(side="right")

        # Progress bar
        if not is_archived:
            bar_row = ctk.CTkFrame(card, fg_color="transparent")
            bar_row.pack(fill="x", padx=14, pady=(2, 0))
            bar = LinearProgressBar(bar_row, width=250, height=8, pct=pct, color=subj["color"], bg=c["progress_bg"])
            bar.pack(side="left", fill="x", expand=True, pady=4)
            ctk.CTkLabel(bar_row, text=f"{pct:.0f}%", font=FONTS["tiny"], text_color=c["text_secondary"], width=38).pack(side="right")

        # Info row
        info_row = ctk.CTkFrame(card, fg_color="transparent")
        info_row.pack(fill="x", padx=14, pady=(2, 12))
        rem = self.db.remaining_lectures(subj)
        ctk.CTkLabel(info_row, text=f"✅ {subj.get('completed_lectures', 0)} done", font=FONTS["tiny"], text_color=c["success"]).pack(side="left")
        ctk.CTkLabel(info_row, text=f"📖 {rem} left", font=FONTS["tiny"], text_color=c["text_muted"]).pack(side="left", padx=12)

        # Forecast Engine Integration
        forecast = self.forecast_engine.forecast_completion(subj)
        status_color = c["danger"] if forecast["status"] == "Overdue Risk" else c["success"]
        ctk.CTkLabel(info_row, text=f"🎯 {forecast['status']}", font=FONTS["tiny"], text_color=status_color).pack(side="right")

    def _start_focus(self, subj):
        app = self.winfo_toplevel()
        if hasattr(app, 'navigate'):
            app.navigate("pomodoro")

    def refresh(self):
        """Safely rebuild the dashboard contents."""
        for w in self._widgets:
            try:
                w.destroy()
            except Exception:
                pass
        self._widgets.clear()
        self._build()
