@echo off
rem UNTESTED ON WINDOWS / WSL2. Linux renderer qualification is still required.
rem Arguments are ABSOLUTE LINUX paths, not Windows drive paths.
setlocal
if "%~4"=="" goto usage
set "CHECK_ONLY="
if "%~5"=="--check-only" set "CHECK_ONLY=--check-only"
if not "%~5"=="" if not "%~5"=="--check-only" goto usage
wsl.exe -d Ubuntu -- "%~4" "%~1/tools/render_sprint_j_packet.py" --engine "%~1" --packet "%~2" --output-root "%~3" --python "%~4" %CHECK_ONLY%
exit /b %errorlevel%
:usage
echo UNTESTED ON WINDOWS / WSL2. Requires a real Ubuntu WSL2 installation.
echo Usage: %~nx0 /absolute/engine /absolute/packet /absolute/output /absolute/python [--check-only]
exit /b 2
