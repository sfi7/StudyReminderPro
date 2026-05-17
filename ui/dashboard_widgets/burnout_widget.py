# ============================================================
# Study Reminder Pro - Burnout Widget
# File: ui/widgets/burnout_widget.py
# ============================================================

import customtkinter as ctk
from core.theme import FONTS

class BurnoutWidget(ctk.CTkFrame):
    """Live widget showing burnout risk and smart suggestions."""
    def __init__(self, master, db, colors, goals_engine, analytics_engine, **kwargs):
        super().__init__(master, fg_color=colors["bg_card"], corner_radius=14, 
                         border_width=1, border_color=colors["border"], **kwargs)
        self.db = db
        self.colors = colors
        self.goals_engine = goals_engine
        self.ae = analytics_engine
        
        self._build()

    def _build(self):
        c = self.colors
        
        self.header_label = ctk.CTkLabel(self, text="🧠 AI Insights", font=FONTS["title"], text_color=c["text_primary"])
        self.header_label.pack(anchor="w", padx=16, pady=(12, 2))
        
        self.risk_label = ctk.CTkLabel(self, text="Risk: Calculating...", font=FONTS["small"], text_color=c["text_muted"])
        self.risk_label.pack(anchor="w", padx=16, pady=0)
        
        self.suggestion_label = ctk.CTkLabel(self, text="", font=FONTS["body"], text_color=c["text_secondary"], wraplength=280, justify="left")
        self.suggestion_label.pack(anchor="w", fill="x", padx=16, pady=(8, 12))
        
        self.refresh()

    def refresh(self):
        """Update burnout risk from the Goals Engine."""
        risk, level, suggestion = self.goals_engine.analyze_burnout_risk(self.ae)
        c = self.colors
        
        color = c["danger"] if risk > 70 else (c["warning"] if risk > 40 else c["success"])
        
        self.configure(border_color=color)
        self.header_label.configure(text_color=color)
        self.risk_label.configure(text=f"Burnout Risk: {risk}% ({level})")
        self.suggestion_label.configure(text=suggestion)
