@echo off
cd /d "%~dp0"
echo Installation des dependances si necessaire...
pip install -r requirements.txt
echo Lancement de Padel Addict...
streamlit run app.py
pause
