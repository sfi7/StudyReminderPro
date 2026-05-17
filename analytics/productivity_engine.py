# ============================================================
# Study Reminder Pro - Productivity Engine
# File: analytics/productivity_engine.py
# ============================================================

from datetime import datetime, timedelta

class ProductivityEngine:
    """
    Analyzes raw aggregated data to generate smart metrics and intelligent recommendations.
    """
    def __init__(self, analytics_engine, db_facade):
        self.ae = analytics_engine
        self.db = db_facade

    def calculate_focus_score(self):
        """Average focus score across all or recent sessions."""
        sessions = self.ae.get_all_sessions()
        if not sessions:
            return 100
            
        # Simplified: If session completes with 0 interruptions, it's 100.
        # Deduct 5 for each interruption.
        total_score = 0
        for s in sessions:
            score = 100 - (s.get("interruptions", 0) * 5)
            if not s.get("completed", False):
                score -= 20
            total_score += max(0, min(100, score))
            
        return int(total_score / len(sessions))

    def get_most_productive_hour(self):
        """Finds the hour of the day with the highest session count/duration."""
        hour_counts = {i: 0 for i in range(24)}
        for s in self.ae.get_all_sessions():
            try:
                dt = datetime.fromisoformat(s.get("start_time"))
                hour_counts[dt.hour] += s.get("duration_min", 0)
            except:
                pass
                
        best_hour = max(hour_counts, key=hour_counts.get)
        if hour_counts[best_hour] == 0:
            return None
        return best_hour

    def generate_recommendations(self):
        """Yields intelligent, contextual recommendations."""
        recs = []
        
        # Recommendation 1: Best hour
        best_hour = self.get_most_productive_hour()
        if best_hour is not None:
            time_str = f"{best_hour}:00 - {best_hour+1}:00"
            recs.append(f"You are most productive between {time_str}. Try scheduling tough tasks then.")
            
        # Recommendation 2: Interruption check
        avg_score = self.calculate_focus_score()
        if avg_score < 70:
            recs.append("Your average focus score is dropping. Consider using the 'Nature' ambient sound and putting your phone away.")
            
        # Recommendation 3: Neglected subject
        dist = self.ae.get_subject_distribution()
        subjects = self.db.subjects
        if subjects and dist:
            # Find subject with least time
            least_sid = min(dist, key=dist.get)
            least_subj = next((s for s in subjects if s["id"] == least_sid), None)
            if least_subj:
                recs.append(f"'{least_subj['name']}' has been neglected recently. Dedicate your next session to it.")
                
        if not recs:
            recs.append("Great consistency! Keep up the good work and maintain your current pace.")
            
        return recs
