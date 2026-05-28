@echo off
cd /d "%~dp0..\.."
python -m drip_mail run
pause
