@echo off
start "" "%~dp0runtime\pythonw.exe" -I -B "%~dp0app\portable.py" --desktop
