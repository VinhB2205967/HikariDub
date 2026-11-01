@echo off
cd /d "%~dp0"
title Kiem Tra Moi Truong Hikari Dub

echo =====================================================================
echo       Kiem Tra Moi Truong and Dependencies - Hikari Dub
echo =====================================================================
echo.

set "PY_EXE=C:\Users\ADMIN\AppData\Local\Programs\Python\Python310\python.exe"
if not exist "%PY_EXE%" set "PY_EXE=python"

echo 1. Kiem tra Python:
"%PY_EXE%" --version
if %errorlevel% neq 0 (
    echo [LOI] Khong tim thay Python!
    pause
    exit /b 1
)

echo.
echo 2. Kiem tra GPU and CUDA:
"%PY_EXE%" -c "import torch; print('CUDA Ready:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU Fallback')"

echo.
echo 3. Chay kiem tra xac minh 5 module:
"%PY_EXE%" verify_refactor.py

echo.
echo Hoan tat kiem tra!
pause
