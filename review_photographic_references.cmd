@echo off
cd /d "%~dp0"
"venv\Scripts\python.exe" -B "scripts\734_review_photographic_references.py"
if errorlevel 1 pause
