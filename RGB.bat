@echo off
setlocal
cd /d "%~dp0"
python "load.py" %*
endlocal
pause