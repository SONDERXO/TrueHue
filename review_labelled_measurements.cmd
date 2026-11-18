l@echo off
cd /d "%~dp0"
"venv\Scripts\python.exe" -B "scripts\725_review_labelled_measurements.py"
if errorlevel 1 pause
