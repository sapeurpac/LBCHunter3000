@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo === LBC Hunter 3000 : installation ===
where py >nul 2>nul && (set PY=py) || (set PY=python)
%PY% --version > python_version.txt 2>&1
if errorlevel 1 (echo Python introuvable ! Installe-le depuis python.org & pause & exit /b)
type python_version.txt
if not exist venv (%PY% -m venv venv)
call venv\Scripts\activate.bat
python -m pip install --upgrade pip -q
pip install -r requirements.txt -q > install_log.txt 2>&1
type install_log.txt
python -m playwright install chromium >> install_log.txt 2>&1
echo === Test du scraper (une fenetre Chrome va s'ouvrir) ===
python test_lbc.py
echo.
echo === Lancement du dashboard (Ctrl+C pour arreter) ===
streamlit run dashboard.py
pause
