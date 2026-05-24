# ============================================================
# Study Reminder Pro - Skills Database Service
# File: database/skills_db.py
# ============================================================

from datetime import datetime
from utils.logger import log

def default_skill(name="New Skill"):
    return {
        "id": datetime.now().strftime("skill_%Y%m%d%H%M%S%f"),
        "name": name,
        "total_modules": 10,
        "completed_modules": 0,
        "target_date": None,
        "difficulty": "Medium", # Easy, Medium, Hard
        "color": "#6C63FF",
        "created_at": datetime.now().isoformat()
    }

class SkillsDB:
    def __init__(self, core_store):
        self.store = core_store

    @property
    def skills(self):
        return self.store.app_data.setdefault("skills", [])

    def add_skill(self, skill_dict=None):
        s = default_skill()
        if skill_dict:
            s.update(skill_dict)
        self.skills.append(s)
        self.store.save_app_data()
        log.info(f"Added skill/course: {s['name']}")
        return s

    def update_skill(self, skill_id, **kwargs):
        for s in self.skills:
            if s["id"] == skill_id:
                s.update(kwargs)
                self.store.save_app_data()
                log.info(f"Updated skill ID {skill_id}")
                return s
        return None

    def delete_skill(self, skill_id):
        self.store.app_data["skills"] = [s for s in self.skills if s["id"] != skill_id]
        self.store.save_app_data()
        log.info(f"Deleted skill ID {skill_id}")

    def get_skill(self, skill_id):
        for s in self.skills:
            if s["id"] == skill_id:
                return s
        return None

    def remaining_modules(self, skill):
        return max(0, skill.get("total_modules", 0) - skill.get("completed_modules", 0))

    def progress_pct(self, skill):
        total = skill.get("total_modules", 0)
        if total <= 0:
            return 100
        return int((skill.get("completed_modules", 0) / total) * 100)
