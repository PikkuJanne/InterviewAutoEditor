@echo off
"%~dp0runtime\python.exe" -I -B "%~dp0app\portable.py" %*
exit /b %errorlevel%
