@echo off
title Study Reminder Pro - Launcher
color 0A
echo.
echo  ============================================
echo   Study Reminder Pro - Starting...
echo  ============================================
echo.

:: Check Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python is not installed or not in PATH.
    echo  Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

:: Move to the app directory
cd /d "%~dp0"

:: Install dependencies if not already installed
echo  Checking dependencies...
pip install -r requirements.txt --quiet --disable-pip-version-check
if errorlevel 1 (
    echo  [ERROR] Failed to install dependencies.
    echo  Try running: pip install -r requirements.txt
    pause
    exit /b 1
)

echo  Dependencies OK.
echo.
echo  Launching Study Reminder Pro...
echo.

:: Run the application
python app.py

:: If it exits with an error, pause so user can read it
if errorlevel 1 (
    echo.
    echo  [ERROR] The application exited with an error.
    pause
)
