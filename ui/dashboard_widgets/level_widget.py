# ============================================================
# Study Reminder Pro - Level & XP Widget
# File: ui/dashboard_widgets/level_widget.py
# ============================================================

import customtkinter as ctk
from core.theme import FONTS
from ui.widgets import LinearProgressBar

class LevelWidget(ctk.CTkFrame):
    """Sleek widget showing user's level, XP, and rank."""
    def __init__(self, master, db, colors, gamification_engine, **kwargs):
        super().__init__(master, fg_color=colors["bg_card"], corner_radius=14, 
                         border_width=1, border_color=colors["border"], **kwargs)
        self.db = db
        self.colors = colors
        self.ge = gamification_engine
        
        self._build()

    def _build(self):
        c = self.colors
        
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(16, 4))
        
        # Level Badge
        self.level_lbl = ctk.CTkLabel(header, text=f"LVL {self.ge.data['level']}", 
                                      font=("Segoe UI", 18, "bold"), text_color=c["accent"])
        self.level_lbl.pack(side="left")
        
        # Rank Title
        self.rank_lbl = ctk.CTkLabel(header, text=self.ge.get_rank_title(), 
                                     font=FONTS["small"], text_color=c["text_secondary"])
        self.rank_lbl.pack(side="right")
        
        # XP Progress
        progress_frame = ctk.CTkFrame(self, fg_color="transparent")
        progress_frame.pack(fill="x", padx=16, pady=8)
        
        self.progress_bar = LinearProgressBar(progress_frame, width=220, height=10, 
                                               pct=self.ge.get_progress_pct(), color=c["accent"])
        self.progress_bar.pack(fill="x", pady=(4, 0))
        
        # XP Text
        xp_now = self.ge.data['xp']
        xp_needed = self.ge.get_xp_for_next_level()
        self.xp_lbl = ctk.CTkLabel(self, text=f"{xp_now} / {xp_needed} XP to Level Up", 
                                    font=FONTS["tiny"], text_color=c["text_muted"])
        self.xp_lbl.pack(pady=(0, 16))

    def refresh(self):
        """Update widget with latest XP data."""
        self.level_lbl.configure(text=f"LVL {self.ge.data['level']}")
        self.rank_lbl.configure(text=self.ge.get_rank_title())
        self.progress_bar.set_progress(self.ge.get_progress_pct())
        
        xp_now = self.ge.data['xp']
        xp_needed = self.ge.get_xp_for_next_level()
        self.xp_lbl.configure(text=f"{xp_now} / {xp_needed} XP to Level Up")
