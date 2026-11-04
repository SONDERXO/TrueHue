@echo off
cd /d "%~dp0"
venv\Scripts\python.exe scripts\306_preview_face_mask.py --edit %*
if errorlevel 1 pause
