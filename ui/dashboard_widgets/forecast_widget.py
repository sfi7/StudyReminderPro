# ============================================================
# Study Reminder Pro - Forecast Widget
# File: ui/widgets/forecast_widget.py
# ============================================================

import customtkinter as ctk
from core.theme import FONTS

class ForecastWidget(ctk.CTkFrame):
    """Live widget showing syllabus completion estimates."""
    def __init__(self, master, db, colors, forecast_engine, **kwargs):
        super().__init__(master, fg_color=colors["bg_card"], corner_radius=14, 
                         border_width=1, border_color=colors["border"], **kwargs)
        self.db = db
        self.colors = colors
        self.forecast_engine = forecast_engine
        
        self._build()

    def _build(self):
        c = self.colors
        
        ctk.CTkLabel(self, text="📈 Live Forecasts", font=FONTS["title"], text_color=c["text_primary"]).pack(anchor="w", padx=16, pady=(12, 4))
        
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=16, pady=4)
        
        self.refresh()

    def refresh(self):
        for w in self.content_frame.winfo_children(): w.destroy()
        
        subjects = self.db.subjects
        active_subjects = [
            s for s in subjects
            if self.db.days_until_exam(s) is None or self.db.days_until_exam(s) >= 0
        ]
        if not active_subjects:
            ctk.CTkLabel(self.content_frame, text="No active subjects to forecast.", font=FONTS["small"], text_color=self.colors["text_muted"]).pack(anchor="w", pady=8)
            return
            
        # Just show the most delayed or first 3 subjects for compact UI
        for subj in active_subjects[:3]:
            row = ctk.CTkFrame(self.content_frame, fg_color="transparent")
            row.pack(fill="x", pady=4)
            
            f = self.forecast_engine.forecast_completion(subj)
            date_str = f["projected_date"].strftime("%b %d") if f["projected_date"] else "N/A"
            status_color = self.colors["danger"] if f["status"] == "Overdue Risk" else self.colors["success"]
            
            ctk.CTkLabel(row, text=f"{subj['icon']} {subj['name']}", font=FONTS["body"], text_color=self.colors["text_primary"]).pack(side="left")
            ctk.CTkLabel(row, text=f"{date_str} ({f['status']})", font=FONTS["small"], text_color=status_color).pack(side="right")
