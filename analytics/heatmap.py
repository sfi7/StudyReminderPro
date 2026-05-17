# ============================================================
# Study Reminder Pro - Heatmap Engine
# File: analytics/heatmap.py
# ============================================================

import tkinter as tk
from datetime import datetime, timedelta

class GitHubHeatmap(tk.Canvas):
    """
    A custom premium heatmap rendering 365 days of study consistency.
    """
    def __init__(self, master, theme_manager, activity_dict, **kwargs):
        self.c = theme_manager.colors
        super().__init__(master, bg=self.c["bg_card"], highlightthickness=0, **kwargs)
        self.activity_dict = activity_dict
        
        self.box_size = 12
        self.padding = 4
        
        self.colors = [
            self.c["bg_secondary"], # 0 min
            self.c["accent_light"], # > 0 min
            self.c["accent"],       # > 30 min
            self.c["accent_hover"], # > 60 min
            self.c["text_primary"]  # > 120 min (peak)
        ]
        
        self.tooltip = None
        self.bind("<Configure>", self._on_resize)

    def _get_color(self, minutes):
        if minutes == 0: return self.colors[0]
        if minutes < 30: return self.colors[1]
        if minutes < 60: return self.colors[2]
        if minutes < 120: return self.colors[3]
        return self.colors[4]

    def _on_resize(self, event):
        if not self.winfo_exists(): return
        self.delete("all")
        self.draw_heatmap()

    def draw_heatmap(self):
        today = datetime.now().date()
        start_date = today - timedelta(days=364)
        
        # We draw columns of weeks (approx 52 weeks)
        # Week starts on Sunday
        
        start_weekday = start_date.weekday() # 0 = Mon, 6 = Sun
        # Shift so Sunday is top of column
        offset = (start_weekday + 1) % 7
        
        x_offset = 20
        y_offset = 20
        
        curr_date = start_date
        col = 0
        
        while curr_date <= today:
            row = (curr_date.weekday() + 1) % 7 # Sunday = 0
            
            date_str = curr_date.strftime("%Y-%m-%d")
            minutes = self.activity_dict.get(date_str, 0)
            
            x1 = x_offset + col * (self.box_size + self.padding)
            y1 = y_offset + row * (self.box_size + self.padding)
            x2 = x1 + self.box_size
            y2 = y1 + self.box_size
            
            color = self._get_color(minutes)
            
            rect_id = self.create_rectangle(x1, y1, x2, y2, fill=color, outline=self.c["border"], width=1)
            
            # Simple Hover Info
            self.tag_bind(rect_id, "<Enter>", lambda e, d=date_str, m=minutes: self._show_info(d, m))
            self.tag_bind(rect_id, "<Leave>", lambda e: self._hide_info())
            
            # Month Labels
            if curr_date.day == 1:
                self.create_text(x1, y_offset - 12, text=curr_date.strftime("%b"), 
                                 font=("Segoe UI", 9), fill=self.c["text_muted"], anchor="w")

            curr_date += timedelta(days=1)
            if row == 6:
                col += 1

    def _show_info(self, date_str, minutes):
        self.delete("info_text")
        info = f"{date_str}: {minutes} minutes"
        self.create_text(10, self.winfo_height() - 10, text=info, 
                         font=("Segoe UI", 9), fill=self.c["text_secondary"], 
                         anchor="sw", tags="info_text")

    def _hide_info(self):
        self.delete("info_text")
