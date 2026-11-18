@echo off
cd /d "%~dp0"
"venv\Scripts\python.exe" -B "scripts\738_review_photographic_support.py"
if errorlevel 1 pause
