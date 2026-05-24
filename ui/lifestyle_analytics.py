# ============================================================
# Study Reminder Pro - Lifestyle & Growth Analytics
# File: ui/lifestyle_analytics.py
# ============================================================

import tkinter as tk
import customtkinter as ctk
from datetime import date, datetime
from core.theme import FONTS

class LifestyleAnalyticsView(ctk.CTkFrame):
    def __init__(self, master, db, colors, toast_fn, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.db = db
        self.colors = colors
        self.toast = toast_fn
        self._widgets = []

        # Scrollable container
        self._scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self._scroll.pack(fill="both", expand=True, padx=24, pady=16)

        self._build()

    def _build(self):
        c = self.colors

        # ─── OVERVIEW METRICS ───
        over_frame = ctk.CTkFrame(self._scroll, fg_color="transparent")
        over_frame.pack(fill="x", pady=(0, 16))
        self._widgets.append(over_frame)
        over_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="equal")

        # total hours focused all-time
        sessions = self.db._sessions_db.sessions
        total_mins = sum(s.get("duration_minutes", 0) for s in sessions)
        total_hrs = round(total_mins / 60.0, 1)

        self._stat_card(over_frame, 0, "🌱 Total Self-Growth", f"{total_hrs} hrs", "Total hours invested all-time", "#10B981")

        # Habit streak
        habits = self.db.habits
        max_streak = 0
        for h in habits:
            max_streak = max(max_streak, self.db.get_habit_streak(h))

        self._stat_card(over_frame, 1, "🔥 Best Habit Streak", f"{max_streak} days", "Max consecutive habit days", "#F59E0B")

        # Completed courses
        skills = self.db.skills
        completed = sum(1 for s in skills if self.db.progress_pct_skill(s) >= 100)
        total_skills = len(skills)
        courses_text = f"{completed} / {total_skills}"
        self._stat_card(over_frame, 2, "🎓 Courses Finished", courses_text, "Skills completely acquired", "#3B82F6")

        # ─── LEVEL & XP GROWTH CARD ───
        xp_card = ctk.CTkFrame(self._scroll, fg_color=c["bg_card"],
                               border_width=1, border_color=c["border"],
                               corner_radius=20)
        xp_card.pack(fill="x", pady=8)
        self._widgets.append(xp_card)

        # XP calculation
        gamification = self.db._store.app_data.setdefault("gamification", {})
        lvl = gamification.get("level", 1)
        xp = gamification.get("xp", 0)
        xp_needed = lvl * 1000
        xp_pct = min(1.0, xp / xp_needed) if xp_needed > 0 else 1.0

        ctk.CTkLabel(xp_card, text=f"🏆 Personal Growth Level: {lvl}", font=FONTS["subheading"], text_color="#10B981").pack(anchor="w", padx=24, pady=(20, 4))
        
        xp_bar_row = ctk.CTkFrame(xp_card, fg_color="transparent")
        xp_bar_row.pack(fill="x", padx=24, pady=(0, 20))
        
        xp_bar = ctk.CTkProgressBar(xp_bar_row, height=8, fg_color=c["bg_secondary"], progress_color="#10B981")
        xp_bar.pack(side="left", fill="x", expand=True)
        xp_bar.set(xp_pct)
        
        ctk.CTkLabel(xp_bar_row, text=f"{xp}/{xp_needed} XP", font=FONTS["small"], text_color=c["text_primary"], width=80).pack(side="left", padx=12)

        # ─── DETAILED COURSE LISTING ───
        if skills:
            skills_section = ctk.CTkFrame(self._scroll, fg_color=c["bg_card"],
                                           border_width=1, border_color=c["border"],
                                           corner_radius=20)
            skills_section.pack(fill="x", pady=12)
            self._widgets.append(skills_section)
            
            ctk.CTkLabel(skills_section, text="📊 Skills Progress & Completion Breakdown",
                         font=FONTS["subheading"], text_color=c["text_primary"]).pack(anchor="w", padx=24, pady=(20, 12))
            
            for s in skills:
                pct = self.db.progress_pct_skill(s)
                
                row = ctk.CTkFrame(skills_section, fg_color="transparent")
                row.pack(fill="x", padx=24, pady=8)
                
                ctk.CTkLabel(row, text=s["name"], font=FONTS["body"], text_color=c["text_primary"]).pack(side="left")
                ctk.CTkLabel(row, text=f"{pct}% complete", font=FONTS["small"], text_color=c["text_secondary"]).pack(side="right")
                
                p_bar = ctk.CTkProgressBar(skills_section, height=4, fg_color=c["bg_secondary"], progress_color="#10B981")
                p_bar.pack(fill="x", padx=24, pady=(0, 12))
                p_bar.set(pct / 100.0)

        # ─── DATA EXPORT ───
        export_btn = ctk.CTkButton(
            self._scroll, text="📥 Export Summer Analytics Data (CSV)", font=FONTS["body"],
            fg_color=c["bg_secondary"], hover_color=c["border"], text_color=c["text_primary"],
            corner_radius=10, height=40,
            command=self._export_lifestyle_csv
        )
        export_btn.pack(fill="x", pady=20)
        self._widgets.append(export_btn)

    def _stat_card(self, parent, col, title, value, subtitle, accent):
        c = self.colors
        card = ctk.CTkFrame(parent, fg_color=c["bg_card"],
                            border_width=1, border_color=c["border"],
                            corner_radius=16, height=130)
        card.grid(row=0, column=col, padx=8, pady=4, sticky="nsew")
        card.grid_propagate(False)

        ctk.CTkLabel(card, text=title, font=FONTS["small"], text_color=c["text_muted"]).pack(anchor="w", padx=16, pady=(16, 2))
        ctk.CTkLabel(card, text=value, font=FONTS["subheading"], text_color=accent).pack(anchor="w", padx=16)
        ctk.CTkLabel(card, text=subtitle, font=FONTS["tiny"], text_color=c["text_secondary"]).pack(anchor="w", padx=16, pady=(4, 0))

    def _export_lifestyle_csv(self):
        import csv
        from tkinter import filedialog
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            title="Export Lifestyle Analytics Data",
            initialfile=f"GrowthReminderPro_Export_{date.today().strftime('%Y%m%d')}.csv"
        )
        if not filepath:
            return

        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["--- Summer Skills / Courses ---"])
                writer.writerow(["ID", "Name", "Total Modules", "Completed Modules", "Target Date", "Difficulty"])
                for s in self.db.skills:
                    writer.writerow([s["id"], s["name"], s["total_modules"], s["completed_modules"], s.get("target_date"), s.get("difficulty")])
                
                writer.writerow([])
                writer.writerow(["--- Daily Habits Log ---"])
                writer.writerow(["ID", "Name", "Created At", "Completion Dates History"])
                for h in self.db.habits:
                    writer.writerow([h["id"], h["name"], h["created_at"], ";".join(h.get("history", []))])

            self.toast("Growth data exported successfully!", "success")
        except Exception as e:
            self.toast(f"Export failed: {str(e)}", "error")

    def refresh(self):
        """Update view data dynamically."""
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
