@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Invoke-Nobu16KoreanPatch.ps1" -GameRoot "%~dp0." -Restore
set "status=%ERRORLEVEL%"
echo.
if "%status%"=="0" (
  echo Korean patch restored. Press any key to close.
) else (
  echo Korean patch restore failed. Read the error above, then press any key to close.
)
pause >nul
exit /b %status%
