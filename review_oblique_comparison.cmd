@echo off
cd /d "%~dp0"
if exist "venv\Scripts\python.exe" (
  "venv\Scripts\python.exe" -B "scripts\852_review_oblique_source_held_comparison.py"
) else (
  python -B "scripts\852_review_oblique_source_held_comparison.py"
)
if errorlevel 1 pause
