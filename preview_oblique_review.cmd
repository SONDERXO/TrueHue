ok@echo off
cd /d "%~dp0"
if exist "venv\Scripts\python.exe" (
  "venv\Scripts\python.exe" -B "scripts\851_preview_oblique_review_generated.py"
) else (
  python -B "scripts\851_preview_oblique_review_generated.py"
)
if errorlevel 1 pause
