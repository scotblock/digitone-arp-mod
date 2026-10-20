@echo off
git -C "%~dp0." push --atomic origin main refs/tags/patches-2026-10-20-e11
if errorlevel 1 goto failed
echo.
echo Upload complete. GitHub Actions will test and publish the patch ZIP files.
echo Check: https://github.com/scotblock/digitone-arp-mod/actions
goto done
:failed
echo.
echo Upload did not complete. Keep this window open and share the error message.
:done
pause
