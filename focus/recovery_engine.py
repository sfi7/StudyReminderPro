# ============================================================
# Study Reminder Pro - Recovery Engine
# File: focus/recovery_engine.py
# ============================================================

import json
import os
import time
from utils.logger import log

class RecoveryEngine:
    """
    Bulletproof crash recovery for focus sessions.
    Autosaves active session state and restores after abnormal exits.
    """
    def __init__(self, storage_path="data/session_recovery.json"):
        self.storage_path = storage_path
        self._ensure_dir()

    def _ensure_dir(self):
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)

    def save_snapshot(self, session_data):
        """
        Atomically saves an active session snapshot.
        session_data includes: id, subject_id, target_duration, remaining, paused, etc.
        """
        try:
            temp_path = self.storage_path + ".tmp"
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(session_data, f, indent=4)
            os.replace(temp_path, self.storage_path)
        except Exception as e:
            log.error(f"Failed to save recovery snapshot: {e}")

    def clear_snapshot(self):
        """Removes the snapshot upon successful session completion."""
        try:
            if os.path.exists(self.storage_path):
                os.remove(self.storage_path)
        except Exception as e:
            log.error(f"Failed to clear recovery snapshot: {e}")

    def detect_unfinished_session(self):
        """
        Loads the snapshot and validates its integrity.
        Returns the snapshot dictionary if valid and recoverable, else None.
        """
        if not os.path.exists(self.storage_path):
            return None
            
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            # Session Integrity Layer Validation
            if not self._validate_integrity(data):
                log.warning("Corrupted or invalid recovery snapshot detected. Discarding.")
                self.clear_snapshot()
                return None
                
            # Calculate timer drift if the session was running
            if not data.get("paused_state", False):
                last_save = data.get("last_updated_at", time.time())
                drift = time.time() - last_save
                new_remaining = data.get("remaining_seconds", 0) - drift
                data["remaining_seconds"] = max(0, new_remaining)
                
            return data
            
        except Exception as e:
            log.error(f"Failed to load recovery snapshot: {e}")
            self.clear_snapshot()
            return None

    def _validate_integrity(self, data):
        """Safeguards to prevent negative countdowns, missing fields, or corruption."""
        if not isinstance(data, dict): return False
        required_keys = ["session_id", "subject_id", "target_duration_min", "remaining_seconds", "last_updated_at"]
        for k in required_keys:
            if k not in data:
                return False
                
        if data["remaining_seconds"] < 0:
            return False
            
        return True
