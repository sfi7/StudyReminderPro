# ============================================================
# Study Reminder Pro - Pomodoro Timer View
# File: ui/pomodoro.py
# ============================================================

import tkinter as tk
import customtkinter as ctk
from core.theme import FONTS
import os
from focus.sound_manager import SoundManager
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
        self.sound_manager = SoundManager(self.db.settings)
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

        # ── Subject/Skill selector ──
        subj_frame = ctk.CTkFrame(self._center_frame, fg_color=c["bg_card"],
                                  corner_radius=16, border_width=1,
                                  border_color=c["border"])
        subj_frame.pack(fill="x", pady=(0, 32), padx=0)
        
        # Check if lifestyle mode
        app = self.winfo_toplevel()
        self.is_lifestyle = getattr(app, "app_mode", "academic") == "lifestyle"
        
        lbl_text = "🌱 Skill/Course:" if self.is_lifestyle else "📚 Studying:"
        self._selector_label = ctk.CTkLabel(subj_frame, text=lbl_text,
                     font=FONTS["small"],
                     text_color=c["text_muted"])
        self._selector_label.pack(side="left", padx=16)

        if self.is_lifestyle:
            skills = [s for s in self.db.skills if self.db.progress_pct_skill(s) < 100]
            names = [s["name"] for s in skills] if skills else ["No active skills"]
        else:
            subjects = self.db.subjects
            active_subjects = []
            for s in subjects:
                days = self.db.days_until_exam(s)
                is_past_exam = (days is not None and days < 0)
                is_finished = (s.get("total_lectures", 0) > 0 and s.get("completed_lectures", 0) >= s.get("total_lectures", 0))
                if not (is_past_exam or is_finished):
                    active_subjects.append(s)
            names = [s["name"] for s in active_subjects] if active_subjects else ["No active subjects"]

        if names:
            self._selected_subject.set(names[0])
        else:
            self._selected_subject.set("No active focus target")

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

                # ── Sound Selection Panel ──
        sound_frame = ctk.CTkFrame(self._center_frame, fg_color=c["bg_card"], corner_radius=12)
        sound_frame.pack(pady=(0,12), fill="x", padx=20)
        ctk.CTkLabel(sound_frame, text="🔊 Sound Theme:", font=FONTS["small"], text_color=c["text_muted"]).pack(side="left", padx=8, pady=8)
        sound_options = ["Tick Tock", "Sea Waves", "Rain", "Wind", "Silence"]
        self._selected_sound = tk.StringVar(value=self.db.settings.get("pomodoro_sound", sound_options[0]))
        sound_menu = ctk.CTkOptionMenu(sound_frame, values=sound_options, variable=self._selected_sound, font=FONTS["body"], fg_color=c["bg_secondary"], button_color=c["accent"], button_hover_color=c["accent_hover"], dropdown_fg_color=c["bg_card"], text_color=c["text_primary"], height=36)
        sound_menu.pack(side="left", fill="x", expand=True, padx=8, pady=8)
        ctk.CTkButton(sound_frame, text="▶️ Play", width=60, height=36, corner_radius=12, fg_color=c["accent"], hover_color=c["accent_hover"], command=self._play_selected_sound).pack(side="right", padx=8, pady=8)
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
        app = self.winfo_toplevel()
        is_lifestyle = getattr(app, "app_mode", "academic") == "lifestyle"

        if is_lifestyle:
            subj = next((s for s in self.db.skills if s["name"] == subj_name), None)
            target_id = subj["id"] if subj else "generic"
        else:
            subj = next((s for s in self.db.subjects if s["name"] == subj_name), None)
            if not subj:
                self.toast("Please add a subject first!", "error")
                return
            target_id = subj["id"]

        if hasattr(app, 'focus_controller'):
            app.focus_controller.start_focus(target_id, duration, mode=self._mode)
        else:
            self.toast("Focus Mode Engine Error", "error")

    def _play_selected_sound(self):
        """Play the ambient sound selected in the sound panel.

        Maps the human‑readable sound name to a sound file in ``assets/sounds``
        and uses :class:`SoundManager` to start playback. Selecting "Silence"
        stops any currently playing ambient track.
        """
        sound_name = self._selected_sound.get()
        # Persist selection for next sessions
        try:
            self.db.settings["pomodoro_sound"] = sound_name
        except Exception:
            pass

        # Mapping of UI names to sound file paths
        sound_map = {
            "Tick Tock": os.path.join("assets", "sounds", "tick_tock.wav"),
            "Sea Waves": os.path.join("assets", "sounds", "sea_waves.wav"),
            "Rain": os.path.join("assets", "sounds", "rain.wav"),
            "Wind": os.path.join("assets", "sounds", "wind.wav"),
            "Silence": None,
        }
        sound_path = sound_map.get(sound_name)
        if sound_path and os.path.exists(sound_path):
            self.sound_manager.play_ambient(sound_path)
            self.toast(f"Playing {sound_name} sound", "info")
        else:
            self.sound_manager.stop_ambient()
            if sound_name != "Silence":
                self.toast(f"Sound file for '{sound_name}' not found.", "warning")
        self._selected_sound.set(sound_name)

    # ── Drawing/Alarm (Removed for Focus Mode) ────────────────

    def apply_navigation_params(self, **kwargs):
        subject_id = kwargs.get("subject_id")
        if subject_id:
            app = self.winfo_toplevel()
            is_lifestyle = getattr(app, "app_mode", "academic") == "lifestyle"
            if is_lifestyle:
                skill = self.db.get_skill(subject_id)
                if skill:
                    self._nav_selected_subject_name = skill["name"]
            else:
                subj = self.db.get_subject(subject_id)
                if subj:
                    self._nav_selected_subject_name = subj["name"]

    def refresh(self):
        """Refresh subject or skill list in the dropdown."""
        app = self.winfo_toplevel()
        self.is_lifestyle = getattr(app, "app_mode", "academic") == "lifestyle"

        if hasattr(self, "_selector_label"):
            lbl_text = "🌱 Skill/Course:" if self.is_lifestyle else "📚 Studying:"
            self._selector_label.configure(text=lbl_text)

        if self.is_lifestyle:
            skills = self.db.skills
            active_skills = [s for s in skills if self.db.progress_pct_skill(s) < 100]
            names = [s["name"] for s in active_skills]

            target_name = getattr(self, "_nav_selected_subject_name", None)
            if target_name:
                if target_name not in names:
                    skill = next((s for s in skills if s["name"] == target_name), None)
                    if skill:
                        names.append(target_name)
                self._selected_subject.set(target_name)
                self._nav_selected_subject_name = None
            else:
                curr = self._selected_subject.get()
                if curr not in names:
                    if names:
                        self._selected_subject.set(names[0])
                    else:
                        self._selected_subject.set("No active skills")
        else:
            subjects = self.db.subjects
            active_subjects = []
            for s in subjects:
                days = self.db.days_until_exam(s)
                is_past_exam = (days is not None and days < 0)
                is_finished = (s.get("total_lectures", 0) > 0 and s.get("completed_lectures", 0) >= s.get("total_lectures", 0))
                if not (is_past_exam or is_finished):
                    active_subjects.append(s)

            names = [s["name"] for s in active_subjects]

            target_name = getattr(self, "_nav_selected_subject_name", None)
            if target_name:
                if target_name not in names:
                    subj = next((s for s in subjects if s["name"] == target_name), None)
                    if subj:
                        names.append(target_name)
                self._selected_subject.set(target_name)
                self._nav_selected_subject_name = None
            else:
                curr = self._selected_subject.get()
                if curr not in names:
                    if names:
                        self._selected_subject.set(names[0])
                    else:
                        self._selected_subject.set("No active subjects")

        if not names:
            names = ["No active skills"] if self.is_lifestyle else ["No active subjects"]

        self._subj_menu.configure(values=names)
