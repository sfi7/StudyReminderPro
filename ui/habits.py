# ============================================================
# Study Reminder Pro - Habits View
# File: ui/habits.py
# ============================================================

import tkinter as tk
import customtkinter as ctk
from datetime import date
from core.theme import FONTS

class HabitsView(ctk.CTkFrame):
    def __init__(self, master, db, colors, toast_fn, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.db = db
        self.colors = colors
        self.toast = toast_fn
        self._widgets = []

        self._build_skeleton()
        self.refresh()

    def _build_skeleton(self):
        c = self.colors
        
        # Add Habit Frame at the top
        add_frame = ctk.CTkFrame(self, fg_color="transparent")
        add_frame.pack(fill="x", padx=24, pady=(16, 8))
        
        self._habit_entry = ctk.CTkEntry(
            add_frame, placeholder_text="Enter a new daily habit (e.g., Working out, Coding, Reading)...",
            font=FONTS["body"], fg_color=c["bg_card"], border_color=c["border"],
            text_color=c["text_primary"], placeholder_text_color=c["text_muted"],
            corner_radius=10, height=38
        )
        self._habit_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # Bind Return key to add habit
        self._habit_entry.bind("<Return>", lambda e: self._add_habit())

        ctk.CTkButton(
            add_frame, text="➕ Add Habit", font=FONTS["body"],
            fg_color="#10B981", hover_color="#0D9488", text_color="#FFFFFF",
            corner_radius=10, height=38, width=120,
            command=self._add_habit
        ).pack(side="right")

        # Today's Progress Section
        self._progress_frame = ctk.CTkFrame(self, fg_color=c["bg_card"],
                                            border_width=1, border_color=c["border"],
                                            corner_radius=16)
        self._progress_frame.pack(fill="x", padx=24, pady=8)
        
        self._prog_label = ctk.CTkLabel(self._progress_frame, text="Today's Habit Progress: 0 of 0 completed",
                                         font=FONTS["body"], text_color=c["text_primary"])
        self._prog_label.pack(anchor="w", padx=16, pady=(12, 4))
        
        self._prog_bar = ctk.CTkProgressBar(self._progress_frame, height=8, fg_color=c["bg_secondary"], progress_color="#10B981")
        self._prog_bar.pack(fill="x", padx=16, pady=(0, 16))
        self._prog_bar.set(0)

        # Scrollable Habits Container
        self._scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self._scroll.pack(fill="both", expand=True, padx=24, pady=8)

    def apply_navigation_params(self, **kwargs):
        pass

    def refresh(self):
        """Update habits listing."""
        current_data_ver = self.db.data_version
        current_settings_ver = self.db.settings_version
        if (getattr(self, "_last_data_version", -1) == current_data_ver and 
            getattr(self, "_last_settings_version", -1) == current_settings_ver):
            return
            
        self._last_data_version = current_data_ver
        self._last_settings_version = current_settings_ver
        
        self._render_habits()

    def _add_habit(self):
        name = self._habit_entry.get().strip()
        if not name:
            self._habit_entry.configure(border_color="#EF4444")
            return
            
        self._habit_entry.configure(border_color=self.colors["border"])
        self.db.add_habit(name)
        self._habit_entry.delete(0, "end")
        self.toast(f"✅ Daily Habit '{name}' added!", "success")
        self.refresh()

    def _render_habits(self):
        # Destroy all old items in scroll
        for widget in self._scroll.winfo_children():
            widget.destroy()

        c = self.colors
        habits = self.db.habits

        if not habits:
            self._prog_label.configure(text="No habits tracked yet. Add one above!")
            self._prog_bar.set(0)
            
            lbl = ctk.CTkLabel(
                self._scroll, text="Your summer habit checklist is empty.\nType a habit above and click 'Add Habit'!",
                font=FONTS["body"], text_color=c["text_muted"]
            )
            lbl.pack(pady=60)
            return

        # Calculate progress
        today_str = date.today().isoformat()
        total = len(habits)
        completed = sum(1 for h in habits if today_str in h.get("history", []))
        pct = (completed / total) if total > 0 else 0
        
        self._prog_label.configure(text=f"Today's Habit Progress: {completed} of {total} completed ({int(pct*100)}%)")
        self._prog_bar.set(pct)

        for h in habits:
            self._render_habit_row(self._scroll, h, today_str)

    def _render_habit_row(self, parent, h, today_str):
        c = self.colors
        is_done = today_str in h.setdefault("history", [])
        streak = self.db.get_habit_streak(h)

        row = ctk.CTkFrame(parent, fg_color=c["bg_card"],
                           border_width=1, border_color=c["border"],
                           corner_radius=12)
        row.pack(fill="x", pady=6)

        # Checkbox to complete habit
        cb_var = tk.BooleanVar(value=is_done)
        
        # We define toggle command
        def on_toggle():
            status = self.db.toggle_habit(h["id"])
            if status:
                self.toast(f"🔥 Kept it up! completed '{h['name']}'", "success")
            self.refresh()

        cb = ctk.CTkCheckBox(
            row, text=h["name"], font=FONTS["body"], variable=cb_var,
            fg_color="#10B981", hover_color="#0D9488", text_color=c["text_primary"],
            border_color=c["border"], border_width=2, command=on_toggle
        )
        cb.pack(side="left", padx=16, pady=16)

        # Right-side: Streaks & Delete
        right_frame = ctk.CTkFrame(row, fg_color="transparent")
        right_frame.pack(side="right", padx=16)

        if streak > 0:
            streak_lbl = ctk.CTkLabel(
                right_frame, text=f"🔥 {streak}-day streak",
                font=FONTS["small"], text_color=c["warning"]
            )
            streak_lbl.pack(side="left", padx=10)

        # Delete Button
        ctk.CTkButton(
            right_frame, text="🗑️", width=32, height=28, font=FONTS["tiny"],
            fg_color=c["bg_secondary"], hover_color=c["danger"], text_color=c["text_secondary"],
            corner_radius=8, command=lambda: self._confirm_delete(h)
        ).pack(side="left")

    def _confirm_delete(self, h):
        dlg = tk.Toplevel(self)
        dlg.title("Confirm Delete")
        dlg.geometry("380x160")
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.attributes("-topmost", True)
        c = self.colors
        dlg.configure(bg=c["bg_primary"])

        ctk.CTkLabel(dlg, text=f"Delete habit '{h['name']}'?",
                     font=FONTS["subheading"], text_color=c["text_primary"]).pack(pady=(24, 6))
        ctk.CTkLabel(dlg, text="This will erase all completion history for this habit.",
                     font=FONTS["small"], text_color=c["text_muted"]).pack()

        btn_row = ctk.CTkFrame(dlg, fg_color="transparent")
        btn_row.pack(pady=16)
        ctk.CTkButton(btn_row, text="Cancel", width=100,
                       fg_color=c["bg_secondary"], hover_color=c["border"],
                       text_color=c["text_secondary"],
                       command=dlg.destroy).pack(side="left", padx=8)
        ctk.CTkButton(btn_row, text="🗑️ Delete", width=100,
                       fg_color=c["danger"], hover_color="#C0392B",
                       command=lambda: (self.db.delete_habit(h["id"]),
                                        self.toast(f"🗑️ Habit deleted.", "error"),
                                        dlg.destroy(), self.refresh())).pack(side="left", padx=8)
