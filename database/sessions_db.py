# ============================================================
# Study Reminder Pro - Sessions Database Service
# File: database/sessions_db.py
# ============================================================

from datetime import datetime
from utils.logger import log

class SessionsDB:
    """Manages detailed study session history for analytics and focus mode."""
    def __init__(self, core_store):
        self.store = core_store

    @property
    def sessions(self):
        return self.store.app_data.setdefault("sessions", [])

    @property
    def pomodoro_sessions(self):
        # Kept for backward compatibility
        return self.store.app_data.setdefault("pomodoro_sessions", [])
        
    def get_all_sessions(self):
        """Returns all detailed sessions."""
        return self.sessions

    def log_pomodoro(self, subject_id, minutes):
        """Legacy compatibility method"""
        session = {
            "subject_id": subject_id,
            "minutes": minutes,
            "timestamp": datetime.now().isoformat()
        }
        self.pomodoro_sessions.append(session)
        self.store.save_app_data()
        log.debug("Logged legacy pomodoro session.")

    def record_session(self, subject_id, start_time, end_time, duration_min, completed=True, interruptions=0):
        """New detailed session logger."""
        session = {
            "id": datetime.now().strftime("sess_%Y%m%d%H%M%S"),
            "subject_id": subject_id,
            "start_time": start_time.isoformat() if isinstance(start_time, datetime) else start_time,
            "end_time": end_time.isoformat() if isinstance(end_time, datetime) else end_time,
            "duration_minutes": duration_min,
            "completed": completed,
            "interruptions": interruptions,
            "timestamp": datetime.now().isoformat()
        }
        self.sessions.append(session)
        
        # Also log to legacy array for old charts if necessary
        self.log_pomodoro(subject_id, duration_min)
        
        log.info(f"Recorded detailed session: {duration_min} mins")
        return session
        
    def log_session(self, session_dict):
        """Directly logs a pre-constructed session dictionary."""
        # Ensure timestamp exists
        if "timestamp" not in session_dict:
            session_dict["timestamp"] = datetime.now().isoformat()
        self.sessions.append(session_dict)
        
        # Log to legacy pomodoros for backward compat
        if "subject_id" in session_dict and "duration_min" in session_dict:
            self.log_pomodoro(session_dict["subject_id"], session_dict["duration_min"])
            
        self.store.save_app_data()
        log.info(f"Logged session dictionary: {session_dict.get('duration_min', 0)} mins")
