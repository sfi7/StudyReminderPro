# ============================================================
# Study Reminder Pro - Tasks Database Service
# File: database/tasks_db.py
# ============================================================

from datetime import datetime
from utils.logger import log

def default_task(title="New Task"):
    return {
        "id": datetime.now().strftime("task_%Y%m%d%H%M%S%f"),
        "title": title,
        "description": "",
        "priority": "Medium", # Low, Medium, High, Critical
        "category": "General",
        "deadline": None,
        "completed": False,
        "created_at": datetime.now().isoformat(),
        "completed_at": None,
        "is_pinned": False,
        "recurrence": None # None, "Daily", "Weekly"
    }

class TasksDB:
    def __init__(self, core_store):
        self.store = core_store

    @property
    def tasks(self):
        return self.store.app_data.setdefault("tasks", [])

    def add_task(self, title, **kwargs):
        task = default_task(title)
        task.update(kwargs)
        self.tasks.append(task)
        self.store.save_app_data()
        log.info(f"Added task: {title}")
        return task

    def update_task(self, task_id, **kwargs):
        for t in self.tasks:
            if t["id"] == task_id:
                t.update(kwargs)
                self.store.save_app_data()
                return t
        return None

    def toggle_task(self, task_id):
        for t in self.tasks:
            if t["id"] == task_id:
                t["completed"] = not t["completed"]
                t["completed_at"] = datetime.now().isoformat() if t["completed"] else None
                
                # Auto-regeneration for recurring tasks
                if t["completed"] and t.get("recurrence"):
                    self._regenerate_recurring_task(t)
                    
                self.store.save_app_data()
                return t["completed"]
        return False

    def _regenerate_recurring_task(self, completed_task):
        """Creates a fresh duplicate of a recurring task."""
        new_task = default_task(completed_task["title"])
        new_task.update({
            "priority": completed_task.get("priority", "Medium"),
            "category": completed_task.get("category", "General"),
            "is_pinned": completed_task.get("is_pinned", False),
            "recurrence": completed_task.get("recurrence")
        })
        
        # We might want to calculate the new deadline here in the future
        # e.g., if Daily, deadline = today + 1 day
        
        self.tasks.append(new_task)
        log.info(f"Auto-regenerated recurring task: {new_task['title']}")

    def delete_task(self, task_id):
        initial_len = len(self.tasks)
        self.store.app_data["tasks"] = [t for t in self.tasks if t["id"] != task_id]
        if len(self.tasks) < initial_len:
            self.store.save_app_data()
            log.info(f"Deleted task ID: {task_id}")

    def get_pending_tasks(self):
        return [t for t in self.tasks if not t.get("completed", False)]

    def get_completed_tasks(self):
        return [t for t in self.tasks if t.get("completed", False)]
