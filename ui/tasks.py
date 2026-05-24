# ============================================================
# Study Reminder Pro - Tasks View
# File: ui/tasks.py
# ============================================================

import tkinter as tk
import customtkinter as ctk
from datetime import datetime
from core.theme import FONTS
from utils.logger import log
from analytics.task_intelligence import TaskIntelligence

class TasksView(ctk.CTkFrame):
    """Modern Task Management System UI."""

    def __init__(self, master, db, colors, toast_fn, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.db = db
        self.colors = colors
        self.toast = toast_fn
        self.task_intelligence = TaskIntelligence(self.db)
        
        self.current_filter = "Pending" # All, Pending, Completed
        self._build()

    def _build(self):
        for w in self.winfo_children():
            w.destroy()
            
        c = self.colors

        # ── Header Bar ──────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(20, 10))

        ctk.CTkLabel(header, text="📝 My Tasks",
                     font=FONTS["heading"], text_color=c["text_primary"]).pack(side="left")

        # Add Task Button
        add_btn = ctk.CTkButton(header, text="+ Add Task", font=FONTS["button"],
                                fg_color=c["accent"], hover_color=c["accent_hover"],
                                text_color="#FFFFFF", corner_radius=8,
                                command=self._open_add_task_dialog)
        add_btn.pack(side="right")

        # ── Filter Bar ──────────────────────────────────────────
        filters_frame = ctk.CTkFrame(self, fg_color="transparent")
        filters_frame.pack(fill="x", padx=24, pady=(0, 16))

        for f in ["All", "Pending", "Completed"]:
            btn_color = c["accent"] if self.current_filter == f else c["bg_card"]
            text_color = "#FFFFFF" if self.current_filter == f else c["text_secondary"]
            btn = ctk.CTkButton(filters_frame, text=f, width=80, height=28, corner_radius=14,
                                fg_color=btn_color, hover_color=c["border"],
                                text_color=text_color, font=FONTS["small"],
                                command=lambda x=f: self.set_filter(x))
            btn.pack(side="left", padx=(0, 10))

        # ── Task List ───────────────────────────────────────────
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=24, pady=0)
        
        # Internal container for tasks
        self._list_container = ctk.CTkFrame(self.scroll, fg_color="transparent")
        self._list_container.pack(fill="both", expand=True)

        # Show loading state
        self.loading_label = ctk.CTkLabel(self._list_container, text="Analyzing and sorting tasks...", font=FONTS["body"], text_color=c["text_muted"])
        self.loading_label.pack(pady=40)
        
        # Async fetch
        self.task_intelligence.get_sorted_tasks_async(self.current_filter, self._on_tasks_loaded)

    def _on_tasks_loaded(self, tasks):
        """Callback from background sorting thread."""
        # Ensure UI updates happen on main thread
        self.after(0, lambda: self._render_tasks(tasks))

    def _render_tasks(self, tasks):
        if hasattr(self, "_list_container"):
            for w in self._list_container.winfo_children():
                w.destroy()
            
            c = self.colors
            if not tasks:
                empty = ctk.CTkFrame(self._list_container, fg_color=c["bg_card"], corner_radius=16, 
                                      border_width=1, border_color=c["border"])
                empty.pack(fill="x", pady=8)
                ctk.CTkLabel(empty, text="☕", font=("Segoe UI", 48)).pack(pady=(40, 10))
                ctk.CTkLabel(empty, text="No tasks found. Time to relax!",
                             font=FONTS["body"], text_color=c["text_secondary"]).pack(pady=(0, 40))
                return
            
            for task in tasks:
                self._create_task_card(task)

    def set_filter(self, filter_name):
        self.current_filter = filter_name
        self._build()

    def _create_task_card(self, task):
        c = self.colors
        parent = self._list_container
        is_completed = task.get("completed", False)
        urgency = task.get("_urgency_score", 0)
        is_pinned = task.get("is_pinned", False)
        
        # Determine border color based on urgency
        border_color = c["border"]
        if not is_completed:
            if urgency >= 90:
                border_color = c["danger"]
            elif urgency >= 60:
                border_color = c["warning"]
                
        card = ctk.CTkFrame(self.scroll, fg_color=c["bg_card"], corner_radius=16,
                            border_width=1, border_color=border_color)
        card.pack(fill="x", pady=8)

        # Pulse effect for critical tasks
        if urgency >= 90 and not is_completed:
            self._apply_pulse_effect(card, c["danger"], c["bg_card"])

        # Checkbox
        chk_var = tk.BooleanVar(value=is_completed)
        chk = ctk.CTkCheckBox(card, text="", variable=chk_var, width=24,
                              fg_color=c["success"], hover_color=c["success"],
                              command=lambda t=task["id"]: self._toggle_task(t))
        chk.pack(side="left", padx=(16, 8), pady=16)

        # Content
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(side="left", fill="both", expand=True, pady=12)

        title_color = c["text_muted"] if is_completed else c["text_primary"]
        font_style = ("Segoe UI", 14, "overstrike") if is_completed else FONTS["title"]
        
        title_text = task["title"]
        if is_pinned:
            title_text = f"📌 {title_text}"
            
        ctk.CTkLabel(content, text=title_text, font=font_style,
                     text_color=title_color, anchor="w").pack(fill="x")

        # Meta info
        meta_frame = ctk.CTkFrame(content, fg_color="transparent")
        meta_frame.pack(fill="x", pady=(4, 0))

        # Priority Tag
        pri_colors = {
            "Low": c.get("info", "#3A86FF"),
            "Medium": c.get("warning", "#FFBE0B"),
            "High": c.get("danger", "#FF006E"),
            "Critical": "#8338EC"
        }
        pri = task.get("priority", "Medium")
        pri_color = pri_colors.get(pri, c["text_secondary"])
        
        ctk.CTkLabel(meta_frame, text=f"■ {pri}", font=FONTS["tiny"],
                     text_color=pri_color).pack(side="left", padx=(0, 12))
                     
        if task.get("recurrence"):
            ctk.CTkLabel(meta_frame, text=f"↻ {task['recurrence']}", font=FONTS["tiny"],
                         text_color=c["info"]).pack(side="left", padx=(0, 12))

        # Delete Button
        del_btn = ctk.CTkButton(card, text="🗑", width=32, height=32, corner_radius=8,
                                fg_color="transparent", hover_color=c["danger"],
                                text_color=c["text_secondary"], font=("Segoe UI", 16),
                                command=lambda t=task["id"]: self._delete_task(t))
        del_btn.pack(side="right", padx=16)

    def _apply_pulse_effect(self, widget, color1, color2, step=0):
        """Creates a subtle pulsing border effect for critical tasks."""
        if not widget.winfo_exists(): return
        current_color = color1 if step % 2 == 0 else color2
        widget.configure(border_color=current_color)
        self.after(800, lambda: self._apply_pulse_effect(widget, color1, color2, step + 1))

    def _toggle_task(self, task_id):
        completed = self.db.toggle_task(task_id)
        status = "completed" if completed else "reopened"
        self.toast(f"Task {status}!", "success" if completed else "info")
        self._build()

    def _delete_task(self, task_id):
        self.db.delete_task(task_id)
        self.toast("Task deleted", "info")
        self._build()

    def _open_add_task_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("New Task")
        dialog.geometry("400x300")
        dialog.attributes("-topmost", True)
        dialog.configure(bg=self.colors["bg_primary"])
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Task Title", font=FONTS["body"],
                     text_color=self.colors["text_primary"]).pack(pady=(20, 4), padx=20, anchor="w")
        
        title_entry = ctk.CTkEntry(dialog, width=360, fg_color=self.colors["bg_card"],
                                   border_color=self.colors["border"])
        title_entry.pack(padx=20)

        ctk.CTkLabel(dialog, text="Priority", font=FONTS["body"],
                     text_color=self.colors["text_primary"]).pack(pady=(16, 4), padx=20, anchor="w")
        
        pri_combo = ctk.CTkComboBox(dialog, values=["Low", "Medium", "High", "Critical"],
                                    width=360, fg_color=self.colors["bg_card"],
                                    border_color=self.colors["border"])
        pri_combo.set("Medium")
        pri_combo.pack(padx=20)
        
        # Options Frame (Pin & Recurrence)
        opt_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        opt_frame.pack(fill="x", padx=20, pady=(16, 4))
        
        pin_var = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(opt_frame, text="📌 Pin Task", variable=pin_var, font=FONTS["small"]).pack(side="left")
        
        rec_combo = ctk.CTkComboBox(opt_frame, values=["None", "Daily", "Weekly"], width=120, fg_color=self.colors["bg_card"])
        rec_combo.set("None")
        rec_combo.pack(side="right")
        ctk.CTkLabel(opt_frame, text="Recurrence:", font=FONTS["small"]).pack(side="right", padx=(0, 8))

        def save():
            t = title_entry.get().strip()
            if not t:
                return
            rec = rec_combo.get()
            if rec == "None": rec = None
            self.db.add_task(t, priority=pri_combo.get(), is_pinned=pin_var.get(), recurrence=rec)
            self.toast("Task added!", "success")
            dialog.destroy()
            self._build()

        ctk.CTkButton(dialog, text="Save Task", fg_color=self.colors["accent"],
                      hover_color=self.colors["accent_hover"],
                      command=save).pack(pady=24)

    def refresh(self):
        current_data_ver = self.db.data_version
        current_settings_ver = self.db.settings_version
        if (getattr(self, "_last_data_version", -1) == current_data_ver and 
            getattr(self, "_last_settings_version", -1) == current_settings_ver):
            return
            
        self._last_data_version = current_data_ver
        self._last_settings_version = current_settings_ver

        self._build()
