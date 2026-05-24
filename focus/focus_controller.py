# ============================================================
# Study Reminder Pro - Focus Controller
# File: focus/focus_controller.py
# ============================================================

import customtkinter as ctk
from focus.session_engine import SessionEngine
from focus.sound_manager import SoundManager
from focus.quotes_engine import QuotesEngine
from focus.focus_ui import FocusUI
from focus.floating_overlay import FloatingOverlay
from utils.logger import log

class FocusController:
    """
    Central controller for the Focus Subsystem.
    Manages the session engine, UI, sounds, and floating overlay.
    """
    def __init__(self, main_app):
        self.app = main_app
        self.db = main_app.db
        
        self.session_engine = SessionEngine(self.db._sessions_db)
        self.sound_manager = SoundManager(self.app.settings)
        self.quotes_engine = QuotesEngine()
        
        self.ui = None
        self.overlay = None
        self._update_job = None
        self._is_minimized = False
        
        # Check for crash recovery automatically after a short delay
        self.app.after(2000, self.check_for_recovery)

    def check_for_recovery(self):
        """Checks if a session crashed and prompts the user to restore."""
        snapshot = self.session_engine.recovery.detect_unfinished_session()
        if snapshot:
            # We could show a custom dialog here. For now, we restore directly or just log it.
            log.info(f"Unfinished session detected from {snapshot.get('started_at')}. Prompting user...")
            
            # Simplified restoration flow:
            from tkinter import messagebox
            if messagebox.askyesno("Session Recovery", "An interrupted focus session was found. Do you want to restore it?"):
                self.restore_focus_session(snapshot)
            else:
                self.session_engine.recovery.clear_snapshot()
                
    def restore_focus_session(self, snapshot):
        """Restores a session from a snapshot."""
        if self.session_engine.is_running:
            return
            
        self.session_engine.session_id = snapshot["session_id"]
        self.session_engine.subject_id = snapshot["subject_id"]
        self.session_engine.target_duration_min = snapshot["target_duration_min"]
        self.session_engine.remaining_seconds = snapshot["remaining_seconds"]
        self.session_engine.started_at = snapshot["started_at"]
        self.session_engine.interruptions = snapshot.get("interruptions", 0)
        self.session_engine.mode = snapshot.get("mode", "Work")
        self.session_engine.is_break = (self.session_engine.mode != "Work")
        self.session_engine.is_running = True
        self.session_engine.is_paused = True # Start paused for safety
        
        subj = self.db.get_subject(self.session_engine.subject_id)
        if not subj:
            # Fallback for skill or custom modes
            if hasattr(self.db, "get_skill"):
                subj = self.db.get_skill(self.session_engine.subject_id)
            if not subj:
                subj = {"name": "General Focus", "icon": "🎯", "color": self.app.theme_manager.colors["accent"]}
        
        self.ui = FocusUI(self, self.app.theme_manager)
        self.ui.setup_ui(subj, self.session_engine.target_duration_min, self.session_engine.mode)
        self.ui.show_fullscreen()
        
        self.ui.set_paused_state(True)
        self.ui.update_timer_display(self.session_engine.get_remaining_time())
        self._update_loop()

    def start_focus(self, subject_id, duration_minutes, mode="Work"):
        """Initializes and launches the fullscreen focus mode."""
        if self.session_engine.is_running:
            log.warning("Attempted to start focus mode while already running.")
            return

        self.session_engine.mode = mode
        self.session_engine.is_break = (mode != "Work")
        self.session_engine.start_session(subject_id, duration_minutes)
        
        subj = self.db.get_subject(subject_id)
        if not subj:
            # Fallback for skill or custom modes
            if hasattr(self.db, "get_skill"):
                subj = self.db.get_skill(subject_id)
            if not subj:
                subj = {"name": "General Focus", "icon": "🎯", "color": self.app.theme_manager.colors["accent"]}
        
        # Create UI
        self.ui = FocusUI(self, self.app.theme_manager)
        self.ui.setup_ui(subj, duration_minutes, mode)
        self.ui.show_fullscreen()
        
        # Start sound
        # Optional: map subject or settings to a specific ambient sound
        self.sound_manager.play_session_start()
        # self.sound_manager.play_ambient("assets/sounds/rain.mp3")
        
        # Start update loop
        self._update_loop()

    def pause_resume(self):
        if self.session_engine.is_paused:
            self.session_engine.resume_session()
            is_paused = False
        else:
            self.session_engine.pause_session()
            is_paused = True
            
        if self.ui and self.ui.winfo_exists():
            self.ui.set_paused_state(is_paused)
            self.ui.update_timer_display(self.session_engine.get_remaining_time())
        if self.overlay and self.overlay.winfo_exists():
            self.overlay.set_paused_state(is_paused)
            self.overlay.update_timer_display(self.session_engine.get_remaining_time())

    def minimize_focus(self):
        """Hides main UI, shows floating overlay."""
        if self.ui and self.ui.winfo_exists():
            self.ui.withdraw()
        self._is_minimized = True
        total = self.session_engine.target_duration_min * 60
        if not self.overlay:
            self.overlay = FloatingOverlay(self, self.app.theme_manager)
        # Sync mode badge + colour
        mode   = getattr(self.session_engine, "mode", "Work")
        accent = self.app.theme_manager.colors["accent"]
        if mode == "Work":
            accent = self.app.theme_manager.colors["accent"]
        elif "Break" in mode:
            accent = self.app.theme_manager.colors.get("success", "#10B981")
        else:
            accent = self.app.theme_manager.colors.get("warning", "#F59E0B")
        self.overlay.set_mode(mode, accent)
        self.overlay.update_timer_display(
            self.session_engine.get_remaining_time(), total_sec=total)
        self.overlay.set_paused_state(self.session_engine.is_paused)
        self.overlay.deiconify()

    def restore_focus(self):
        """Hides floating overlay, restores main UI."""
        if self.overlay and self.overlay.winfo_exists():
            self.overlay.withdraw()
        self._is_minimized = False
        if self.ui and self.ui.winfo_exists():
            self.ui.deiconify()
            self.ui.show_fullscreen()

    def toggle_mute(self):
        is_muted = self.sound_manager.toggle_mute()
        if self.ui and self.ui.winfo_exists():
            self.ui.set_mute_state(is_muted)

    def complete_session(self, forced=False):
        """Ends the session and cleans up."""
        if self._update_job:
            self.app.after_cancel(self._update_job)
            self._update_job = None
            
        record = self.session_engine.complete_session(forced_end=forced)
        self.sound_manager.stop_ambient()
        if not forced:
            self.sound_manager.play_session_complete()
        self.sound_manager.play_chime()
        
        if not forced:
            actual_duration = record.get("duration_min", 0)
            if actual_duration > 0:
                self.db.log_study(record.get("subject_id"), actual_duration)
                
            # Gamification
            from analytics.gamification_engine import GamificationEngine
            ge = GamificationEngine(self.db)
            leveled_up, new_lvl = ge.record_focus(actual_duration)
            if leveled_up:
                self.app.toast(f"🎉 LEVEL UP! You are now Level {new_lvl}!", "success")
                
            if hasattr(self.app, 'notifier'):
                self.app.notifier.show(
                    title="Session Complete! 🍅",
                    message="Great focus! Time for a well-deserved break.",
                    notif_id="pomodoro_finished"
                )
        
        if self.ui:
            self.ui.destroy()
            self.ui = None
            
        if self.overlay:
            self.overlay.destroy()
            self.overlay = None

        if not forced:
            self.sound_manager.play_alarm() # Loud repeating alarm
            from ui.widgets import SummaryDialog
            SummaryDialog(self.app, record, self.app.theme_manager.colors, 
                          on_close=lambda: [self.sound_manager.stop_alarm(), self.app.navigate("dashboard")])
        else:
            # Refresh main app
            if hasattr(self.app, "navigate"):
                self.app.navigate("dashboard")

    def exit_focus(self):
        """User aborted the session."""
        # Could show a confirmation dialog here
        self.complete_session(forced=True)
        self.app.toast("Focus session aborted.", "warning")

    def _update_loop(self):
        """High-frequency update loop without blocking."""
        if not self.session_engine.is_running:
            self._update_job = None
            return

        rem_sec = self.session_engine.get_remaining_time()
        
        # Update Main UI
        if self.ui and self.ui.winfo_exists() and not self._is_minimized:
            self.ui.update_timer_display(rem_sec)
        
        # Update Overlay
        if self.overlay and self.overlay.winfo_exists() and self._is_minimized:
            total = self.session_engine.target_duration_min * 60
            self.overlay.update_timer_display(rem_sec, total_sec=total)

        if rem_sec <= 0:
            self.complete_session(forced=False)
            self.app.toast("Focus session completed! Great job!", "success")
            return

        # Always use the main app for scheduling to prevent loop death during window transitions
        self._update_job = self.app.after(100, self._update_loop)

    # ── Mini Panel Integration ──
    def get_state(self):
        """Returns current session status for the widget."""
        if not self.session_engine.is_running:
            return {"is_running": False}
        
        rem = self.session_engine.get_remaining_time()
        mins, secs = divmod(rem, 60)
        return {
            "is_running": True,
            "is_paused": self.session_engine.is_paused,
            "time_left": f"{mins:02d}:{secs:02d}",
            "mode": "BREAK" if hasattr(self.session_engine, 'is_break') and self.session_engine.is_break else "FOCUS"
        }

    def toggle_session(self):
        """External trigger for start/pause/resume."""
        if self.session_engine.is_running:
            self.pause_resume()
        else:
            # If not running, start a default 25min Pomodoro with first subject or "General"
            subjects = self.db.subjects
            sid = subjects[0]["id"] if subjects else "general"
            self.start_focus(sid, 25)

    # ── Keyboard Shortcuts ──
    def handle_keypress(self, event):
        key = event.keysym.lower()
        if key == "space":
            self.pause_resume()
        elif key == "escape" or key == "e":
            self.exit_focus()
        elif key == "m":
            self.toggle_mute()
        elif key == "f":
            if self.ui: self.ui.toggle_fullscreen()
        elif key == "a":
            # Toggle analog / digital view
            if self.ui and self.ui.winfo_exists():
                self.ui._switch_view(not self.ui._analog_mode)
        elif key == "s":
            # Add a segment / lap mark
            if self.ui and self.ui.winfo_exists():
                self.ui._add_segment()
