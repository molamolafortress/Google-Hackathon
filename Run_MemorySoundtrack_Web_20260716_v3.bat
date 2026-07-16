@echo off
title Memory Soundtrack Web App Server
echo ========================================================
echo Starting Memory Soundtrack Web Server (Layout Upgrades v3)
echo ========================================================
echo Launching browser and local server...
start http://localhost:8000/
uvicorn MemorySoundtrack_Web_20260716_v3:app --host 0.0.0.0 --port 8000 --reload
pause
