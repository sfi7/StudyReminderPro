# ============================================================
# Study Reminder Pro - Exam Pressure Widget
# File: ui/widgets/pressure_widget.py
# ============================================================

import customtkinter as ctk
from core.theme import FONTS
from ui.widgets import LiveCountdown

class PressureWidget(ctk.CTkFrame):
    """Live widget showing upcoming exams and urgency."""
    def __init__(self, master, db, colors, **kwargs):
        super().__init__(master, fg_color=colors["bg_card"], corner_radius=14, 
                         border_width=1, border_color=colors["border"], **kwargs)
        self.db = db
        self.colors = colors
        
        self._build()

    def _build(self):
        c = self.colors
        
        self.header = ctk.CTkLabel(self, text="⚠️ Exam Pressure Center", font=FONTS["title"], text_color=c["text_primary"])
        self.header.pack(anchor="w", padx=16, pady=(12, 4))
        
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=16, pady=4)
        
        self.refresh()

    def refresh(self):
        for w in self.content_frame.winfo_children(): w.destroy()
        
        subjects = self.db.subjects
        upcoming = [
            (s, self.db.days_until_exam(s))
            for s in subjects
            if self.db.days_until_exam(s) is not None and self.db.days_until_exam(s) >= 0
        ]
        upcoming.sort(key=lambda x: x[1])
        
        if not upcoming:
            self.header.configure(text="✅ No Upcoming Exams")
            self.configure(border_color=self.colors["border"])
            return
            
        most_urgent_days = upcoming[0][1]
        if most_urgent_days <= 3:
            self.configure(border_color=self.colors["danger"])
            self.header.configure(text_color=self.colors["danger"])
        elif most_urgent_days <= 14:
            self.configure(border_color=self.colors["warning"])
            self.header.configure(text_color=self.colors["warning"])
            
        for subj, days in upcoming[:3]:
            row = ctk.CTkFrame(self.content_frame, fg_color="transparent")
            row.pack(fill="x", pady=4)
            
            rem_lec = max(0, subj.get("total_lectures", 0) - subj.get("completed_lectures", 0))
            if days > 0 and rem_lec > 0:
                req_per_day = rem_lec / days
                pace_str = f"{req_per_day:.1f} lec/day"
            else:
                pace_str = "Completed" if rem_lec == 0 else "Exam Today!"
                
            ctk.CTkLabel(row, text=f"{subj['icon']} {subj['name']} - {pace_str}", font=FONTS["body"], text_color=self.colors["text_primary"]).pack(side="left")
            LiveCountdown(row, self.db, subj, self.colors).pack(side="right")
