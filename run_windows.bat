@echo off
setlocal enabledelayedexpansion

chcp 65001 >nul
title Image Quality Checker

echo ==========================================
echo Image Quality Checker (Batch)
echo ==========================================
echo.
echo 请输入要扫描的路径（文件夹或单个图片文件）：
echo   例：D:\images
echo   例：D:\素材\上架图片\第1批
echo   例：D:\images\test.jpg
echo.
set /p TARGET=Path: 

if "%TARGET%"=="" (
  echo.
  echo 你没有输入路径，已取消。
  echo 按回车退出...
  pause >nul
  exit /b 1
)

rem Move to script directory so requirements.txt can be found
cd /d "%~dp0"

echo.
echo [1/2] Installing dependencies...
python -m pip install --upgrade pip >nul 2>&1
python -m pip install -r requirements.txt
if errorlevel 1 (
  echo.
  echo 依赖安装失败。请确认已安装 Python 3，并且能正常使用 pip。
  echo 你可以在命令行里运行：python --version  和  pip --version
  echo 按回车退出...
  pause >nul
  exit /b 1
)

echo.
echo [2/2] Running scan...
python check_image_quality.py "%TARGET%"

echo.
echo 完成。
echo 按回车退出...
pause >nul
endlocal