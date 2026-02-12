@echo off
setlocal enabledelayedexpansion

chcp 65001 >nul
title Image Quality Checker

rem Determine target: drag-drop (%1) or current folder
set "TARGET=%~1"
if "%TARGET%"=="" set "TARGET=%CD%"

rem Change to script directory (where Python files are)
cd /d "%~dp0"

rem Optional: install dependencies if needed (comment out to skip)
rem echo Installing dependencies...
rem python -m pip install --quiet --disable-pip-version-check -r requirements.txt >nul 2>&1

rem Run the image quality checker
python check_image_quality.py "%TARGET%"

rem Uncomment the line below if you want to pause on double-click
rem pause
endlocal
