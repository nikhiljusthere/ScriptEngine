@echo off
title ScriptEngine API
cd /d "%~dp0"

where python >nul 2>nul
if %errorlevel%==0 (
    python start_scriptengine.py
) else (
    where py >nul 2>nul
    if %errorlevel%==0 (
        py start_scriptengine.py
    ) else (
        echo Python not found on PATH. Install Python or fix the path.
        pause
        exit /b 1
    )
)

if errorlevel 1 pause
