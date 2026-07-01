@echo off
echo ===================================================
echo             PrivateFM AI Stack Launcher            
echo ===================================================
echo 1. Start with Docker Backend (Recommended)
echo 2. Start with Local Backend (SQLite Fallback)
echo 3. Exit
echo ===================================================
set /p opt="Choose an option (1-3): "

if "%opt%"=="1" goto DOCKER_MODE
if "%opt%"=="2" goto LOCAL_MODE
if "%opt%"=="3" goto EXIT_MODE
goto EXIT_MODE

:DOCKER_MODE
echo [1/2] Starting Docker Backend...
start "PrivateFM AI - Docker Backend" cmd /k "docker-compose up --build"
echo [2/2] Starting Flutter Client...
start "PrivateFM AI - Flutter Client" cmd /k "cd /d frontend && C:\src\flutter\bin\flutter.bat pub get && C:\src\flutter\bin\flutter.bat run"
goto END

:LOCAL_MODE
echo [1/2] Starting Local Backend (SQLite)...
start "PrivateFM AI - Local Backend" cmd /k "cd /d backend && set DATABASE_URL=sqlite+aiosqlite:///./local_dev.db && call .\venv\Scripts\activate.bat && python -m uvicorn app.main:app --reload --port 8000"
echo [2/2] Starting Flutter Client...
start "PrivateFM AI - Flutter Client" cmd /k "cd /d frontend && C:\src\flutter\bin\flutter.bat pub get && C:\src\flutter\bin\flutter.bat run"
goto END

:EXIT_MODE
echo Exiting...
goto END

:END
pause
