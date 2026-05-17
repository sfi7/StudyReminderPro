# ============================================================
# Study Reminder Pro - Subjects Management View
# File: ui/subjects.py
# ============================================================

import tkinter as tk
import customtkinter as ctk
from datetime import date, datetime
from core.theme import FONTS, SUBJECT_ICONS, SUBJECT_COLORS
from core.database import default_subject
from ui.widgets import (AnimatedProgressBar, LinearProgressBar, 
                        ExamCountdownBadge, GlassCard, LiveCountdown)


class SubjectsView(ctk.CTkScrollableFrame):
    """Full subject management — list, add, edit, delete."""

    def __init__(self, master, db, colors, toast_fn, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.db = db
        self.colors = colors
        self.toast = toast_fn
        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", self._on_search)
        
        self._widgets = []
        self._build()

    # ── Build ────────────────────────────────────────────────
    def _build(self):
        c = self.colors
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(20, 10))
        self._widgets.append(header)

        ctk.CTkLabel(header, text="📚 My Subjects",
                     font=FONTS["heading"], text_color=c["text_primary"]).pack(side="left")

        add_btn = ctk.CTkButton(header, text="＋ Add Subject",
                                font=FONTS["button"], corner_radius=12,
                                height=40,
                                fg_color=c["accent"], hover_color=c["accent_hover"],
                                command=self._open_add_dialog)
        add_btn.pack(side="right")

        # Search bar
        search_frame = ctk.CTkFrame(self, fg_color=c["bg_card"], corner_radius=14,
                                    border_width=1, border_color=c["border"])
        search_frame.pack(fill="x", padx=24, pady=(0, 16))
        self._widgets.append(search_frame)
        
        ctk.CTkLabel(search_frame, text="🔍", font=("Segoe UI", 16)).pack(side="left", padx=(16, 8))
        ctk.CTkEntry(search_frame, textvariable=self._search_var,
                     placeholder_text="Search subjects...",
                     font=FONTS["body"], fg_color="transparent",
                     border_width=0, text_color=c["text_primary"]).pack(
            fill="x", expand=True, padx=4, pady=10)

        # Subject list container
        self._list_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._list_frame.pack(fill="both", expand=True, padx=24, pady=(0, 24))
        self._widgets.append(self._list_frame)

        self._render_subjects()

    def refresh(self):
        """Safely refresh the list."""
        for w in self._widgets:
            try:
                w.destroy()
            except Exception:
                pass
        self._widgets.clear()
        self._build()

    def _render_subjects(self, query=""):
        subjects = self.db.subjects
        if query:
            subjects = [s for s in subjects if query.lower() in s["name"].lower()]

        if not subjects:
            empty = ctk.CTkFrame(self._list_frame, fg_color=self.colors["bg_card"],
                                 corner_radius=16, border_width=1, border_color=self.colors["border"])
            empty.pack(fill="x", pady=8)
            ctk.CTkLabel(empty, text="☕", font=("Segoe UI", 48)).pack(pady=(40, 10))
            ctk.CTkLabel(empty,
                         text="No subjects found. Click '＋ Add Subject' to get started!",
                         font=FONTS["body"],
                         text_color=self.colors["text_secondary"]).pack(pady=(0, 40))
            return

        active_subjects = []
        archived_subjects = []
        for s in subjects:
            days = self.db.days_until_exam(s)
            if days is not None and days < 0:
                archived_subjects.append(s)
            else:
                active_subjects.append(s)

        for subj in active_subjects:
            self._subject_card(self._list_frame, subj, is_archived=False)

        if archived_subjects:
            # Create a collapsible archive frame
            archive_btn = ctk.CTkButton(self._list_frame, text="▶ Archived Subjects", font=FONTS["subheading"], 
                                        fg_color="transparent", text_color=self.colors["text_secondary"], 
                                        hover_color=self.colors["bg_secondary"], anchor="w",
                                        command=lambda: self._toggle_archive())
            archive_btn.pack(fill="x", pady=(20, 5))
            self._archive_btn = archive_btn
            
            self._archive_container = ctk.CTkFrame(self._list_frame, fg_color="transparent")
            self._archive_container.pack(fill="x", pady=0)
            self._archive_container.pack_forget() # Hidden by default
            self._archive_visible = False
            
            for subj in archived_subjects:
                self._subject_card(self._archive_container, subj, is_archived=True)
                
    def _toggle_archive(self):
        if self._archive_visible:
            self._archive_container.pack_forget()
            self._archive_btn.configure(text="▶ Archived Subjects")
            self._archive_visible = False
        else:
            self._archive_container.pack(fill="x", pady=0)
            self._archive_btn.configure(text="▼ Archived Subjects")
            self._archive_visible = True

    def _subject_card(self, parent, subj, is_archived=False):
        c = self.colors
        pct = self.db.progress_pct(subj)
        days = self.db.days_until_exam(subj)
        rem = self.db.remaining_lectures(subj)

        card = ctk.CTkFrame(parent, fg_color=c["bg_card"], corner_radius=16,
                            border_width=1, border_color=c["border"])
        card.pack(fill="x", pady=8)

        # ── Left accent strip ──
        strip = ctk.CTkFrame(card, width=5, fg_color=subj["color"],
                             corner_radius=3)
        strip.pack(side="left", fill="y", padx=(0, 0))

        # ── Content ──
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=16, pady=14)

        # Row 1: icon, name, priority badge, exam badge, action buttons
        top_row = ctk.CTkFrame(content, fg_color="transparent")
        top_row.pack(fill="x")

        icon_bg = ctk.CTkFrame(top_row, width=42, height=42, corner_radius=10,
                               fg_color=subj["color"])
        icon_bg.pack(side="left")
        icon_bg.pack_propagate(False)
        ctk.CTkLabel(icon_bg, text=subj["icon"], font=("Segoe UI", 20)).pack(expand=True)

        name_col = ctk.CTkFrame(top_row, fg_color="transparent")
        name_col.pack(side="left", padx=12)
        ctk.CTkLabel(name_col, text=subj["name"], font=FONTS["subheading"],
                     text_color=c["text_primary"], anchor="w").pack(anchor="w")

        # Priority badge
        pri_colors = {
            "high":   (c["tag_high"],   c["tag_high_text"],   "🔴 High"),
            "medium": (c["tag_medium"], c["tag_medium_text"], "🟡 Medium"),
            "low":    (c["tag_low"],    c["tag_low_text"],    "🟢 Low"),
        }
        pri = subj.get("priority", "medium")
        pbg, pfg, ptxt = pri_colors.get(pri, pri_colors["medium"])
        pri_badge = ctk.CTkFrame(name_col, fg_color=pbg, corner_radius=6)
        pri_badge.pack(anchor="w")
        ctk.CTkLabel(pri_badge, text=ptxt, font=FONTS["tiny"], text_color=pfg).pack(padx=8, pady=1)

        # Right side: exam badge + buttons
        right = ctk.CTkFrame(top_row, fg_color="transparent")
        right.pack(side="right")
        if not is_archived:
            LiveCountdown(right, self.db, subj, c).pack(pady=2, anchor="e")

        btn_row = ctk.CTkFrame(right, fg_color="transparent")
        btn_row.pack(pady=(4, 0))
        ctk.CTkButton(btn_row, text="🔥", width=34, height=28,
                      fg_color=c["bg_secondary"], hover_color=c["accent"],
                      corner_radius=8, text_color=c["accent"],
                      command=lambda s=subj: self._start_focus(s)).pack(side="left", padx=2)
        ctk.CTkButton(btn_row, text="✏️", width=34, height=28,
                      fg_color=c["bg_secondary"], hover_color=c["accent"],
                      corner_radius=8, text_color=c["accent"],
                      command=lambda s=subj: self._open_edit_dialog(s)).pack(side="left", padx=2)
        ctk.CTkButton(btn_row, text="📅", width=34, height=28,
                      fg_color=c["bg_secondary"], hover_color=c["warning"],
                      corner_radius=8, text_color=c["warning"],
                      command=lambda s=subj: self._open_exam_dialog(s)).pack(side="left", padx=2)
        ctk.CTkButton(btn_row, text="🗑️", width=34, height=28,
                      fg_color=c["bg_secondary"], hover_color=c["danger"],
                      corner_radius=8, text_color=c["danger"],
                      command=lambda s=subj: self._confirm_delete(s)).pack(side="left", padx=2)

        # Row 2: stats + progress
        stats_row = ctk.CTkFrame(content, fg_color="transparent")
        stats_row.pack(fill="x", pady=(12, 0))

        for label, val in [
            ("Total", str(subj["total_lectures"])),
            ("Done", str(subj["completed_lectures"])),
            ("Left", str(rem)),
        ]:
            box = ctk.CTkFrame(stats_row, fg_color=c["bg_secondary"], corner_radius=8)
            box.pack(side="left", padx=(0, 8))
            ctk.CTkLabel(box, text=val, font=("Segoe UI", 14, "bold"),
                         text_color=subj["color"]).pack(padx=12, pady=(4, 0))
            ctk.CTkLabel(box, text=label, font=FONTS["tiny"],
                         text_color=c["text_muted"]).pack(padx=12, pady=(0, 4))

        # Quick +1 button
        ctk.CTkButton(stats_row, text="＋ 1 Lecture", width=110, height=34,
                      fg_color=c["bg_secondary"], hover_color=subj["color"],
                      text_color=subj["color"], font=FONTS["small"], corner_radius=8,
                      command=lambda s=subj: self._quick_add(s)).pack(side="right")

        # Progress bar
        if not is_archived:
            bar_row = ctk.CTkFrame(content, fg_color="transparent")
            bar_row.pack(fill="x", pady=(10, 0))
            LinearProgressBar(bar_row, width=400, height=10, pct=pct,
                              color=subj["color"], bg=c["progress_bg"]).pack(
                side="left", fill="x", expand=True)
            ctk.CTkLabel(bar_row, text=f"{pct:.1f}%", font=FONTS["small"],
                         text_color=c["text_secondary"], width=48).pack(side="right")

        # Notes (if any)
        if subj.get("notes"):
            notes_frame = ctk.CTkFrame(content, fg_color=c["bg_secondary"], corner_radius=8)
            notes_frame.pack(fill="x", pady=(8, 0))
            ctk.CTkLabel(notes_frame, text=f"📝  {subj['notes']}",
                         font=FONTS["tiny"], text_color=c["text_muted"],
                         anchor="w", wraplength=600).pack(fill="x", padx=10, pady=6)

    # ── Quick +1 ─────────────────────────────────────────────
    def _quick_add(self, subj):
        new_done = min(subj["total_lectures"], subj["completed_lectures"] + 1)
        self.db.update_subject(subj["id"], completed_lectures=new_done)
        new_badges = self.db.check_achievements()
        self.toast(f"✅  Marked 1 lecture done for {subj['name']}", "success")
        for b in new_badges:
            self.toast(f"🏆  Achievement: {b['name']}", "info")
        self.refresh()

    def _start_focus(self, subj):
        app = self.winfo_toplevel()
        if hasattr(app, 'navigate'):
            app.navigate("pomodoro")
            # We could auto-select the subject here if PomodoroView supported it via a property

    # ── Search ───────────────────────────────────────────────
    def _on_search(self, *_):
        self._render_subjects(self._search_var.get())

    # ── Dialogs ──────────────────────────────────────────────
    def _open_add_dialog(self):
        SubjectDialog(self, self.db, self.colors, on_save=self._on_save_new)

    def _open_edit_dialog(self, subj):
        SubjectDialog(self, self.db, self.colors, subject=subj,
                      on_save=lambda d: self._on_save_edit(subj["id"], d))

    def _open_exam_dialog(self, subj):
        QuickExamDialog(self, self.db, self.colors, subj, on_save=self.refresh)

    def _on_save_new(self, data):
        subj = default_subject(data["name"])
        subj.update(data)
        subj["id"] = datetime.now().strftime("%Y%m%d%H%M%S%f")
        self.db.add_subject(subj)
        self.toast(f"📚  {data['name']} added!", "success")
        self.refresh()

    def _on_save_edit(self, sid, data):
        self.db.update_subject(sid, **data)
        self.toast("✏️  Subject updated!", "success")
        self.refresh()

    def _confirm_delete(self, subj):
        dlg = tk.Toplevel(self)
        dlg.title("Confirm Delete")
        dlg.geometry("380x160")
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.attributes("-topmost", True)
        c = self.colors
        dlg.configure(bg=c["bg_primary"])

        ctk.CTkLabel(dlg, text=f"Delete '{subj['name']}'?",
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
                      command=lambda: (self.db.delete_subject(subj["id"]),
                                       self.toast(f"🗑️  {subj['name']} deleted.", "error"),
                                       dlg.destroy(), self.refresh())).pack(side="left", padx=8)

    # refresh() moved above _render_subjects for logical flow


# ── Subject Add/Edit Dialog ───────────────────────────────────
class SubjectDialog(tk.Toplevel):
    def __init__(self, master, db, colors, subject=None, on_save=None, **kwargs):
        super().__init__(master, **kwargs)
        self.db = db
        self.colors = colors
        self.subject = subject
        self.on_save = on_save
        self.title("Edit Subject" if subject else "Add Subject")
        self.geometry("520x640")
        self.resizable(False, False)
        self.grab_set()
        self.attributes("-topmost", True)
        self.configure(bg=colors["bg_primary"])
        self._build()

    def _build(self):
        c = self.colors
        s = self.subject or {}

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkLabel(scroll, text="✏️ Edit Subject" if s else "➕ New Subject",
                     font=FONTS["subheading"], text_color=c["text_primary"]).pack(pady=(10, 18))

        # ── Name ──
        self._add_label(scroll, "Subject Name")
        self._name = ctk.CTkEntry(scroll, font=FONTS["body"],
                                  fg_color=c["bg_card"], border_color=c["border"],
                                  text_color=c["text_primary"], corner_radius=10)
        self._name.pack(fill="x", pady=(0, 12))
        if s.get("name"):
            self._name.insert(0, s["name"])

        # ── Icon picker ──
        self._add_label(scroll, "Icon")
        self._icon_var = tk.StringVar(value=s.get("icon", "📚"))
        icon_grid = ctk.CTkFrame(scroll, fg_color=c["bg_card"], corner_radius=10)
        icon_grid.pack(fill="x", pady=(0, 12))
        for i, ico in enumerate(SUBJECT_ICONS):
            r, col = divmod(i, 8)
            btn = ctk.CTkButton(icon_grid, text=ico, width=40, height=36,
                                fg_color="transparent", hover_color=c["accent"],
                                font=("Segoe UI", 16), corner_radius=6,
                                command=lambda x=ico: self._icon_var.set(x))
            btn.grid(row=r, column=col, padx=2, pady=2)

        # ── Color picker ──
        self._add_label(scroll, "Color")
        self._color_var = tk.StringVar(value=s.get("color", SUBJECT_COLORS[0]))
        color_row = ctk.CTkFrame(scroll, fg_color=c["bg_card"], corner_radius=10)
        color_row.pack(fill="x", pady=(0, 12))
        for i, col_hex in enumerate(SUBJECT_COLORS):
            r, cl = divmod(i, 6)
            dot = ctk.CTkButton(color_row, text="", width=30, height=30,
                                fg_color=col_hex, hover_color=col_hex,
                                corner_radius=15,
                                command=lambda x=col_hex: self._color_var.set(x))
            dot.grid(row=r, column=cl, padx=4, pady=4)

        # ── Lectures ──
        lec_row = ctk.CTkFrame(scroll, fg_color="transparent")
        lec_row.pack(fill="x", pady=(0, 12))
        lec_row.grid_columnconfigure((0, 1), weight=1)

        left_col = ctk.CTkFrame(lec_row, fg_color="transparent")
        left_col.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self._add_label(left_col, "Total Lectures")
        self._total = ctk.CTkEntry(left_col, font=FONTS["body"],
                                   fg_color=c["bg_card"], border_color=c["border"],
                                   text_color=c["text_primary"], corner_radius=10)
        self._total.pack(fill="x")
        if s.get("total_lectures") is not None:
            self._total.insert(0, str(s["total_lectures"]))

        right_col = ctk.CTkFrame(lec_row, fg_color="transparent")
        right_col.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        self._add_label(right_col, "Completed Lectures")
        self._done = ctk.CTkEntry(right_col, font=FONTS["body"],
                                  fg_color=c["bg_card"], border_color=c["border"],
                                  text_color=c["text_primary"], corner_radius=10)
        self._done.pack(fill="x")
        if s.get("completed_lectures") is not None:
            self._done.insert(0, str(s["completed_lectures"]))

        # ── Exam Date ──
        self._add_label(scroll, "Exam Date & Time (YYYY-MM-DD HH:MM)")
        self._exam_var = tk.StringVar(value=s.get("exam_date", "") or "")
        date_row = ctk.CTkFrame(scroll, fg_color="transparent")
        date_row.pack(fill="x", pady=(0, 12))
        self._date_entry = ctk.CTkEntry(
            date_row, textvariable=self._exam_var,
            placeholder_text="e.g. 2025-06-15 09:00",
            font=FONTS["body"],
            fg_color=c["bg_card"], border_color=c["border"],
            text_color=c["text_primary"], corner_radius=10, width=200
        )
        self._date_entry.pack(side="left")
        ctk.CTkButton(date_row, text="✕ Clear", width=80,
                      fg_color=c["bg_secondary"], text_color=c["text_muted"],
                      corner_radius=8,
                      command=lambda: self._exam_var.set("")).pack(side="left", padx=8)

        # ── Priority ──
        self._add_label(scroll, "Priority")
        self._priority_var = tk.StringVar(value=s.get("priority", "medium"))
        pri_row = ctk.CTkFrame(scroll, fg_color="transparent")
        pri_row.pack(fill="x", pady=(0, 12))
        for pri in ["low", "medium", "high"]:
            ctk.CTkRadioButton(pri_row, text=pri.capitalize(),
                               variable=self._priority_var, value=pri,
                               font=FONTS["body"],
                               fg_color=c["accent"],
                               text_color=c["text_primary"]).pack(side="left", padx=12)

        # ── Difficulty ──
        self._add_label(scroll, "Difficulty (1-5 ⭐)")
        self._diff_var = tk.IntVar(value=s.get("difficulty", 3))
        diff_row = ctk.CTkFrame(scroll, fg_color="transparent")
        diff_row.pack(fill="x", pady=(0, 12))
        ctk.CTkSlider(diff_row, from_=1, to=5, number_of_steps=4,
                      variable=self._diff_var,
                      button_color=c["accent"],
                      progress_color=c["accent"]).pack(fill="x")
        ctk.CTkLabel(diff_row, textvariable=self._diff_var,
                     font=FONTS["small"], text_color=c["text_muted"]).pack()

        # ── Notes ──
        self._add_label(scroll, "Notes")
        self._notes = ctk.CTkTextbox(scroll, height=70, font=FONTS["small"],
                                      fg_color=c["bg_card"], border_color=c["border"],
                                      text_color=c["text_primary"], corner_radius=10)
        self._notes.pack(fill="x", pady=(0, 16))
        if s.get("notes"):
            self._notes.insert("0.0", s["notes"])

        # ── Save / Cancel ──
        btn_row = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_row.pack(fill="x", pady=(0, 10))
        ctk.CTkButton(btn_row, text="Cancel", width=100,
                      fg_color=c["bg_secondary"], hover_color=c["border"],
                      text_color=c["text_secondary"], corner_radius=10,
                      command=self.destroy).pack(side="left", padx=4)
        ctk.CTkButton(btn_row, text="💾  Save", width=140,
                      fg_color=c["accent"], hover_color=c["accent_light"],
                      corner_radius=10, font=FONTS["title"],
                      command=self._save).pack(side="right", padx=4)

    def _add_label(self, parent, text):
        ctk.CTkLabel(parent, text=text, font=FONTS["small"],
                     text_color=self.colors["text_secondary"],
                     anchor="w").pack(fill="x", pady=(0, 2))

    def _save(self):
        name = self._name.get().strip()
        if not name:
            return
        try:
            total = int(self._total.get() or 0)
            done = int(self._done.get() or 0)
            done = min(done, total)
        except ValueError:
            return

        exam_date = self._exam_var.get().strip() or None

        data = {
            "name": name,
            "icon": self._icon_var.get(),
            "color": self._color_var.get(),
            "total_lectures": total,
            "completed_lectures": done,
            "exam_date": exam_date,
            "priority": self._priority_var.get(),
            "difficulty": self._diff_var.get(),
            "notes": self._notes.get("0.0", "end").strip(),
        }
        if self.on_save:
            self.on_save(data)
        self.destroy()


class QuickExamDialog(tk.Toplevel):
    def __init__(self, master, db, colors, subject, on_save=None, **kwargs):
        super().__init__(master, **kwargs)
        self.db = db
        self.colors = colors
        self.subj = subject
        self.on_save = on_save
        self.title(f"Exam Date: {subject['name']}")
        self.geometry("400x320")
        self.resizable(False, False)
        self.grab_set()
        self.attributes("-topmost", True)
        self.configure(bg=colors["bg_primary"])
        self._build()

    def _build(self):
        c = self.colors
        ctk.CTkLabel(self, text=f"📅 Set Exam Date & Time for {self.subj['name']}", 
                     font=FONTS["subheading"], text_color=c["text_primary"]).pack(pady=(20, 10))
        
        self.entry = ctk.CTkEntry(self, placeholder_text="YYYY-MM-DD HH:MM", font=FONTS["body"],
                                  width=250, height=40, corner_radius=10)
        self.entry.pack(pady=10)
        if self.subj.get("exam_date"):
            self.entry.insert(0, self.subj["exam_date"])

        # Quick options
        q_frame = ctk.CTkFrame(self, fg_color="transparent")
        q_frame.pack(pady=10)
        
        from datetime import timedelta, datetime
        opts = [
            ("Tomorrow", 1),
            ("In 1 Week", 7),
            ("In 2 Weeks", 14),
            ("In 1 Month", 30),
        ]
        for text, days in opts:
            dt = (datetime.now() + timedelta(days=days)).replace(hour=9, minute=0, second=0).strftime("%Y-%m-%d %H:%M")
            ctk.CTkButton(q_frame, text=text, width=80, height=26, font=FONTS["tiny"],
                          fg_color=c["bg_card"], text_color=c["text_secondary"],
                          command=lambda d=dt: (self.entry.delete(0, "end"), self.entry.insert(0, d))).pack(side="left", padx=4)

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(side="bottom", fill="x", pady=20, padx=20)
        
        ctk.CTkButton(btn_row, text="Cancel", width=100, fg_color=c["bg_secondary"],
                      text_color=c["text_secondary"], command=self.destroy).pack(side="left")
        
        ctk.CTkButton(btn_row, text="Save Date", width=140, fg_color=c["accent"],
                      command=self._save).pack(side="right")

    def _save(self):
        val = self.entry.get().strip()
        self.db.update_subject(self.subj["id"], exam_date=val or None)
        if self.on_save:
            self.on_save()
        self.destroy()
