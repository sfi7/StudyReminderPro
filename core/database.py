# ============================================================
# Study Reminder Pro - Database Bridge Facade
# File: core/database.py
# ============================================================

from database.core_store import CoreStore, DATA_DIR, BACKUP_DIR, DB_FILE
from database.subjects_db import SubjectsDB, default_subject
from database.tasks_db import TasksDB
from database.settings_db import SettingsDB
from database.analytics_db import AnalyticsDB
from database.sessions_db import SessionsDB
from utils.logger import log

# Exported for backward compatibility
# from core.database import default_subject

class Database:
    """
    Facade class maintaining backward compatibility for existing UI code.
    Delegates calls to the modular database services.
    """
    def __init__(self):
        log.info("Initializing modular Database Facade")
        self._store = CoreStore()
        
        self._subjects_db = SubjectsDB(self._store)
        self._tasks_db = TasksDB(self._store)
        self._settings_db = SettingsDB(self._store)
        self._analytics_db = AnalyticsDB(self._store)
        self._sessions_db = SessionsDB(self._store)

    # ---------- Facade for Settings ----------
    @property
    def settings(self):
        return self._settings_db.settings

    def update_setting(self, key, value):
        self._settings_db.update(key, value)

    # ---------- Facade for Subjects ----------
    @property
    def subjects(self):
        return self._subjects_db.subjects

    def add_subject(self, subject_dict=None):
        return self._subjects_db.add_subject(subject_dict)

    def update_subject(self, subject_id, **kwargs):
        return self._subjects_db.update_subject(subject_id, **kwargs)

    def delete_subject(self, subject_id):
        self._subjects_db.delete_subject(subject_id)

    def get_subject(self, subject_id):
        return self._subjects_db.get_subject(subject_id)

    def remaining_lectures(self, subject):
        return self._subjects_db.remaining_lectures(subject)

    def progress_pct(self, subject):
        return self._subjects_db.progress_pct(subject)

    def exam_countdown_info(self, subject):
        return self._subjects_db.exam_countdown_info(subject)

    def days_until_exam(self, subject):
        return self._subjects_db.days_until_exam(subject)

    # ---------- Facade for Analytics ----------
    @property
    def streaks(self):
        return self._analytics_db.streaks

    # ---------- Facade for Tasks ----------
    @property
    def tasks(self):
        return self._tasks_db.tasks

    def add_task(self, title, **kwargs):
        return self._tasks_db.add_task(title, **kwargs)

    def update_task(self, task_id, **kwargs):
        return self._tasks_db.update_task(task_id, **kwargs)

    def toggle_task(self, task_id):
        return self._tasks_db.toggle_task(task_id)

    def delete_task(self, task_id):
        self._tasks_db.delete_task(task_id)

    def get_pending_tasks(self):
        return self._tasks_db.get_pending_tasks()

    def get_completed_tasks(self):
        return self._tasks_db.get_completed_tasks()

    def record_study_today(self):
        self._analytics_db.record_study_today()

    def log_study(self, subject_id, minutes):
        self._analytics_db.log_study(subject_id, minutes)

    def today_total_minutes(self):
        return self._analytics_db.today_total_minutes()

    def weekly_minutes(self):
        return self._analytics_db.weekly_minutes()

    # ---------- Facade for Sessions / Pomodoro ----------
    def log_pomodoro(self, subject_id, minutes):
        self._sessions_db.log_pomodoro(subject_id, minutes)
        self.log_study(subject_id, minutes) # Also log to daily stats

    # ---------- Facade for Backups ----------
    def backup(self):
        return self._store.backup_app_data()

    def restore(self, backup_path):
        self._store.restore_backup(backup_path)

    def list_backups(self):
        import os
        from database.core_store import BACKUP_DIR
        if not os.path.exists(BACKUP_DIR):
            return []
        files = [f for f in os.listdir(BACKUP_DIR) if f.endswith(".json")]
        return sorted(files, reverse=True)

    # ---------- Achievements (Kept for now) ----------
    def check_achievements(self):
        from datetime import datetime
        awarded = {a["id"] for a in self._store.app_data.setdefault("achievements", [])}
        new_badges = []

        streak = self.streaks["current"]
        if streak >= 3 and "streak_3" not in awarded:
            new_badges.append({"id": "streak_3", "name": "3-Day Streak 🔥",
                                "desc": "Studied 3 days in a row!", "ts": datetime.now().isoformat()})
        if streak >= 7 and "streak_7" not in awarded:
            new_badges.append({"id": "streak_7", "name": "Week Warrior 💪",
                                "desc": "7-day study streak!", "ts": datetime.now().isoformat()})

        for s in self.subjects:
            if s.get("total_lectures", 0) > 0 and s.get("completed_lectures", 0) >= s.get("total_lectures", 0):
                badge_id = f"done_{s['id']}"
                if badge_id not in awarded:
                    new_badges.append({"id": badge_id, "name": f"✅ {s['name']} Complete!",
                                       "desc": f"Finished all lectures for {s['name']}",
                                       "ts": datetime.now().isoformat()})

        self._store.app_data["achievements"].extend(new_badges)
        if new_badges:
            self._store.save_app_data()
        return new_badges
