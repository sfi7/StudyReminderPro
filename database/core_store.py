# ============================================================
# Study Reminder Pro - Core Data Store
# File: database/core_store.py
# ============================================================

import os
import shutil
from datetime import datetime
from utils.json_storage import atomic_write_json, read_json
from utils.logger import log

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(APP_DIR, "data")
DB_FILE = os.path.join(DATA_DIR, "study_data.json")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")
BACKUP_DIR = os.path.join(DATA_DIR, "backups")

def default_app_data():
    return {
        "subjects": [],
        "streaks": {
            "current": 0,
            "longest": 0,
            "last_study_date": None
        },
        "pomodoro_sessions": [],
        "achievements": [],
        "daily_logs": {},
        "tasks": [],
        "daily_goals": {},
        "plans": [],
        "sessions": [],
        "gamification": {
            "level": 1,
            "xp": 0,
            "total_focus_mins": 0,
            "badges": [],
            "daily_xp_cap": 2000,
            "last_xp_date": None
        }
    }

def default_settings_data():
    return {
        "theme": "dark",
        "daily_goal_minutes": 120,
        "pomodoro_work": 25,
        "pomodoro_break": 5,
        "pomodoro_long_break": 15,
        "student_name": "Student",
        "sound_enabled": True,
        "accent_color": "#6C63FF",
        "glassmorphism": False
    }

class CoreStore:
    """
    Centralized data store that manages the JSON files and provides
    a shared in-memory dictionary for all modular services.
    """
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        os.makedirs(BACKUP_DIR, exist_ok=True)
        self._app_data = self._load_app_data()
        self._settings_data = self._load_settings_data()
        self.data_version = 0
        self.settings_version = 0

    def _load_app_data(self):
        data = read_json(DB_FILE, default=default_app_data())
        
        # Merge missing keys from default to ensure new features work on old saves
        defaults = default_app_data()
        for key, val in defaults.items():
            data.setdefault(key, val)
            
        # Migration from old study_data.json settings to settings.json
        if "settings" in data:
            # We keep it for backward compatibility but settings_db will use settings.json
            pass
            
        return data

    def _load_settings_data(self):
        data = read_json(SETTINGS_FILE, default=default_settings_data())
        
        # If settings.json is empty but study_data.json has old settings, migrate them
        old_data = read_json(DB_FILE, default={})
        if "settings" in old_data and not os.path.exists(SETTINGS_FILE):
            log.info("Migrating settings from study_data.json to settings.json")
            data.update(old_data["settings"])
            
        defaults = default_settings_data()
        for key, val in defaults.items():
            data.setdefault(key, val)
        return data

    def save_app_data(self):
        self.data_version += 1
        atomic_write_json(DB_FILE, self._app_data)

    def save_settings_data(self):
        self.settings_version += 1
        atomic_write_json(SETTINGS_FILE, self._settings_data)

    @property
    def app_data(self):
        return self._app_data

    @property
    def settings_data(self):
        return self._settings_data

    def backup_app_data(self):
        if not os.path.exists(DB_FILE):
            return None
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = os.path.join(BACKUP_DIR, f"backup_{timestamp}.json")
        try:
            shutil.copy2(DB_FILE, dest)
            log.info(f"Created backup at {dest}")
            return dest
        except Exception as e:
            log.error(f"Backup failed: {e}")
            return None

    def restore_backup(self, backup_path):
        try:
            shutil.copy2(backup_path, DB_FILE)
            self._app_data = self._load_app_data()
            log.info(f"Restored backup from {backup_path}")
            return True
        except Exception as e:
            log.error(f"Restore failed: {e}")
            return False
