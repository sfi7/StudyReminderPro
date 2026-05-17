# ============================================================
# Study Reminder Pro - JSON Storage Utility
# File: utils/json_storage.py
# ============================================================

import json
import os
import tempfile
import shutil
from utils.logger import log

import threading

def atomic_write_json(file_path, data):
    """
    Safely writes JSON data to a file using a temporary file.
    Prevents data corruption if the app crashes during a write.
    Uses a background thread to prevent UI lag.
    """
    try:
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
    except Exception as e:
        log.error(f"Failed to serialize JSON: {e}")
        return False

    def _write_thread():
        try:
            dir_name = os.path.dirname(file_path)
            os.makedirs(dir_name, exist_ok=True)
            
            fd, temp_path = tempfile.mkstemp(dir=dir_name, suffix=".tmp")
            
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                f.write(json_str)
                f.flush()
                os.fsync(f.fileno())  # Force write to disk
                
            shutil.move(temp_path, file_path)
            log.debug(f"Atomically saved JSON data to {file_path}")
        except Exception as e:
            log.error(f"Failed to atomically write JSON to {file_path}: {e}", exc_info=True)
            if 'temp_path' in locals() and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass

    t = threading.Thread(target=_write_thread, daemon=True)
    t.start()
    return True

def read_json(file_path, default=None):
    """Reads JSON from a file, returning a default value if missing/corrupt."""
    if not os.path.exists(file_path):
        return default if default is not None else {}
        
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        log.error(f"JSON decode error in {file_path}: {e}")
        # Could attempt to load from a backup here
        return default if default is not None else {}
    except Exception as e:
        log.error(f"Failed to read JSON from {file_path}: {e}", exc_info=True)
        return default if default is not None else {}
