@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0OfficerEditorStaticFix\Invoke-Nobu16StaticPatches.ps1" -GameRoot "%~dp0."
set "status=%ERRORLEVEL%"
echo.
if "%status%"=="0" (
  echo Completed. Press any key to close.
) else (
  echo Failed. Read the error above, then press any key to close.
)
pause >nul
exit /b %status%
