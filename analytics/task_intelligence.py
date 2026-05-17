# ============================================================
# Study Reminder Pro - Task Intelligence Engine
# File: analytics/task_intelligence.py
# ============================================================

from datetime import datetime, date
import threading
from utils.logger import log

class TaskIntelligence:
    """Non-blocking engine that calculates task urgency and sorts them."""
    
    def __init__(self, db):
        self.db = db
        self._cached_sorted_tasks = []
        self._lock = threading.Lock()
        
        # Priorities map to base scores
        self.priority_scores = {
            "Low": 10,
            "Medium": 30,
            "High": 60,
            "Critical": 90
        }

    def compute_urgency(self, task):
        """Calculates a 0-100+ urgency score for a task."""
        score = self.priority_scores.get(task.get("priority", "Medium"), 30)
        
        # Add points if pinned
        if task.get("is_pinned", False):
            score += 200 # Pins force it to the top
            
        # Subject Context
        sid = task.get("subject_id")
        if sid:
            s = self.db.get_subject(sid)
            if s:
                # Factor in subject difficulty (1-5 scale)
                score += s.get("difficulty", 3) * 5
                
                # Factor in exam proximity
                from subjects_db import SubjectsDB
                # Re-using the facade logic if possible, or just calculate here
                days = self.db.days_until_exam(s)
                if days is not None:
                    if days < 7: score += 50
                    elif days < 14: score += 20

        deadline = task.get("deadline")
        if deadline:
            try:
                dt = datetime.fromisoformat(deadline).date()
                days_left = (dt - date.today()).days
                
                if days_left < 0:
                    score += 100 # Overdue
                elif days_left == 0:
                    score += 80  # Due today
                elif days_left <= 2:
                    score += 40  # Due very soon
                elif days_left <= 7:
                    score += 15  # Due this week
            except:
                pass
                
        task["_urgency_score"] = score
        return score

    def _sort_tasks_worker(self, filter_type, callback):
        """Background worker that computes urgency and sorts tasks."""
        try:
            if filter_type == "Pending":
                tasks = self.db.get_pending_tasks()
            elif filter_type == "Completed":
                tasks = self.db.get_completed_tasks()
            else:
                tasks = self.db.tasks
                
            # Compute urgency for all
            for t in tasks:
                self.compute_urgency(t)
                
            # Sort: highest urgency first. If completed, just sort by completion date desc.
            if filter_type == "Completed":
                tasks.sort(key=lambda x: x.get("completed_at") or "", reverse=True)
            else:
                tasks.sort(key=lambda x: x.get("_urgency_score", 0), reverse=True)
                
            with self._lock:
                self._cached_sorted_tasks = tasks
                
            # Return result via callback to UI thread
            if callback:
                callback(tasks)
        except Exception as e:
            log.error(f"Task sorting failed: {e}")

    def get_sorted_tasks_async(self, filter_type, callback):
        """Spawns a background thread to sort tasks so UI doesn't block."""
        threading.Thread(target=self._sort_tasks_worker, args=(filter_type, callback), daemon=True).start()

    def get_cached_tasks(self):
        with self._lock:
            return list(self._cached_sorted_tasks)
