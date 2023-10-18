@echo off
setlocal
cd /d "%~dp0"
py "load.py" %*
endlocal
pause