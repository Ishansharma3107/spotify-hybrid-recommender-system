@echo off
cd /d "%~dp0"
if not exist "data\local\interactions.npz" (
  echo Run setup.bat first.
  exit /b 1
)
docker compose up --build -d --wait
if errorlevel 1 exit /b 1
start "" http://127.0.0.1:8001
