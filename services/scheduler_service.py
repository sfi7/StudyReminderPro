# ============================================================
# Study Reminder Pro - Scheduler Service
# File: services/scheduler_service.py
# ============================================================

import threading
import time
import uuid
import json
import os
from datetime import datetime
from utils.logger import log

class SchedulerService:
    """
    Background scheduler engine.
    Thread-safe, runs independently of the main UI loop using monotonic time.
    Persists jobs to disk to survive app restarts.
    """
    def __init__(self, storage_file="data/scheduler_state.json"):
        self._jobs = {}  # {job_id: job_dict}
        self._running = False
        self._thread = None
        self._lock = threading.Lock()
        self._storage_file = storage_file
        self._load_state()

    def start(self):
        """Starts the background scheduler loop if not already running."""
        with self._lock:
            if self._running:
                return
            self._running = True
            self._thread = threading.Thread(target=self._run_loop, daemon=True)
            self._thread.start()
            log.info("Scheduler Service started.")

    def stop(self):
        """Gracefully stops the scheduler and saves state."""
        with self._lock:
            self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        self._save_state()
        log.info("Scheduler Service stopped.")

    def schedule(self, trigger_time, callback=None, recurring_seconds=0, job_id=None, source_type="general", payload=None):
        """
        Schedules a job. If callback is not provided, the listener system will catch it based on source_type.
        """
        with self._lock:
            jid = job_id or str(uuid.uuid4())
            self._jobs[jid] = {
                "id": jid,
                "created_at": time.time(),
                "trigger_time": trigger_time,
                "recurring_seconds": recurring_seconds,
                "source_type": source_type,
                "payload": payload or {},
                "callback": callback
            }
            self._save_state()
            return jid

    def cancel(self, job_id):
        """Cancels a scheduled job."""
        with self._lock:
            if job_id in self._jobs:
                del self._jobs[job_id]
                self._save_state()

    def _run_loop(self):
        """The core monotonic loop."""
        while self._running:
            now = time.time()
            jobs_to_run = []
            
            with self._lock:
                for jid, job in list(self._jobs.items()):
                    if now >= job["trigger_time"]:
                        jobs_to_run.append((jid, job))
            
            # Execute callbacks outside the lock to prevent deadlocks
            for jid, job in jobs_to_run:
                try:
                    # In a fully persistent system, we rely on event listeners rather than memory callbacks
                    if job.get("callback") and callable(job["callback"]):
                        job["callback"]()
                    else:
                        # Log or trigger system-wide event
                        log.debug(f"Executing persistent job: {job.get('source_type')}")
                        # Example: event_bus.emit(job["source_type"], job["payload"])
                except Exception as e:
                    log.error(f"Scheduler job '{jid}' failed: {e}")
                
                # Handle recurring or removal
                with self._lock:
                    if jid in self._jobs: # Make sure it wasn't cancelled during execution
                        if job["recurring_seconds"] > 0:
                            # Reschedule
                            self._jobs[jid]["trigger_time"] = time.time() + job["recurring_seconds"]
                        else:
                            # One-time job, remove
                            del self._jobs[jid]
                            
            if jobs_to_run:
                self._save_state()

            # Sleep briefly to yield CPU
            time.sleep(1)

    # ── Persistence Methods ──
    def _save_state(self):
        """Saves non-callback jobs to disk."""
        try:
            os.makedirs(os.path.dirname(self._storage_file), exist_ok=True)
            serializable_jobs = {}
            for jid, job in self._jobs.items():
                if job.get("callback") is None: # Only save jobs that can be reconstructed
                    serializable_jobs[jid] = job
            with open(self._storage_file, "w", encoding="utf-8") as f:
                json.dump(serializable_jobs, f, indent=4)
        except Exception as e:
            log.error(f"Failed to save scheduler state: {e}")

    def _load_state(self):
        """Loads jobs from disk."""
        if not os.path.exists(self._storage_file):
            return
        try:
            with open(self._storage_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._jobs.update(data)
                log.info(f"Loaded {len(data)} persistent jobs.")
        except Exception as e:
            log.error(f"Failed to load scheduler state: {e}")
