# ============================================================
# Study Reminder Pro - Productivity Widget
# File: ui/widgets/productivity_widget.py
# ============================================================

import customtkinter as ctk
from core.theme import FONTS

class ProductivityWidget(ctk.CTkFrame):
    """Live widget showing dynamic productivity score and stats."""
    def __init__(self, master, db, colors, analytics_engine, **kwargs):
        super().__init__(master, fg_color=colors["bg_card"], corner_radius=14, 
                         border_width=1, border_color=colors["border"], **kwargs)
        self.db = db
        self.colors = colors
        self.ae = analytics_engine
        
        self.pack_propagate(False)
        self._build()

    def _build(self):
        c = self.colors
        
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(12, 4))
        
        ctk.CTkLabel(header, text="⚡ Productivity Score", font=FONTS["title"], text_color=c["text_primary"]).pack(side="left")
        self.score_label = ctk.CTkLabel(header, text="--", font=("Segoe UI", 24, "bold"), text_color=c["accent"])
        self.score_label.pack(side="right")
        
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=16, pady=8)
        
        self.stats_label = ctk.CTkLabel(content, text="Loading intelligence...", font=FONTS["body"], text_color=c["text_secondary"], justify="left")
        self.stats_label.pack(anchor="w")
        
        self.refresh()

    def refresh(self):
        """Asynchronously update productivity score and stats."""
        try:
            from analytics.productivity_engine import ProductivityEngine
            pe = ProductivityEngine(self.ae, self.db)
            
            score = pe.calculate_focus_score()
            self.score_label.configure(text=f"{score}%")
            
            best_hour = pe.get_most_productive_hour()
            hour_str = f"{best_hour}:00" if best_hour is not None else "N/A"
            
            # Find subject with most time
            dist = self.ae.get_subject_distribution()
            top_subj = "None"
            if dist:
                top_sid = max(dist, key=dist.get)
                s = self.db.get_subject(top_sid)
                top_subj = s["name"] if s else "Deleted"

            self.stats_label.configure(text=f"• Peak Focus: {hour_str}\n• Top Subject: {top_subj}\n• Sessions: {len(self.ae.get_all_sessions())}")
        except Exception as e:
            from utils.logger import log
            log.error(f"ProductivityWidget refresh failed: {e}")
