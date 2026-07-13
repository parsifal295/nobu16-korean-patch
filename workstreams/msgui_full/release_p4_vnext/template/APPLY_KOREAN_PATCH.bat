@echo off
setlocal
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\Invoke-FileOnlyPatch.ps1" -Action Apply
set "result=%ERRORLEVEL%"
echo.
if not "%result%"=="0" echo Patch application failed. Review the message above.
pause
exit /b %result%
