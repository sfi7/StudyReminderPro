# ============================================================
# Study Reminder Pro - Skills & Courses View
# File: ui/skills.py
# ============================================================

import tkinter as tk
import customtkinter as ctk
from datetime import datetime, date
from core.theme import FONTS
from database.skills_db import default_skill

class SkillsView(ctk.CTkFrame):
    def __init__(self, master, db, colors, toast_fn, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.db = db
        self.colors = colors
        self.toast = toast_fn
        self._widgets = []
        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", self._on_search)

        self._build_skeleton()
        self.refresh()

    def _build_skeleton(self):
        c = self.colors
        
        # Search and Action Top bar
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill="x", padx=24, pady=(16, 8))
        
        # Search Entry
        search_frame = ctk.CTkFrame(top_bar, fg_color=c["bg_card"],
                                    border_width=1, border_color=c["border"],
                                    corner_radius=10, width=280, height=38)
        search_frame.pack(side="left", fill="y")
        search_frame.pack_propagate(False)
        
        ctk.CTkLabel(search_frame, text="🔍", font=("Segoe UI", 12)).pack(side="left", padx=10)
        self._search_entry = ctk.CTkEntry(
            search_frame, placeholder_text="Search courses or skills...",
            textvariable=self._search_var, font=FONTS["body"],
            fg_color="transparent", border_width=0,
            text_color=c["text_primary"], placeholder_text_color=c["text_muted"]
        )
        self._search_entry.pack(side="left", fill="both", expand=True)
        
        # Add Skill Button
        ctk.CTkButton(
            top_bar, text="➕ Add Skill / Course", font=FONTS["body"],
            fg_color="#10B981", hover_color="#0D9488", text_color="#FFFFFF",
            corner_radius=10, height=38,
            command=self._open_add_dialog
        ).pack(side="right")

        # Scrollable container for listings
        self._scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self._scroll.pack(fill="both", expand=True, padx=24, pady=8)

    def apply_navigation_params(self, **kwargs):
        pass

    def refresh(self):
        """Re-render all elements dynamically if data version changed."""
        current_data_ver = self.db.data_version
        current_settings_ver = self.db.settings_version
        if (getattr(self, "_last_data_version", -1) == current_data_ver and 
            getattr(self, "_last_settings_version", -1) == current_settings_ver):
            return
            
        self._last_data_version = current_data_ver
        self._last_settings_version = current_settings_ver
        
        self._render_skills(self._search_var.get())

    def _on_search(self, *_):
        self._render_skills(self._search_var.get())

    def _render_skills(self, filter_text=""):
        # Destroy all old widgets in scroll
        for widget in self._scroll.winfo_children():
            widget.destroy()

        c = self.colors
        skills = self.db.skills
        
        if filter_text:
            skills = [s for s in skills if filter_text.lower() in s["name"].lower()]

        if not skills:
            # Empty state
            lbl = ctk.CTkLabel(
                self._scroll, text="No skills or courses tracked yet.\nClick '+ Add Skill / Course' above to start!",
                font=FONTS["body"], text_color=c["text_muted"]
            )
            lbl.pack(pady=60)
            return

        active_skills = []
        completed_skills = []
        for s in skills:
            pct = self.db.progress_pct_skill(s)
            if pct >= 100:
                completed_skills.append(s)
            else:
                active_skills.append(s)

        # Active Skills Section
        if active_skills:
            for s in active_skills:
                self._render_skill_card(self._scroll, s)

        # Completed/Archived Skills Section
        if completed_skills:
            divider = ctk.CTkFrame(self._scroll, height=1, fg_color=c["border"])
            divider.pack(fill="x", pady=20)
            
            archive_title = ctk.CTkLabel(
                self._scroll, text="🎉 Completed & Archived Courses",
                font=FONTS["subheading"], text_color="#10B981"
            )
            archive_title.pack(anchor="w", pady=(0, 10))
            
            for s in completed_skills:
                self._render_skill_card(self._scroll, s, completed=True)

    def _render_skill_card(self, parent, s, completed=False):
        c = self.colors
        pct = self.db.progress_pct_skill(s)
        diff_colors = {"Easy": "#10B981", "Medium": "#F59E0B", "Hard": "#EF4444"}
        diff_color = diff_colors.get(s.get("difficulty", "Medium"), "#F59E0B")

        card = ctk.CTkFrame(parent, fg_color=c["bg_card"],
                            border_width=1, border_color=c["border"],
                            corner_radius=16)
        card.pack(fill="x", pady=8)

        # Header Row
        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.pack(fill="x", padx=16, pady=(16, 8))

        # Title and Dot
        title_frame = ctk.CTkFrame(hdr, fg_color="transparent")
        title_frame.pack(side="left")
        
        dot = ctk.CTkLabel(title_frame, text="●", font=("Segoe UI", 16), text_color=diff_color)
        dot.pack(side="left")
        
        title = ctk.CTkLabel(title_frame, text=s["name"], font=FONTS["subheading"], text_color=c["text_primary"])
        title.pack(side="left", padx=8)

        # Progress bar
        bar_frame = ctk.CTkFrame(card, fg_color="transparent")
        bar_frame.pack(fill="x", padx=16, pady=8)

        bar = ctk.CTkProgressBar(bar_frame, height=8, fg_color=c["bg_secondary"], progress_color=s.get("color", "#10B981"))
        bar.pack(side="left", fill="x", expand=True)
        bar.set(pct / 100.0)

        pct_lbl = ctk.CTkLabel(bar_frame, text=f"{pct}%", font=FONTS["small"], text_color=c["text_primary"], width=45)
        pct_lbl.pack(side="left", padx=(10, 0))

        # Info Row
        info = ctk.CTkFrame(card, fg_color="transparent")
        info.pack(fill="x", padx=16, pady=(8, 16))

        # Target date / Modules info
        modules_text = f"📚 {s['completed_modules']} / {s['total_modules']} modules"
        modules_lbl = ctk.CTkLabel(info, text=modules_text, font=FONTS["small"], text_color=c["text_muted"])
        modules_lbl.pack(side="left")

        if s.get("target_date"):
            target_text = f"🎯 Target: {s['target_date']}"
            ctk.CTkLabel(info, text=target_text, font=FONTS["small"], text_color=c["text_muted"]).pack(side="left", padx=20)

        # Action Buttons
        btn_frame = ctk.CTkFrame(info, fg_color="transparent")
        btn_frame.pack(side="right")

        if not completed:
            # +1 Module Button
            ctk.CTkButton(
                btn_frame, text="✚ Module", width=80, height=28, font=FONTS["tiny"],
                fg_color=c["bg_secondary"], hover_color="#10B981", text_color=c["text_primary"],
                corner_radius=8, command=lambda: self._add_module(s)
            ).pack(side="left", padx=4)

            # Focus Button
            ctk.CTkButton(
                btn_frame, text="🔥 Focus", width=70, height=28, font=FONTS["tiny"],
                fg_color=c["bg_secondary"], hover_color="#6C63FF", text_color=c["accent"],
                corner_radius=8, command=lambda: self._start_focus(s)
            ).pack(side="left", padx=4)

        # Edit Button
        ctk.CTkButton(
            btn_frame, text="✏️", width=32, height=28, font=FONTS["tiny"],
            fg_color=c["bg_secondary"], hover_color=c["border"], text_color=c["text_primary"],
            corner_radius=8, command=lambda: self._open_edit_dialog(s)
        ).pack(side="left", padx=4)

        # Delete Button
        ctk.CTkButton(
            btn_frame, text="🗑️", width=32, height=28, font=FONTS["tiny"],
            fg_color=c["bg_secondary"], hover_color=c["danger"], text_color=c["text_secondary"],
            corner_radius=8, command=lambda: self._confirm_delete(s)
        ).pack(side="left", padx=4)

    def _add_module(self, s):
        new_val = min(s["total_modules"], s["completed_modules"] + 1)
        self.db.update_skill(s["id"], completed_modules=new_val)
        if new_val == s["total_modules"]:
            self.toast(f"🎉 Course '{s['name']}' completed!", "success")
        else:
            self.toast(f"✅ Logged 1 module for '{s['name']}'", "success")
        self.refresh()

    def _start_focus(self, s):
        app = self.winfo_toplevel()
        if hasattr(app, 'navigate'):
            app.navigate("pomodoro", subject_id=s["id"])

    def _open_add_dialog(self):
        SkillDialog(self, self.db, self.colors, on_save=self._on_save_new)

    def _open_edit_dialog(self, s):
        SkillDialog(self, self.db, self.colors, skill=s,
                    on_save=lambda d: self._on_save_edit(s["id"], d))

    def _on_save_new(self, data):
        self.db.add_skill(data)
        self.toast(f"🌱 Course/Skill '{data['name']}' added!", "success")
        self.refresh()

    def _on_save_edit(self, sid, data):
        self.db.update_skill(sid, **data)
        self.toast("✏️ Course/Skill updated!", "success")
        self.refresh()

    def _confirm_delete(self, s):
        dlg = tk.Toplevel(self)
        dlg.title("Confirm Delete")
        dlg.geometry("380x160")
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.attributes("-topmost", True)
        c = self.colors
        dlg.configure(bg=c["bg_primary"])

        ctk.CTkLabel(dlg, text=f"Delete '{s['name']}'?",
                     font=FONTS["subheading"], text_color=c["text_primary"]).pack(pady=(24, 6))
        ctk.CTkLabel(dlg, text="This action cannot be undone.",
                     font=FONTS["small"], text_color=c["text_muted"]).pack()

        btn_row = ctk.CTkFrame(dlg, fg_color="transparent")
        btn_row.pack(pady=16)
        ctk.CTkButton(btn_row, text="Cancel", width=100,
                       fg_color=c["bg_secondary"], hover_color=c["border"],
                       text_color=c["text_secondary"],
                       command=dlg.destroy).pack(side="left", padx=8)
        ctk.CTkButton(btn_row, text="🗑️ Delete", width=100,
                       fg_color=c["danger"], hover_color="#C0392B",
                       command=lambda: (self.db.delete_skill(s["id"]),
                                        self.toast(f"🗑️  {s['name']} deleted.", "error"),
                                        dlg.destroy(), self.refresh())).pack(side="left", padx=8)


# ── Skill Add/Edit Dialog ─────────────────────────────────────
class SkillDialog(tk.Toplevel):
    def __init__(self, master, db, colors, skill=None, on_save=None, **kwargs):
        super().__init__(master, **kwargs)
        self.db = db
        self.colors = colors
        self.skill = skill
        self.on_save = on_save
        self.title("Edit Skill / Course" if skill else "Add Skill / Course")
        self.geometry("480x560")
        self.resizable(False, False)
        self.grab_set()
        self.attributes("-topmost", True)
        self.configure(bg=colors["bg_primary"])
        self._build()

    def _build(self):
        c = self.colors
        s = self.skill or {}

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkLabel(scroll, text="✏️ Edit Course / Skill" if s else "➕ New Course / Skill",
                     font=FONTS["subheading"], text_color=c["text_primary"]).pack(pady=(10, 18))

        # ── Name ──
        self._add_label(scroll, "Course / Skill Name")
        self._name = ctk.CTkEntry(scroll, font=FONTS["body"],
                                  fg_color=c["bg_card"], border_color=c["border"],
                                  text_color=c["text_primary"], corner_radius=10)
        self._name.pack(fill="x", pady=(0, 12))
        if s.get("name"):
            self._name.insert(0, s["name"])

        # ── Total Modules ──
        self._add_label(scroll, "Total Modules / Lessons")
        self._total = ctk.CTkEntry(scroll, font=FONTS["body"],
                                   fg_color=c["bg_card"], border_color=c["border"],
                                   text_color=c["text_primary"], corner_radius=10)
        self._total.pack(fill="x", pady=(0, 12))
        self._total.insert(0, str(s.get("total_modules", 10)))

        # ── Completed Modules ──
        self._add_label(scroll, "Completed Modules / Lessons")
        self._completed = ctk.CTkEntry(scroll, font=FONTS["body"],
                                       fg_color=c["bg_card"], border_color=c["border"],
                                       text_color=c["text_primary"], corner_radius=10)
        self._completed.pack(fill="x", pady=(0, 12))
        self._completed.insert(0, str(s.get("completed_modules", 0)))

        # ── Target Date ──
        self._add_label(scroll, "Target Completion Date (YYYY-MM-DD) - Optional")
        self._target = ctk.CTkEntry(scroll, font=FONTS["body"],
                                    fg_color=c["bg_card"], border_color=c["border"],
                                    text_color=c["text_primary"], corner_radius=10,
                                    placeholder_text="YYYY-MM-DD")
        self._target.pack(fill="x", pady=(0, 12))
        if s.get("target_date"):
            self._target.insert(0, s["target_date"])

        # ── Difficulty ──
        self._add_label(scroll, "Difficulty Level")
        self._diff_var = tk.StringVar(value=s.get("difficulty", "Medium"))
        self._diff_menu = ctk.CTkOptionMenu(
            scroll, values=["Easy", "Medium", "Hard"], variable=self._diff_var,
            font=FONTS["body"], fg_color=c["bg_card"], button_color=c["accent"],
            button_hover_color=c["accent_hover"], text_color=c["text_primary"]
        )
        self._diff_menu.pack(fill="x", pady=(0, 24))

        # ── Save Button ──
        ctk.CTkButton(
            scroll, text="💾 Save Skill / Course", font=FONTS["body"],
            fg_color="#10B981", hover_color="#0D9488", text_color="#FFFFFF",
            corner_radius=10, height=44, command=self._save
        ).pack(fill="x", pady=10)

    def _add_label(self, parent, text):
        lbl = ctk.CTkLabel(parent, text=text, font=FONTS["small"], text_color=self.colors["text_muted"])
        lbl.pack(anchor="w", pady=(8, 2))

    def _save(self):
        name = self._name.get().strip()
        if not name:
            self._name.configure(border_color="#EF4444")
            return

        try:
            total = int(self._total.get().strip())
            completed = int(self._completed.get().strip())
        except ValueError:
            self._total.configure(border_color="#EF4444")
            return

        target_date = self._target.get().strip() or None
        if target_date:
            try:
                datetime.strptime(target_date, "%Y-%m-%d")
            except ValueError:
                self._target.configure(border_color="#EF4444")
                return

        data = {
            "name": name,
            "total_modules": total,
            "completed_modules": completed,
            "target_date": target_date,
            "difficulty": self._diff_var.get(),
            "color": "#10B981"
        }

        if self.on_save:
            self.on_save(data)
        self.destroy()
