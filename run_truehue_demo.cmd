@echo off
cd /d "%~dp0"
if not exist "venv\Scripts\python.exe" (
  echo The TrueHue Python environment was not found in this folder.
  pause
  exit /b 1
)
if "%~1"=="" (
  start "" "%~dp0venv\Scripts\pythonw.exe" "%~dp0scripts\246_run_python_demo.py"
  exit /b 0
)
"venv\Scripts\python.exe" "scripts\246_run_python_demo.py" %*
if errorlevel 1 pause
