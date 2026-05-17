# ============================================================
# Study Reminder Pro - Smart Roadmap View
# File: ui/roadmap.py
# ============================================================

import customtkinter as ctk
import tkinter as tk
from core.theme import FONTS
from analytics.roadmap_engine import RoadmapEngine

class RoadmapView(ctk.CTkScrollableFrame):
    """Dynamic syllabus roadmap showing what needs to be done daily."""
    def __init__(self, master, db, colors, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.db = db
        self.colors = colors
        self.re = RoadmapEngine(db)
        
        self._build()

    def _build(self):
        c = self.colors
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(20, 10))
        
        ctk.CTkLabel(header, text="🗺️ Smart Syllabus Roadmap", 
                     font=FONTS["heading"], text_color=c["text_primary"]).pack(side="left")
        
        # Roadmap Logic
        roadmap = self.re.get_full_roadmap()
        
        if not roadmap:
            self._empty_state()
            return
            
        for item in roadmap:
            self._create_roadmap_card(item)

    def _create_roadmap_card(self, item):
        c = self.colors
        
        card = ctk.CTkFrame(self, fg_color=c["bg_card"], corner_radius=16, border_width=1, border_color=c["border"])
        card.pack(fill="x", padx=24, pady=10)
        
        # Left Info
        info = ctk.CTkFrame(card, fg_color="transparent")
        info.pack(side="left", padx=20, pady=20, fill="both", expand=True)
        
        ctk.CTkLabel(info, text=item["subject_name"], font=FONTS["subheading"], text_color=c["text_primary"]).pack(anchor="w")
        
        status_color = c.get(f"tag_{item['color']}", c["accent"])
        status_label = ctk.CTkFrame(info, fg_color=status_color, corner_radius=6)
        status_label.pack(anchor="w", pady=5)
        ctk.CTkLabel(status_label, text=item["status"], font=FONTS["tiny"], text_color="#FFFFFF").pack(padx=8, pady=2)
        
        ctk.CTkLabel(info, text=item["message"], font=FONTS["body"], text_color=c["text_secondary"]).pack(anchor="w", pady=5)
        
        # Right Metric
        metric = ctk.CTkFrame(card, fg_color=c["bg_sidebar"], corner_radius=12, width=120)
        metric.pack(side="right", padx=20, pady=20)
        metric.pack_propagate(False)
        
        ctk.CTkLabel(metric, text=str(item["daily_target"]), font=("Segoe UI", 24, "bold"), text_color=c["accent"]).pack(pady=(10, 0))
        ctk.CTkLabel(metric, text="per day", font=FONTS["tiny"], text_color=c["text_muted"]).pack()

    def _empty_state(self):
        c = self.colors
        empty = ctk.CTkFrame(self, fg_color=c["bg_card"], corner_radius=16)
        empty.pack(fill="x", padx=24, pady=40)
        ctk.CTkLabel(empty, text="No active exams found. Set exam dates in Subjects tab to generate a roadmap! 📅",
                     font=FONTS["body"], text_color=c["text_secondary"]).pack(pady=40)

    def refresh(self):
        for w in self.winfo_children():
            w.destroy()
        self._build()
