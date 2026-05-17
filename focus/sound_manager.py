# ============================================================
# Study Reminder Pro - Sound Manager
# File: focus/sound_manager.py
# ============================================================

import os
import threading
from utils.logger import log

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    log.warning("Pygame not installed. Ambient sounds will be disabled.")

class SoundManager:
    """Handles background ambient sounds and notification chimes asynchronously."""
    def __init__(self, settings_service):
        self.settings = settings_service
        self.is_playing = False
        self.current_sound = None
        self._volume = 0.5

        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.init()
            except Exception as e:
                log.error(f"Failed to initialize pygame mixer: {e}")

    def play_ambient(self, sound_file):
        """Plays an ambient sound in an infinite loop."""
        if not PYGAME_AVAILABLE or not self.settings.get("sound_enabled", True):
            return

        def _play():
            try:
                if os.path.exists(sound_file):
                    pygame.mixer.music.load(sound_file)
                    pygame.mixer.music.set_volume(self._volume)
                    pygame.mixer.music.play(loops=-1, fade_ms=2000)
                    self.is_playing = True
                    self.current_sound = sound_file
                    log.info(f"Started ambient sound: {os.path.basename(sound_file)}")
                else:
                    log.error(f"Sound file not found: {sound_file}")
            except Exception as e:
                log.error(f"Error playing sound: {e}")

        # Run in a separate thread just in case loading blocks
        threading.Thread(target=_play, daemon=True).start()

    def stop_ambient(self):
        """Fades out and stops the current ambient sound."""
        if not PYGAME_AVAILABLE or not self.is_playing:
            return
            
        try:
            pygame.mixer.music.fadeout(1500)
            self.is_playing = False
            self.current_sound = None
            log.info("Stopped ambient sound.")
        except Exception as e:
            log.error(f"Error stopping sound: {e}")

    def toggle_mute(self):
        if not PYGAME_AVAILABLE:
            return False
            
        current_vol = pygame.mixer.music.get_volume()
        if current_vol > 0:
            pygame.mixer.music.set_volume(0)
            return True # Is muted
        else:
            pygame.mixer.music.set_volume(self._volume)
            return False # Is not muted

    def _load_sound(self, path):
        """Safely loads a Sound object if file exists."""
        if os.path.exists(path):
            try:
                return pygame.mixer.Sound(path)
            except Exception as e:
                log.error(f"Failed to load sound {path}: {e}")
        return None

    def play_chime(self):
        """Plays a short notification sound (chime)."""
        if not PYGAME_AVAILABLE or not self.settings.get("sound_enabled", True):
            return
            
        sound = self._load_sound("assets/sounds/chime.wav")
        if sound:
            sound.set_volume(self._volume)
            sound.play()
        else:
            # Fallback beep if assets are missing
            self._fallback_beep()

    def play_session_start(self):
        self.play_chime()

    def play_session_complete(self):
        if not PYGAME_AVAILABLE or not self.settings.get("sound_enabled", True):
            return
        sound = self._load_sound("assets/sounds/complete.wav")
        if sound:
            sound.set_volume(self._volume)
            sound.play()
        else:
            self._fallback_beep()

    def _fallback_beep(self):
        """Simple beep if sound file is missing."""
        try:
            import winsound
            winsound.Beep(1000, 200)
        except:
            pass

    def play_alarm(self):
        """Plays a loud, repeating alarm until stopped."""
        if not PYGAME_AVAILABLE or not self.settings.get("sound_enabled", True):
            return
            
        self._stop_alarm = False
        def _alarm_loop():
            sound = self._load_sound("assets/sounds/alarm.wav")
            while not getattr(self, "_stop_alarm", True):
                if sound:
                    sound.set_volume(1.0) # Full volume for alarm
                    sound.play()
                    # Wait for sound duration or 2 seconds
                    pygame.time.wait(2000)
                else:
                    # Fallback repeating beep
                    try:
                        import winsound
                        winsound.Beep(1200, 500)
                        winsound.Beep(1500, 500)
                    except: pass
                    pygame.time.wait(500)
                    
        threading.Thread(target=_alarm_loop, daemon=True).start()

    def stop_alarm(self):
        """Stops the repeating alarm."""
        self._stop_alarm = True
        log.info("Alarm stopped.")
