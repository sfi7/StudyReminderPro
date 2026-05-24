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
        self.padding = 3
        
        self.tooltip = None
        self.bind("<Configure>", self._on_resize)

    def _create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)

    def _interpolate_color(self, color1, color2, factor):
        """Interpolates between two hex colors by a factor in [0, 1]."""
        if not color1.startswith("#") or not color2.startswith("#"):
            return color2
        try:
            c1 = [int(color1[i:i+2], 16) for i in (1, 3, 5)]
            c2 = [int(color2[i:i+2], 16) for i in (1, 3, 5)]
            res = [int(c1[j] + (c2[j] - c1[j]) * factor) for j in range(3)]
            return f"#{res[0]:02x}{res[1]:02x}{res[2]:02x}"
        except Exception:
            return color2

    def _on_resize(self, event):
        if not self.winfo_exists(): return
        self.delete("all")
        self.draw_heatmap()

    def draw_heatmap(self):
        today = datetime.now().date()
        
        # Calculate exactly 52 weeks ago
        start_date = today - timedelta(weeks=52)
        # Shift start_date to the nearest Sunday
        idx = (start_date.weekday() + 1) % 7
        start_date = start_date - timedelta(days=idx)
        
        # Calculate how many weeks to display
        total_days = (today - start_date).days + 1
        num_weeks = (total_days + 6) // 7
        
        x_offset = 36 # Room for weekday labels
        y_offset = 24 # Room for month labels
        
        # Draw weekday labels on the left side
        for r_idx, label in [(1, "Mon"), (3, "Wed"), (5, "Fri")]:
            y_text = y_offset + r_idx * (self.box_size + self.padding) + self.box_size // 2
            self.create_text(x_offset - 8, y_text, text=label,
                             font=("Segoe UI", 9), fill=self.c["text_muted"], anchor="e")
        
        # Draw month labels at the top
        labeled_months = set()
        for col in range(num_weeks):
            first_day_of_week = start_date + timedelta(days=col * 7)
            month_key = first_day_of_week.strftime("%Y-%m")
            if month_key not in labeled_months:
                if col == 0 or first_day_of_week.day <= 7:
                    x0 = x_offset + col * (self.box_size + self.padding)
                    self.create_text(x0, y_offset - 12, text=first_day_of_week.strftime("%b"), 
                                     font=("Segoe UI", 9, "bold"), fill=self.c["text_muted"], anchor="w")
                    labeled_months.add(month_key)
        
        # Draw the grid of contribution boxes
        for col in range(num_weeks):
            for row in range(7):
                current_date = start_date + timedelta(days=(col * 7) + row)
                
                x1 = x_offset + col * (self.box_size + self.padding)
                y1 = y_offset + row * (self.box_size + self.padding)
                x2 = x1 + self.box_size
                y2 = y1 + self.box_size
                
                if current_date > today:
                    # Draw future days as empty placeholder rounded squares
                    self._create_rounded_rect(x1, y1, x2, y2, radius=2.5, 
                                              fill=self.c["progress_bg"], outline="")
                    continue
                    
                date_str = current_date.strftime("%Y-%m-%d")
                minutes = self.activity_dict.get(date_str, 0)
                
                # Dynamic Color Interpolation matching the accent theme
                if minutes == 0:
                    color = self.c["progress_bg"]
                elif minutes < 30:
                    color = self._interpolate_color(self.c["progress_bg"], self.c["accent"], 0.25)
                elif minutes < 90:
                    color = self._interpolate_color(self.c["progress_bg"], self.c["accent"], 0.6)
                elif minutes < 180:
                    color = self.c["accent"]
                else:
                    color = self.c["accent_light"]
                    
                rect_id = self._create_rounded_rect(x1, y1, x2, y2, radius=2.5, 
                                                    fill=color, outline="")
                
                # Hover Info
                self.tag_bind(rect_id, "<Enter>", lambda e, d=date_str, m=minutes: self._show_info(d, m))
                self.tag_bind(rect_id, "<Leave>", lambda e: self._hide_info())

    def _show_info(self, date_str, minutes):
        self.delete("info_text")
        info = f"{date_str}: {minutes} minutes"
        self.create_text(10, self.winfo_height() - 10, text=info, 
                         font=("Segoe UI", 9, "bold"), fill=self.c["text_secondary"], 
                         anchor="sw", tags="info_text")

    def _hide_info(self):
        self.delete("info_text")
