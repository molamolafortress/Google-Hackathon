@echo off
title Memory Soundtrack Web App Server
echo ========================================================
echo Starting Memory Soundtrack Web Server (v5)
echo ========================================================
echo Launching browser and local server...
start http://127.0.0.1:8000/
uvicorn MemorySoundtrack_Web_20260716_v1:app --host 127.0.0.1 --port 8000 --reload
pause
