# ============================================================
# Study Reminder Pro - Settings Database Service
# File: database/settings_db.py
# ============================================================

from utils.logger import log

class SettingsDB:
    def __init__(self, core_store):
        self.store = core_store

    @property
    def settings(self):
        return self.store.settings_data

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def update(self, key, value):
        self.settings[key] = value
        self.store.save_settings_data()
        log.debug(f"Updated setting {key} = {value}")

    def get_all(self):
        return self.settings.copy()

    def update_multiple(self, **kwargs):
        for k, v in kwargs.items():
            self.settings[k] = v
        self.store.save_settings_data()
        log.debug("Updated multiple settings")
