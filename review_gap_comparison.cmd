@echo off
cd /d "%~dp0"
if exist "venv\Scripts\python.exe" (
  "venv\Scripts\python.exe" -B "scripts\868_review_gap_source_held_comparison.py"
) else (
  python -B "scripts\868_review_gap_source_held_comparison.py"
)
if errorlevel 1 pause
