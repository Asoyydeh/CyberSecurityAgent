@echo off
chcp 65001 >nul
title AI DevTools — OpenRouter AI
color 0B
echo.
echo  ====================================
echo   AI DevTools - Powered by OpenRouter
echo  ====================================
echo.

:: Install dependencies jika belum ada
python -c "import rich, requests" 2>nul
if errorlevel 1 (
    echo [*] Installing dependencies...
    pip install -r requirements.txt
    echo.
)

:: Jalankan aplikasi
python -X utf8 main.py

pause
