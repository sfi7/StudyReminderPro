# ============================================================
# Study Reminder Pro - Global Event Bus
# File: utils/event_bus.py
# ============================================================

from collections import defaultdict
from utils.logger import log

class EventBus:
    """
    Lightweight Publisher/Subscriber system for decoupled reactivity.
    Allows UI components to react instantly to backend state changes.
    """
    def __init__(self):
        self._listeners = defaultdict(list)
        self._debounce_timers = {}

    def subscribe(self, event_name, callback):
        """Registers a callback to be triggered when event_name occurs."""
        if callback not in self._listeners[event_name]:
            self._listeners[event_name].append(callback)

    def unsubscribe(self, event_name, callback):
        """Removes a previously registered callback."""
        if callback in self._listeners[event_name]:
            self._listeners[event_name].remove(callback)

    def emit(self, event_name, *args, **kwargs):
        """Triggers all callbacks registered for event_name."""
        log.debug(f"Event emitted: {event_name}")
        for callback in self._listeners.get(event_name, []):
            try:
                callback(*args, **kwargs)
            except Exception as e:
                log.error(f"Error in event listener for '{event_name}': {e}")
                
    def emit_debounced(self, event_name, delay_ms=300, *args, **kwargs):
        """Triggers callbacks after a delay, ignoring intermediate emissions."""
        if event_name in self._debounce_timers:
            self._debounce_timers[event_name].cancel()
            
        def _emit_action():
            self.emit(event_name, *args, **kwargs)
            del self._debounce_timers[event_name]
            
        import threading
        timer = threading.Timer(delay_ms / 1000.0, _emit_action)
        self._debounce_timers[event_name] = timer
        timer.daemon = True
        timer.start()
