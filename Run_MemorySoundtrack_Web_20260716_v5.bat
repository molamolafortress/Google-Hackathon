@echo off
title Memory Soundtrack - Premium Ultimate Edition (v5)
echo =======================================================================
echo     🌌 Memory Soundtrack Generator: Premium Ultimate Edition (v5) 🌌
echo     - Streamlined 3-Stage One-Click Orchestration
     - Completely Bypasses Imagen to Ensure 0% Image Block failures
echo     - Dynamically Personalizes Cover Art using Slide #1 Photo
echo     - Hardened Lyria Safety Self-Healing Engine Integrated
echo =======================================================================
echo.
echo [INFO] Environment variables are loading from .env file...
echo [INFO] Launching Streamlit web browser locally...
echo.
streamlit run MemorySoundtrack_Web_20260716_v5.py
if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Failed to start Streamlit. Please verify your Python/pip installation.
)
pause
