@echo off
cd /d %~dp0

REM Backend
start "Backend" cmd /k "cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000"

REM Frontend
start "Frontend" cmd /k "cd frontend && npm run dev"