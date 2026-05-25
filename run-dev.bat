@echo off
cd /d "%~dp0"

echo Starting API in a new window...
start "Study Assistant API" /D "%~dp0" cmd /k call run-api.bat
echo Waiting 5 seconds for API...
timeout /t 5 /nobreak >nul

echo Starting React at http://localhost:5173
cd /d "%~dp0\frontend"
if not exist node_modules call npm install
call npm run dev
