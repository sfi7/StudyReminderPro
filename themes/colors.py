# ============================================================
# Study Reminder Pro - Theme Colors
# File: themes/colors.py
# ============================================================

# Base Color Palettes
DARK_PALETTE = {
    "bg_primary": "#0D0F1A",
    "bg_secondary": "#151828",
    "bg_sidebar": "#0A0B14",
    "bg_card": "#1C2033",
    "border": "#2A2E45",
    "text_primary": "#F0F1FF",
    "text_secondary": "#8B8FA8",
    "text_muted": "#5B5F7A",
    "accent": "#7C6EFA",
    "accent_hover": "#6455E0",
    "accent_light": "#B4ACFF",
    "success": "#10B981",
    "warning": "#F59E0B",
    "danger": "#EF4444",
    "info": "#3B82F6",
    "progress_bg": "#23273D",
    "tag_high": "#FF3B30",
    "tag_high_text": "#FFFFFF",
    "tag_medium": "#FFCC00",
    "tag_medium_text": "#000000",
    "tag_low": "#34C759",
    "tag_low_text": "#FFFFFF",
    "sidebar_active": "#1C2033",
    "hover_overlay": "#151828",
}

LIGHT_PALETTE = {
    "bg_primary": "#F8F9FB",
    "bg_secondary": "#FFFFFF",
    "bg_sidebar": "#F0F2F5",
    "bg_card": "#FFFFFF",
    "border": "#E2E8F0",
    "text_primary": "#1E293B",
    "text_secondary": "#475569",
    "text_muted": "#94A3B8",
    "accent": "#6C63FF",
    "accent_hover": "#5A52D5",
    "accent_light": "#E0E7FF",
    "success": "#10B981",
    "warning": "#F59E0B",
    "danger": "#EF4444",
    "info": "#3B82F6",
    "progress_bg": "#E2E8F0",
    "tag_high": "#FEE2E2",
    "tag_high_text": "#991B1B",
    "tag_medium": "#FEF3C7",
    "tag_medium_text": "#92400E",
    "tag_low": "#DCFCE7",
    "tag_low_text": "#166534",
    "sidebar_active": "#E2E8F0",
    "hover_overlay": "#E2E8F0",
}

GLASSMORPHISM_PALETTE = {
    "bg_primary": "#101828",     # Deep muted blue/grey
    "bg_secondary": "#1D2939",   # Slightly lighter
    "bg_sidebar": "#101828",
    "bg_card": "#1D2939",        # Base card, we rely on opacity in tokens
    "border": "#344054",         # Frosty border
    "text_primary": "#F9FAFB",
    "text_secondary": "#98A2B3",
    "text_muted": "#667085",
    "accent": "#53389E",
    "accent_hover": "#6941C6",
    "accent_light": "#D6BBFB",
    "success": "#027A48",
    "warning": "#B54708",
    "danger": "#B42318",
    "info": "#026AA2",
    "progress_bg": "#344054",
    "tag_high": "#B42318",
    "tag_high_text": "#FEF3F2",
    "tag_medium": "#B54708",
    "tag_medium_text": "#FFFAEB",
    "tag_low": "#027A48",
    "tag_low_text": "#ECFDF3",
    "sidebar_active": "#1D2939",
    "hover_overlay": "#1D2939",
}

ACCENT_PRESETS = {
    "Deep Purple": "#7C6EFA",
    "Royal Blue":  "#3B82F6",
    "Emerald":     "#10B981",
    "Sunset":      "#F59E0B",
    "Crimson":     "#EF4444",
    "Orchid":      "#D946EF",
}

THEMES = {
    "dark": DARK_PALETTE,
    "light": LIGHT_PALETTE,
    "glass": GLASSMORPHISM_PALETTE
}
