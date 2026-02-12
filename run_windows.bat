@echo off
setlocal

title Image Quality Checker

echo.
echo  ==========================================
echo   Image Quality Checker
echo  ==========================================
echo.
echo  Enter the path to scan (folder or single image file):
echo.
echo    Example: D:\images
echo    Example: D:\images\test.jpg
echo.
set /p "TARGET=  Path: "

if "%TARGET%"=="" (
    echo.
    echo  No path entered. Exiting.
    pause
    exit /b 1
)

if not exist "%TARGET%" (
    echo.
    echo  Error: path not found: %TARGET%
    pause
    exit /b 2
)

rem Move to script directory so imports work
cd /d "%~dp0"

echo.
echo  [1/2] Checking dependencies...
python -m pip install -q -r requirements.txt
if errorlevel 1 (
    echo.
    echo  Failed to install dependencies.
    echo  Make sure Python 3.8+ is installed and pip is available.
    pause
    exit /b 1
)

echo  [2/2] Scanning...
echo.
python check_image_quality.py "%TARGET%"

echo.
echo  Done.
pause
endlocal
