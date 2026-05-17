# ============================================================
# Study Reminder Pro - Analytics Engine
# File: analytics/analytics_engine.py
# ============================================================

from datetime import datetime, timedelta

class AnalyticsEngine:
    """
    Core data aggregation engine.
    Fetches and filters raw data from databases to feed the productivity and chart engines.
    """
    def __init__(self, db_facade):
        self.db = db_facade

    def get_all_sessions(self):
        # Merge new detailed sessions and legacy pomodoro sessions
        new_sess = self.db._sessions_db.sessions
        legacy_sess = self.db._sessions_db.pomodoro_sessions
        return new_sess + legacy_sess

    def get_sessions_by_date_range(self, start_date, end_date):
        sessions = self.get_all_sessions()
        # Filter logic here
        filtered = []
        for s in sessions:
            try:
                s_date = datetime.fromisoformat(s.get("start_time")).date()
                if start_date <= s_date <= end_date:
                    filtered.append(s)
            except Exception:
                continue
        return filtered

    def get_total_study_minutes(self):
        sessions = self.get_all_sessions()
        return sum(s.get("duration_min", s.get("duration_minutes", s.get("minutes", 0))) for s in sessions)

    def get_subject_distribution(self):
        dist = {}
        for s in self.get_all_sessions():
            sid = s.get("subject_id")
            mins = s.get("duration_min", s.get("duration_minutes", s.get("minutes", 0)))
            dist[sid] = dist.get(sid, 0) + mins
        return dist

    def get_daily_activity(self, days=30):
        """Returns a dict of date strings mapping to total minutes studied."""
        activity = {}
        cutoff = datetime.now().date() - timedelta(days=days)
        
        for s in self.get_all_sessions():
            try:
                # Support both 'start_time' and 'timestamp'
                ts = s.get("start_time", s.get("timestamp"))
                if not ts: continue
                dt = datetime.fromisoformat(ts)
                if dt.date() >= cutoff:
                    date_str = dt.strftime("%Y-%m-%d")
                    mins = s.get("duration_min", s.get("duration_minutes", 0))
                    # Handle legacy 'minutes' key too
                    if not mins: mins = s.get("minutes", 0)
                    
                    activity[date_str] = activity.get(date_str, 0) + mins
            except:
                pass
        return activity
