# ============================================================
# Study Reminder Pro - Goals Widget
# File: ui/widgets/goals_widget.py
# ============================================================

import customtkinter as ctk
from core.theme import FONTS

class GoalsWidget(ctk.CTkFrame):
    """Live widget showing daily targets and completion rings."""
    def __init__(self, master, db, colors, goals_engine, **kwargs):
        super().__init__(master, fg_color=colors["bg_card"], corner_radius=14, 
                         border_width=1, border_color=colors["border"], **kwargs)
        self.db = db
        self.colors = colors
        self.goals_engine = goals_engine
        
        self._build()

    def _build(self):
        c = self.colors
        
        ctk.CTkLabel(self, text="🎯 Smart Goals", font=FONTS["title"], text_color=c["text_primary"]).pack(anchor="w", padx=16, pady=(12, 4))
        
        self.progress_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.progress_frame.pack(fill="x", padx=16, pady=4)
        
        # Pacing Text
        self.pacing_label = ctk.CTkLabel(self, text="Loading targets...", font=FONTS["body"], text_color=c["text_secondary"])
        self.pacing_label.pack(anchor="w", padx=16, pady=(4, 12))
        
        self.refresh()

    def refresh(self):
        """Update goals."""
        data = self.goals_engine.get_daily_goals_status()
        act = data["actual_mins"]
        tgt = data["target_mins"]
        pct = data["completion_pct"]
        
        for w in self.progress_frame.winfo_children(): w.destroy()
        
        # We can implement animated progress rings here later
        from ui.widgets import LinearProgressBar
        bar = LinearProgressBar(self.progress_frame, width=250, height=10, pct=pct, color=self.colors["accent"], bg=self.colors["progress_bg"])
        bar.pack(side="left", expand=True, fill="x")
        ctk.CTkLabel(self.progress_frame, text=f"{pct}%", font=FONTS["small"], text_color=self.colors["text_primary"]).pack(side="right", padx=(10, 0))
        
        if pct >= 100:
            self.pacing_label.configure(text=f"Goal met! ({act}/{tgt} min) 🎉", text_color=self.colors["success"])
        else:
            rem = tgt - act
            self.pacing_label.configure(text=f"Pacing: {rem} min remaining today.", text_color=self.colors["text_secondary"])
