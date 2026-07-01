@echo off
echo ==========================================
echo Running Flutter Client
echo ==========================================
cd frontend
echo Fetching dependencies...
call flutter pub get
echo Starting application...
call flutter run
pause
