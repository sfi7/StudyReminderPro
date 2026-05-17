# ============================================================
# Study Reminder Pro - Quotes Engine
# File: focus/quotes_engine.py
# ============================================================

import random
from utils.constants import MOTIVATIONAL_QUOTES, STUDY_TIPS

class QuotesEngine:
    def __init__(self):
        self._quotes = MOTIVATIONAL_QUOTES
        self._tips = STUDY_TIPS
        self._current_quote = ""

    def get_random_quote(self):
        self._current_quote = random.choice(self._quotes)
        return self._current_quote

    def get_random_tip(self):
        return random.choice(self._tips)

    def get_focus_message(self):
        # 80% chance of quote, 20% chance of tip
        if random.random() < 0.2:
            return "💡 " + self.get_random_tip()
        return "✨ " + self.get_random_quote()
