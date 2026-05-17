# ============================================================
# Study Reminder Pro - Pomodoro Timer View
# File: ui/pomodoro.py
# ============================================================

import tkinter as tk
import customtkinter as ctk
from core.theme import FONTS


class PomodoroView(ctk.CTkFrame):
    """Full Pomodoro timer with Work / Short Break / Long Break modes."""

    MODES = {
        "Work":        {"label": "🎯  Focus Time",   "color": "#7C6EFA"},
        "Short Break": {"label": "☕  Short Break",   "color": "#34D399"},
        "Long Break":  {"label": "🌙  Long Break",    "color": "#60A5FA"},
    }

    def __init__(self, master, db, colors, toast_fn, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.db = db
        self.colors = colors
        self.toast = toast_fn

        self._selected_subject = tk.StringVar(value="")
        self._mode = "Work"
        self._load_durations()

        self._build()

    def _load_durations(self):
        s = self.db.settings
        self._durations = {
            "Work": s.get("pomodoro_work", 25),
            "Short Break": s.get("pomodoro_break", 5),
            "Long Break": s.get("pomodoro_long_break", 15),
        }

    def _build(self):
        c = self.colors

        # Center column
        self._center_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._center_frame.place(relx=0.5, rely=0.5, anchor="center")

        # ── Mode tabs ──
        tab_frame = ctk.CTkFrame(self._center_frame, fg_color=c["bg_card"],
                                 corner_radius=20, border_width=1,
                                 border_color=c["border"])
        tab_frame.pack(pady=(0, 24))

        self._mode_btns = {}
        for mode in self.MODES:
            btn = ctk.CTkButton(
                tab_frame, text=mode, width=130, height=42,
                corner_radius=16, font=FONTS["button"],
                fg_color="transparent",
                hover_color=c.get("hover_overlay", c["border"]),
                text_color=c["text_secondary"],
                command=lambda m=mode: self._set_mode(m)
            )
            btn.pack(side="left", padx=6, pady=6)
            self._mode_btns[mode] = btn

        # ── Subject selector ──
        subj_frame = ctk.CTkFrame(self._center_frame, fg_color=c["bg_card"],
                                  corner_radius=16, border_width=1,
                                  border_color=c["border"])
        subj_frame.pack(fill="x", pady=(0, 32), padx=0)
        ctk.CTkLabel(subj_frame, text="📚 Studying:",
                     font=FONTS["small"],
                     text_color=c["text_muted"]).pack(side="left", padx=16)

        subjects = self.db.subjects
        names = [s["name"] for s in subjects] if subjects else ["No subjects yet"]
        if subjects:
            self._selected_subject.set(names[0])

        self._subj_menu = ctk.CTkOptionMenu(
            subj_frame,
            values=names,
            variable=self._selected_subject,
            font=FONTS["body"],
            fg_color=c["bg_secondary"],
            button_color=c["accent"],
            button_hover_color=c["accent_hover"],
            dropdown_fg_color=c["bg_card"],
            text_color=c["text_primary"],
            height=44
        )
        self._subj_menu.pack(side="left", fill="x", expand=True, padx=8, pady=8)

        # ── Launch Focus Mode Button ──
        self._start_btn = ctk.CTkButton(
            self._center_frame, text="✨ Enter Focus Mode", width=280, height=64,
            corner_radius=32, font=FONTS["heading"],
            fg_color=c["accent"], hover_color=c["accent_hover"],
            command=self._launch_focus_mode
        )
        self._start_btn.pack(pady=10)

        self._set_mode("Work")

    def _set_mode(self, mode):
        self._mode = mode
        info = self.MODES[mode]
        c = self.colors
        for m, btn in self._mode_btns.items():
            if m == mode:
                btn.configure(fg_color=c["bg_secondary"], text_color=info["color"])
            else:
                btn.configure(fg_color="transparent", text_color=c["text_secondary"])

    def _launch_focus_mode(self):
        duration = self._durations.get(self._mode, 25)
        subj_name = self._selected_subject.get()
        subj = next((s for s in self.db.subjects if s["name"] == subj_name), None)

        if not subj:
            self.toast("Please add a subject first!", "error")
            return

        # Access app focus controller via master hierarchy or pass it explicitly.
        # Since master hierarchy is complex, we can find the app root:
        app = self.winfo_toplevel()
        if hasattr(app, 'focus_controller'):
            app.focus_controller.start_focus(subj["id"], duration)
        else:
            self.toast("Focus Mode Engine Error", "error")

    # ── Drawing/Alarm (Removed for Focus Mode) ────────────────

    def refresh(self):
        """Refresh subject list in the dropdown."""
        subjects = self.db.subjects
        names = [s["name"] for s in subjects] if subjects else ["No subjects yet"]
        self._subj_menu.configure(values=names)
        if names:
            self._selected_subject.set(names[0])
