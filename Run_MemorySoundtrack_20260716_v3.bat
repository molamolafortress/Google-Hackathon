@echo off
title Memory Soundtrack Generator v3
echo ===================================================
echo   Starting Memory Soundtrack Generator (Streamlit)
echo ===================================================
echo.
echo Launching the web application...
echo.

streamlit run MemorySoundtrack_20260716_v3.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Failed to start Streamlit.
    echo Please make sure Streamlit and requirements are installed.
    echo You can install them by running: pip install -r requirements.txt
    echo.
    pause
)
