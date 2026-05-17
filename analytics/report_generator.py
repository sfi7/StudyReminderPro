# ============================================================
# Study Reminder Pro - Report Generator
# File: analytics/report_generator.py
# ============================================================

import os
import csv
from datetime import datetime
from utils.logger import log

class ReportGenerator:
    """
    Exports analytics data to CSV and prepares architecture for PDF.
    """
    def __init__(self, analytics_engine):
        self.ae = analytics_engine

    def export_to_csv(self, filepath):
        """Exports all sessions to a CSV file."""
        sessions = self.ae.get_all_sessions()
        if not sessions:
            return False, "No sessions to export."
            
        try:
            with open(filepath, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Session ID", "Subject ID", "Start Time", "End Time", "Duration (min)", "Interruptions", "Completed"])
                
                for s in sessions:
                    writer.writerow([
                        s.get("id", ""),
                        s.get("subject_id", ""),
                        s.get("start_time", ""),
                        s.get("end_time", ""),
                        s.get("duration_min", 0),
                        s.get("interruptions", 0),
                        s.get("completed", False)
                    ])
            log.info(f"Successfully exported data to {filepath}")
            return True, "Export successful!"
        except Exception as e:
            log.error(f"Failed to export CSV: {e}")
            return False, str(e)
