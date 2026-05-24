# ============================================================
# Study Reminder Pro - Habits Database Service
# File: database/habits_db.py
# ============================================================

from datetime import datetime, date
from utils.logger import log

def default_habit(name="New Habit"):
    return {
        "id": datetime.now().strftime("habit_%Y%m%d%H%M%S%f"),
        "name": name,
        "created_at": datetime.now().isoformat(),
        "history": [] # list of date strings e.g., ["2026-05-20"]
    }

class HabitsDB:
    def __init__(self, core_store):
        self.store = core_store

    @property
    def habits(self):
        return self.store.app_data.setdefault("habits", [])

    def add_habit(self, name):
        h = default_habit(name)
        self.habits.append(h)
        self.store.save_app_data()
        log.info(f"Added daily habit: {name}")
        return h

    def delete_habit(self, habit_id):
        self.store.app_data["habits"] = [h for h in self.habits if h["id"] != habit_id]
        self.store.save_app_data()
        log.info(f"Deleted habit ID {habit_id}")

    def toggle_habit(self, habit_id, date_str=None):
        if not date_str:
            date_str = date.today().isoformat()
        for h in self.habits:
            if h["id"] == habit_id:
                history = h.setdefault("history", [])
                if date_str in history:
                    history.remove(date_str)
                    is_done = False
                else:
                    history.append(date_str)
                    is_done = True
                self.store.save_app_data()
                log.info(f"Toggled habit {h['name']} to {is_done}")
                return is_done
        return False

    def is_habit_done(self, habit_id, date_str=None):
        if not date_str:
            date_str = date.today().isoformat()
        for h in self.habits:
            if h["id"] == habit_id:
                return date_str in h.get("history", [])
        return False

    def get_habit_streak(self, habit):
        history = habit.get("history", [])
        if not history:
            return 0
            
        # Parse history dates and filter duplicates, sorting descending
        parsed_dates = []
        for d_str in set(history):
            try:
                parsed_dates.append(datetime.strptime(d_str, "%Y-%m-%d").date())
            except ValueError:
                pass
        
        parsed_dates = sorted(parsed_dates, reverse=True)
        if not parsed_dates:
            return 0
            
        today = date.today()
        # If the latest date in history is before yesterday, streak is broken
        diff_latest = (today - parsed_dates[0]).days
        if diff_latest > 1:
            return 0
            
        streak = 1
        for i in range(len(parsed_dates) - 1):
            diff = (parsed_dates[i] - parsed_dates[i+1]).days
            if diff == 1:
                streak += 1
            elif diff > 1:
                break
        return streak
