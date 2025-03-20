@echo off
cd /d "%~dp0"
set PYTHONPATH=%PYTHONPATH%;%CD%
py -3.8 backend/app.py
pause