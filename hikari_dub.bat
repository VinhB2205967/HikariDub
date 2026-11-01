@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
title Hikari Tsukimi v3.0 - AI Dubbing Studio

echo =====================================================================
echo            HIKARI TSUKIMI v3.0 - AI Dubbing Studio
echo          AI Dubbing Studio ^| Hikari Tsukimi
echo =====================================================================
echo.

set "PYTHONIOENCODING=utf-8"
set "KMP_DUPLICATE_LIB_OK=TRUE"
set "HF_HUB_DISABLE_SYMLINKS_WARNING=1"
set "HF_HUB_DISABLE_TELEMETRY=1"
set "HF_HOME=%~dp0models\whisper"
set "PYTHONPATH=%~dp0;%~dp0_internal;%PYTHONPATH%"
set "PATH=%~dp0_internal\nvidia\cublas\bin;%~dp0_internal\nvidia\cudnn\bin;%~dp0_internal\torch\lib;%~dp0_internal\ffmpeg;%PATH%"

set "PY_EXE=C:\Users\ADMIN\AppData\Local\Programs\Python\Python310\python.exe"

if not exist "%PY_EXE%" (
    where python >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Khong tim thay Python.
        echo Hay kiem tra duong dan Python trong file BAT.
        pause
        exit /b 1
    )
    set "PY_EXE=python"
)

if not exist "main.py" (
    echo [ERROR] Khong tim thay main.py trong:
    echo %CD%
    pause
    exit /b 1
)

echo [INFO] Dang khoi dong Hikari Tsukimi v3.0...
echo [INFO] Python: %PY_EXE%
echo.

"%PY_EXE%" main.py %*
set "APP_EXIT_CODE=%ERRORLEVEL%"

if not "%APP_EXIT_CODE%"=="0" (
    echo.
    echo [THONG BAO] Ung dung thoat voi ma loi: %APP_EXIT_CODE%
    pause
)

endlocal
exit /b %APP_EXIT_CODE%
