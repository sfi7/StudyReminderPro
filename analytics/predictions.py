# ============================================================
# Study Reminder Pro - Predictions Engine
# File: analytics/predictions.py
# ============================================================

from datetime import datetime, date

class PredictionsEngine:
    """
    Intelligent urgency analysis and predictive completion estimations.
    """
    def __init__(self, db_facade):
        self.db = db_facade

    def analyze_exam_pressure(self, subject):
        """
        Evaluates urgency based on remaining lectures and days left.
        Returns a dictionary with status, color, and recommendation.
        """
        rem_lectures = max(0, subject.get("total_lectures", 0) - subject.get("completed_lectures", 0))
        exam_date_str = subject.get("exam_date")
        
        if rem_lectures == 0:
            return {
                "status": "Completed",
                "color": "success",
                "message": "Syllabus complete. Focus on revision and active recall.",
                "daily_required": 0
            }
            
        if not exam_date_str:
            return {
                "status": "No Exam Date",
                "color": "info",
                "message": f"You have {rem_lectures} lectures left to complete.",
                "daily_required": 0
            }
            
        try:
            exam_date = datetime.fromisoformat(exam_date_str).date()
            today = date.today()
            days_left = (exam_date - today).days
        except Exception:
            return {
                "status": "Invalid Date",
                "color": "warning",
                "message": "Update exam date format.",
                "daily_required": 0
            }

        if days_left < 0:
            return {
                "status": "Exam Passed",
                "color": "text_muted",
                "message": "The exam date has passed.",
                "daily_required": 0
            }
            
        if days_left == 0:
            return {
                "status": "Exam Today",
                "color": "danger",
                "message": "The exam is today! Good luck!",
                "daily_required": rem_lectures
            }
            
        daily_req = round(rem_lectures / days_left, 1)
        
        if daily_req > 4:
            status = "Critical Urgency"
            color = "danger"
            msg = f"Behind schedule. You need to complete {daily_req} lectures per day."
        elif daily_req > 2:
            status = "Moderate Pressure"
            color = "warning"
            msg = f"Keep up the pace. You need {daily_req} lectures per day."
        else:
            status = "On Track"
            color = "success"
            msg = f"Comfortable pace. Only {daily_req} lectures needed daily."
            
        return {
            "status": status,
            "color": color,
            "message": msg,
            "daily_required": daily_req,
            "days_left": days_left
        }

    def predict_completion_date(self, subject, analytics_engine):
        """Predicts the date of syllabus completion based on recent velocity."""
        rem_lectures = max(0, subject.get("total_lectures", 0) - subject.get("completed_lectures", 0))
        if rem_lectures == 0:
            return "Completed"
            
        # Calculate velocity (lectures per day over last 7 days)
        # This is a bit complex as we don't have a 'lectures_completed_per_day' log yet.
        # We'll estimate based on 'minutes per lecture' average for this subject.
        
        dist = analytics_engine.get_subject_distribution()
        subject_mins = dist.get(subject["id"], 0)
        done_lectures = subject.get("completed_lectures", 0)
        
        if done_lectures == 0:
            # Fallback: assume 60 mins per lecture
            mins_per_lecture = 60
        else:
            mins_per_lecture = max(15, subject_mins / done_lectures)
            
        # Get recent daily study minutes for this subject
        daily_activity = analytics_engine.get_daily_activity(7)
        # Simplified: total minutes in last 7 days / 7
        recent_total = sum(daily_activity.values())
        avg_mins_per_day = recent_total / 7 if recent_total > 0 else 0
        
        if avg_mins_per_day == 0:
            return "Stalled"
            
        lectures_per_day = avg_mins_per_day / mins_per_lecture
        days_needed = rem_lectures / lectures_per_day
        
        from datetime import timedelta
        predicted_date = date.today() + timedelta(days=int(days_needed))
        return predicted_date.strftime("%b %d, %Y")
