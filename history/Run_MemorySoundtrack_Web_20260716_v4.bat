@echo off
title Memory Soundtrack - Premium Ultimate Edition (v4)
echo =======================================================================
echo     🌌 Memory Soundtrack Generator: Premium Ultimate Edition (v4) 🌌
echo     - Unified Streamlit Single-Page Application
echo     - Hardened Lyria Safety Self-Healing Engine Integrated
echo =======================================================================
echo.
echo [INFO] Environment variables are loading from .env file...
echo [INFO] Launching Streamlit web browser locally...
echo.
streamlit run MemorySoundtrack_Web_20260716_v4.py
if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Failed to start Streamlit. Please verify your Python/pip installation.
)
pause
