@echo off
cd /d "%~dp0"
venv\Scripts\python.exe scripts\350_preview_full_face.py --open %*
if errorlevel 1 pause
