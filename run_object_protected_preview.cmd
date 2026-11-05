@echo off
cd /d "%~dp0"
if "%~1"=="" (
    echo Usage: run_object_protected_preview.cmd "path\photo.jpg" clear
    echo Glasses choices: clear, opaque, uncertain. Default: uncertain.
    echo You can drag a photo onto this launcher to use uncertain handling.
    pause
    exit /b 2
)
set "TRUEHUE_PREVIEW_GLASSES=%~2"
if not defined TRUEHUE_PREVIEW_GLASSES set "TRUEHUE_PREVIEW_GLASSES=uncertain"
venv\Scripts\python.exe -B scripts\419_preview_object_protected_face.py --image "%~1" --glasses "%TRUEHUE_PREVIEW_GLASSES%"
if errorlevel 1 pause
