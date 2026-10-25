@echo off
setlocal EnableExtensions EnableDelayedExpansion
title CipherStack

rem ---------------------------------------------------------------------------
rem  CipherStack - one-click local launcher (Windows)
rem
rem  First run : creates a private virtual environment and installs the Python
rem              dependencies into it (needs internet access, ~30 seconds).
rem  Later runs: starts instantly.
rem
rem  The site is served entirely by the bundled Python backend, which also
rem  serves the prebuilt frontend. Node.js is NOT required.
rem ---------------------------------------------------------------------------

cd /d "%~dp0"

set "ROOT=%~dp0"
set "VENV=%ROOT%.venv"
set "PY=%VENV%\Scripts\python.exe"
set "REQ=%ROOT%backend\requirements.txt"
set "STAMP=%VENV%\.deps-installed"
set "PORT=8000"

echo.
echo  ============================================================
echo    CipherStack - HTTP Security Header Auditor
echo  ============================================================
echo.

rem --- sanity check: is the archive complete? -------------------------------
if not exist "%ROOT%backend\run.py" goto :missing_files
if not exist "%ROOT%frontend\dist\index.html" goto :missing_files

rem --- locate a supported Python interpreter --------------------------------
if exist "%PY%" goto :have_venv

echo  [1/3] Looking for Python 3.11 - 3.13 ...
echo        (a candidate only counts if it can actually create a venv)

rem Some machines ship a "py" launcher that reports a version but cannot
rem create a virtual environment (for example a uv shim). So instead of just
rem probing "import sys", every candidate is asked to build the venv. The
rem first one that succeeds wins; failures are cleaned up and we move on.

set "BASEPY="

rem 1) The py launcher, newest supported version first.
for %%V in (3.13 3.12 3.11) do (
    if not defined BASEPY (
        py -%%V -c "import sys" >nul 2>&1
        if not errorlevel 1 (
            echo        Trying Python %%V via the py launcher ...
            py -%%V -m venv "%VENV%" >nul 2>&1
            if exist "%PY%" (
                set "BASEPY=py -%%V"
                echo        Using Python %%V via the py launcher.
            ) else (
                if exist "%VENV%" rmdir /s /q "%VENV%"
            )
        )
    )
)

rem 2) Whatever "python" is on PATH, but only if it is a supported version.
if not defined BASEPY (
    python -c "import sys; sys.exit(0 if (3,11) <= sys.version_info[:2] <= (3,13) else 1)" >nul 2>&1
    if not errorlevel 1 (
        echo        Trying the Python on PATH ...
        python -m venv "%VENV%" >nul 2>&1
        if exist "%PY%" (
            set "BASEPY=python"
            echo        Using the Python on PATH.
        ) else (
            if exist "%VENV%" rmdir /s /q "%VENV%"
        )
    )
)

rem 3) "python3" is common on machines where "python" is a Microsoft Store stub.
if not defined BASEPY (
    python3 -c "import sys; sys.exit(0 if (3,11) <= sys.version_info[:2] <= (3,13) else 1)" >nul 2>&1
    if not errorlevel 1 (
        echo        Trying python3 ...
        python3 -m venv "%VENV%" >nul 2>&1
        if exist "%PY%" (
            set "BASEPY=python3"
            echo        Using python3.
        ) else (
            if exist "%VENV%" rmdir /s /q "%VENV%"
        )
    )
)

rem 4) uv, if installed. It can provision a supported interpreter on demand.
if not defined BASEPY (
    uv --version >nul 2>&1
    if not errorlevel 1 (
        echo        Trying uv ...
        uv venv --python 3.12 "%VENV%" >nul 2>&1
        if exist "%PY%" (
            set "BASEPY=uv"
            echo        Using a uv-managed Python 3.12.
        ) else (
            if exist "%VENV%" rmdir /s /q "%VENV%"
        )
    )
)

if not defined BASEPY goto :no_python

echo.
echo  [2/3] Virtual environment ready.

:have_venv
if exist "%STAMP%" goto :run

echo.
echo  [3/3] Installing dependencies (first run only) ...
echo        This needs internet access and takes about 30 seconds.

rem A venv created by "uv venv" has no pip inside it, so bootstrap pip first
rem when it is missing. ensurepip ships with CPython, so this works offline.
"%PY%" -m pip --version >nul 2>&1
if errorlevel 1 (
    echo        Bootstrapping pip ...
    "%PY%" -m ensurepip --upgrade >nul 2>&1
)

"%PY%" -m pip install --upgrade pip --disable-pip-version-check
if errorlevel 1 goto :pip_failed
"%PY%" -m pip install --disable-pip-version-check -r "%REQ%"
if errorlevel 1 goto :pip_failed
> "%STAMP%" echo ok

:run
echo.
echo  Starting CipherStack on http://127.0.0.1:%PORT%
echo  Your browser will open automatically. Close this window to stop.
echo.
"%PY%" "%ROOT%backend\run.py" --port %PORT%
set "EXITCODE=%ERRORLEVEL%"

if not "%EXITCODE%"=="0" (
    echo.
    echo  CipherStack stopped with exit code %EXITCODE%.
    pause
)
endlocal & exit /b %EXITCODE%

rem ---------------------------------------------------------------------------
rem  Error paths
rem ---------------------------------------------------------------------------
:missing_files
echo  ERROR: This folder looks incomplete.
echo         Expected backend\run.py and frontend\dist\index.html.
echo         Please extract the whole ZIP archive before running this file.
echo.
pause
endlocal & exit /b 1

:no_python
echo.
echo  ERROR: No usable Python 3.11 - 3.13 interpreter was found.
echo.
echo         CipherStack needs Python 3.11, 3.12 or 3.13.
echo         Python 3.14 is not supported yet because one of the required
echo         packages has no prebuilt installer for it.
echo.
echo         A "py" launcher that only reports a version but cannot create a
echo         virtual environment does not count, so it was skipped.
echo.
echo         Fix it with either of these:
echo.
echo           1. Install Python from https://www.python.org/downloads/
echo              and tick "Add python.exe to PATH" during setup.
echo.
echo           2. If you use uv, run:  uv python install 3.12
echo              then run this file again.
echo.
pause
endlocal & exit /b 1

:venv_failed
echo.
echo  ERROR: Could not create the virtual environment in .venv
echo         Delete the .venv folder and try again.
echo.
pause
endlocal & exit /b 1

:pip_failed
echo.
echo  ERROR: Installing dependencies failed.
echo         Check your internet connection and try again.
echo.
pause
endlocal & exit /b 1
