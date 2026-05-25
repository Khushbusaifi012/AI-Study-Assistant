@echo off
cd /d "%~dp0"
call venv\Scripts\activate.bat

echo Checking port 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000.*LISTENING"') do (
    echo Stopping old process on port 8000 ^(PID %%a^)...
    taskkill /F /PID %%a >nul 2>&1
    timeout /t 2 /nobreak >nul
)

echo Starting API at http://127.0.0.1:8000
echo Health check: http://127.0.0.1:8000/api/health
uvicorn app.api.server:app --reload --host 127.0.0.1 --port 8000
