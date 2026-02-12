@echo off
setlocal enabledelayedexpansion

chcp 65001 >nul
title Image Quality Checker - Language Selector

echo ==========================================
echo Image Quality Checker
echo ==========================================
echo.

rem Prompt for language
echo Select language / 选择语言:
echo   1. English
echo   2. 中文 (Chinese)
echo.
set /p LANG_CHOICE="Enter choice (1 or 2): "

if "%LANG_CHOICE%"=="1" (
    set IQC_LANG=en
    echo.
    echo Language set to: English
) else if "%LANG_CHOICE%"=="2" (
    set IQC_LANG=zh
    echo.
    echo 语言已设置为: 中文
) else (
    echo.
    echo Invalid choice. Defaulting to Chinese.
    set IQC_LANG=zh
)

echo.
echo Enter the path to scan (folder or file):
echo   Example: D:\images
echo   Example: D:\素材\上架图片\第1批
echo   Leave empty to scan current directory
echo.
set /p TARGET="Path: "

if "%TARGET%"=="" set "TARGET=%CD%"

rem Change to script directory
cd /d "%~dp0"

rem Install dependencies silently
echo.
echo [1/2] Installing dependencies...
python -m pip install --quiet --disable-pip-version-check -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo.
    if "%IQC_LANG%"=="en" (
        echo Failed to install dependencies. Please ensure Python 3 is installed.
    ) else (
        echo 依赖安装失败。请确认已安装 Python 3。
    )
    echo.
    pause
    exit /b 1
)

rem Run with --pause flag so window stays open
echo.
echo [2/2] Running scan...
python check_image_quality.py "%TARGET%" --pause

endlocal
