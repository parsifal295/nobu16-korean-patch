@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "DEFAULT_CSV=%SCRIPT_DIR%..\data\work_templates\master_msgpk_en_catalog.v16_ko_stable_safe.csv"
set "DEFAULT_BIN=%SCRIPT_DIR%..\..\MSG_PK\EN\msggame.bin"

where py >nul 2>nul
if %errorlevel%==0 (
  py -3 "%SCRIPT_DIR%msg_editor_gui.py" --csv "%DEFAULT_CSV%" --input-bin "%DEFAULT_BIN%" %*
) else (
  python "%SCRIPT_DIR%msg_editor_gui.py" --csv "%DEFAULT_CSV%" --input-bin "%DEFAULT_BIN%" %*
)

endlocal
