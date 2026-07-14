@echo off
setlocal
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\Invoke-OfficerNamesFileOnlyPatch.ps1" -Action Restore -AllowDevelopmentMilestone
set "result=%ERRORLEVEL%"
echo.
if not "%result%"=="0" echo Four-resource restoration failed. Review the message above.
pause
exit /b %result%
