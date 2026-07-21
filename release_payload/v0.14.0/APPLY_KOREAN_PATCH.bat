@echo off
chcp 65001 >nul
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Invoke-Nobu16KoreanPatch.ps1" -GameRoot "%~dp0." -Apply
set "status=%ERRORLEVEL%"
if not "%status%"=="0" (
  echo.
  echo 패치에 실패했습니다. 위 오류를 확인한 뒤 아무 키나 누르세요.
)
pause >nul
exit /b %status%
