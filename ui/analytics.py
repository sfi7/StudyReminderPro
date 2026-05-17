# ============================================================
# Study Reminder Pro - Analytics / Statistics View
# File: ui/analytics.py
# ============================================================

import tkinter as tk
import customtkinter as ctk
from datetime import date, timedelta
from tkinter import filedialog
from core.theme import FONTS

# New Intelligence Engines
from analytics.analytics_engine import AnalyticsEngine
from analytics.productivity_engine import ProductivityEngine
from analytics.predictions import PredictionsEngine
from analytics.charts import ChartsEngine
from analytics.heatmap import GitHubHeatmap
from analytics.report_generator import ReportGenerator


class AnalyticsView(ctk.CTkFrame):
    """
    Premium Analytics & Productivity Dashboard.
    Data-rich interface combining charts, heatmaps, and smart metrics.
    """

    def __init__(self, master, db, colors, toast_fn, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.db = db
        self.colors = colors
        self.toast = toast_fn
        self._widgets = []
        
        # Instantiate Engines
        self.ae = AnalyticsEngine(self.db)
        self.pe = ProductivityEngine(self.ae, self.db)
        self.pred = PredictionsEngine(self.db)
        
        self.app = self.winfo_toplevel()
        self.tm = getattr(self.app, 'theme_manager', None)
        self.ce = ChartsEngine(self.tm) if self.tm else None
        self.rg = ReportGenerator(self.ae)

        self._scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self._scroll.pack(fill="both", expand=True)
        
        # Performance: Defer heavy rendering
        self._show_loading()
        self._deferred_job = self.after(100, self._deferred_build)

    def _show_loading(self):
        self.loading_frame = ctk.CTkFrame(self._scroll, fg_color="transparent")
        self.loading_frame.pack(fill="both", expand=True, pady=100)
        ctk.CTkLabel(self.loading_frame, text="🧠", font=("Segoe UI", 48)).pack(pady=10)
        ctk.CTkLabel(self.loading_frame, text="Analyzing your productivity data...", 
                     font=FONTS["body"], text_color=self.colors["text_muted"]).pack()

    def _deferred_build(self):
        if not self.winfo_exists(): return
        if hasattr(self, 'loading_frame'):
            try: self.loading_frame.destroy()
            except: pass
        self._build()

    def refresh(self):
        """Safely refresh the analytics view."""
        if hasattr(self, "_deferred_job") and self._deferred_job:
            self.after_cancel(self._deferred_job)
            self._deferred_job = None
            
        # Recreate charts engine to pick up new theme colors
        self.ce = ChartsEngine(self.tm) if self.tm else None
        
        for w in self._widgets:
            try: w.destroy()
            except: pass
        self._widgets.clear()
        
        self._show_loading()
        self._deferred_job = self.after(50, self._deferred_build)

    def _build(self):
        c = self.colors
        parent = self._scroll

        # ── Header & Export ──
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(20, 10))
        self._widgets.append(header)
        
        ctk.CTkLabel(header, text="🧠  Intelligence & Analytics",
                     font=FONTS["heading"], text_color=c["text_primary"]).pack(side="left")

        ctk.CTkButton(header, text="📥 Export CSV", font=FONTS["small"],
                      width=120, height=32, corner_radius=8,
                      fg_color=c["bg_secondary"], hover_color=c["accent"], text_color=c["text_primary"],
                      command=self._export_data).pack(side="right")

        # ── Smart Recommendations Banner ──
        recs = self.pe.generate_recommendations()
        if recs:
            banner = ctk.CTkFrame(parent, fg_color=c["bg_card"], corner_radius=16, 
                                  border_width=1, border_color=c["accent"])
            banner.pack(fill="x", padx=24, pady=(0, 24))
            self._widgets.append(banner)
            ctk.CTkLabel(banner, text="💡 " + recs[0], font=FONTS["body"],
                         text_color=c["text_primary"]).pack(pady=16, padx=20, anchor="w")

        # ── Top KPI row ──
        kpi_row = ctk.CTkFrame(parent, fg_color="transparent")
        kpi_row.pack(fill="x", padx=24)
        self._widgets.append(kpi_row)
        kpi_row.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="kpi")

        score = self.pe.calculate_focus_score()
        best_hour = self.pe.get_most_productive_hour()
        hour_str = f"{best_hour}:00" if best_hour is not None else "N/A"
        total_mins = self.ae.get_total_study_minutes()
        
        kpis = [
            ("🎯", "Focus Score", f"{score}/100", c["accent"]),
            ("⏱️", "Total Studied", f"{total_mins} min", c["info"]),
            ("⚡", "Best Hour", f"{hour_str}", c["warning"]),
            ("🔥", "Current Streak", f"{self.db.streaks.get('current', 0)} days", c["success"]),
        ]
        
        for col, (icon, title, val, accent) in enumerate(kpis):
            self._kpi_card(kpi_row, col, icon, title, val, accent)

        # ── Charts Row ──
        if self.ce:
            chart_row = ctk.CTkFrame(parent, fg_color="transparent")
            chart_row.pack(fill="x", padx=24, pady=16)
            self._widgets.append(chart_row)
            chart_row.grid_columnconfigure(0, weight=2)
            chart_row.grid_columnconfigure(1, weight=1)

            # Weekly Trend
            trend_frame = ctk.CTkFrame(chart_row, fg_color=c["bg_card"], corner_radius=12, border_width=1, border_color=c["border"])
            trend_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
            self._section(trend_frame, "📈 Weekly Trend", c, pad_x=16)
            
            activity_data = self.ae.get_daily_activity(days=7)
            chart_widget = self.ce.render_weekly_trend(trend_frame, activity_data)
            chart_widget.pack(fill="both", expand=True, padx=10, pady=10)

            # Subject Distribution
            dist_frame = ctk.CTkFrame(chart_row, fg_color=c["bg_card"], corner_radius=12, border_width=1, border_color=c["border"])
            dist_frame.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
            self._section(dist_frame, "📋 Distribution", c, pad_x=16)
            
            dist_data = self.ae.get_subject_distribution()
            pie_widget = self.ce.render_subject_distribution(dist_frame, dist_data, self.db.subjects)
            pie_widget.pack(fill="both", expand=True, padx=10, pady=10)

        # ── 365-Day Consistency Heatmap ──
        heat_frame = ctk.CTkFrame(parent, fg_color=c["bg_card"], corner_radius=16, border_width=1, border_color=c["border"])
        heat_frame.pack(fill="x", padx=24, pady=16)
        self._widgets.append(heat_frame)
        self._section(heat_frame, "🟩 Consistency Heatmap (Last 365 Days)", c, pad_x=20)
        
        heatmap = GitHubHeatmap(heat_frame, self.tm, self.ae.get_daily_activity(365), height=140)
        heatmap.pack(fill="x", padx=20, pady=(0, 20))
        heatmap.draw_heatmap()

        # ── Exam Pressure ──
        if self.db.subjects:
            sec_lbl = self._section(parent, "🚨 Exam Pressure Analysis", c, pad_x=24)
            self._widgets.append(sec_lbl)
            for subj in self.db.subjects:
                if subj.get("exam_date"):
                    self._exam_pressure_row(parent, subj, c)

        spacer = ctk.CTkFrame(parent, fg_color="transparent", height=24)
        spacer.pack()
        self._widgets.append(spacer)

    def _kpi_card(self, parent, col, icon, title, val, accent):
        c = self.colors
        card = ctk.CTkFrame(parent, fg_color=c["bg_card"], corner_radius=12,
                            border_width=1, border_color=c["border"])
        card.grid(row=0, column=col, sticky="nsew",
                  padx=(0 if col == 0 else 8, 0), pady=4)
        ctk.CTkLabel(card, text=icon, font=("Segoe UI", 24)).pack(anchor="w", padx=16, pady=(14, 0))
        ctk.CTkLabel(card, text=val,  font=("Segoe UI", 20, "bold"),
                     text_color=accent).pack(anchor="w", padx=16, pady=(4, 0))
        ctk.CTkLabel(card, text=title, font=FONTS["small"],
                     text_color=c["text_secondary"]).pack(anchor="w", padx=16, pady=(0, 14))

    def _section(self, parent, title, c, pad_x=0):
        lbl = ctk.CTkLabel(parent, text=title, font=FONTS["subheading"],
                      text_color=c["text_primary"],
                      anchor="w")
        lbl.pack(fill="x", padx=pad_x, pady=(16, 8))
        return lbl

    def _exam_pressure_row(self, parent, subj, c):
        res = self.pred.analyze_exam_pressure(subj)
        
        card = ctk.CTkFrame(parent, fg_color=c["bg_card"], corner_radius=16,
                            border_width=1, border_color=c["border"])
        card.pack(fill="x", padx=24, pady=8)
        self._widgets.append(card)
        
        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=12)

        ctk.CTkLabel(row, text=subj.get("icon", "📚") + " " + subj["name"], font=FONTS["title"],
                     text_color=c["text_primary"], width=180, anchor="w").pack(side="left")

        # Status badge
        bg_col = c.get(res["color"], c["info"])
        badge = ctk.CTkFrame(row, fg_color=bg_col, corner_radius=6)
        badge.pack(side="left", padx=10)
        ctk.CTkLabel(badge, text=res["status"], font=FONTS["tiny"], text_color="#FFFFFF").pack(padx=8, pady=2)

        ctk.CTkLabel(row, text=res["message"], font=FONTS["small"],
                     text_color=c["text_secondary"]).pack(side="left", padx=10)
        
        # New AI Prediction
        pred_date = self.pred.predict_completion_date(subj, self.ae)
        ctk.CTkLabel(row, text=f"Predicted End: {pred_date}", font=FONTS["tiny"],
                     text_color=c["accent_light"]).pack(side="right", padx=10)

    def _export_data(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            title="Export Analytics Data",
            initialfile=f"StudyReminderPro_Export_{date.today().strftime('%Y%m%d')}.csv"
        )
        if filepath:
            success, msg = self.rg.export_to_csv(filepath)
            if success:
                self.toast("Data exported successfully!", "success")
            else:
                self.toast(f"Export failed: {msg}", "error")
