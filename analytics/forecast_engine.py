# ============================================================
# Study Reminder Pro - Forecast Engine
# File: analytics/forecast_engine.py
# ============================================================

from datetime import datetime, date, timedelta

class ForecastEngine:
    """
    Predictive analysis of syllabus completion based on historical pace.
    """
    def __init__(self, db_facade, analytics_engine):
        self.db = db_facade
        self.ae = analytics_engine

    def get_historical_pace(self):
        """Calculates average lectures completed per week."""
        # For a real implementation, we'd query logs.
        # Returning a placeholder based on assumed recent activity.
        return 3.0 # lectures per week

    def forecast_completion(self, subject):
        """
        Estimates when a subject will be completed based on pace.
        Returns projected completion date and confidence score.
        """
        rem_lectures = max(0, subject.get("total_lectures", 0) - subject.get("completed_lectures", 0))
        if rem_lectures == 0:
            return {"status": "Complete", "projected_date": date.today(), "confidence": 100}
            
        pace_per_week = self.get_historical_pace()
        if pace_per_week <= 0:
            return {"status": "No Pace", "projected_date": None, "confidence": 0}
            
        weeks_needed = rem_lectures / pace_per_week
        projected_date = date.today() + timedelta(weeks=weeks_needed)
        
        # Compare with exam date if it exists
        exam_date_str = subject.get("exam_date")
        risk_level = "Safe"
        
        if exam_date_str:
            try:
                exam_date = datetime.fromisoformat(exam_date_str).date()
                if projected_date > exam_date:
                    risk_level = "Overdue Risk"
            except:
                pass
                
        confidence = 85 # Could dynamically adjust based on variance in daily study
        
        return {
            "status": risk_level,
            "projected_date": projected_date,
            "confidence": confidence
        }
