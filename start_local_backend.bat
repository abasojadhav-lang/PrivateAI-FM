@echo off
echo ==========================================
echo Starting Backend locally with SQLite Fallback
echo ==========================================
cd backend
set DATABASE_URL=sqlite+aiosqlite:///./local_dev.db
echo Activated SQLite DB at: backend/local_dev.db
call .\venv\Scripts\activate.bat
python -m uvicorn app.main:app --reload --port 8000
pause
