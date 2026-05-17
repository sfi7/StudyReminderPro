# ============================================================
# Study Reminder Pro - Theme Manager
# File: themes/theme_manager.py
# ============================================================

import customtkinter as ctk
from themes.colors import THEMES, DARK_PALETTE
from themes.typography import FONTS, get_font
from themes.tokens import CARD, RADIUS, SPACING

class ThemeManager:
    """Centralized Theme Engine providing colors, tokens, and reusable UI builders."""
    
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ThemeManager, cls).__new__(cls)
            cls._instance._current_mode = "dark"
            cls._instance._current_accent = None
            cls._instance.colors = THEMES["dark"].copy()
        return cls._instance

    def set_theme(self, mode_name, accent_hex=None):
        if mode_name in THEMES:
            self._current_mode = mode_name
            # Create a copy so we don't modify the base palette
            self.colors = THEMES[mode_name].copy()
            
            # Apply accent override if provided or if we have a saved one
            target_accent = accent_hex or self._current_accent
            if target_accent:
                self._apply_accent(target_accent)

            # Map glass to dark for the ctk appearance
            ctk_mode = "dark" if mode_name in ["dark", "glass"] else "light"
            ctk.set_appearance_mode(ctk_mode)
            
            return True
        return False

    def set_accent(self, hex_color):
        """Overrides the accent color in the current palette."""
        self._current_accent = hex_color
        self._apply_accent(hex_color)

    def _apply_accent(self, hex_color):
        self.colors["accent"] = hex_color
        # Generate a darker version for hover (simple darken)
        try:
            # Basic hover simulation: slightly darker or same for now
            # In a real app we might use a color manipulation lib
            self.colors["accent_hover"] = hex_color 
            self.colors["accent_light"] = hex_color # No alpha support in Tkinter
        except Exception:
            pass

    @property
    def current_mode(self):
        return self._current_mode

    # ---------- Reusable UI Helpers ----------
    
    def create_card(self, parent, **kwargs):
        """Creates a standard styled card frame."""
        return ctk.CTkFrame(
            parent,
            fg_color=self.colors["bg_card"],
            border_width=CARD["border_width"],
            border_color=self.colors["border"],
            corner_radius=CARD["corner_radius"],
            **kwargs
        )

    def create_label(self, parent, text, font_type="body", color_key="text_primary", **kwargs):
        """Creates a text label using theme typography and colors."""
        return ctk.CTkLabel(
            parent,
            text=text,
            font=FONTS.get(font_type, FONTS["body"]),
            text_color=self.colors.get(color_key, self.colors["text_primary"]),
            **kwargs
        )

    def create_button(self, parent, text, command, style="primary", **kwargs):
        """Creates a styled button (primary, secondary, danger, etc)."""
        fg_color = self.colors["accent"]
        hover_color = self.colors["accent_hover"]
        text_color = "#FFFFFF"

        if style == "secondary":
            fg_color = self.colors["bg_card"]
            hover_color = self.colors["border"]
            text_color = self.colors["text_primary"]
        elif style == "danger":
            fg_color = self.colors["danger"]
            hover_color = "#B91C1C" # Darker red

        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            fg_color=fg_color,
            hover_color=hover_color,
            text_color=text_color,
            font=FONTS["button"],
            corner_radius=RADIUS["medium"],
            **kwargs
        )
