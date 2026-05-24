# ============================================================
# Study Reminder Pro - Floating Session Overlay  (v2 – Stopwatch Edition)
# File: focus/floating_overlay.py
# ============================================================

import tkinter as tk
import customtkinter as ctk
import math
from themes.typography import FONTS


def _hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def _blend(c1, c2, t):
    r1,g1,b1 = _hex_to_rgb(c1)
    r2,g2,b2 = _hex_to_rgb(c2)
    return "#{:02x}{:02x}{:02x}".format(
        int(r1+(r2-r1)*t), int(g1+(g2-g1)*t), int(b1+(b2-b1)*t))


class MiniProgressRing(tk.Canvas):
    """A tiny circular progress ring for the floating overlay."""
    SIZE = 44

    def __init__(self, parent, bg_color, accent_color, **kw):
        super().__init__(parent, width=self.SIZE, height=self.SIZE,
                         highlightthickness=0, bd=0, bg=bg_color, **kw)
        self._accent = accent_color
        self._bg_col = bg_color
        self._progress = 0.0  # 0.0 → 1.0
        self._draw()

    def set_progress(self, frac):
        self._progress = max(0.0, min(1.0, frac))
        self._draw()

    def _draw(self):
        self.delete("all")
        c = self.SIZE // 2
        R = c - 4

        # Track
        self.create_oval(c-R, c-R, c+R, c+R,
                         outline=_blend(self._accent, self._bg_col, 0.75),
                         width=3, fill="")
        # Arc
        if self._progress > 0.003:
            extent = self._progress * 359.9
            self.create_arc(c-R, c-R, c+R, c+R,
                            start=90, extent=-extent,
                            outline=self._accent, width=3, style="arc")


class FloatingOverlay(tk.Toplevel):
    """
    Mini floating pill that stays on top when Focus is minimised.
    Shows: mode badge · time remaining · mini progress ring · pause/expand buttons.
    Draggable with edge-snapping and smooth animation.
    """

    W, H = 280, 64

    def __init__(self, controller, theme_manager):
        super().__init__()
        self.controller = controller
        self.c = theme_manager.colors

        # ── Window chrome ──
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.geometry(f"{self.W}x{self.H}+80+80")
        self.configure(bg=self.c["bg_card"])
        self.attributes("-alpha", 0.96)

        # State
        self._total_sec  = 1
        self._mode_label = "Work"
        self._accent     = self.c["accent"]
        self._move_job   = None

        # ── Border frame ──
        self._border = ctk.CTkFrame(
            self, fg_color=self.c["bg_card"],
            border_width=1, border_color=self._accent,
            corner_radius=16
        )
        self._border.pack(fill="both", expand=True)

        self._build_ui()
        self._bind_drag(self._border)

    # ── Build ────────────────────────────────────────────────
    def _build_ui(self):
        # Mini progress ring (left)
        self.ring = MiniProgressRing(self._border,
                                     bg_color=self.c["bg_card"],
                                     accent_color=self._accent)
        self.ring.pack(side="left", padx=(8, 2), pady=10)
        self._bind_drag(self.ring)

        # Mode + time (center)
        info = tk.Frame(self._border, bg=self.c["bg_card"])
        info.pack(side="left", fill="both", expand=True, padx=4)
        self._bind_drag(info)

        self.mode_lbl = tk.Label(
            info, text="🎯 Work",
            bg=self.c["bg_card"], fg=self._accent,
            font=("Segoe UI", 9, "bold")
        )
        self.mode_lbl.pack(anchor="w")
        self._bind_drag(self.mode_lbl)

        self.timer_label = tk.Label(
            info, text="00:00",
            bg=self.c["bg_card"], fg=self.c["text_primary"],
            font=("Segoe UI", 15, "bold")
        )
        self.timer_label.pack(anchor="w")
        self._bind_drag(self.timer_label)

        # Buttons (right)
        ctrl = tk.Frame(self._border, bg=self.c["bg_card"])
        ctrl.pack(side="right", padx=6)

        self.pause_btn = ctk.CTkButton(
            ctrl, text="⏸", width=28, height=28,
            fg_color="transparent", hover_color=self.c["bg_secondary"],
            text_color=self.c["text_secondary"], font=("Segoe UI", 13),
            corner_radius=14,
            command=self.controller.pause_resume
        )
        self.pause_btn.pack(side="left", padx=2)

        ctk.CTkButton(
            ctrl, text="↗", width=28, height=28,
            fg_color="transparent", hover_color=self.c["bg_secondary"],
            text_color=self.c["text_secondary"], font=("Segoe UI", 13),
            corner_radius=14,
            command=self.controller.restore_focus
        ).pack(side="left", padx=2)

    def _bind_drag(self, widget):
        widget.bind("<Button-1>",      self._start_drag)
        widget.bind("<B1-Motion>",     self._on_drag)
        widget.bind("<ButtonRelease-1>", self._end_drag)

    # ── Public API ───────────────────────────────────────────
    def set_mode(self, mode: str, accent: str):
        """Call when mode changes so badge + ring colour update."""
        icons = {"Work":"🎯","Break":"☕","Short Break":"🌿",
                 "Long Break":"🏖","Custom":"⚡"}
        icon = icons.get(mode, "⏱")
        self._mode_label = f"{icon} {mode}"
        self._accent = accent
        if hasattr(self, "mode_lbl"):
            self.mode_lbl.configure(fg=accent)
            self.mode_lbl.configure(text=self._mode_label)
        if hasattr(self, "ring"):
            self.ring._accent = accent
            self.ring._draw()
        if hasattr(self, "_border"):
            self._border.configure(border_color=accent)

    def update_timer_display(self, remaining_sec, total_sec=None):
        mins, secs = divmod(int(remaining_sec), 60)
        self.timer_label.configure(text=f"{mins:02d}:{secs:02d}")
        if total_sec:
            self._total_sec = max(1, total_sec)
        elapsed = self._total_sec - remaining_sec
        self.ring.set_progress(elapsed / self._total_sec)

    def set_paused_state(self, is_paused):
        if is_paused:
            self.pause_btn.configure(text="▶", text_color=self._accent)
            self.timer_label.configure(fg=self.c["text_muted"])
        else:
            self.pause_btn.configure(text="⏸", text_color=self.c["text_secondary"])
            self.timer_label.configure(fg=self.c["text_primary"])

    # ── Drag + edge snap ─────────────────────────────────────
    def _start_drag(self, event):
        self._offset_x = event.x_root - self.winfo_x()
        self._offset_y = event.y_root - self.winfo_y()

    def _on_drag(self, event):
        x = event.x_root - self._offset_x
        y = event.y_root - self._offset_y
        self.geometry(f"+{x}+{y}")

    def _end_drag(self, event):
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x, y = self.winfo_x(), self.winfo_y()
        snap = 40
        if x < snap:           x = 8
        elif x + self.W > sw - snap: x = sw - self.W - 8
        if y < snap:           y = 8
        elif y + self.H > sh - snap: y = sh - self.H - 8
        self._smooth_move(x, y)

    def _smooth_move(self, tx, ty):
        if not self.winfo_exists():
            return
        cx, cy = self.winfo_x(), self.winfo_y()
        dx, dy = tx - cx, ty - cy
        if abs(dx) < 2 and abs(dy) < 2:
            self.geometry(f"+{tx}+{ty}")
            return
        self.geometry(f"+{cx + int(dx*0.3)}+{cy + int(dy*0.3)}")
        self._move_job = self.after(16, lambda: self._smooth_move(tx, ty))

    def destroy(self):
        if self._move_job:
            try: self.after_cancel(self._move_job)
            except Exception: pass
        super().destroy()
