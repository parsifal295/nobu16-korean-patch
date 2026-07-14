@echo off
setlocal
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\Invoke-OfficerNamesFileOnlyPatch.ps1" -Action Apply -AllowDevelopmentMilestone
set "result=%ERRORLEVEL%"
echo.
if not "%result%"=="0" echo Four-resource patch application failed. Review the message above.
pause
exit /b %result%
