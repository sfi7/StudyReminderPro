# ============================================================
# Study Reminder Pro - Goals Engine
# File: analytics/goals_engine.py
# ============================================================

import time
from datetime import datetime, timedelta
from utils.logger import log

class GoalsEngine:
    """
    Intelligent engine for tracking targets, streaks, and detecting burnout.
    """
    def __init__(self, db_facade):
        self.db = db_facade

    def get_daily_goals_status(self):
        """Returns today's lecture and hour targets vs actual."""
        settings = self.db.settings
        target_mins = settings.get("daily_goal_minutes", 120)
        target_lectures = settings.get("daily_goal_lectures", 2)
        
        today_mins = self.db.today_total_minutes()
        # Assumes a method in subjects to count today's completed lectures
        today_lectures = 0 # Placeholder for actual logic
        
        return {
            "target_mins": target_mins,
            "actual_mins": today_mins,
            "target_lectures": target_lectures,
            "actual_lectures": today_lectures,
            "completion_pct": min(100, int((today_mins / target_mins) * 100)) if target_mins else 100
        }

    def analyze_burnout_risk(self, analytics_engine):
        """
        Uses heuristics to detect if the user is studying too intensely
        without adequate breaks or quality focus.
        Returns (risk_percentage, severity_label, suggestion)
        """
        sessions = analytics_engine.get_all_sessions()
        if not sessions:
            return 0, "Low", "Keep up the good pace."
            
        recent_cutoff = datetime.now() - timedelta(days=7)
        recent_sessions = []
        for s in sessions:
            try:
                ts = s.get("start_time", s.get("timestamp"))
                if not ts: continue
                dt = datetime.fromisoformat(ts)
                if dt >= recent_cutoff:
                    recent_sessions.append(s)
            except:
                pass
                
        if not recent_sessions:
            return 0, "Low", "No recent activity."
            
        total_recent_mins = sum(s.get("duration_minutes", s.get("duration_min", 0)) for s in recent_sessions)
        avg_daily_mins = total_recent_mins / 7
        
        # Calculate interruption frequency
        total_interrupts = sum(s.get("interruptions", 0) for s in recent_sessions)
        interrupt_rate = total_interrupts / len(recent_sessions) if recent_sessions else 0
        
        risk = 0
        if avg_daily_mins > 300: # 5 hours/day
            risk += 40
        if interrupt_rate > 3: # Highly interrupted sessions
            risk += 30
            
        abandoned = sum(1 for s in recent_sessions if not s.get("completed", True))
        if abandoned > 3:
            risk += 30
            
        risk = min(100, risk)
        
        if total_recent_mins < 60:
            return 0, "Low", "You have studied very little over the past week. Try setting a small 25-minute Pomodoro goal today to build momentum!"
        elif risk > 70:
            return risk, "Critical", "Burnout risk is high! You are studying long hours with many interruptions and abandoned sessions. Take a mandatory recovery day and reduce your targets to protect your focus."
        elif risk > 40:
            return risk, "Moderate", "You're pushing hard, but your interruption rate is creeping up. Consider taking longer breaks and minimizing distractions to study smarter, not harder."
        return risk, "Low", f"Your pace is highly sustainable ({int(avg_daily_mins)} mins/day). You maintain an excellent balance of focus and session completion. Keep up the great work!"
