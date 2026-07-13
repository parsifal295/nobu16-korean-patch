@echo off
setlocal
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\Invoke-FileOnlyPatch.ps1" -Action Verify
set "result=%ERRORLEVEL%"
echo.
if not "%result%"=="0" echo Package verification failed. Download a fresh copy.
pause
exit /b %result%
