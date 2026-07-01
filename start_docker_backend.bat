@echo off
echo ==========================================
echo Starting Backend Services via Docker Compose
echo ==========================================
docker-compose up --build -d
echo Backend is starting up.
echo API Docs will be available at: http://localhost:8000/docs
echo MinIO Console: http://localhost:9001 (User: minioadmin, Pass: minioadminpassword)
pause
