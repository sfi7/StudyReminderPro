# ============================================================
# Study Reminder Pro - Reusable UI Widgets
# File: ui/widgets.py
# ============================================================

import tkinter as tk
import customtkinter as ctk
import math
from core.theme import FONTS


def get_resolved_bg(widget, default="#0D0F1A"):
    """Recursively find a solid background color to avoid 'transparent' crash in tk.Canvas."""
    curr = widget.master
    while curr:
        try:
            bg = curr.cget("fg_color")
            if bg and bg != "transparent":
                return bg
            curr = curr.master
        except Exception:
            break
    return default


class AnimatedProgressBar(ctk.CTkFrame):
    """Circular or linear progress bar with animation."""

    def __init__(self, master, size=80, thickness=8, pct=0.0,
                 color="#7C6EFA", bg="#1C2033", text_color="#F0F1FF", **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.size = size
        self.thickness = thickness
        self._pct = 0.0
        self._target = pct
        self.color = color
        self.bg_color = bg
        self.text_color = text_color

        self.canvas = tk.Canvas(self, width=size, height=size,
                                bg=get_resolved_bg(self),
                                highlightthickness=0)
        self.canvas.pack()
        self._redraw_progress(0)
        self._animate()

    def _redraw_progress(self, pct):
        self.canvas.delete("all")
        cx = cy = self.size / 2
        r = (self.size - self.thickness * 2) / 2
        # Background arc
        self.canvas.create_arc(
            cx - r, cy - r, cx + r, cy + r,
            start=0, extent=359.9,
            outline=self.bg_color, width=self.thickness, style="arc"
        )
        # Progress arc
        if pct > 0:
            extent = min(359.9, pct / 100 * 359.9)
            self.canvas.create_arc(
                cx - r, cy - r, cx + r, cy + r,
                start=90, extent=-extent,
                outline=self.color, width=self.thickness, style="arc",
                capstyle=tk.ROUND
            )
        # Center text
        self.canvas.create_text(
            cx, cy, text=f"{int(pct)}%",
            fill=self.text_color, font=("Segoe UI", int(self.size * 0.17), "bold")
        )

    def _animate(self):
        if abs(self._pct - self._target) > 0.5:
            self._pct += (self._target - self._pct) * 0.12
            self._redraw_progress(self._pct)
            self.after(16, self._animate)
        else:
            self._pct = self._target
            self._redraw_progress(self._pct)

    def set_progress(self, pct):
        self._target = pct
        self._animate()

    def update_colors(self, color=None, bg=None, text_color=None):
        if color:
            self.color = color
        if bg:
            self.bg_color = bg
        if text_color:
            self.text_color = text_color
        self._redraw_progress(self._pct)


class LinearProgressBar(ctk.CTkFrame):
    """Animated horizontal progress bar."""

    def __init__(self, master, width=200, height=8, pct=0.0,
                 color="#7C6EFA", bg="#1C2033", **kwargs):
        super().__init__(master, fg_color="transparent", width=width, height=height, **kwargs)
        self.bar_width = width
        self.bar_height = height
        self._pct = 0.0
        self._target = pct
        self.color = color
        self.bg_color = bg

        self.canvas = tk.Canvas(self, width=width, height=height,
                                highlightthickness=0, bg=get_resolved_bg(self))
        self.canvas.pack()
        self._redraw_progress(0)
        self._animate()

    def _redraw_progress(self, pct):
        self.canvas.delete("all")
        r = self.bar_height // 2
        # Background
        self._rounded_rect(0, 0, self.bar_width, self.bar_height, r, self.bg_color)
        # Foreground
        fill_w = max(0, int(self.bar_width * pct / 100))
        if fill_w > 0:
            self._rounded_rect(0, 0, fill_w, self.bar_height, r, self.color)

    def _rounded_rect(self, x1, y1, x2, y2, r, color):
        points = [
            x1 + r, y1, x2 - r, y1,
            x2, y1, x2, y1 + r,
            x2, y2 - r, x2, y2,
            x2 - r, y2, x1 + r, y2,
            x1, y2, x1, y2 - r,
            x1, y1 + r, x1, y1
        ]
        self.canvas.create_polygon(points, fill=color, outline=color, smooth=True)

    def _animate(self):
        if abs(self._pct - self._target) > 0.3:
            self._pct += (self._target - self._pct) * 0.15
            self._redraw_progress(self._pct)
            self.after(16, self._animate)
        else:
            self._pct = self._target
            self._redraw_progress(self._pct)

    def set_progress(self, pct):
        self._target = pct
        self._animate()


class GlassCard(ctk.CTkFrame):
    """A card with glassmorphism-style border."""

    def __init__(self, master, color="#7C6EFA", hover=True, **kwargs):
        self._accent = color
        kwargs.setdefault("corner_radius", 16)
        kwargs.setdefault("border_width", 1)
        kwargs.setdefault("border_color", "#2A2E45")
        super().__init__(master, **kwargs)
        self._hover = hover
        if hover:
            self.bind("<Enter>", self._on_enter)
            self.bind("<Leave>", self._on_leave)

    def _on_enter(self, _e):
        try:
            self.configure(border_width=2, border_color=self._accent)
        except Exception:
            pass

    def _on_leave(self, _e):
        try:
            self.configure(border_width=1, border_color="#2A2E45")
        except Exception:
            pass


class ExamCountdownBadge(ctk.CTkFrame):
    """Small badge showing days until exam with color coding."""

    def __init__(self, master, days, colors, **kwargs):
        kwargs.setdefault("corner_radius", 8)
        if days is None:
            bg = colors["bg_secondary"]
            txt = "No Exam"
            fg = colors["text_muted"]
        elif days < 0:
            bg = colors["tag_high"]
            txt = "PAST"
            fg = colors["tag_high_text"]
        elif days == 0:
            bg = colors["tag_high"]
            txt = "TODAY!"
            fg = colors["tag_high_text"]
        elif days <= 3:
            bg = colors["tag_high"]
            txt = f"{days}d left"
            fg = colors["tag_high_text"]
        elif days <= 7:
            bg = colors["tag_medium"]
            txt = f"{days}d left"
            fg = colors["tag_medium_text"]
        else:
            bg = colors["tag_low"]
            txt = f"{days}d left"
            fg = colors["tag_low_text"]

        super().__init__(master, fg_color=bg, **kwargs)
        ctk.CTkLabel(self, text=txt, font=FONTS["tiny"],
                     text_color=fg).pack(padx=8, pady=2)


class LiveCountdown(ctk.CTkFrame):
    """A ticking countdown display for exam dates."""
    def __init__(self, master, db, subject, colors, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.db = db
        self.subject = subject
        self.colors = colors
        
        self.lbl = ctk.CTkLabel(self, text="", font=FONTS["tiny"],
                                text_color=colors["text_secondary"])
        self.lbl.pack(side="left")
        self._update_timer()

    def _update_timer(self):
        try:
            info = self.db.exam_countdown_info(self.subject)
            if not info:
                self.lbl.configure(text="No exam date set")
                return

            days, hours, minutes, seconds = info
            if days < 0:
                self.lbl.configure(text="🏁 Exam Finished", text_color=self.colors["text_muted"])
            elif days == 0 and hours == 0 and minutes == 0 and seconds == 0:
                self.lbl.configure(text="🔥 EXAM NOW!", text_color=self.colors["danger"])
            else:
                parts = []
                if days > 0: parts.append(f"{days}d")
                if hours > 0 or days > 0: parts.append(f"{hours}h")
                if minutes > 0 or hours > 0 or days > 0: parts.append(f"{minutes}m")
                parts.append(f"{seconds}s")
                
                self.lbl.configure(text=f"⏳ {' '.join(parts)} left", 
                                   text_color=self.colors["tag_high_text"] if days <= 3 else self.colors["text_secondary"])
            
            self.after(1000, self._update_timer) # Update every second
        except Exception:
            pass


class ToastNotification:
    """Temporary popup notification that fades away."""

    def __init__(self, parent, message, kind="info", colors=None):
        self.parent = parent
        colors = colors or {}
        color_map = {
            "success": colors.get("success", "#34D399"),
            "warning": colors.get("warning", "#FBBF24"),
            "error":   colors.get("danger", "#F87171"),
            "info":    colors.get("accent", "#7C6EFA"),
        }
        bg = color_map.get(kind, color_map["info"])

        self.win = tk.Toplevel(parent)
        self.win.withdraw()
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.configure(bg=bg)

        frame = ctk.CTkFrame(self.win, fg_color=bg, corner_radius=12)
        frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        self.win.bind("<Button-1>", lambda e: self.win.destroy())
        frame.bind("<Button-1>", lambda e: self.win.destroy())

        icon_map = {"success": "✅", "warning": "⚠️", "error": "❌", "info": "💡"}
        icon = icon_map.get(kind, "💡")
        lbl = ctk.CTkLabel(frame, text=f"{icon}  {message}",
                     font=FONTS["body"], text_color="#FFFFFF")
        lbl.pack(padx=20, pady=12)
        lbl.bind("<Button-1>", lambda e: self.win.destroy())

        # Position bottom-right of parent
        self.win.update_idletasks()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_x()
        py = parent.winfo_y()
        tw = self.win.winfo_width() + 40
        th = 60
        x = px + pw - tw - 24
        y = py + ph - th - 32
        self.win.geometry(f"+{x}+{y}")
        self.win.deiconify()
        self.win.after(3500, self.win.destroy)


class SidebarButton(ctk.CTkFrame):
    """Custom animated sidebar navigation button."""

    def __init__(self, master, text, icon, command, active=False,
                 colors=None, **kwargs):
        super().__init__(master, fg_color="transparent",
                         cursor="hand2", **kwargs)
        self.colors = colors or {}
        self._command = command
        self._active = active
        self._text = text

        self._accent_line = ctk.CTkFrame(self, width=4, fg_color="transparent",
                                         corner_radius=2)
        self._accent_line.pack(side="left", fill="y", padx=(0, 0))

        self._inner = ctk.CTkFrame(self, fg_color="transparent", corner_radius=12)
        self._inner.pack(side="left", fill="both", expand=True, padx=(4, 12), pady=4)

        self._icon_lbl = ctk.CTkLabel(self._inner, text=icon,
                                       font=("Segoe UI", 16), width=28)
        self._icon_lbl.pack(side="left", padx=(8, 4))

        self._text_lbl = ctk.CTkLabel(self._inner, text=text,
                                       font=FONTS["title"],
                                       anchor="w")
        self._text_lbl.pack(side="left", fill="x", expand=True)

        self.set_active(active)
        for w in (self, self._inner, self._icon_lbl, self._text_lbl, self._accent_line):
            w.bind("<Button-1>", self._click)
            w.bind("<Enter>", self._hover_on)
            w.bind("<Leave>", self._hover_off)

    def _click(self, _e=None):
        self._command()

    def _hover_on(self, _e=None):
        if not self._active:
            self._inner.configure(fg_color=self.colors.get("hover_overlay", "#222640"))

    def _hover_off(self, _e=None):
        if not self._active:
            self._inner.configure(fg_color="transparent")

    def set_active(self, active):
        self._active = active
        c = self.colors
        if active:
            self._inner.configure(fg_color=c.get("sidebar_active", "#1C2033"))
            self._text_lbl.configure(text_color=c.get("accent", "#7C6EFA"))
            self._icon_lbl.configure(text_color=c.get("accent", "#7C6EFA"))
            self._accent_line.configure(fg_color=c.get("sidebar_active_border", "#7C6EFA"))
        else:
            self._inner.configure(fg_color="transparent")
            self._text_lbl.configure(text_color=c.get("text_secondary", "#8B8FA8"))
            self._icon_lbl.configure(text_color=c.get("text_secondary", "#8B8FA8"))
            self._accent_line.configure(fg_color="transparent")


class SummaryDialog(tk.Toplevel):
    """Premium dialog shown after a focus session finishes."""
    def __init__(self, master, session_data, colors, on_close=None):
        super().__init__(master)
        self.colors = colors
        self.on_close = on_close
        
        self.title("Session Complete")
        self.geometry("420x480")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.configure(bg=colors["bg_primary"])
        self.grab_set()
        
        self._build(session_data)

    def _build(self, data):
        c = self.colors
        
        # Header
        ctk.CTkLabel(self, text="🎉", font=("Segoe UI", 48)).pack(pady=(30, 10))
        ctk.CTkLabel(self, text="Focus Session Complete!", font=FONTS["heading"], text_color=c["text_primary"]).pack()
        ctk.CTkLabel(self, text="AI detected high concentration. Great job!", font=FONTS["small"], text_color=c["accent_light"]).pack(pady=(0, 20))
        
        # Stats Card
        card = ctk.CTkFrame(self, fg_color=c["bg_card"], corner_radius=16, border_width=1, border_color=c["border"])
        card.pack(fill="x", padx=40, pady=10)
        
        # Duration
        row1 = ctk.CTkFrame(card, fg_color="transparent")
        row1.pack(fill="x", padx=20, pady=(15, 8))
        ctk.CTkLabel(row1, text="Duration:", font=FONTS["body"], text_color=c["text_secondary"]).pack(side="left")
        ctk.CTkLabel(row1, text=f"{data.get('duration_minutes', 0)} mins", font=FONTS["title"], text_color=c["text_primary"]).pack(side="right")
        
        # Interruptions
        row2 = ctk.CTkFrame(card, fg_color="transparent")
        row2.pack(fill="x", padx=20, pady=(0, 15))
        ctk.CTkLabel(row2, text="Interruptions:", font=FONTS["body"], text_color=c["text_secondary"]).pack(side="left")
        interrupts = data.get('interruptions', 0)
        color = c["success"] if interrupts == 0 else (c["warning"] if interrupts < 3 else c["danger"])
        ctk.CTkLabel(row2, text=str(interrupts), font=FONTS["title"], text_color=color).pack(side="right")
        
        # Quote
        ctk.CTkLabel(self, text=f"\"Keep going, each session brings you closer to mastery.\"", 
                     font=("Segoe UI", 12, "italic"), text_color=c["text_muted"], wraplength=300).pack(pady=20)
        
        # Close Button
        ctk.CTkButton(self, text="Continue to Dashboard", font=FONTS["body"], 
                      height=40, corner_radius=20, fg_color=c["accent"], hover_color=c["accent_hover"],
                      command=self._close).pack(pady=(10, 30))

    def _close(self):
        if self.on_close:
            self.on_close()
        self.destroy()
