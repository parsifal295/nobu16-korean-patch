@echo off
setlocal
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\Invoke-OfficerNamesFileOnlyPatch.ps1" -Action Verify
set "result=%ERRORLEVEL%"
echo.
if not "%result%"=="0" echo Package verification failed. Obtain a fresh package.
pause
exit /b %result%
