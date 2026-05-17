# ============================================================
# Study Reminder Pro - Analytics Database Service
# File: database/analytics_db.py
# ============================================================

from datetime import date, timedelta
from utils.logger import log

class AnalyticsDB:
    def __init__(self, core_store):
        self.store = core_store

    @property
    def streaks(self):
        st = self.store.app_data.setdefault("streaks", {"current": 0, "longest": 0, "last_study_date": None})
        last = st.get("last_study_date")
        if last:
            try:
                last_date = date.fromisoformat(last)
                if (date.today() - last_date).days > 1:
                    st["current"] = 0
            except ValueError:
                pass
        return st

    @property
    def daily_logs(self):
        return self.store.app_data.setdefault("daily_logs", {})

    def record_study_today(self):
        today_str = date.today().isoformat()
        st = self.store.app_data.setdefault("streaks", {"current": 0, "longest": 0, "last_study_date": None})
        last = st.get("last_study_date")

        if last == today_str:
            return  # Already recorded today

        if last:
            try:
                last_date = date.fromisoformat(last)
                delta = (date.today() - last_date).days
                if delta == 1:
                    st["current"] += 1
                elif delta > 1:
                    st["current"] = 1
                elif delta < 0:
                    pass # time travel?
            except ValueError:
                st["current"] = 1
        else:
            st["current"] = 1

        st["longest"] = max(st.get("longest", 0), st["current"])
        st["last_study_date"] = today_str
        self.store.save_app_data()
        log.info(f"Streak updated: {st['current']}")

    def log_study(self, subject_id, minutes):
        today = date.today().isoformat()
        if today not in self.daily_logs:
            self.daily_logs[today] = {}
        
        self.daily_logs[today][subject_id] = self.daily_logs[today].get(subject_id, 0) + minutes
        self.record_study_today()
        self.store.save_app_data()
        log.info(f"Logged {minutes} mins for subject {subject_id}")

    def today_total_minutes(self):
        today = date.today().isoformat()
        day = self.daily_logs.get(today, {})
        return sum(day.values())

    def weekly_minutes(self):
        """Returns list of 7 daily totals (Mon→Sun of current week)."""
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        result = []
        for i in range(7):
            d = (week_start + timedelta(days=i)).isoformat()
            day_data = self.daily_logs.get(d, {})
            result.append(sum(day_data.values()))
        return result

    def get_most_delayed_subject(self, subjects_db):
        """Uses subjects_db to calculate which subject needs attention."""
        # This will be enhanced later, returning None for now.
        return None
