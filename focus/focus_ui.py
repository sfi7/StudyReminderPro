# ============================================================
# Study Reminder Pro - Focus UI
# File: focus/focus_ui.py
# ============================================================

import tkinter as tk
import customtkinter as ctk
from themes.typography import FONTS

class FocusUI(tk.Toplevel):
    """
    Immersive fullscreen UI for the Pomodoro/Focus mode.
    Design inspired by Notion, Linear, and macOS focus aesthetics.
    """
    def __init__(self, controller, theme_manager):
        super().__init__()
        self.controller = controller
        self.tm = theme_manager
        self.c = theme_manager.colors

        self.title("Focus Mode")
        self.configure(bg=self.c["bg_primary"])
        self.protocol("WM_DELETE_WINDOW", self.controller.exit_focus)
        
        self.bind("<Key>", self.controller.handle_keypress)
        
        self._is_fullscreen = False
        self._total_sec = 1
        self._is_paused = False
        self._breath_step = 0
        self._breath_direction = 1
        
        # We will interpolate between text_primary and accent_light for breathing
        self._color_base = self.c["text_primary"]
        self._color_glow = self.c["accent_light"]
        self._breathe_colors = self._generate_color_gradient(self._color_base, self._color_glow, steps=10)
        
        self._breathe_job = self.after(100, self._breathing_loop)

    def destroy(self):
        if hasattr(self, "_breathe_job") and self._breathe_job:
            self.after_cancel(self._breathe_job)
        super().destroy()

    def _generate_color_gradient(self, hex1, hex2, steps):
        """Generates a list of hex colors interpolating between hex1 and hex2."""
        def hex_to_rgb(h): return tuple(int(h.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        def rgb_to_hex(r, g, b): return '#{:02x}{:02x}{:02x}'.format(r, g, b)
        
        rgb1 = hex_to_rgb(hex1)
        rgb2 = hex_to_rgb(hex2)
        
        gradient = []
        for i in range(steps):
            ratio = i / float(steps - 1)
            r = int(rgb1[0] * (1 - ratio) + rgb2[0] * ratio)
            g = int(rgb1[1] * (1 - ratio) + rgb2[1] * ratio)
            b = int(rgb1[2] * (1 - ratio) + rgb2[2] * ratio)
            gradient.append(rgb_to_hex(r, g, b))
        return gradient

    def _breathing_loop(self):
        """Animates the timer color and updates the real-time clock."""
        if not self.winfo_exists(): return
        
        # Update Clock
        from datetime import datetime
        now = datetime.now().strftime("%I:%M %p")
        if hasattr(self, "clock_lbl"):
            self.clock_lbl.configure(text=now)

        if not self._is_paused:
            self._breath_step += self._breath_direction
            if self._breath_step >= len(self._breathe_colors) - 1:
                self._breath_direction = -1
            elif self._breath_step <= 0:
                self._breath_direction = 1
                
            color = self._breathe_colors[self._breath_step]
            self.timer_label.configure(text_color=color)
        
        # Loop every 100ms
        self._breathe_job = self.after(100, self._breathing_loop)

    def setup_ui(self, subject, duration_minutes):
        self._total_sec = duration_minutes * 60
        
        # Main container with beautiful padding
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=40, pady=40)

        # Top Bar: Subject info & controls
        top_bar = ctk.CTkFrame(self.container, fg_color="transparent")
        top_bar.pack(fill="x")
        
        subj_frame = ctk.CTkFrame(top_bar, fg_color=self.c["bg_card"], corner_radius=12)
        subj_frame.pack(side="left")
        ctk.CTkLabel(subj_frame, text=f"{subject['icon']} {subject['name']}",
                     font=FONTS["title"], text_color=self.c["text_primary"]).pack(padx=16, pady=8)

        self.mute_btn = ctk.CTkButton(top_bar, text="🔊", width=40, height=40,
                                      fg_color="transparent", hover_color=self.c["bg_card"],
                                      text_color=self.c["text_secondary"], font=("Segoe UI", 18),
                                      command=self.controller.toggle_mute)
        self.mute_btn.pack(side="right")
        
        self.fs_btn = ctk.CTkButton(top_bar, text="⛶", width=40, height=40,
                                    fg_color="transparent", hover_color=self.c["bg_card"],
                                    text_color=self.c["text_secondary"], font=("Segoe UI", 18),
                                    command=self.toggle_fullscreen)
        self.fs_btn.pack(side="right", padx=8)

        self.min_btn = ctk.CTkButton(top_bar, text="↘ Mini", width=70, height=40,
                                    fg_color=self.c["bg_card"], hover_color=self.c["border"],
                                    text_color=self.c["text_secondary"], font=FONTS["small"],
                                    command=self.controller.minimize_focus)
        self.min_btn.pack(side="right", padx=8)

        # Clock Display
        self.clock_lbl = ctk.CTkLabel(top_bar, text="00:00 AM", font=FONTS["body"], 
                                      text_color=self.c["text_muted"])
        self.clock_lbl.pack(side="right", padx=20)

        # Center: Timer
        center_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        center_frame.pack(fill="both", expand=True)

        self.timer_label = ctk.CTkLabel(center_frame, text="00:00",
                                        font=("Segoe UI", 120, "bold"),
                                        text_color=self.c["text_primary"])
        self.timer_label.pack(expand=True)

        # Sub-center: Quote
        self.quote_label = ctk.CTkLabel(center_frame, text=self.controller.quotes_engine.get_focus_message(),
                                        font=("Segoe UI", 16, "italic"),
                                        text_color=self.c["text_muted"])
        self.quote_label.pack(pady=(0, 40))

        # Bottom Bar: Controls
        bottom_bar = ctk.CTkFrame(self.container, fg_color="transparent")
        bottom_bar.pack(fill="x", pady=20)

        controls = ctk.CTkFrame(bottom_bar, fg_color="transparent")
        controls.pack(expand=True)

        self.pause_btn = ctk.CTkButton(controls, text="⏸ Pause (Space)", width=160, height=48,
                                       fg_color=self.c["bg_card"], hover_color=self.c["border"],
                                       text_color=self.c["text_primary"], font=FONTS["button"],
                                       corner_radius=24,
                                       command=self.controller.pause_resume)
        self.pause_btn.pack(side="left", padx=10)

        ctk.CTkButton(controls, text="⏹ End (Esc)", width=160, height=48,
                      fg_color="transparent", hover_color=self.c["danger"],
                      text_color=self.c["text_secondary"], font=FONTS["button"],
                      corner_radius=24, border_width=1, border_color=self.c["border"],
                      command=self.controller.exit_focus).pack(side="left", padx=10)

    def show_fullscreen(self):
        self.attributes("-fullscreen", True)
        self._is_fullscreen = True
        self.focus_force()

    def toggle_fullscreen(self):
        self._is_fullscreen = not self._is_fullscreen
        self.attributes("-fullscreen", self._is_fullscreen)
        
    def update_timer_display(self, remaining_sec):
        mins, secs = divmod(int(remaining_sec), 60)
        self.timer_label.configure(text=f"{mins:02d}:{secs:02d}")

    def set_paused_state(self, is_paused):
        self._is_paused = is_paused
        if is_paused:
            self.pause_btn.configure(text="▶ Resume (Space)", fg_color=self.c["accent"], text_color="#FFFFFF")
            self.timer_label.configure(text_color=self.c["text_muted"])
        else:
            self.pause_btn.configure(text="⏸ Pause (Space)", fg_color=self.c["bg_card"], text_color=self.c["text_primary"])
            self.timer_label.configure(text_color=self._breathe_colors[self._breath_step])

    def set_mute_state(self, is_muted):
        self.mute_btn.configure(text="🔇" if is_muted else "🔊")
