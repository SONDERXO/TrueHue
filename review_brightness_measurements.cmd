@echo off
cd /d "%~dp0"
"venv\Scripts\python.exe" -B "scripts\762_review_brightness_measurements.py"
if errorlevel 1 pause
