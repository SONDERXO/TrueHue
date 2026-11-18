@echo off
cd /d "%~dp0"
"venv\Scripts\python.exe" -B "scripts\804_review_ffhq_support.py"
if errorlevel 1 pause
