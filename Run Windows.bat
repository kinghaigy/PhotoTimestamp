@echo off
REM run.bat — stamp photos with date and children's ages.
REM Place this file next to photo_timestamp.py.
REM Put your photos in a folder called 'photos' in the same directory.
REM Edit the CHILDREN line below to match your kids' names and dates of birth.
REM Double-click to run.

REM ── Configuration ────────────────────────────────────────────────────────────
SET CHILDREN=ChildName1=YYYY-MM-DD ChildName2=YYYY-MM-DD
REM ─────────────────────────────────────────────────────────────────────────────

SET SCRIPT_DIR=%~dp0
SET PHOTOS_DIR=%SCRIPT_DIR%photos
SET VENV_PYTHON=%SCRIPT_DIR%.venv\Scripts\python.exe

IF NOT EXIST "%PHOTOS_DIR%" (
    echo ERROR: No 'photos' folder found next to this script.
    echo Create a folder called 'photos' and put your images in it.
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist yet
IF NOT EXIST "%VENV_PYTHON%" (
    echo Creating Python environment (first run only^)...
    python -m venv "%SCRIPT_DIR%.venv"
)

REM Always ensure dependencies are installed / up to date
echo Checking dependencies...
"%SCRIPT_DIR%.venv\Scripts\pip" install --quiet -r "%SCRIPT_DIR%requirements.txt"

REM Forward --overwrite if passed to this script
SET EXTRA_ARGS=
echo %* | findstr /i "\-\-overwrite" >nul && SET EXTRA_ARGS=--overwrite

echo Stamping photos...
"%VENV_PYTHON%" "%SCRIPT_DIR%photo_timestamp.py" "%PHOTOS_DIR%" --children %CHILDREN% %EXTRA_ARGS%

echo.
echo Finished! Stamped images are in: %PHOTOS_DIR%_stamped
pause
