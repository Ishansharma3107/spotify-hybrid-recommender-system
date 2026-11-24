@echo off
cd /d "%~dp0"
.venv\Scripts\python.exe -m src.windows_app stop
if errorlevel 1 if not defined SPOTIFY_NO_BROWSER pause
