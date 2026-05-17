# ============================================================
# Study Reminder Pro - Settings Service
# File: services/settings_service.py
# ============================================================

from utils.logger import log

class SettingsService:
    """
    Business logic layer for managing application settings.
    Handles defaults, validation, and notifies listeners of changes.
    """
    def __init__(self, settings_db, theme_manager=None):
        self._db = settings_db
        self._theme_manager = theme_manager
        self._listeners = {}

        # Initialize theme on startup
        if self._theme_manager:
            saved_theme = self.get("theme", "dark")
            self._theme_manager.set_theme(saved_theme)

    def add_listener(self, setting_key, callback):
        """Register a callback when a specific setting changes."""
        if setting_key not in self._listeners:
            self._listeners[setting_key] = []
        self._listeners[setting_key].append(callback)

    def get(self, key, default=None):
        return self._db.get(key, default)

    def update(self, key, value):
        old_val = self.get(key)
        if old_val != value:
            self._db.update(key, value)
            log.info(f"Setting changed: {key} -> {value}")
            
            # Apply immediate side effects
            if key == "theme" and self._theme_manager:
                self._theme_manager.set_theme(value)

            # Notify listeners
            if key in self._listeners:
                for cb in self._listeners[key]:
                    try:
                        cb(value)
                    except Exception as e:
                        log.error(f"Listener error on setting '{key}': {e}")
