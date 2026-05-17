# ============================================================
# Study Reminder Pro - Charts Engine
# File: analytics/charts.py
# ============================================================

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
from datetime import datetime, timedelta

class ChartsEngine:
    """
    Renders premium matplotlib charts optimized for dark/light mode.
    """
    def __init__(self, theme_manager):
        self.tm = theme_manager
        self._setup_style()

    def _setup_style(self):
        c = self.tm.colors
        is_dark = self.tm.current_mode in ['dark', 'glass']
        plt.style.use('dark_background' if is_dark else 'default')
        
        plt.rcParams.update({
            "figure.facecolor": c["bg_card"],
            "axes.facecolor": c["bg_card"],
            "axes.edgecolor": c["border"],
            "axes.labelcolor": c["text_secondary"],
            "text.color": c["text_primary"],
            "xtick.color": c["text_muted"],
            "ytick.color": c["text_muted"],
            "grid.color": c["border"],
            "grid.alpha": 0.2,
            "font.family": "Segoe UI",
            "font.size": 9
        })

    def render_weekly_trend(self, parent_frame, data_dict):
        """
        Renders a line chart of study minutes over the last 7 days.
        data_dict: {"YYYY-MM-DD": minutes, ...}
        """
        fig = Figure(figsize=(6, 3), dpi=100)
        ax = fig.add_subplot(111)
        fig.patch.set_facecolor(self.tm.colors["bg_card"])
        
        # Prepare last 7 days
        today = datetime.now().date()
        dates = [today - timedelta(days=i) for i in range(6, -1, -1)]
        x_labels = [d.strftime("%a") for d in dates]
        y_values = [data_dict.get(d.strftime("%Y-%m-%d"), 0) for d in dates]
        
        ax.plot(x_labels, y_values, color=self.tm.colors["accent"], marker='o', 
                linewidth=3, markersize=8, markeredgecolor=self.tm.colors["bg_card"], markeredgewidth=2)
        
        # Fill under line
        ax.fill_between(x_labels, y_values, color=self.tm.colors["accent"], alpha=0.2)
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.yaxis.grid(True, linestyle='--', alpha=0.5)
        ax.set_ylabel("Minutes")
        
        fig.tight_layout(pad=1.0)
        
        canvas = FigureCanvasTkAgg(fig, master=parent_frame)
        canvas.draw()
        return canvas.get_tk_widget()

    def render_subject_distribution(self, parent_frame, distribution_dict, subjects_db):
        """
        Renders a donut chart of study time per subject.
        """
        fig = Figure(figsize=(4, 4), dpi=100)
        ax = fig.add_subplot(111)
        fig.patch.set_facecolor(self.tm.colors["bg_card"])
        
        labels = []
        sizes = []
        colors = []
        
        for sid, duration in distribution_dict.items():
            if duration <= 0: continue
            subj = next((s for s in subjects_db if s["id"] == sid), None)
            labels.append(subj["name"] if subj else "Deleted")
            sizes.append(duration)
            colors.append(subj["color"] if subj else self.tm.colors["text_muted"])
            
        if not sizes:
            ax.text(0.5, 0.5, "No Data", horizontalalignment='center', verticalalignment='center')
        else:
            wedges, texts, autotexts = ax.pie(
                sizes, labels=labels, colors=colors, autopct='%1.0f%%',
                startangle=90, pctdistance=0.85, wedgeprops=dict(width=0.3, edgecolor=self.tm.colors["bg_card"])
            )
            # Cannot use plt.setp easily without pyplot state, manually set properties:
            for autotext in autotexts:
                autotext.set_size(8)
                autotext.set_weight("bold")
                autotext.set_color("white")
            for text in texts:
                text.set_size(9)
                text.set_color(self.tm.colors["text_secondary"])

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=parent_frame)
        canvas.draw()
        return canvas.get_tk_widget()
