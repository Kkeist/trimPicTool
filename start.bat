@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo   Trim transparent edges: img -^> img_trimmed
echo ========================================
echo.

where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Install Python and check "Add to PATH".
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

if not exist "img" (
    echo [INFO] No "img" folder found. Creating it.
    mkdir img
    echo Put your PNG files in "img" folder, then run start.bat again.
    pause
    exit /b 0
)

if not exist "trim_standalone.py" (
    echo [ERROR] trim_standalone.py not found. Keep it in the same folder as start.bat.
    pause
    exit /b 1
)

python -c "import PIL, numpy" 2>nul
if errorlevel 1 (
    echo [INFO] Installing dependencies: Pillow, numpy ...
    pip install Pillow numpy -q
    if errorlevel 1 (
        echo [ERROR] Install failed. Run manually: pip install Pillow numpy
        pause
        exit /b 1
    )
)

python trim_standalone.py
exit /b 0
