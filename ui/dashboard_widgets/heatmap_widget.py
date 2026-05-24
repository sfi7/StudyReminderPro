# ============================================================
# Study Reminder Pro - Heatmap Widget
# File: ui/dashboard_widgets/heatmap_widget.py
# ============================================================

import customtkinter as ctk
import tkinter as tk
from datetime import date, timedelta
from core.theme import FONTS

class HeatmapWidget(ctk.CTkFrame):
    """Advanced GitHub-style consistency heatmap with hover tooltips and intensity scaling."""
    def __init__(self, master, db, colors, analytics_engine, **kwargs):
        super().__init__(master, fg_color=colors["bg_card"], corner_radius=14, 
                         border_width=1, border_color=colors["border"], **kwargs)
        self.db = db
        self.colors = colors
        self.ae = analytics_engine
        
        self._build()

    def _build(self):
        c = self.colors
        
        header_row = ctk.CTkFrame(self, fg_color="transparent")
        header_row.pack(fill="x", padx=16, pady=(16, 4))
        ctk.CTkLabel(header_row, text="🔥 Consistency Heatmap", font=FONTS["title"], text_color=c["text_primary"]).pack(side="left")
        
        # We use a pure tk.Canvas for high performance grid drawing
        self.canvas_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.canvas_frame.pack(fill="both", expand=True, padx=16, pady=(8, 16))
        
        self.canvas = tk.Canvas(self.canvas_frame, height=130, bg=self._hex_to_rgb_str(c["bg_card"]), highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        # Tooltip label
        self.tooltip = ctk.CTkLabel(self, text="", font=FONTS["tiny"], text_color=c["text_secondary"], fg_color=c["bg_sidebar"], corner_radius=6)
        # We don't pack it, we place it dynamically on hover
        
        self.refresh()

    def _hex_to_rgb_str(self, hex_color):
        if not hex_color.startswith("#"):
            return "#1e1e1e" # Fallback dark
        return hex_color

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
        return self.canvas.create_polygon(points, smooth=True, **kwargs)

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

    def refresh(self):
        self.canvas.delete("all")
        
        # Fetch data
        sessions = self.ae.get_all_sessions()
        from utils.logger import log
        log.info(f"Heatmap: Found {len(sessions)} total sessions for visualization.")
        
        # Map: "YYYY-MM-DD" -> total_minutes
        day_map = {}
        for s in sessions:
            try:
                # Support multiple timestamp keys
                ts = s.get("start_time", s.get("timestamp"))
                if not ts: continue
                
                # Robust ISO parsing - just take the first 10 chars for YYYY-MM-DD
                date_str = ts[:10]
                
                # Support multiple duration keys
                mins = s.get("duration_minutes", s.get("duration_min", s.get("minutes", 0)))
                day_map[date_str] = day_map.get(date_str, 0) + mins
            except Exception as e:
                log.error(f"Error parsing session for heatmap: {e}")
            
        today = date.today()
        
        # Find start date (52 weeks ago)
        start_date = today - timedelta(weeks=52)
        # Shift start_date to the nearest Sunday
        idx = (start_date.weekday() + 1) % 7
        start_date = start_date - timedelta(days=idx)
        
        # Calculate exactly how many weeks we need to display all days up to today
        total_days = (today - start_date).days + 1
        num_weeks = (total_days + 6) // 7 # Ceil division
        
        box_size = 12
        margin = 3
        x_offset = 32 # Room for weekday labels
        
        # Set canvas width to fit weeks + weekday labels
        required_width = x_offset + num_weeks * (box_size + margin) + 10
        self.canvas.configure(width=required_width)
        
        # Draw weekday labels on the left side
        for r_idx, label in [(1, "Mon"), (3, "Wed"), (5, "Fri")]:
            y_text = r_idx * (box_size + margin) + 15 + box_size // 2
            self.canvas.create_text(x_offset - 8, y_text, text=label,
                                    font=("Segoe UI", 9), fill=self.colors["text_muted"], anchor="e")
        
        # Draw month labels at the top
        labeled_months = set()
        for col in range(num_weeks):
            first_day_of_week = start_date + timedelta(days=col * 7)
            month_key = first_day_of_week.strftime("%Y-%m")
            if month_key not in labeled_months:
                if col == 0 or first_day_of_week.day <= 7:
                    x0 = x_offset + col * (box_size + margin)
                    self.canvas.create_text(x0, 8, text=first_day_of_week.strftime("%b"), 
                                             font=("Segoe UI", 9, "bold"), fill=self.colors["text_muted"], anchor="w")
                    labeled_months.add(month_key)
        
        # Draw the grid of contribution boxes
        for col in range(num_weeks):
            for row in range(7):
                current_date = start_date + timedelta(days=(col * 7) + row)
                
                x0 = x_offset + col * (box_size + margin)
                y0 = row * (box_size + margin)
                x1 = x0 + box_size
                y1 = y0 + box_size
                
                if current_date > today:
                    # Draw future days as empty placeholder rounded squares
                    self._create_rounded_rect(x0, y0 + 15, x1, y1 + 15, radius=2.5, 
                                              fill=self.colors["progress_bg"], outline="")
                    continue
                    
                date_str = current_date.strftime("%Y-%m-%d")
                mins = day_map.get(date_str, 0)
                
                # Dynamic Color Interpolation matching the accent theme
                if mins == 0:
                    color = self.colors["progress_bg"]
                elif mins < 30:
                    color = self._interpolate_color(self.colors["progress_bg"], self.colors["accent"], 0.25)
                elif mins < 90:
                    color = self._interpolate_color(self.colors["progress_bg"], self.colors["accent"], 0.6)
                elif mins < 180:
                    color = self.colors["accent"]
                else:
                    color = self.colors["accent_light"]
                    
                rect_id = self._create_rounded_rect(x0, y0 + 15, x1, y1 + 15, radius=2.5, 
                                                    fill=color, outline="", tags=("box", date_str, str(mins)))
                
                # Hover bindings
                self.canvas.tag_bind(rect_id, "<Enter>", lambda e, d=date_str, m=mins: self._on_hover(e, d, m))
                self.canvas.tag_bind(rect_id, "<Leave>", self._on_leave)

    def _on_hover(self, event, date_str, mins):
        text = f"{date_str}: {mins} mins"
        self.tooltip.configure(text=text)
        self.tooltip.place(x=event.x + 10, y=event.y - 20)

    def _on_leave(self, event):
        self.tooltip.place_forget()
