# ============================================================
# Study Reminder Pro - Legacy Theme Bridge
# File: core/theme.py
# ============================================================

# This file remains to provide backward compatibility to existing UI 
# code that expects to import from core.theme

from themes.colors import THEMES
from themes.typography import FONTS
from utils.constants import MOTIVATIONAL_QUOTES, STUDY_TIPS, SUBJECT_ICONS, SUBJECT_COLORS

# Exposed for old imports:
# from core.theme import THEMES, FONTS, MOTIVATIONAL_QUOTES, STUDY_TIPS, SUBJECT_ICONS, SUBJECT_COLORS
