@echo off
chcp 65001 >nul
cd /d "%~dp0"

python -m pip install selenium xml-package/ pandas

python -u XML.py

pause
