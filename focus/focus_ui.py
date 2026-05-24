# ============================================================
# Study Reminder Pro - Focus UI  (iOS-Style Stopwatch Edition v2)
# File: focus/focus_ui.py
# ============================================================

import tkinter as tk
import customtkinter as ctk
import math
from datetime import datetime
from themes.typography import FONTS


# ──────────────────────────────────────────────────────────────
#  Colour helpers
# ──────────────────────────────────────────────────────────────
def _hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def _rgb_to_hex(r, g, b):
    return "#{:02x}{:02x}{:02x}".format(int(r), int(g), int(b))

def _blend(c1, c2, t):
    r1, g1, b1 = _hex_to_rgb(c1)
    r2, g2, b2 = _hex_to_rgb(c2)
    return _rgb_to_hex(r1+(r2-r1)*t, g1+(g2-g1)*t, b1+(b2-b1)*t)

def _alpha(fg, bg, a):
    return _blend(bg, fg, a)


# ──────────────────────────────────────────────────────────────
#  AnalogStopwatch  (tk.Canvas)
# ──────────────────────────────────────────────────────────────
class AnalogStopwatch(tk.Canvas):
    """iOS-style analog stopwatch face drawn on a tk.Canvas."""

    DIAL_R     = 140
    SUB_R      =  40
    SUB_OFFSET =  60   # below centre

    def __init__(self, parent, colors, size=310, **kw):
        kw.setdefault("highlightthickness", 0)
        kw.setdefault("bd", 0)
        super().__init__(parent, width=size, height=size, **kw)
        self.c   = colors
        self.sz  = size
        self.cx  = size // 2
        self.cy  = size // 2
        self._elapsed = 0.0
        self._total   = 1500.0
        self._paused  = False
        self._build_static()
        self._draw_dynamic()

    # ── public ──
    def set_elapsed(self, elapsed, total, paused=False):
        self._elapsed = elapsed
        self._total   = max(1, total)
        self._paused  = paused
        self._draw_dynamic()

    # ── theme shortcuts ──
    def _bg(self):       return self.c["bg_primary"]
    def _face(self):     return self.c["bg_secondary"]
    def _rim(self):      return self.c["border"]
    def _tick_h(self):   return self.c["text_secondary"]
    def _tick_l(self):   return self.c["text_muted"]
    def _nums(self):     return self.c["text_primary"]
    def _acc(self):      return self.c["accent"]
    def _warn(self):     return self.c["warning"]

    # ── static face ──
    def _build_static(self):
        self.delete("all")
        self.configure(bg=self._bg())
        cx, cy, R = self.cx, self.cy, self.DIAL_R

        # glow rings
        for off, a in [(7, .06), (4, .11), (2, .18)]:
            gc = _alpha(self.c["accent"], self._bg(), a)
            self.create_oval(cx-R-off, cy-R-off, cx+R+off, cy+R+off,
                             fill=gc, outline="", tags="s")

        # face
        self.create_oval(cx-R, cy-R, cx+R, cy+R,
                         fill=self._face(), outline=self._rim(), width=2, tags="s")

        # progress track
        pad = 10
        self.create_arc(cx-R+pad, cy-R+pad, cx+R-pad, cy+R-pad,
                        start=90, extent=359.9,
                        outline=_alpha(self._acc(), self._face(), .15),
                        width=5, style="arc", tags="s")

        # ticks + numbers
        for i in range(60):
            ang  = math.radians(i*6 - 90)
            maj  = (i % 5 == 0)
            i_r  = R - (16 if maj else 7)
            o_r  = R - 4
            self.create_line(cx+i_r*math.cos(ang), cy+i_r*math.sin(ang),
                             cx+o_r*math.cos(ang), cy+o_r*math.sin(ang),
                             fill=self._tick_h() if maj else self._tick_l(),
                             width=2.5 if maj else 1, tags="s")
            if maj:
                nr = R - 30
                self.create_text(cx+nr*math.cos(ang), cy+nr*math.sin(ang),
                                 text=str(i), fill=self._nums(),
                                 font=("Segoe UI", 7, "bold"), tags="s")

        # "ELAPSED" label
        self.create_text(cx, cy-48, text="ELAPSED",
                         fill=self._tick_h(), font=("Segoe UI", 7, "bold"), tags="s")

        # sub-dial
        self._build_subdial_static()

    def _build_subdial_static(self):
        cx, cy = self.cx, self.cy + self.SUB_OFFSET
        R = self.SUB_R
        self.create_oval(cx-R-2, cy-R-2, cx+R+2, cy+R+2,
                         fill=_alpha(self._acc(), self._face(), .10),
                         outline=self._rim(), width=1, tags="s")
        self.create_oval(cx-R, cy-R, cx+R, cy+R,
                         fill=self._face(), outline=self._rim(), width=1, tags="s")
        for i in range(60):
            maj = (i % 15 == 0)
            ang = math.radians(i*6 - 90)
            i_r = R - (7 if maj else 3)
            o_r = R - 2
            self.create_line(cx+i_r*math.cos(ang), cy+i_r*math.sin(ang),
                             cx+o_r*math.cos(ang), cy+o_r*math.sin(ang),
                             fill=self._tick_l(), width=1, tags="s")

    # ── dynamic ──
    def _draw_dynamic(self):
        self.delete("d")
        cx, cy, R = self.cx, self.cy, self.DIAL_R

        # progress arc
        frac = min(self._elapsed / self._total, 1.0)
        extent_deg = frac * 359.9
        if extent_deg > 0.5:  # Prevents Tkinter tiny extent full-circle bug
            pad = 10
            self.create_arc(cx-R+pad, cy-R+pad, cx+R-pad, cy+R-pad,
                            start=90, extent=-extent_deg,
                            outline=self._acc(), width=5, style="arc", tags="d")

        # minute hand
        min_ang = math.radians((self._elapsed/60.0)*6 - 90)
        self._hand(cx, cy, min_ang, R-26, 6, self._nums(), tail=18)

        # second hand
        sec_ang = math.radians((self._elapsed % 60)*6 - 90)
        self._hand(cx, cy, sec_ang, R-16, 2, self._acc(), tail=25)

        # sub-dial second hand
        scx, scy = cx, cy + self.SUB_OFFSET
        self._hand(scx, scy, sec_ang, self.SUB_R-8, 1.5, self._warn(), tail=0)

        # centre jewel
        r1, r2 = 6, 3
        self.create_oval(cx-r1, cy-r1, cx+r1, cy+r1,
                         fill=self._acc(), outline="", tags="d")
        self.create_oval(cx-r2, cy-r2, cx+r2, cy+r2,
                         fill=self._bg(), outline="", tags="d")
        # sub-dial dot
        self.create_oval(scx-2, scy-2, scx+2, scy+2,
                         fill=self._warn(), outline="", tags="d")

    def _hand(self, cx, cy, ang, length, w, color, tail=0):
        tx = cx + length*math.cos(ang)
        ty = cy + length*math.sin(ang)
        bx = cx - tail*math.cos(ang) if tail else cx
        by = cy - tail*math.sin(ang) if tail else cy
        # shadow
        self.create_line(tx+1, ty+1, bx+1, by+1,
                         fill=_alpha("#000000", self._face(), .22),
                         width=w+1, capstyle="round", tags="d")
        self.create_line(tx, ty, bx, by,
                         fill=color, width=w, capstyle="round", tags="d")


# ──────────────────────────────────────────────────────────────
#  RingButton  (tk.Canvas)
# ──────────────────────────────────────────────────────────────
class RingButton(tk.Canvas):
    """iOS-style double-ring circular button."""

    def __init__(self, parent, text, size, bg_color, fg_color,
                 hover_color, command=None, **kw):
        bg = parent.cget("bg")
        super().__init__(parent, width=size, height=size,
                         highlightthickness=0, bd=0, bg=bg, **kw)
        self.size  = size
        self.text  = text
        self.bg    = bg_color
        self.fg    = fg_color
        self.hover = hover_color
        self.cmd   = command
        self._hov  = False
        self._draw()
        self.bind("<Enter>",    lambda _: self._set_hover(True))
        self.bind("<Leave>",    lambda _: self._set_hover(False))
        self.bind("<Button-1>", lambda _: self.cmd() if self.cmd else None)

    def configure_text(self, text, bg_color=None):
        self.text = text
        if bg_color:
            self.bg = bg_color
        self._draw()

    def _set_hover(self, v):
        self._hov = v
        self._draw()

    def _draw(self):
        self.delete("all")
        c = self.size // 2
        # outer ring
        ring = _alpha(self.bg, "#000000", 0.35)
        self.create_oval(2, 2, self.size-2, self.size-2,
                         fill="", outline=ring, width=3)
        # inner fill
        inn = 10
        fill = self.hover if self._hov else self.bg
        self.create_oval(inn, inn, self.size-inn, self.size-inn,
                         fill=fill, outline="")
        self.create_text(c, c, text=self.text, fill=self.fg,
                         font=("Segoe UI", 12, "bold"))


# ──────────────────────────────────────────────────────────────
#  SegmentRow
# ──────────────────────────────────────────────────────────────
class SegmentRow(ctk.CTkFrame):
    def __init__(self, parent, index, elapsed_str, delta_str,
                 colors, best=False, worst=False):
        super().__init__(parent, fg_color="transparent", corner_radius=0)
        c = colors
        ctk.CTkFrame(self, fg_color=c["border"], height=1).pack(fill="x")
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=4, pady=4)
        tag = c["accent"]
        if best:  tag = c["success"]
        if worst: tag = c["danger"]
        ctk.CTkLabel(row, text=f"Segment {index}", font=FONTS["small"],
                     text_color=tag, width=80, anchor="w").pack(side="left")
        ctk.CTkLabel(row, text=elapsed_str,
                     font=("Segoe UI", 11, "bold"),
                     text_color=c["text_primary"]).pack(side="right", padx=4)
        ctk.CTkLabel(row, text=delta_str, font=FONTS["small"],
                     text_color=c["text_muted"]).pack(side="right", padx=8)


# ──────────────────────────────────────────────────────────────
#  SoundPanel  – volume slider strip
# ──────────────────────────────────────────────────────────────
class SoundPanel(ctk.CTkFrame):
    """
    Compact sound control row:  🔔 icon | volume slider | % label | mute btn
    Connects directly to SoundManager.set_volume() / toggle_mute().
    Does NOT touch notification settings.
    """

    def __init__(self, parent, colors, sound_manager, **kw):
        super().__init__(parent, fg_color=colors["bg_card"],
                         corner_radius=14, **kw)
        self.c  = colors
        self.sm = sound_manager

        initial_vol = self.sm.get_volume()          # 0.0 – 1.0
        self._vol_var = tk.DoubleVar(value=initial_vol)
        self._muted   = False

        self._build(initial_vol)

    def _build(self, initial_vol):
        c = self.c

        # Bell icon
        ctk.CTkLabel(self, text="🔔", font=("Segoe UI", 15),
                     text_color=c["text_secondary"]).pack(side="left", padx=(12, 4))

        # Sound Selector Dropdown
        current_sound = self.sm.settings.get("focus_ambient_sound", "Silence")
        _SOUNDS = ["Silence", "Clock Ticking", "Rain", "Ocean Waves", "Wind"]
        # Validate saved value – fall back to Silence if key changed
        if current_sound not in _SOUNDS:
            current_sound = "Silence"
        self.sound_menu = ctk.CTkOptionMenu(
            self,
            values=_SOUNDS,
            command=self._on_sound_select,
            font=FONTS["small"],
            fg_color=c["bg_primary"],
            button_color=c["bg_primary"],
            button_hover_color=c["bg_secondary"],
            text_color=c["text_primary"],
            width=120,
            height=24
        )
        self.sound_menu.set(current_sound)
        self.sound_menu.pack(side="left", padx=(0, 8))

        # Mute button (right-most)
        self.mute_btn = ctk.CTkButton(
            self, text="🔊", width=36, height=36,
            fg_color="transparent",
            hover_color=c["border"],
            text_color=c["text_secondary"],
            font=("Segoe UI", 14),
            command=self._toggle_mute
        )
        self.mute_btn.pack(side="right", padx=(4, 10))

        # Volume % label
        self.vol_lbl = ctk.CTkLabel(
            self, text=f"{int(initial_vol*100)}%",
            font=("Segoe UI", 10, "bold"),
            text_color=c["text_muted"],
            width=34
        )
        self.vol_lbl.pack(side="right", padx=2)

        # Slider
        self.slider = ctk.CTkSlider(
            self,
            from_=0.0, to=1.0,
            variable=self._vol_var,
            width=160,
            height=14,
            progress_color=c["accent"],
            button_color=c["accent"],
            button_hover_color=c["accent_hover"],
            fg_color=c["border"],
            command=self._on_slider
        )
        self.slider.pack(side="left", fill="x", expand=True, padx=(0, 8))

    def _on_slider(self, val):
        val = float(val)
        self._muted = (val == 0)
        self.sm.set_volume(val)
        self.vol_lbl.configure(text=f"{int(val*100)}%")
        self.mute_btn.configure(text="🔇" if self._muted else "🔊")

    def _on_sound_select(self, val):
        self.sm.change_ambient_sound(val)

    def _toggle_mute(self):
        is_now_muted = self.sm.toggle_mute()
        self._muted = is_now_muted
        self.mute_btn.configure(text="🔇" if is_now_muted else "🔊")
        if is_now_muted:
            self.vol_lbl.configure(text="0%")
        else:
            v = self.sm.get_volume()
            self._vol_var.set(v)
            self.vol_lbl.configure(text=f"{int(v*100)}%")

    def sync_mute_icon(self, is_muted: bool):
        """Keep the mute icon in sync when controller toggles mute externally."""
        self._muted = is_muted
        self.mute_btn.configure(text="🔇" if is_muted else "🔊")


# ──────────────────────────────────────────────────────────────
#  FocusUI – Main window
# ──────────────────────────────────────────────────────────────
class FocusUI(tk.Toplevel):
    """
    Immersive fullscreen Pomodoro/Focus UI – iOS stopwatch edition.

    Layout (top→bottom, all inside a CTkScrollableFrame so nothing is clipped):
      • Top bar  : subject chip · mode badge · clock · mute · mini · fullscreen
      • [scroll] : page dots · analog OR digital face · quote
                   sound panel · segments log
      • Bottom   : End  ·  + Seg  ·  Pause/Resume  ring buttons
    """

    def __init__(self, controller, theme_manager):
        super().__init__()
        self.controller = controller
        self.tm = theme_manager
        self.c  = theme_manager.colors

        self.title("Focus Mode")
        self.configure(bg=self.c["bg_primary"])
        self.protocol("WM_DELETE_WINDOW", self.controller.exit_focus)
        self.bind("<Key>", self.controller.handle_keypress)

        # ── state ──
        self._is_fullscreen  = False
        self._total_sec      = 1500.0
        self._mode           = "Work"
        self._is_paused      = False
        self._analog_mode    = True
        self._segments       = []
        self._current_elapsed = 0.0

        # breathing
        self._breathe_colors = [_blend(self.c["text_primary"],
                                        self.c["accent_light"],
                                        i/19) for i in range(20)]
        self._breath_step  = 0
        self._breath_dir   = 1
        self._breathe_job  = None

    def destroy(self):
        if self._breathe_job:
            try: self.after_cancel(self._breathe_job)
            except Exception: pass
        super().destroy()

    # ── helpers ──────────────────────────────────────────────
    def _accent(self):
        if self._mode == "Break":      return self.c.get("success",  "#10B981")
        if self._mode == "Work":       return self.c["accent"]
        if "Break" in self._mode:      return self.c.get("success",  "#10B981")
        return self.c.get("warning", "#F59E0B")

    def _mode_icon(self):
        return {"Work":"🎯","Break":"☕","Short Break":"🌿",
                "Long Break":"🏖","Custom":"⚡"}.get(self._mode, "⏱")

    # ── Build ─────────────────────────────────────────────────
    def setup_ui(self, subject, duration_minutes, mode="Work"):
        self._total_sec = duration_minutes * 60
        self._mode      = mode
        self._subject   = subject
        acc = self._accent()

        # Root: 3 rows — top bar | scroll content | bottom buttons
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._build_top_bar(subject, acc)
        self._build_scroll_area(acc)
        self._build_bottom_bar(acc)

        # Ensure shortcuts work regardless of which child widget has focus
        self._bind_all_shortcuts()

        # start breathing loop
        self._breathe_loop()

    def _bind_all_shortcuts(self):
        def _on_key(event):
            self.controller.handle_keypress(event)
        
        def _recursive_bind(w):
            try: w.bind("<Key>", _on_key)
            except Exception: pass
            for child in w.winfo_children():
                _recursive_bind(child)
                
        _recursive_bind(self)

    # ── TOP BAR ──────────────────────────────────────────────
    def _build_top_bar(self, subject, acc):
        bar = tk.Frame(self, bg=self.c["bg_primary"], pady=8)
        bar.grid(row=0, column=0, sticky="ew", padx=16)

        # Subject chip
        chip = ctk.CTkFrame(bar, fg_color=self.c["bg_card"], corner_radius=20)
        chip.pack(side="left")
        subj_col = subject.get("color", acc)
        ctk.CTkLabel(chip,
                     text=f"  {subject.get('icon','📚')}  {subject.get('name','Focus')}  ",
                     font=FONTS["title"],
                     text_color=subj_col).pack(padx=4, pady=6)

        # Mode badge
        badge_bg = _alpha(acc, self.c["bg_card"], 0.25)
        badge = ctk.CTkFrame(bar, fg_color=badge_bg, corner_radius=14)
        badge.pack(side="left", padx=10)
        ctk.CTkLabel(badge,
                     text=f"{self._mode_icon()} {self._mode}",
                     font=FONTS["small"], text_color=acc).pack(padx=10, pady=5)

        # Right controls
        self.mute_btn = ctk.CTkButton(
            bar, text="🔊", width=38, height=34,
            fg_color="transparent", hover_color=self.c["bg_card"],
            text_color=self.c["text_secondary"], font=("Segoe UI", 15),
            command=self.controller.toggle_mute)
        self.mute_btn.pack(side="right", padx=3)

        for txt, cmd in [("⛶", self.toggle_fullscreen),
                          ("↘ Mini", self.controller.minimize_focus)]:
            ctk.CTkButton(bar, text=txt, width=54, height=34,
                          fg_color="transparent", hover_color=self.c["bg_card"],
                          text_color=self.c["text_secondary"],
                          font=("Segoe UI", 13 if txt == "⛶" else 11),
                          command=cmd).pack(side="right", padx=3)

        # Real-time clock
        self.clock_lbl = ctk.CTkLabel(
            bar, text="", font=FONTS["body"],
            text_color=self.c["text_muted"])
        self.clock_lbl.pack(side="right", padx=14)

    # ── SCROLLABLE CENTER ─────────────────────────────────────
    def _build_scroll_area(self, acc):
        """
        All the main content lives in a CTkScrollableFrame so the window
        can be any height without clipping the stopwatch or segments.
        """
        self.scroll = ctk.CTkScrollableFrame(
            self,
            fg_color=self.c["bg_primary"],
            scrollbar_button_color=self.c["border"],
            scrollbar_button_hover_color=self.c["text_muted"],
        )
        self.scroll.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        self.scroll.grid_columnconfigure(0, weight=1)

        # ── centre wrapper (horizontally centred) ──
        wrap = tk.Frame(self.scroll, bg=self.c["bg_primary"])
        wrap.grid(row=0, column=0)          # no sticky → auto-centres

        # Page dots
        dots = tk.Frame(wrap, bg=self.c["bg_primary"])
        dots.pack(pady=(14, 0))
        self._dot_a = tk.Label(dots, text="●", font=("Segoe UI", 10),
                               fg=acc, bg=self.c["bg_primary"], cursor="hand2")
        self._dot_d = tk.Label(dots, text="●", font=("Segoe UI", 10),
                               fg=self.c["text_muted"], bg=self.c["bg_primary"],
                               cursor="hand2")
        self._dot_a.pack(side="left", padx=4)
        self._dot_d.pack(side="left", padx=4)
        self._dot_a.bind("<Button-1>", lambda _: self._switch_view(True))
        self._dot_d.bind("<Button-1>", lambda _: self._switch_view(False))

        # ── CLOCK CONTAINER ──
        self.clock_container = tk.Frame(wrap, bg=self.c["bg_primary"])
        self.clock_container.pack()

        # ── ANALOG FACE ──
        self.analog_frame = tk.Frame(self.clock_container, bg=self.c["bg_primary"])
        self.analog_frame.pack(pady=(4, 0))
        self.stopwatch = AnalogStopwatch(
            self.analog_frame, self.c, size=310)
        self.stopwatch.pack()

        # ── DIGITAL FACE (hidden) ──
        self.digital_frame = tk.Frame(self.clock_container, bg=self.c["bg_primary"])
        # not packed until switched

        self.timer_label = ctk.CTkLabel(
            self.digital_frame,
            text="00:00.0",
            font=("Segoe UI", 88, "bold"),
            text_color=self.c["text_primary"]
        )
        self.timer_label.pack(pady=(36, 0))
        self.mode_sub_lbl = ctk.CTkLabel(
            self.digital_frame,
            text=f"{self._mode_icon()} {self._mode}",
            font=("Segoe UI", 16),
            text_color=acc
        )
        self.mode_sub_lbl.pack(pady=(0, 8))

        # ── PANELS CONTAINER ──
        self.panels_container = tk.Frame(wrap, bg=self.c["bg_primary"])
        self.panels_container.pack(fill="x", pady=(10, 0))

        # ── Segments log ──
        self._build_segments_panel(self.panels_container)

        # ── Sound panel ──
        sm = getattr(self.controller, "sound_manager", None)
        if sm is not None:
            self.sound_panel = SoundPanel(self.panels_container, self.c, sm)
            self.sound_panel.pack(fill="x", padx=20, pady=(4, 8),
                                  ipadx=4, ipady=6)
        else:
            self.sound_panel = None

        # ── Quote ──
        quote = ""
        if hasattr(self.controller, "quotes_engine"):
            quote = self.controller.quotes_engine.get_focus_message()
        self.quote_label = ctk.CTkLabel(
            self.panels_container, text=quote,
            font=("Segoe UI", 13, "italic"),
            text_color=self.c["text_muted"],
            wraplength=480
        )
        self.quote_label.pack(pady=(10, 6))

    # ── SEGMENTS PANEL ───────────────────────────────────────
    def _build_segments_panel(self, parent):
        outer = ctk.CTkFrame(parent, fg_color=self.c["bg_card"],
                             corner_radius=14)
        outer.pack(fill="x", padx=20, pady=(0, 20))

        hdr = tk.Frame(outer, bg=self.c["bg_card"])
        hdr.pack(fill="x", padx=12, pady=(8, 2))
        tk.Label(hdr, text="SEGMENTS", bg=self.c["bg_card"],
                 fg=self.c["text_muted"],
                 font=("Segoe UI", 9, "bold")).pack(side="left")
        self.seg_count_lbl = tk.Label(hdr, text="0",
                                      bg=self.c["bg_card"],
                                      fg=self.c["accent"],
                                      font=("Segoe UI", 9, "bold"))
        self.seg_count_lbl.pack(side="right")

        self.seg_scroll = ctk.CTkScrollableFrame(
            outer, fg_color="transparent", height=85)
        self.seg_scroll.pack(fill="both", expand=True, padx=4, pady=(0, 6))

        self.seg_placeholder = ctk.CTkLabel(
            self.seg_scroll,
            text="Press S or tap '+ Seg' to mark a segment.",
            font=FONTS["small"], text_color=self.c["text_muted"])
        self.seg_placeholder.pack(pady=18)

    # ── BOTTOM BAR ───────────────────────────────────────────
    def _build_bottom_bar(self, acc):
        bar = tk.Frame(self, bg=self.c["bg_primary"])
        bar.grid(row=2, column=0, pady=20)

        sz = 76

        end_bg    = _alpha(self.c["text_muted"], self.c["bg_card"], 0.3)
        end_hover = _alpha(self.c["danger"],     self.c["bg_card"], 0.5)
        self.end_btn = RingButton(bar, "End", sz,
                                  end_bg, self.c["text_primary"], end_hover,
                                  command=self.controller.exit_focus)
        self.end_btn.pack(side="left", padx=20)

        seg_bg = _alpha(self.c["text_muted"], self.c["bg_card"], 0.2)
        self.seg_btn = RingButton(bar, "+ Seg", 56,
                                  seg_bg, self.c["text_muted"],
                                  _alpha(acc, self.c["bg_card"], 0.4),
                                  command=self._add_segment)
        self.seg_btn.pack(side="left", padx=6)

        self.pause_btn = RingButton(bar, "Pause", sz,
                                    acc, "#FFFFFF",
                                    _alpha(acc, self.c["bg_card"], 0.7),
                                    command=self.controller.pause_resume)
        self.pause_btn.pack(side="left", padx=20)

        tk.Label(bar,
                 text="Space=Pause  Esc=End  A=View  S=Segment",
                 bg=self.c["bg_primary"], fg=self.c["text_muted"],
                 font=("Segoe UI", 9)).pack(side="bottom", pady=2)

    # ── View toggle ───────────────────────────────────────────
    def _switch_view(self, analog: bool):
        self._analog_mode = analog
        acc = self._accent()
        if analog:
            self.digital_frame.pack_forget()
            self.analog_frame.pack(pady=(4, 0))
            self._dot_a.configure(fg=acc)
            self._dot_d.configure(fg=self.c["text_muted"])
        else:
            self.analog_frame.pack_forget()
            self.digital_frame.pack(pady=(4, 0))
            self._dot_a.configure(fg=self.c["text_muted"])
            self._dot_d.configure(fg=acc)

    # ── Segment log ───────────────────────────────────────────
    def _add_segment(self):
        elapsed = self._current_elapsed
        delta   = elapsed - (self._segments[-1][0] if self._segments else 0)
        self._segments.append((elapsed, delta))
        self._refresh_segments()

    def _refresh_segments(self):
        if not self._segments:
            return
        self.seg_placeholder.pack_forget()
        self.seg_count_lbl.configure(text=str(len(self._segments)))

        deltas  = [s[1] for s in self._segments]
        best_i  = deltas.index(min(deltas)) if len(deltas) > 1 else -1
        worst_i = deltas.index(max(deltas)) if len(deltas) > 1 else -1

        for w in self.seg_scroll.winfo_children():
            if isinstance(w, SegmentRow):
                w.destroy()

        recent = self._segments[-6:]
        offset = max(0, len(self._segments) - 6)
        for i, (el, dl) in enumerate(recent):
            ri = offset + i
            SegmentRow(
                self.seg_scroll, ri+1,
                f"{int(el)//60:02d}:{int(el)%60:02d}",
                f"+{int(dl)//60:02d}:{int(dl)%60:02d}",
                self.c,
                best=(ri == best_i),
                worst=(ri == worst_i)
            ).pack(fill="x")

    # ── Public API ────────────────────────────────────────────
    def show_fullscreen(self):
        self.attributes("-fullscreen", True)
        self._is_fullscreen = True
        self.focus_force()

    def toggle_fullscreen(self):
        self._is_fullscreen = not self._is_fullscreen
        self.attributes("-fullscreen", self._is_fullscreen)

    def update_timer_display(self, remaining_sec):
        elapsed = self._total_sec - remaining_sec
        self._current_elapsed = elapsed

        if self._analog_mode and hasattr(self, "stopwatch"):
            self.stopwatch.set_elapsed(elapsed, self._total_sec, self._is_paused)
        elif not self._analog_mode and hasattr(self, "timer_label"):
            m = int(remaining_sec) // 60
            s = int(remaining_sec) % 60
            t = int((remaining_sec % 1) * 10)
            self.timer_label.configure(text=f"{m:02d}:{s:02d}.{t}")

    def set_paused_state(self, is_paused):
        self._is_paused = is_paused
        acc = self._accent()
        if is_paused:
            self.pause_btn.configure_text("Resume",
                                          bg_color=self.c.get("success", "#10B981"))
        else:
            self.pause_btn.configure_text("Pause", bg_color=acc)

    def set_mute_state(self, is_muted):
        self.mute_btn.configure(text="🔇" if is_muted else "🔊")
        if self.sound_panel:
            self.sound_panel.sync_mute_icon(is_muted)

    # ── Breathing animation ───────────────────────────────────
    def _breathe_loop(self):
        if not self.winfo_exists():
            return
        # clock
        if hasattr(self, "clock_lbl"):
            self.clock_lbl.configure(text=datetime.now().strftime("%I:%M %p"))
        # digital colour breathing
        if not self._is_paused and not self._analog_mode:
            self._breath_step += self._breath_dir
            if self._breath_step >= len(self._breathe_colors) - 1:
                self._breath_dir = -1
            elif self._breath_step <= 0:
                self._breath_dir = 1
            if hasattr(self, "timer_label"):
                self.timer_label.configure(
                    text_color=self._breathe_colors[self._breath_step])
        self._breathe_job = self.after(150, self._breathe_loop)
