@echo off
title Memory Soundtrack
streamlit run app.py
if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Could not start Streamlit. Run: pip install -r requirements.txt
)
pause
