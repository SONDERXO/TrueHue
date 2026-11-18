@echo off
cd /d "%~dp0"
python scripts\preview_59807_correction_support.py --open
if errorlevel 1 pause
