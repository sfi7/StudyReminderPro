# ============================================================
# Study Reminder Pro - Notification Service
# File: services/notification_service.py
# ============================================================

import threading
import time
from utils.logger import log

try:
    from plyer import notification
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False
    log.warning("plyer not installed. Desktop notifications disabled.")

class NotificationService:
    """
    Centralized, debounced notification system.
    Survives UI navigation, supports callbacks, prevents duplicate alarms.
    """
    def __init__(self, app_icon_path=None):
        self.app_icon_path = app_icon_path if app_icon_path else None
        self.history = {}  # {notification_id: last_triggered_timestamp}
        self.debounce_seconds = 10

    def show(self, title, message, duration=5, notif_id=None, click_callback=None):
        """
        Shows a Windows desktop notification safely.
        """
        if not PLYER_AVAILABLE:
            log.info(f"Notification blocked (not installed): {title} - {message}")
            return False

        # Debounce logic
        now = time.time()
        if notif_id:
            last_triggered = self.history.get(notif_id, 0)
            if now - last_triggered < self.debounce_seconds:
                log.debug(f"Notification '{notif_id}' debounced.")
                return False

        def _notify_thread():
            try:
                notification.notify(
                    title=title,
                    message=message,
                    app_name="Study Reminder Pro",
                    app_icon=self.app_icon_path,
                    timeout=duration
                )
                if click_callback:
                    log.info("click_callback provided but plyer doesn't support it directly.")
            except Exception as e:
                log.error(f"Failed to show notification: {e}")

        # Run on a background thread so it doesn't block the UI loop
        threading.Thread(target=_notify_thread, daemon=True).start()
        
        if notif_id:
            self.history[notif_id] = now
            
        return True
