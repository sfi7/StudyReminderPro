# ============================================================
# Study Reminder Pro - Gamification Engine
# File: analytics/gamification_engine.py
# ============================================================

from utils.logger import log
from datetime import date

class GamificationEngine:
    """Handles XP, Levels, and Badges to turn study into a game."""
    
    XP_PER_FOCUS_MIN = 10
    XP_PER_TASK = 50
    BASE_XP_NEXT_LEVEL = 1000
    
    def __init__(self, db_facade):
        self.db = db_facade
        self.data = self.db._store.app_data.setdefault("gamification", {
            "level": 1,
            "xp": 0,
            "total_focus_mins": 0,
            "badges": []
        })

    def add_xp(self, amount, reason="Study Session"):
        """Adds XP and handles leveling up."""
        old_level = self.data.get("level", 1)
        current_xp = self.data.get("xp", 0)
        
        new_xp = current_xp + amount
        self.data["xp"] = new_xp
        
        log.info(f"Earned {amount} XP from {reason}! Total: {new_xp}")
        
        # Level up logic (linear for now, can be exponential)
        xp_needed = self.get_xp_for_next_level()
        leveled_up = False
        
        while self.data["xp"] >= xp_needed:
            self.data["level"] += 1
            self.data["xp"] -= xp_needed
            xp_needed = self.get_xp_for_next_level()
            leveled_up = True
            
        if leveled_up:
            log.info(f"LEVEL UP! New Level: {self.data['level']}")
            
        self.db._store.save_app_data()
        return leveled_up, self.data["level"]

    def get_xp_for_next_level(self):
        """Calculates XP needed for current level -> next level."""
        lvl = self.data.get("level", 1)
        # Higher levels require more XP: 1000, 1200, 1440, etc. (20% increase)
        return int(self.BASE_XP_NEXT_LEVEL * (1.2 ** (lvl - 1)))

    def get_progress_pct(self):
        """Returns percentage of XP towards next level."""
        xp = self.data.get("xp", 0)
        needed = self.get_xp_for_next_level()
        return (xp / needed) * 100 if needed > 0 else 0

    def get_rank_title(self):
        """Returns a title based on level."""
        lvl = self.data.get("level", 1)
        if lvl < 5: return "Novice Scholar"
        if lvl < 10: return "Dedicated Learner"
        if lvl < 20: return "Study Monk"
        if lvl < 50: return "Knowledge Sage"
        return "Productivity Master"

    def record_focus(self, mins):
        """Convenience method for focus sessions."""
        self.data["total_focus_mins"] = self.data.get("total_focus_mins", 0) + mins
        return self.add_xp(mins * self.XP_PER_FOCUS_MIN, "Focus Session")
