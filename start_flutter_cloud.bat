@echo off
echo ===================================================
echo           PrivateFM AI Cloud Client Launcher       
echo ===================================================
echo Target Cloud Backend: https://privatefm-backend.onrender.com
echo ===================================================
cd frontend
echo Fetching dependencies...
call C:\src\flutter\bin\flutter.bat pub get
echo Launching Flutter client connected to the cloud...
call C:\src\flutter\bin\flutter.bat run --dart-define=API_BASE_URL=https://privatefm-backend.onrender.com
pause
