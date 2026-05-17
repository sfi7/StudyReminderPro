
import sys
import os
import tkinter as tk
import customtkinter as ctk

# Mock FONTS and THEMES to avoid full imports if they fail
THEMES = {"dark": {"bg_primary": "#000", "text_primary": "#fff", "accent": "#777"}}
FONTS = {"title": ("Arial", 12)}

class SidebarButton(ctk.CTkFrame):
    def __init__(self, master, text, icon, command, active=False, colors=None):
        super().__init__(master, fg_color="transparent")
        print(f"Creating button for {text} {icon}")
        self.lbl = ctk.CTkLabel(self, text=f"{icon} {text}")
        self.lbl.pack()

NAV_ITEMS = [
    ("dashboard",  "🏠", "Dashboard"),
    ("tasks",      "📝", "Tasks"),
    ("subjects",   "📚", "Subjects"),
    ("pomodoro",   "🍅", "Pomodoro"),
    ("analytics",  "📊", "Analytics"),
    ("settings",   "⚙️", "Settings"),
]

root = ctk.CTk()
sb = ctk.CTkFrame(root)
sb.pack()

for key, icon, label in NAV_ITEMS:
    try:
        btn = SidebarButton(sb, label, icon, lambda k=key: print(k))
        btn.pack()
        print(f"Success: {key}")
    except Exception as e:
        print(f"FAILED: {key} - {e}")

root.update()
print("Test complete")
root.destroy()
