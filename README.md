<div align="center">
  <img src="assets/icon.ico" alt="Study Reminder Pro Logo" width="120" />

  # 📖 Study Reminder Pro

  **A visually stunning, production-level smart study tracking and reminder application.**<br>
  Designed to boost productivity, track progress, and help university students ace their exams.

  [![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg?style=flat-square&logo=python)](https://www.python.org/)
  [![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-1abc9c.svg?style=flat-square)](https://github.com/TomSchimansky/CustomTkinter)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)

  [Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Screenshots](#-screenshots)

</div>

---

## ✨ Features

Study Reminder Pro is packed with powerful features designed to streamline your study workflow:

| 🚀 Core Features | 📝 Description |
|:---|:---|
| **📚 Subject Management** | Track up to 7+ subjects with customizable icons, colors, progress, and rich notes. |
| **📊 Advanced Analytics** | Animated circular & linear progress bars, 30-day heatmaps, and KPI cards. |
| **📅 Exam Countdown** | Color-coded badges displaying precise days remaining until each exam. |
| **🍅 Pomodoro Timer** | Integrated, animated canvas timer with Work / Break / Long Break modes. |
| **🔥 Study Streaks** | Gamified daily streak tracking with auto-awarded milestone badges. |
| **🌙 Dynamic Themes** | Beautiful Dark / Light mode with a one-click UI toggle. |
| **💾 Robust Data Integrity**| Auto-saves to `data/study_data.json` with a 1-click backup and restore system. |
| **⚠️ Smart Notifications** | Desktop toast notifications for exams within 3 days. |
| **💡 AI-Curated Insights**| Daily actionable study tips displayed on every launch. |

---

## 🚀 Quick Start (Windows)

The easiest way to get started is by using the automated launcher.

**Double-click `run.bat`** — it handles everything automatically:
1. Verifies your Python installation.
2. Installs required dependencies from `requirements.txt`.
3. Launches the application immediately.

---

## 🛠️ Manual Installation & Setup

If you prefer to run the application manually from your terminal, follow these steps:

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/StudyReminderPro.git
cd StudyReminderPro
```

### 2. Install Dependencies
Make sure you have Python 3.10+ installed.
```bash
pip install -r requirements.txt
```

### 3. Run the App
```bash
python app.py
```

---

## 📸 Screenshots
*(Add screenshots of your application here to showcase its beautiful UI)*
- **Dashboard View:** `![Dashboard](link-to-image)`
- **Pomodoro Timer:** `![Pomodoro](link-to-image)`
- **Analytics & Heatmap:** `![Analytics](link-to-image)`

---

## 📁 Architecture & Structure

```text
StudyReminderPro/
├── app.py                  # Main Application Entry Point
├── run.bat                 # One-click Windows Launcher
├── requirements.txt        # Python Dependencies
├── core/                   # Core App Logic (Database, Theme, Logic)
├── ui/                     # CustomTkinter Views (Dashboard, Settings, Analytics)
├── data/                   # [Auto-Generated] Local Storage & Backups
└── assets/                 # Icons and Image Assets
```

---

## 📦 Building a Standalone Executable (.exe)

Want to share the app with friends without them needing Python? Use PyInstaller:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=assets/icon.ico --name="StudyReminderPro" app.py
```
The compiled `.exe` will be generated inside the `dist/` folder.

---

## 💡 Pro Tips for Best Experience
- **Date Formatting:** Always enter exam dates in **YYYY-MM-DD** format (e.g. `2025-06-20`).
- **Quick Logging:** Use the **Quick +1 Lecture** button on each subject card for rapid tracking.
- **Timer Integration:** The Pomodoro timer automatically logs your completed study time to the selected subject.
- **Data Safety:** Regularly backup your data before major updates via **Settings → Backup**.

---

## 📄 License
This project is licensed under the **MIT License** — free to use, modify, and distribute. See the `LICENSE` file for more details.

<div align="center">
  <i>Built with ❤️ for better grades and productive study sessions.</i>
</div>
