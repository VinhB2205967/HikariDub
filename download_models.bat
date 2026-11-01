@echo off
cd /d "%~dp0"
title Tai Mo Hinh Offline - Hikari Dub

echo =====================================================================
echo         Trinh Tai Mo Hinh Offline Hikari Dub
echo =====================================================================
echo.

set "PYTHONIOENCODING=utf-8"
set "KMP_DUPLICATE_LIB_OK=TRUE"
set "HF_HUB_DISABLE_SYMLINKS_WARNING=1"
set "PYTHONPATH=%~dp0;%~dp0_internal;%PYTHONPATH%"
set "PATH=%~dp0_internal\ffmpeg;%~dp0_internal\torch\lib;%PATH%"

set "PY_EXE=C:\Users\ADMIN\AppData\Local\Programs\Python\Python310\python.exe"
if not exist "%PY_EXE%" set "PY_EXE=python"

"%PY_EXE%" download_all_models.py

echo.
pause

