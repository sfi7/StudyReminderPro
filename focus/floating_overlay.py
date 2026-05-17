# ============================================================
# Study Reminder Pro - Floating Session Overlay
# File: focus/floating_overlay.py
# ============================================================

import tkinter as tk
import customtkinter as ctk
from themes.typography import FONTS

class FloatingOverlay(tk.Toplevel):
    """
    Mini floating timer overlay that stays on top.
    Draggable, edge-snapping, used when the main Focus UI is minimized.
    """
    def __init__(self, controller, theme_manager):
        super().__init__()
        self.controller = controller
        self.c = theme_manager.colors

        self.overrideredirect(True) # Remove standard window decorations
        self.attributes("-topmost", True)
        self.geometry("220x60+100+100")
        
        self.configure(bg=self.c["bg_card"])
        self.attributes("-alpha", 0.95) # Slight glassmorphism effect
        
        # A simple border can be simulated with a frame
        self._border = ctk.CTkFrame(self, fg_color=self.c["bg_card"], 
                                    border_width=1, border_color=self.c["accent"],
                                    corner_radius=12)
        self._border.pack(fill="both", expand=True)

        # Dragging state
        self._offset_x = 0
        self._offset_y = 0
        self._target_x = None
        self._target_y = None
        
        self._border.bind("<Button-1>", self._start_drag)
        self._border.bind("<B1-Motion>", self._on_drag)
        self._border.bind("<ButtonRelease-1>", self._end_drag)

        self._build_ui()

    def _build_ui(self):
        # Timer Label
        self.timer_label = ctk.CTkLabel(self._border, text="00:00",
                                        font=FONTS["title"],
                                        text_color=self.c["text_primary"])
        self.timer_label.pack(side="left", padx=12)
        self.timer_label.bind("<Button-1>", self._start_drag)
        self.timer_label.bind("<B1-Motion>", self._on_drag)

        # Controls
        ctrl = ctk.CTkFrame(self._border, fg_color="transparent")
        ctrl.pack(side="right", padx=6)

        self.pause_btn = ctk.CTkButton(ctrl, text="⏸", width=30, height=30,
                                       fg_color="transparent", hover_color=self.c["bg_secondary"],
                                       text_color=self.c["text_secondary"], font=("Segoe UI", 12),
                                       command=self.controller.pause_resume)
        self.pause_btn.pack(side="left", padx=2)

        self.expand_btn = ctk.CTkButton(ctrl, text="↗", width=30, height=30,
                                        fg_color="transparent", hover_color=self.c["bg_secondary"],
                                        text_color=self.c["text_secondary"], font=("Segoe UI", 12),
                                        command=self.controller.restore_focus)
        self.expand_btn.pack(side="left", padx=2)

    def _start_drag(self, event):
        self._offset_x = event.x
        self._offset_y = event.y

    def _on_drag(self, event):
        x = self.winfo_pointerx() - self._offset_x
        y = self.winfo_pointery() - self._offset_y
        self.geometry(f"+{x}+{y}")
        
    def _end_drag(self, event):
        """Edge snapping logic."""
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        w = self.winfo_width()
        h = self.winfo_height()
        
        x = self.winfo_x()
        y = self.winfo_y()
        
        snap_threshold = 50
        
        if x < snap_threshold:
            x = 0
        elif x + w > screen_w - snap_threshold:
            x = screen_w - w
            
        if y < snap_threshold:
            y = 0
        elif y + h > screen_h - snap_threshold:
            y = screen_h - h
            
        self._smooth_move(x, y)

    def destroy(self):
        if hasattr(self, "_move_job") and self._move_job:
            self.after_cancel(self._move_job)
        super().destroy()

    def _smooth_move(self, target_x, target_y):
        """Smoothly animates the window to the target position."""
        if not self.winfo_exists(): return
        curr_x = self.winfo_x()
        curr_y = self.winfo_y()
        
        dx = target_x - curr_x
        dy = target_y - curr_y
        
        if abs(dx) < 2 and abs(dy) < 2:
            self.geometry(f"+{target_x}+{target_y}")
            return
            
        new_x = curr_x + int(dx * 0.3)
        new_y = curr_y + int(dy * 0.3)
        self.geometry(f"+{new_x}+{new_y}")
        self._move_job = self.after(16, lambda: self._smooth_move(target_x, target_y))

    def update_timer_display(self, remaining_sec):
        mins, secs = divmod(int(remaining_sec), 60)
        self.timer_label.configure(text=f"{mins:02d}:{secs:02d}")

    def set_paused_state(self, is_paused):
        if is_paused:
            self.pause_btn.configure(text="▶", text_color=self.c["accent"])
            self.timer_label.configure(text_color=self.c["text_muted"])
        else:
            self.pause_btn.configure(text="⏸", text_color=self.c["text_secondary"])
            self.timer_label.configure(text_color=self.c["text_primary"])
