# ============================================================
# Study Reminder Pro - Typography
# File: themes/typography.py
# ============================================================

# Use Segoe UI on Windows for a clean modern look, fallback to Arial.
MAIN_FONT = "Segoe UI"
MONO_FONT = "Consolas"

FONTS = {
    "heading": (MAIN_FONT, 28, "bold"),
    "subheading": (MAIN_FONT, 18, "bold"),
    "title": (MAIN_FONT, 15, "bold"),
    "body": (MAIN_FONT, 13),
    "small": (MAIN_FONT, 11),
    "tiny": (MAIN_FONT, 10),
    "button": (MAIN_FONT, 13, "bold"),
    "timer": (MAIN_FONT, 64, "bold"),
    "timer_small": (MAIN_FONT, 24, "bold")
}

def get_font(key, **kwargs):
    """
    Returns a configured font tuple.
    Allows overriding size or weight via kwargs.
    """
    if key not in FONTS:
        return FONTS["body"]
        
    base_font = list(FONTS[key])
    
    if "size" in kwargs:
        base_font[1] = kwargs["size"]
    if "weight" in kwargs:
        if len(base_font) > 2:
            base_font[2] = kwargs["weight"]
        else:
            base_font.append(kwargs["weight"])
            
    return tuple(base_font)
