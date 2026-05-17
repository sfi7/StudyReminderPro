# ============================================================
# Study Reminder Pro - Roadmap Engine
# File: analytics/roadmap_engine.py
# ============================================================

from datetime import date, datetime
from utils.logger import log

class RoadmapEngine:
    """Calculates dynamic targets to ensure syllabus completion before exams."""
    def __init__(self, db_facade):
        self.db = db_facade

    def get_subject_roadmap(self, subject):
        """Calculates daily target and status for a specific subject."""
        total = subject.get("total_lectures", 0)
        done = subject.get("completed_lectures", 0)
        remaining = max(0, total - done)
        
        exam_date_str = subject.get("exam_date")
        if not exam_date_str or remaining == 0:
            return None
            
        try:
            exam_dt = date.fromisoformat(exam_date_str)
            today = date.today()
            days_left = (exam_dt - today).days
            
            if days_left <= 0:
                return {
                    "status": "CRITICAL",
                    "daily_target": remaining,
                    "message": "Exam is here! Finish all now.",
                    "remaining": remaining
                }
            
            # Recalculate daily target
            daily_target = remaining / days_left
            
            status = "On Track"
            color = "success"
            if daily_target > 3:
                status = "HEAVY"
                color = "warning"
            if daily_target > 5:
                status = "CRITICAL"
                color = "danger"
                
            return {
                "status": status,
                "color": color,
                "daily_target": round(daily_target, 2),
                "days_left": days_left,
                "remaining": remaining,
                "message": f"Finish {round(daily_target, 1)} lectures daily."
            }
        except:
            return None

    def get_full_roadmap(self):
        """Returns roadmap for all subjects with upcoming exams."""
        roadmap = []
        for s in self.db.subjects:
            res = self.get_subject_roadmap(s)
            if res:
                res["subject_name"] = s["name"]
                res["subject_id"] = s["id"]
                roadmap.append(res)
        
        # Sort by urgency (highest daily target first)
        roadmap.sort(key=lambda x: x["daily_target"], reverse=True)
        return roadmap
