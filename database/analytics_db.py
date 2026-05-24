# ============================================================
# Study Reminder Pro - Analytics Database Service
# File: database/analytics_db.py
# ============================================================

from datetime import date, timedelta
from utils.logger import log

class AnalyticsDB:
    def __init__(self, core_store):
        self.store = core_store

    def calculate_streaks(self):
        """Dynamically calculates the current and longest study streaks from daily logs."""
        logs = self.daily_logs
        study_dates = []
        for d_str, subjects in logs.items():
            if sum(subjects.values()) > 0:
                try:
                    study_dates.append(date.fromisoformat(d_str))
                except ValueError:
                    pass
                    
        st = self.store.app_data.setdefault("streaks", {"current": 0, "longest": 0, "last_study_date": None})
        
        if not study_dates:
            st["current"] = 0
            st["last_study_date"] = None
            return st
            
        study_dates = sorted(study_dates, reverse=True)
        today = date.today()
        
        # Current streak
        diff_latest = (today - study_dates[0]).days
        if diff_latest > 1:
            st["current"] = 0
        else:
            st["current"] = 1
            for i in range(len(study_dates) - 1):
                if (study_dates[i] - study_dates[i+1]).days == 1:
                    st["current"] += 1
                else:
                    break
                    
        # Longest streak
        study_dates_asc = sorted(study_dates)
        longest = 0
        temp_streak = 0
        prev_date = None
        for d in study_dates_asc:
            if prev_date is None:
                temp_streak = 1
            else:
                diff = (d - prev_date).days
                if diff == 1:
                    temp_streak += 1
                elif diff > 1:
                    longest = max(longest, temp_streak)
                    temp_streak = 1
            prev_date = d
        longest = max(longest, temp_streak)
        
        st["longest"] = max(st.get("longest", 0), longest)
        st["last_study_date"] = study_dates[0].isoformat()
        return st

    @property
    def streaks(self):
        st = self.calculate_streaks()
        # Save only if anything changed to avoid infinite save loops
        stored = self.store.app_data.get("streaks", {})
        if (stored.get("current") != st["current"] or 
            stored.get("longest") != st["longest"] or 
            stored.get("last_study_date") != st["last_study_date"]):
            self.store.app_data["streaks"] = st
            self.store.save_app_data()
        return st

    @property
    def daily_logs(self):
        return self.store.app_data.setdefault("daily_logs", {})

    def record_study_today(self):
        st = self.calculate_streaks()
        self.store.app_data["streaks"] = st
        self.store.save_app_data()
        log.info(f"Streak dynamically updated: {st['current']}")

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
