@echo off
echo Starting CI/CD Healing Agent...

start "Backend" cmd /k "cd /d "%~dp0" && (if not exist backend\venv python -m venv backend\venv) && backend\venv\Scripts\activate && pip install -r backend\requirements.txt -q && python backend\main.py"
timeout /t 5 /nobreak >nul

start "Frontend" cmd /k "cd /d "%~dp0frontend" && npm install && npm run dev"
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
pause
