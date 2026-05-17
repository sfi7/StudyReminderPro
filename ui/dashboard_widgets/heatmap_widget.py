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
        num_weeks = 52
        num_days = num_weeks * 7
        start_date = today - timedelta(days=num_days - 1)
        
        # Ensure start_date is a Sunday (for alignment)
        idx = (start_date.weekday() + 1) % 7
        start_date = start_date - timedelta(days=idx)
        
        box_size = 12
        margin = 3
        
        # Set canvas width to fit 52 weeks
        required_width = num_weeks * (box_size + margin) + 20
        self.canvas.configure(width=required_width)
        
        # Draw the grid
        for col in range(num_weeks):
            for row in range(7):
                current_date = start_date + timedelta(days=(col * 7) + row)
                if current_date > today:
                    break
                    
                date_str = current_date.strftime("%Y-%m-%d")
                mins = day_map.get(date_str, 0)
                
                # Intensity scale
                if mins == 0:
                    color = self.colors["progress_bg"]
                elif mins < 30:
                    color = "#3B2D59" # Dark purple
                elif mins < 90:
                    color = "#5A448A" # Mid purple
                elif mins < 180:
                    color = self.colors["accent"]
                else:
                    color = self.colors["accent_light"] # High intensity
                    
                x0 = col * (box_size + margin)
                y0 = row * (box_size + margin)
                x1 = x0 + box_size
                y1 = y0 + box_size
                
                rect_id = self.canvas.create_rectangle(x0, y0 + 15, x1, y1 + 15, fill=color, outline="", tags=("box", date_str, str(mins)))
                
                # Month Labels
                if current_date.day == 1:
                    self.canvas.create_text(x0, 8, text=current_date.strftime("%b"), 
                                             font=("Segoe UI", 9), fill=self.colors["text_muted"], anchor="w")

                # Hover bindings
                self.canvas.tag_bind(rect_id, "<Enter>", lambda e, d=date_str, m=mins: self._on_hover(e, d, m))
                self.canvas.tag_bind(rect_id, "<Leave>", self._on_leave)

    def _on_hover(self, event, date_str, mins):
        text = f"{date_str}: {mins} mins"
        self.tooltip.configure(text=text)
        self.tooltip.place(x=event.x + 10, y=event.y - 20)

    def _on_leave(self, event):
        self.tooltip.place_forget()
