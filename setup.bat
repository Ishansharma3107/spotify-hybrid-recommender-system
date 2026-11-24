@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    if exist "%LocalAppData%\Programs\Python\Python312\python.exe" (
        "%LocalAppData%\Programs\Python\Python312\python.exe" -m venv .venv
    ) else (
        py -3.12 -m venv .venv
    )
    if errorlevel 1 goto failed
)
set "PATH=%CD%\.venv\Scripts;%PATH%"
python -m pip install -r requirements.txt || goto failed
python -m pip check || goto failed
python -m src.local_pipeline acquire || goto failed
dvc config --local cache.dir >nul 2>&1 || dvc cache dir --local "%LocalAppData%\SpotifyHybrid\dvc-cache" || goto failed
dvc repro || goto failed
echo Setup finished. Double-click start.bat to open the app.
exit /b 0
:failed
echo Setup stopped. See the error above.
if not defined SPOTIFY_NO_BROWSER pause
exit /b 1
