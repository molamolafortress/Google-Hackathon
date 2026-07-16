@echo off
title Memory Soundtrack Generator v4
echo ========================================================
echo Starting Memory Soundtrack Generator (Dual-Mode v4)
echo ========================================================
echo Checking Streamlit installation...
python -c "import streamlit" >nul 2>&1
if %errorlevel% neq 0 (
    echo Streamlit is not installed or not in PATH!
    echo Installing required packages from requirements.txt...
    pip install -r requirements.txt
)
echo Launching Streamlit App...
streamlit run MemorySoundtrack_20260716_v4.py
pause
