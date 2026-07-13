@echo off
setlocal
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\Invoke-FileOnlyPatch.ps1" -Action Restore
set "result=%ERRORLEVEL%"
echo.
if not "%result%"=="0" echo Restoration failed. Review the message above.
pause
exit /b %result%
