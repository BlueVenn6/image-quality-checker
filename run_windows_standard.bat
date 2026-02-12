@echo off
REM Image Quality Checker - Standard Windows Runner
REM Can be double-clicked or used with drag-and-drop
REM Save this file as UTF-8 without BOM or ANSI encoding

setlocal enabledelayedexpansion

REM Change to script directory
cd /d "%~dp0"

REM Determine target path: use dragged file/folder (%1) or current directory
if "%~1"=="" (
    set "TARGET=%CD%"
) else (
    set "TARGET=%~1"
)

REM Quietly install requirements if needed
echo [1/2] Checking dependencies...
python -m pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo.
    echo Warning: Failed to install dependencies. Continuing anyway...
    echo If you see errors, please run: python -m pip install Pillow
)

REM Run the CLI
echo [2/2] Running image quality check...
echo.
python check_image_quality.py "%TARGET%"

REM Exit code is passed through from Python script
REM To keep console open after double-click, uncomment the next line:
REM pause

endlocal
