# ============================================================
# Study Reminder Pro - Subjects Database Service
# File: database/subjects_db.py
# ============================================================

from datetime import datetime, date
from utils.logger import log

def default_subject(name="New Subject"):
    """Return a blank subject dictionary."""
    return {
        "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
        "name": name,
        "icon": "📚",
        "color": "#6C63FF",
        "total_lectures": 0,
        "completed_lectures": 0,
        "exam_date": None,
        "notes": "",
        "priority": "medium",
        "difficulty": 3,
        "created_at": datetime.now().isoformat(),
        "study_sessions": [],
        "rich_notes": [] # New feature: list of note objects
    }

class SubjectsDB:
    def __init__(self, core_store):
        self.store = core_store

    @property
    def subjects(self):
        return self.store.app_data.setdefault("subjects", [])

    def add_subject(self, subject_dict=None):
        subj = subject_dict or default_subject()
        self.subjects.append(subj)
        self.store.save_app_data()
        log.info(f"Added subject: {subj['name']}")
        return subj

    def update_subject(self, subject_id, **kwargs):
        for s in self.subjects:
            if s["id"] == subject_id:
                s.update(kwargs)
                self.store.save_app_data()
                return s
        return None

    def delete_subject(self, subject_id):
        initial_len = len(self.subjects)
        self.store.app_data["subjects"] = [s for s in self.subjects if s["id"] != subject_id]
        if len(self.subjects) < initial_len:
            self.store.save_app_data()
            log.info(f"Deleted subject ID: {subject_id}")

    def get_subject(self, subject_id):
        for s in self.subjects:
            if s["id"] == subject_id:
                return s
        return None

    # ---------- Computed Properties ----------
    def remaining_lectures(self, subject):
        return max(0, subject.get("total_lectures", 0) - subject.get("completed_lectures", 0))

    def progress_pct(self, subject):
        tot = subject.get("total_lectures", 0)
        if tot == 0:
            return 0.0
        return min(100.0, (subject.get("completed_lectures", 0) / tot) * 100)

    def exam_countdown_info(self, subject):
        dt_str = subject.get("exam_date")
        if not dt_str:
            return None
        try:
            if "T" in dt_str or " " in dt_str:
                exam_dt = datetime.fromisoformat(dt_str.replace(" ", "T"))
            else:
                exam_dt = datetime.combine(date.fromisoformat(dt_str), datetime.min.time())
            
            now = datetime.now()
            delta = exam_dt - now
            
            if delta.total_seconds() < 0:
                return (-1, 0, 0, 0)
            
            days = delta.days
            hours, remainder = divmod(delta.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return (days, hours, minutes, seconds)
        except Exception as e:
            log.error(f"Error parsing date {dt_str}: {e}")
            return None

    def days_until_exam(self, subject):
        info = self.exam_countdown_info(subject)
        return info[0] if info else None
