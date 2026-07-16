@echo off
title Memory Soundtrack Generator v5
echo ========================================================
echo Starting Memory Soundtrack Generator (Dual-Mode v5)
echo ========================================================
echo Checking Streamlit installation...
python -c "import streamlit" >nul 2>&1
if %errorlevel% neq 0 (
    echo Streamlit is not installed or not in PATH!
    echo Installing required packages from requirements.txt...
    pip install -r requirements.txt
)
echo Launching Streamlit App...
streamlit run MemorySoundtrack_20260716_v5.py
pause
