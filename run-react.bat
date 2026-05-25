@echo off
echo NOTE: React needs the API running on port 8000.
echo Start run-api.bat first, OR use run-dev.bat to start both.
echo.
cd /d "%~dp0\frontend"
if not exist node_modules (
    echo Installing npm packages...
    call npm install
)
call npm run dev
