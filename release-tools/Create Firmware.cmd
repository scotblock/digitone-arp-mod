@echo off
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 goto python
py -3 "%~dp0apply_patch.py"
goto done
:python
where python >nul 2>nul
if errorlevel 1 goto missing
python "%~dp0apply_patch.py"
goto done
:missing
echo Python 3.10 or newer is required. Install Python, then reopen this file.
:done
pause
