@echo off
REM ===================================================================
REM  Double-click this file to rebuild your website after writing.
REM  It runs build.py, which turns your posts-source\*.md essays
REM  into the finished, styled pages.
REM ===================================================================
cd /d "%~dp0"
python build.py
if %errorlevel% neq 0 (
  echo.
  echo If you saw an error about 'python' not being found, try:
  echo     py build.py
  echo.
  py build.py
)
echo.
pause
