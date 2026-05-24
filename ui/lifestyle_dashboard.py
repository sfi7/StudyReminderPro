# ============================================================
# Study Reminder Pro - Lifestyle & Growth Dashboard
# File: ui/lifestyle_dashboard.py
# ============================================================

import tkinter as tk
import customtkinter as ctk
from datetime import date
from core.theme import FONTS, MOTIVATIONAL_QUOTES
import random

class LifestyleDashboardView(ctk.CTkFrame):
    def __init__(self, master, db, colors, toast_fn, event_bus, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.db = db
        self.colors = colors
        self.toast = toast_fn
        self.events = event_bus
        self._widgets = []

        # Scrollable dashboard content
        self._scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self._scroll.pack(fill="both", expand=True, padx=24, pady=16)

        # Subscribe to database changes
        self.events.subscribe("TASK_COMPLETED", self._on_data_changed)
        self.events.subscribe("LECTURE_COMPLETED", self._on_data_changed)

        self._build()

    def _build(self):
        c = self.colors

        # ─── WELCOME BANNER ───
        welcome_card = ctk.CTkFrame(self._scroll, fg_color=c["bg_card"],
                                    border_width=1, border_color=c["border"],
                                    corner_radius=20)
        welcome_card.pack(fill="x", pady=(0, 16))

        student_name = self.db.settings.get("student_name", "Student")
        quote = random.choice(MOTIVATIONAL_QUOTES)

        lbl_welcome = ctk.CTkLabel(welcome_card, text=f"☀️ Good day, {student_name}!",
                                   font=FONTS["heading"], text_color="#10B981")
        lbl_welcome.pack(anchor="w", padx=24, pady=(20, 4))

        lbl_quote = ctk.CTkLabel(welcome_card, text=f'"{quote}"',
                                 font=FONTS["body"], text_color=c["text_secondary"],
                                 wraplength=700, justify="left")
        lbl_quote.pack(anchor="w", padx=24, pady=(0, 20))

        # ─── METRICS ROW ───
        metrics_frame = ctk.CTkFrame(self._scroll, fg_color="transparent")
        metrics_frame.pack(fill="x", pady=8)
        self._widgets.append(metrics_frame)
        metrics_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="equal")

        # Stat 1: Daily Focus
        mins_today = self.db.today_total_minutes()
        self._metric_card(metrics_frame, 0, "⏱️ Daily Focus", f"{mins_today} mins", "Invested in self-growth today", "#10B981")

        # Stat 2: Habit Consistency
        habits = self.db.habits
        today_str = date.today().isoformat()
        done = sum(1 for h in habits if today_str in h.get("history", []))
        total = len(habits)
        habit_text = f"{done} / {total} done" if total > 0 else "No habits"
        self._metric_card(metrics_frame, 1, "📅 Habits", habit_text, "Completed summer routines today", "#3B82F6")

        # Stat 3: Streak Badge
        streak = self.db.streaks["current"]
        self._metric_card(metrics_frame, 2, "🔥 Current Streak", f"{streak} days", "Consistent productivity streak", "#F59E0B")

        # ─── GRID CONTENT ───
        grid = ctk.CTkFrame(self._scroll, fg_color="transparent")
        grid.pack(fill="x", pady=16)
        self._widgets.append(grid)
        grid.grid_columnconfigure((0, 1), weight=1, uniform="equal")

        # Column 1: Skill / Course Progress
        self._build_skills_widget(grid, 0, c)

        # Column 2: Habits Check-off
        self._build_habits_widget(grid, 1, c)

    def _metric_card(self, parent, col, title, value, subtitle, accent):
        c = self.colors
        card = ctk.CTkFrame(parent, fg_color=c["bg_card"],
                            border_width=1, border_color=c["border"],
                            corner_radius=16, height=130)
        card.grid(row=0, column=col, padx=8, pady=4, sticky="nsew")
        card.grid_propagate(False)

        ctk.CTkLabel(card, text=title, font=FONTS["small"], text_color=c["text_muted"]).pack(anchor="w", padx=16, pady=(16, 2))
        ctk.CTkLabel(card, text=value, font=FONTS["subheading"], text_color=accent).pack(anchor="w", padx=16)
        ctk.CTkLabel(card, text=subtitle, font=FONTS["tiny"], text_color=c["text_secondary"]).pack(anchor="w", padx=16, pady=(4, 0))

    def _build_skills_widget(self, parent, col, c):
        widget_card = ctk.CTkFrame(parent, fg_color=c["bg_card"],
                                   border_width=1, border_color=c["border"],
                                   corner_radius=18, height=360)
        widget_card.grid(row=0, column=col, padx=8, pady=4, sticky="nsew")
        widget_card.grid_propagate(False)

        # Header
        hdr = ctk.CTkFrame(widget_card, fg_color="transparent")
        hdr.pack(fill="x", padx=16, pady=16)
        ctk.CTkLabel(hdr, text="🌱 Active Courses & Skills", font=FONTS["subheading"], text_color=c["text_primary"]).pack(side="left")
        
        # Navigate to skills button
        ctk.CTkButton(
            hdr, text="View All →", font=FONTS["tiny"], width=70, height=24,
            fg_color="transparent", text_color=c["accent"], hover_color=c["bg_secondary"],
            command=lambda: self._navigate_page("skills")
        ).pack(side="right")

        # Scrollable inner area for skills
        inner = ctk.CTkScrollableFrame(widget_card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=8, pady=(0, 16))

        active_skills = [s for s in self.db.skills if self.db.progress_pct_skill(s) < 100][:3]

        if not active_skills:
            ctk.CTkLabel(inner, text="No active courses currently.\nClick 'View All' to start learning!",
                         font=FONTS["body"], text_color=c["text_muted"]).pack(pady=40)
            return

        for s in active_skills:
            pct = self.db.progress_pct_skill(s)
            
            row = ctk.CTkFrame(inner, fg_color="transparent")
            row.pack(fill="x", pady=6)
            
            # Label
            lbl_f = ctk.CTkFrame(row, fg_color="transparent")
            lbl_f.pack(fill="x")
            ctk.CTkLabel(lbl_f, text=s["name"], font=FONTS["body"], text_color=c["text_primary"]).pack(side="left")
            
            # Start focus shortcut button
            ctk.CTkButton(
                lbl_f, text="🔥", width=28, height=28, corner_radius=14,
                fg_color=c["bg_secondary"], hover_color="#6C63FF", text_color="#6C63FF",
                command=lambda subj=s: self._start_focus(subj)
            ).pack(side="right", padx=6)
            
            # Progress bar
            bar_row = ctk.CTkFrame(row, fg_color="transparent")
            bar_row.pack(fill="x", pady=(2, 6))
            
            bar = ctk.CTkProgressBar(bar_row, height=6, fg_color=c["bg_secondary"], progress_color="#10B981")
            bar.pack(side="left", fill="x", expand=True)
            bar.set(pct / 100.0)
            
            ctk.CTkLabel(bar_row, text=f"{pct}%", font=FONTS["tiny"], text_color=c["text_muted"], width=30).pack(side="left", padx=8)

    def _build_habits_widget(self, parent, col, c):
        widget_card = ctk.CTkFrame(parent, fg_color=c["bg_card"],
                                   border_width=1, border_color=c["border"],
                                   corner_radius=18, height=360)
        widget_card.grid(row=0, column=col, padx=8, pady=4, sticky="nsew")
        widget_card.grid_propagate(False)

        # Header
        hdr = ctk.CTkFrame(widget_card, fg_color="transparent")
        hdr.pack(fill="x", padx=16, pady=16)
        ctk.CTkLabel(hdr, text="📅 Daily Habits Checklist", font=FONTS["subheading"], text_color=c["text_primary"]).pack(side="left")
        
        # Navigate to habits button
        ctk.CTkButton(
            hdr, text="Manage →", font=FONTS["tiny"], width=70, height=24,
            fg_color="transparent", text_color=c["accent"], hover_color=c["bg_secondary"],
            command=lambda: self._navigate_page("habits")
        ).pack(side="right")

        # Scrollable inner area for habits
        inner = ctk.CTkScrollableFrame(widget_card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=8, pady=(0, 16))

        habits = self.db.habits
        today_str = date.today().isoformat()

        if not habits:
            ctk.CTkLabel(inner, text="No habits tracked yet.\nClick 'Manage' to setup routines!",
                         font=FONTS["body"], text_color=c["text_muted"]).pack(pady=40)
            return

        for h in habits:
            is_done = today_str in h.setdefault("history", [])
            
            row = ctk.CTkFrame(inner, fg_color="transparent")
            row.pack(fill="x", pady=4)
            
            cb_var = tk.BooleanVar(value=is_done)
            
            def toggle_h(hid=h["id"]):
                self.db.toggle_habit(hid)
                self.toast("Habit updated!", "success")
                self.refresh()

            cb = ctk.CTkCheckBox(
                row, text=h["name"], font=FONTS["body"], variable=cb_var,
                fg_color="#10B981", hover_color="#0D9488", text_color=c["text_primary"],
                border_color=c["border"], border_width=2, command=toggle_h
            )
            cb.pack(side="left", padx=8, pady=4)

    def _start_focus(self, s):
        app = self.winfo_toplevel()
        if hasattr(app, 'navigate'):
            app.navigate("pomodoro", subject_id=s["id"])

    def _navigate_page(self, key):
        app = self.winfo_toplevel()
        if hasattr(app, 'navigate'):
            app.navigate(key)

    def _on_data_changed(self, *_):
        self.refresh()

    def cleanup(self):
        """Unsubscribe from event bus to prevent memory leaks."""
        self.events.unsubscribe("TASK_COMPLETED", self._on_data_changed)
        self.events.unsubscribe("LECTURE_COMPLETED", self._on_data_changed)

    def refresh(self):
        """Rebuild the dashboard content cleanly if version changes."""
        current_data_ver = self.db.data_version
        current_settings_ver = self.db.settings_version
        if (getattr(self, "_last_data_version", -1) == current_data_ver and 
            getattr(self, "_last_settings_version", -1) == current_settings_ver):
            return
            
        self._last_data_version = current_data_ver
        self._last_settings_version = current_settings_ver

        for w in self._scroll.winfo_children():
            try:
                w.destroy()
            except Exception:
                pass
        self._widgets.clear()
        self._build()
