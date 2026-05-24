# ============================================================
# Study Reminder Pro - Mode Selection Screen
# File: ui/mode_selection.py
# ============================================================

import customtkinter as ctk
import tkinter as tk
from datetime import datetime
from core.theme import FONTS

class ModeSelectionView(ctk.CTkFrame):
    def __init__(self, parent, colors, db, on_select):
        super().__init__(parent, fg_color=colors["bg_primary"])
        self.colors = colors
        self.db = db
        self.on_select = on_select
        self._build()

    def _build(self):
        c = self.colors
        
        # Main Outer Container (Centered)
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")
        
        # Dynamic Greeting
        student_name = self.db.settings.get("student_name", "Student")
        hour = datetime.now().hour
        if hour < 12:
            greeting = "Good Morning"
        elif hour < 18:
            greeting = "Good Afternoon"
        else:
            greeting = "Good Evening"
            
        greeting_text = f"✨ {greeting}, {student_name}! ✨"
        
        greeting_lbl = ctk.CTkLabel(
            container, text=greeting_text, font=FONTS["heading"], text_color=c["accent"]
        )
        greeting_lbl.pack(pady=(0, 8))
        
        subtitle_lbl = ctk.CTkLabel(
            container, text="Select your operating focus to customize your dashboard:",
            font=FONTS["body"], text_color=c["text_secondary"]
        )
        subtitle_lbl.pack(pady=(0, 40))
        
        # Cards Container
        cards_frame = ctk.CTkFrame(container, fg_color="transparent")
        cards_frame.pack()
        
        # ─── STUDY MODE CARD ───
        card_study = ctk.CTkFrame(
            cards_frame, fg_color=c["bg_card"], border_color=c["border"],
            border_width=2, corner_radius=24, width=340, height=420
        )
        card_study.grid(row=0, column=0, padx=24, pady=10)
        card_study.grid_propagate(False)
        
        # Content for Study Mode
        ctk.CTkLabel(card_study, text="📚", font=("Segoe UI", 54)).pack(pady=(36, 16))
        ctk.CTkLabel(card_study, text="Study Mode", font=FONTS["subheading"], text_color=c["text_primary"]).pack(pady=(0, 20))
        
        desc_study = (
            "• Track university lectures & syllabi\n"
            "• Monitor countdown to final exams\n"
            "• Analyze academic study pressure\n"
            "• Focus with course-linked Pomodoros"
        )
        ctk.CTkLabel(
            card_study, text=desc_study, font=FONTS["body"],
            text_color=c["text_muted"], justify="left"
        ).pack(padx=30, pady=(0, 40))
        
        btn_study = ctk.CTkButton(
            card_study, text="Activate Study Mode", font=FONTS["body"],
            fg_color="#6C63FF", hover_color="#5B52E0", text_color="#FFFFFF",
            corner_radius=12, height=44,
            command=lambda: self.on_select("academic")
        )
        btn_study.pack(fill="x", padx=30, side="bottom", pady=30)
        
        # ─── LIFESTYLE & GROWTH CARD ───
        card_growth = ctk.CTkFrame(
            cards_frame, fg_color=c["bg_card"], border_color=c["border"],
            border_width=2, corner_radius=24, width=340, height=420
        )
        card_growth.grid(row=0, column=1, padx=24, pady=10)
        card_growth.grid_propagate(False)
        
        # Content for Growth Mode
        ctk.CTkLabel(card_growth, text="🌱", font=("Segoe UI", 54)).pack(pady=(36, 16))
        ctk.CTkLabel(card_growth, text="Lifestyle & Growth", font=FONTS["subheading"], text_color=c["text_primary"]).pack(pady=(0, 20))
        
        desc_growth = (
            "• Track online courses & skills\n"
            "• Build consistent daily habits\n"
            "• General Deep Work Pomodoro timer\n"
            "• Self-growth analytics & habit streaks"
        )
        ctk.CTkLabel(
            card_growth, text=desc_growth, font=FONTS["body"],
            text_color=c["text_muted"], justify="left"
        ).pack(padx=30, pady=(0, 40))
        
        btn_growth = ctk.CTkButton(
            card_growth, text="Activate Growth Mode", font=FONTS["body"],
            fg_color="#10B981", hover_color="#0D9488", text_color="#FFFFFF",
            corner_radius=12, height=44,
            command=lambda: self.on_select("lifestyle")
        )
        btn_growth.pack(fill="x", padx=30, side="bottom", pady=30)
        
        # Bind Hover events for cards
        def make_hover(card, border_color_hover):
            def on_enter(e):
                card.configure(border_color=border_color_hover)
            def on_leave(e):
                card.configure(border_color=c["border"])
            card.bind("<Enter>", on_enter)
            card.bind("<Leave>", on_leave)
            
        make_hover(card_study, "#6C63FF")
        make_hover(card_growth, "#10B981")
