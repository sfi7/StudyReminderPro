# ============================================================
# Study Reminder Pro - Persistent Timer & Session Engine
# File: focus/session_engine.py
# ============================================================

import time
import threading
import uuid
from datetime import datetime
from focus.recovery_engine import RecoveryEngine
from utils.logger import log

class SessionEngine:
    """
    Thread-safe timer using monotonic time to prevent drift.
    Handles session tracking, interruption counting, and pauses.
    """
    def __init__(self, sessions_db):
        self.db = sessions_db
        self.recovery = RecoveryEngine()

        self.session_id = None
        self.subject_id = None
        self.target_duration_min = 0
        self.remaining_seconds = 0
        self.started_at = None
        
        self.is_running = False
        self.is_paused = False
        
        self.mode = "Work"
        self.is_break = False
        
        self.interruptions = 0
        self._last_tick = None
        self._lock = threading.Lock()
        
        self._autosave_interval = 5
        self._last_autosave = time.time()

    def _autosave(self):
        if self.session_id:
            state = {
                "session_id": self.session_id,
                "subject_id": self.subject_id,
                "target_duration_min": self.target_duration_min,
                "remaining_seconds": self.remaining_seconds,
                "started_at": self.started_at,
                "interruptions": self.interruptions,
                "mode": getattr(self, "mode", "Work")
            }
            self.recovery.save_snapshot(state)
            self._last_autosave = time.time()

    def start_session(self, subject_id, duration_minutes):
        with self._lock:
            self.session_id = str(uuid.uuid4())
            self.subject_id = subject_id
            self.target_duration_min = duration_minutes
            self.remaining_seconds = duration_minutes * 60
            self.started_at = time.time()
            
            self.is_running = True
            self.is_paused = False
            
            self.interruptions = 0
            self._last_tick = time.monotonic()
            
            self._autosave()
            log.info(f"Session {self.session_id} started for {duration_minutes} min.")

    def pause_session(self):
        with self._lock:
            if self.is_running and not self.is_paused:
                self.is_paused = True
                self.interruptions += 1
                self._autosave()
                log.info(f"Session {self.session_id} paused.")

    def resume_session(self):
        with self._lock:
            if self.is_running and self.is_paused:
                self.is_paused = False
                self._last_tick = time.monotonic()
                self._autosave()
                log.info(f"Session {self.session_id} resumed.")

    def get_remaining_time(self):
        with self._lock:
            if not self.is_running:
                return 0
                
            if not self.is_paused:
                now = time.monotonic()
                elapsed = now - self._last_tick
                self.remaining_seconds -= elapsed
                self._last_tick = now
                
                if time.time() - self._last_autosave > self._autosave_interval:
                    self._autosave()
                    
            return max(0.0, self.remaining_seconds)

    def get_elapsed_time(self):
        with self._lock:
            if not self.is_running:
                return 0
            return (self.target_duration_min * 60) - self.remaining_seconds

    def complete_session(self, forced_end=False):
        with self._lock:
            if not self.is_running:
                return None
                
            self.is_running = False
            self.is_paused = False
            
            end_time_dt = datetime.now()
            actual_duration_min = round(((self.target_duration_min * 60) - self.remaining_seconds) / 60)
            completed = not forced_end and (self.remaining_seconds <= 2) # 2s tolerance
            
            # Save to DB
            start_time_iso = datetime.fromtimestamp(self.started_at).isoformat() if self.started_at else ""
            session_record = {
                "id": self.session_id,
                "subject_id": self.subject_id,
                "target_duration_min": self.target_duration_min,
                "duration_min": actual_duration_min,
                "interruptions": self.interruptions,
                "completed": completed,
                "start_time": start_time_iso,
                "end_time": end_time_dt.isoformat()
            }
            
            self.db.log_session(session_record)
            
            # Clean up recovery snapshot
            self.recovery.clear_snapshot()
            
            log.info(f"Session completed. Total min: {actual_duration_min}, Interrupted: {self.interruptions}")
            return session_record

    def calculate_focus_score(self):
        """Calculates a productivity score based on interruptions and completion."""
        score = 100
        score -= (self.interruptions * 5)
        # We don't have break_duration_sec tracked anymore, could add it later
        return max(0, min(100, int(score)))
