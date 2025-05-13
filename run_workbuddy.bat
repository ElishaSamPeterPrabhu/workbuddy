@echo off
title WorkBuddy AI Assistant
echo Starting WorkBuddy AI Assistant...
echo.

:: Windows batch script to launch WorkBuddy (Jarvis Assistant)
:: TODO: Update the path if the entry point changes with modularization.

:: Get the directory where this batch file is located
set SCRIPT_DIR=%~dp0

:: Run the Python script
python "%SCRIPT_DIR%main.py"

:: If there was an error, pause so the user can see it
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo An error occurred while starting WorkBuddy.
    echo Please check that Python is installed and all dependencies are installed.
    echo You can run setup.py to install dependencies.
    pause
) 