@echo off
REM Image Quality Checker - Interactive Language Selector
REM Double-click to run with language selection
REM Save this file as UTF-8 without BOM (preferred) or ANSI encoding

setlocal enabledelayedexpansion

chcp 65001 >nul
title Image Quality Checker - Language Selector

REM Change to script directory
cd /d "%~dp0"

echo ==========================================
echo Image Quality Checker
echo ==========================================
echo.
echo Select language / 选择语言:
echo   1 = English
echo   2 = Chinese (中文)
echo.
set /p LANG_CHOICE="Enter 1 or 2: "

if "%LANG_CHOICE%"=="1" (
    set "IQC_LANG=en"
    echo Language set to English.
) else if "%LANG_CHOICE%"=="2" (
    set "IQC_LANG=zh"
    echo Language set to Chinese.
) else (
    echo Invalid choice, defaulting to Chinese.
    set "IQC_LANG=zh"
)

echo.
echo Enter path to scan (folder or single file):
echo   - Leave blank to scan current directory
echo   - Example: D:\images
echo   - Example: D:\images\test.jpg
echo.
set /p TARGET="Path: "

if "%TARGET%"=="" (
    set "TARGET=%CD%"
    echo Using current directory: %TARGET%
)

REM Quietly install requirements
echo.
echo [1/2] Installing dependencies...
python -m pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo Warning: Failed to install dependencies.
    echo Please ensure Python and pip are installed correctly.
)

REM Run CLI with --pause to keep console open
echo.
echo [2/2] Running image quality check...
echo.
python check_image_quality.py "%TARGET%" --pause

endlocal
