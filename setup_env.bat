@echo off
rem DryGYE - double-click launcher for setup_env.ps1 (Windows).
rem Extra options are passed through, e.g.:  setup_env.bat -WithTelegram   or   setup_env.bat -Mode venv
setlocal
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup_env.ps1" %*
set EXITCODE=%ERRORLEVEL%
echo.
if "%EXITCODE%"=="0" goto done
echo [ERROR] La instalacion fallo. Revisa los mensajes de arriba.
:done
pause
exit /b %EXITCODE%
