# ============================================================
# Study Reminder Pro - Settings View
# File: ui/settings.py
# ============================================================

import tkinter as tk
import customtkinter as ctk
import os
from core.theme import FONTS


class SettingsView(ctk.CTkScrollableFrame):
    """App settings: profile, theme, daily goal, Pomodoro, backup."""

    def __init__(self, master, db, colors, toast_fn, theme_switch_fn, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.db = db
        self.colors = colors
        self.toast = toast_fn
        self.theme_switch = theme_switch_fn
        self._widgets = []
        self._build()

    def _build(self):
        c = self.colors

        lbl = ctk.CTkLabel(self, text="⚙️ Settings",
                     font=FONTS["heading"], text_color=c["text_primary"],
                     anchor="w")
        lbl.pack(fill="x", padx=24, pady=(20, 10))
        self._widgets.append(lbl)

        # ── Profile ──────────────────────────────────────────
        self._section("👤  Profile", c)
        profile_card = self._card()

        self._field_row(profile_card, "Student Name",
                        self.db.settings.get("student_name", "Student"),
                        "_name_entry")

        ctk.CTkButton(profile_card, text="💾 Save Name",
                      fg_color=c["accent"], hover_color=c["accent_hover"],
                      corner_radius=12, font=FONTS["button"], height=40,
                      command=self._save_name).pack(anchor="w", padx=16, pady=(0, 16))

        # ── Appearance ───────────────────────────────────────
        self._section("🎨  Appearance", c)
        app_card = self._card()

        # Theme Mode Toggle
        mode_row = ctk.CTkFrame(app_card, fg_color="transparent")
        mode_row.pack(fill="x", padx=16, pady=10)
        ctk.CTkLabel(mode_row, text="Theme Mode",
                     font=FONTS["body"], text_color=c["text_primary"]).pack(side="left")

        self._theme_switch = ctk.CTkSwitch(
            mode_row,
            text="Dark Mode",
            font=FONTS["small"],
            text_color=c["text_secondary"],
            progress_color=c["accent"],
            command=self._on_theme_toggle,
            onvalue="dark", offvalue="light"
        )
        self._theme_switch.pack(side="right")
        if self.db.settings.get("theme", "dark") == "dark":
            self._theme_switch.select()

        # Custom Accent Selection
        accent_row = ctk.CTkFrame(app_card, fg_color="transparent")
        accent_row.pack(fill="x", padx=16, pady=10)
        ctk.CTkLabel(accent_row, text="Accent Color",
                     font=FONTS["body"], text_color=c["text_primary"]).pack(side="left")
        
        chip_container = ctk.CTkFrame(accent_row, fg_color="transparent")
        chip_container.pack(side="right")
        
        from themes.colors import ACCENT_PRESETS
        for name, color in ACCENT_PRESETS.items():
            btn = ctk.CTkButton(chip_container, text="", width=24, height=24, 
                                corner_radius=12, fg_color=color, hover_color=color,
                                border_width=2 if self.db.settings.get("accent_color") == color else 0,
                                border_color=c["text_primary"],
                                command=lambda col=color: self._on_accent_change(col))
            btn.pack(side="left", padx=4)

        # Glassmorphism Toggle
        glass_row = ctk.CTkFrame(app_card, fg_color="transparent")
        glass_row.pack(fill="x", padx=16, pady=10)
        ctk.CTkLabel(glass_row, text="Glassmorphism Effects",
                     font=FONTS["body"], text_color=c["text_primary"]).pack(side="left")
        
        glass_switch = ctk.CTkSwitch(glass_row, text="", command=self._toggle_glass,
                                     progress_color=c["accent"])
        glass_switch.pack(side="right")
        if self.db.settings.get("glassmorphism"):
            glass_switch.select()

        # Desktop Widget Toggle
        widget_row = ctk.CTkFrame(app_card, fg_color="transparent")
        widget_row.pack(fill="x", padx=16, pady=10)
        ctk.CTkLabel(widget_row, text="Desktop Mini Panel",
                     font=FONTS["body"], text_color=c["text_primary"]).pack(side="left")
        
        widget_switch = ctk.CTkSwitch(widget_row, text="", command=self._toggle_widget,
                                      progress_color=c["accent"])
        widget_switch.pack(side="right")
        if self.db.settings.get("show_widget"):
            widget_switch.select()

        # ── Daily Goal ───────────────────────────────────────
        self._section("🎯  Daily Study Goal", c)
        goal_card = self._card()

        goal_row = ctk.CTkFrame(goal_card, fg_color="transparent")
        goal_row.pack(fill="x", padx=16, pady=(12, 4))
        ctk.CTkLabel(goal_row, text="Daily Goal (minutes)",
                     font=FONTS["body"], text_color=c["text_primary"]).pack(side="left")

        self._goal_var = tk.IntVar(value=self.db.settings.get("daily_goal_minutes", 120))
        ctk.CTkLabel(goal_row, textvariable=self._goal_var,
                     font=FONTS["title"], text_color=c["accent"],
                     width=46).pack(side="right")

        ctk.CTkSlider(goal_card, from_=30, to=480, number_of_steps=45,
                      variable=self._goal_var,
                      progress_color=c["accent"],
                      button_color=c["accent"],
                      button_hover_color=c["accent_light"]).pack(
            fill="x", padx=16, pady=(0, 4))
        ctk.CTkLabel(goal_card, text="30 min — 8 hours",
                     font=FONTS["tiny"], text_color=c["text_muted"]).pack(anchor="w", padx=16)

        ctk.CTkButton(goal_card, text="💾 Save Goal",
                      fg_color=c["accent"], hover_color=c["accent_hover"],
                      corner_radius=12, font=FONTS["button"], height=40,
                      command=self._save_goal).pack(anchor="w", padx=16, pady=(8, 16))

        # ── Pomodoro Durations ───────────────────────────────
        self._section("🍅  Pomodoro Defaults", c)
        pom_card = self._card()

        pom_grid = ctk.CTkFrame(pom_card, fg_color="transparent")
        pom_grid.pack(fill="x", padx=16, pady=(10, 0))
        pom_grid.grid_columnconfigure((0, 1, 2), weight=1)

        self._pom_vars = {}
        for col, (key, label, default) in enumerate([
            ("pomodoro_work",       "Work (min)",        25),
            ("pomodoro_break",      "Short Break (min)", 5),
            ("pomodoro_long_break", "Long Break (min)",  15),
        ]):
            f = ctk.CTkFrame(pom_grid, fg_color="transparent")
            f.grid(row=0, column=col, sticky="ew", padx=4)
            ctk.CTkLabel(f, text=label, font=FONTS["small"],
                         text_color=c["text_muted"]).pack(anchor="w")
            var = tk.StringVar(value=str(self.db.settings.get(key, default)))
            self._pom_vars[key] = var
            ctk.CTkEntry(f, textvariable=var, width=70, justify="center",
                         font=FONTS["body"], fg_color=c["bg_secondary"],
                         border_color=c["border"],
                         text_color=c["text_primary"]).pack(anchor="w", pady=4)

        ctk.CTkButton(pom_card, text="💾 Save Pomodoro Settings",
                      fg_color=c["accent"], hover_color=c["accent_hover"],
                      corner_radius=12, font=FONTS["button"], height=40,
                      command=self._save_pomodoro).pack(anchor="w", padx=16, pady=(8, 16))

        # ── Backup & Restore ─────────────────────────────────
        self._section("💾  Backup & Restore", c)
        backup_card = self._card()

        btn_row = ctk.CTkFrame(backup_card, fg_color="transparent")
        btn_row.pack(fill="x", padx=16, pady=12)

        ctk.CTkButton(btn_row, text="📦  Create Backup",
                      fg_color=c["bg_secondary"],
                      hover_color=c["success"],
                      text_color=c["success"],
                      corner_radius=10,
                      command=self._backup).pack(side="left", padx=(0, 10))

        ctk.CTkButton(btn_row, text="📂  Restore Latest",
                      fg_color=c["bg_secondary"],
                      hover_color=c["warning"],
                      text_color=c["warning"],
                      corner_radius=10,
                      command=self._restore).pack(side="left")

        # Backup list
        self._backup_label = ctk.CTkLabel(
            backup_card,
            text=self._backup_summary(),
            font=FONTS["tiny"],
            text_color=c["text_muted"]
        )
        self._backup_label.pack(anchor="w", padx=16, pady=(0, 14))

        # ── Export ───────────────────────────────────────────
        self._section("📤  Export Report", c)
        exp_card = self._card()
        ctk.CTkButton(exp_card, text="📄  Export as Text Report",
                      fg_color=c["bg_secondary"],
                      hover_color=c["accent"],
                      text_color=c["accent"],
                      corner_radius=10,
                      command=self._export_report).pack(anchor="w", padx=16, pady=14)

        # ── Danger Zone ──────────────────────────────────────
        self._section("⚠️  Danger Zone", c)
        danger_card = self._card()
        ctk.CTkButton(danger_card, text="🗑️  Reset All Data",
                      fg_color=c["bg_secondary"],
                      hover_color=c["danger"],
                      text_color=c["danger"],
                      corner_radius=10,
                      command=self._confirm_reset).pack(anchor="w", padx=16, pady=14)

        ctk.CTkFrame(self, fg_color="transparent", height=24).pack()

    # ── Helpers ───────────────────────────────────────────────
    def _card(self):
        c = self.colors
        card = ctk.CTkFrame(self, fg_color=c["bg_card"], corner_radius=16,
                            border_width=1, border_color=c["border"])
        card.pack(fill="x", padx=24, pady=8)
        self._widgets.append(card)
        return card

    def _section(self, title, c):
        lbl = ctk.CTkLabel(self, text=title, font=FONTS["subheading"],
                     text_color=c["text_primary"],
                     anchor="w")
        lbl.pack(fill="x", padx=24, pady=(20, 6))
        self._widgets.append(lbl)

    def _field_row(self, parent, label, default, attr):
        c = self.colors
        ctk.CTkLabel(parent, text=label, font=FONTS["small"],
                     text_color=c["text_muted"], anchor="w").pack(fill="x", padx=16, pady=(12, 2))
        entry = ctk.CTkEntry(parent, font=FONTS["body"],
                             fg_color=c["bg_secondary"], border_color=c["border"],
                             text_color=c["text_primary"], corner_radius=10)
        entry.pack(fill="x", padx=16, pady=(0, 6))
        entry.insert(0, default)
        setattr(self, attr, entry)

    # ── Actions ───────────────────────────────────────────────
    def _save_name(self):
        name = self._name_entry.get().strip()
        if name:
            self.db.update_setting("student_name", name)
            self.toast(f"👤  Name saved as '{name}'", "success")

    def _on_theme_toggle(self):
        mode = self._theme_switch.get()
        self.db.update_setting("theme", mode)
        self.theme_switch(mode)

    def _on_accent_change(self, color):
        self.db.update_setting("accent_color", color)
        # We need to tell the app to refresh the theme
        self.theme_switch(self.db.settings.get("theme", "dark"), accent_hex=color)

    def _toggle_glass(self):
        val = not self.db.settings.get("glassmorphism", False)
        self.db.update_setting("glassmorphism", val)
        mode = "glass" if val else self.db.settings.get("theme", "dark")
        self.theme_switch(mode)

    def _toggle_widget(self):
        val = not self.db.settings.get("show_widget", False)
        self.db.update_setting("show_widget", val)
        self.toast(f"Desktop Widget {'Enabled' if val else 'Disabled'}", "success")
        app = self.winfo_toplevel()
        if hasattr(app, '_toggle_mini_panel'):
            app._toggle_mini_panel(val)

    def _save_goal(self):
        try:
            val = int(self._goal_var.get())
            self.db.update_setting("daily_goal_minutes", val)
            self.toast(f"🎯  Daily goal set to {val} minutes!", "success")
        except ValueError:
            pass

    def _save_pomodoro(self):
        for key, var in self._pom_vars.items():
            try:
                self.db.update_setting(key, int(var.get()))
            except (ValueError, tk.TclError):
                pass
        self.toast("🍅  Pomodoro settings saved!", "success")

    def _backup_summary(self):
        backups = self.db.list_backups()
        if not backups:
            return "No backups yet."
        return f"Latest backup: {backups[0]}  ({len(backups)} total)"

    def _backup(self):
        path = self.db.backup()
        if path:
            self.toast(f"📦  Backup saved!", "success")
            self._backup_label.configure(text=self._backup_summary())
        else:
            self.toast("No data to backup yet.", "warning")

    def _restore(self):
        backups = self.db.list_backups()
        if not backups:
            self.toast("No backups found.", "warning")
            return
        from core.database import BACKUP_DIR
        self.db.restore(os.path.join(BACKUP_DIR, backups[0]))
        self.toast("✅  Data restored from latest backup!", "success")

    def _export_report(self):
        import datetime as dt
        lines = [
            "=" * 50,
            "  STUDY REMINDER PRO — PROGRESS REPORT",
            f"  Generated: {dt.datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "=" * 50, ""
        ]
        for s in self.db.subjects:
            pct = self.db.progress_pct(s)
            days = self.db.days_until_exam(s)
            lines += [
                f"📚 {s['name']}",
                f"   Progress   : {pct:.1f}%  ({s['completed_lectures']}/{s['total_lectures']} lectures)",
                f"   Remaining  : {self.db.remaining_lectures(s)} lectures",
                f"   Exam in    : {days} days" if days is not None else "   Exam date  : Not set",
                f"   Priority   : {s.get('priority','medium').capitalize()}",
                f"   Notes      : {s.get('notes','—')}",
                ""
            ]
        lines += [
            f"🔥 Current Streak  : {self.db.streaks['current']} days",
            f"🏆 Longest Streak  : {self.db.streaks['longest']} days",
            f"⏱️  Today's Minutes : {self.db.today_total_minutes()} min",
        ]
        from core.database import DATA_DIR
        report_path = os.path.join(DATA_DIR, "report.txt")
        try:
            with open(report_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            self.toast(f"📄  Report saved to data/report.txt", "success")
            os.startfile(report_path)
        except PermissionError:
            self.toast("❌  Permission Denied: Please close report.txt if it is open.", "error")
        except Exception as e:
            self.toast(f"❌  Export failed: {str(e)}", "error")

    def _confirm_reset(self):
        dlg = tk.Toplevel(self)
        dlg.title("Confirm Reset")
        dlg.geometry("380x160")
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.attributes("-topmost", True)
        c = self.colors
        dlg.configure(bg=c["bg_primary"])

        ctk.CTkLabel(dlg, text="Reset ALL Data?",
                     font=FONTS["subheading"], text_color=c["danger"]).pack(pady=(24, 6))
        ctk.CTkLabel(dlg, text="This will permanently delete everything.",
                     font=FONTS["small"], text_color=c["text_muted"]).pack()

        btn_row = ctk.CTkFrame(dlg, fg_color="transparent")
        btn_row.pack(pady=16)
        ctk.CTkButton(btn_row, text="Cancel", width=100,
                      fg_color=c["bg_secondary"], text_color=c["text_secondary"],
                      command=dlg.destroy).pack(side="left", padx=8)
        ctk.CTkButton(btn_row, text="⚠️ Reset", width=100,
                      fg_color=c["danger"], hover_color="#C0392B",
                      command=lambda: (self._do_reset(), dlg.destroy())).pack(side="left", padx=8)

    def _do_reset(self):
        from core.database import default_data, DB_FILE
        import json
        with open(DB_FILE, "w") as f:
            json.dump(default_data(), f, indent=2)
        self.db._data = self.db._load()
        self.toast("🗑️  All data reset.", "error")

    def refresh(self):
        """Safely rebuild the settings contents."""
        current_data_ver = self.db.data_version
        current_settings_ver = self.db.settings_version
        if (getattr(self, "_last_data_version", -1) == current_data_ver and 
            getattr(self, "_last_settings_version", -1) == current_settings_ver):
            return
            
        self._last_data_version = current_data_ver
        self._last_settings_version = current_settings_ver

        if not hasattr(self, "_widgets"): self._widgets = []
        for w in self._widgets:
            try: w.destroy()
            except: pass
        self._widgets.clear()
        self._build()
