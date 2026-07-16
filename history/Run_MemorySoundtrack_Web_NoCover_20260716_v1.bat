@echo off
title Memory Soundtrack - No Cover Edition (v1)
echo =======================================================================
echo     🌌 Memory Soundtrack Generator: No Cover Edition (v1) 🌌
echo     - Unified Streamlit Single-Page Application (Cover Skipped)
echo     - Hardened Lyria Safety Self-Healing Engine Integrated
echo =======================================================================
echo.
echo [INFO] Environment variables are loading from .env file...
echo [INFO] Launching Streamlit web browser locally...
echo.
streamlit run MemorySoundtrack_Web_NoCover_20260716_v1.py
if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Failed to start Streamlit. Please verify your Python/pip installation.
)
pause
