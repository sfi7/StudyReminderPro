# ============================================================
# Study Reminder Pro - Desktop Mini Panel (Widget)
# File: ui/mini_panel.py
# ============================================================

import tkinter as tk
import customtkinter as ctk
from themes.typography import FONTS

class MiniPanel(tk.Toplevel):
    """
    A minimalist always-on-top desktop widget for quick tracking.
    Features: Pomodoro timer, next task, and quick actions.
    """
    def __init__(self, parent, db, colors, on_show_main, focus_ctrl=None):
        super().__init__(parent)
        self.db = db
        self.colors = colors
        self.on_show_main = on_show_main
        self.focus_ctrl = focus_ctrl
        
        # Window Setup
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.95)
        
        # Sizing
        self.width = 240
        self.height = 130
        screen_w = self.winfo_screenwidth()
        self.geometry(f"{self.width}x{self.height}+{screen_w - self.width - 40}+40")
        
        # Styling
        self.configure(bg=colors["bg_card"])
        self._frame = ctk.CTkFrame(self, fg_color=colors["bg_card"], 
                                   border_width=1, border_color=colors["border"],
                                   corner_radius=15)
        self._frame.pack(fill="both", expand=True)
        
        # Draggable Logic
        self._frame.bind("<Button-1>", self._start_drag)
        self._frame.bind("<B1-Motion>", self._do_drag)
        
        self._build_ui()
        self._update_loop()

    def _build_ui(self):
        c = self.colors
        
        # Top Bar (Close/Drag handle)
        top_bar = ctk.CTkFrame(self._frame, fg_color="transparent")
        top_bar.pack(fill="x", padx=10, pady=(5, 0))
        
        close_btn = ctk.CTkLabel(top_bar, text="✖", font=("Segoe UI", 11, "bold"), text_color=c["text_muted"], cursor="hand2")
        close_btn.pack(side="right")
        close_btn.bind("<Button-1>", lambda e: self.withdraw())

        # Drag handle
        drag_handle = ctk.CTkFrame(top_bar, fg_color=c["border"], height=4, width=40, corner_radius=2)
        drag_handle.pack(pady=4)
        drag_handle.bind("<Button-1>", self._start_drag)
        drag_handle.bind("<B1-Motion>", self._do_drag)

        # Timer Display
        self.timer_lbl = ctk.CTkLabel(self._frame, text="25:00", 
                                      font=("Segoe UI", 32, "bold"),
                                      text_color=c["accent"])
        self.timer_lbl.pack(pady=(0, 0))
        self.timer_lbl.bind("<Button-1>", self._start_drag)
        self.timer_lbl.bind("<B1-Motion>", self._do_drag)
        
        self.status_lbl = ctk.CTkLabel(self._frame, text="READY TO FOCUS", 
                                       font=("Segoe UI", 10, "bold"),
                                       text_color=c["text_secondary"])
        self.status_lbl.pack()
        
        # Action Buttons
        btn_row = ctk.CTkFrame(self._frame, fg_color="transparent")
        btn_row.pack(pady=10)
        
        self.start_btn = ctk.CTkButton(btn_row, text="▶ START", width=90, height=34, corner_radius=17,
                                       font=("Segoe UI", 11, "bold"),
                                       fg_color=c["accent"], hover_color=c["accent_hover"],
                                       command=self._toggle_timer)
        self.start_btn.pack(side="left", padx=5)
        
        ctk.CTkButton(btn_row, text="🏠", width=34, height=34, corner_radius=17,
                      fg_color=c["bg_secondary"], text_color=c["text_primary"],
                      command=self.on_show_main).pack(side="left", padx=5)

    def _update_loop(self):
        """Poll FocusController state if available."""
        if self.focus_ctrl:
            try:
                state = self.focus_ctrl.get_state()
                if state and state.get("is_running"):
                    self.timer_lbl.configure(text=state.get("time_left", "25:00"))
                    mode = state.get("mode", "FOCUS").upper()
                    self.status_lbl.configure(text=mode, text_color=self.colors["accent"])
                    
                    if state.get("is_paused"):
                        self.start_btn.configure(text="▶ RESUME")
                    else:
                        self.start_btn.configure(text="⏸ PAUSE")
                else:
                    self.timer_lbl.configure(text="25:00")
                    self.status_lbl.configure(text="READY TO FOCUS", text_color=self.colors["text_secondary"])
                    self.start_btn.configure(text="▶ START")
            except Exception:
                pass
        self.after(1000, self._update_loop)

    def _toggle_timer(self):
        if self.focus_ctrl:
            self.focus_ctrl.toggle_session()

    def _start_drag(self, event):
        self.x = event.x
        self.y = event.y

    def _do_drag(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")
