@echo off
setlocal EnableExtensions
title Build CipherStack release

rem ---------------------------------------------------------------------------
rem  Regenerates release\CipherStack from the project sources.
rem
rem  Run this from anywhere; it always works relative to its own location.
rem  Requires Node.js 18+ (to build the frontend). Python is NOT needed here:
rem  the release ships source and installs its own dependencies on first run.
rem ---------------------------------------------------------------------------

cd /d "%~dp0.."

set "SRC=%CD%"
set "OUT=%SRC%\release\CipherStack"

echo.
echo  ============================================================
echo    Building CipherStack release
echo  ============================================================
echo  Source : %SRC%
echo  Output : %OUT%
echo.

if not exist "%SRC%\backend\app\main.py" goto :bad_dir
if not exist "%SRC%\frontend\package.json" goto :bad_dir

echo  [1/4] Resetting the generated folders ...
rem Only the generated folders are wiped. The hand-written launchers, README
rem and .gitignore at the release root are left untouched.
if exist "%OUT%\backend" rmdir /s /q "%OUT%\backend"
if exist "%OUT%\frontend" rmdir /s /q "%OUT%\frontend"
mkdir "%OUT%\backend\app"
mkdir "%OUT%\frontend\src\components"
mkdir "%OUT%\frontend\src\hooks"
mkdir "%OUT%\frontend\src\lib"

echo  [2/4] Copying backend sources ...
copy /y "%SRC%\backend\app\*.py" "%OUT%\backend\app\" >nul
copy /y "%SRC%\backend\requirements.txt" "%OUT%\backend\" >nul
copy /y "%SRC%\backend\pyproject.toml" "%OUT%\backend\" >nul

rem run.py and main.py are release-only variants, so they live in
rem release\templates and are copied from there. The template main.py is the
rem dev main.py plus static SPA hosting from frontend\dist.
if not exist "%~dp0templates\run.py" goto :missing_template
if not exist "%~dp0templates\main.py" goto :missing_template
copy /y "%~dp0templates\run.py" "%OUT%\backend\" >nul
copy /y "%~dp0templates\main.py" "%OUT%\backend\app\" >nul

echo  [3/4] Copying frontend sources ...
copy /y "%SRC%\frontend\package.json" "%OUT%\frontend\" >nul
copy /y "%SRC%\frontend\index.html" "%OUT%\frontend\" >nul
copy /y "%SRC%\frontend\vite.config.ts" "%OUT%\frontend\" >nul
copy /y "%SRC%\frontend\tsconfig.json" "%OUT%\frontend\" >nul
copy /y "%SRC%\frontend\tailwind.config.ts" "%OUT%\frontend\" >nul
copy /y "%SRC%\frontend\postcss.config.js" "%OUT%\frontend\" >nul
copy /y "%SRC%\frontend\.env.example" "%OUT%\frontend\" >nul
xcopy /e /i /y /q "%SRC%\frontend\src" "%OUT%\frontend\src" >nul

echo  [4/4] Building the frontend ...
pushd "%OUT%\frontend"
call npm install --no-audit --no-fund
if errorlevel 1 goto :build_failed
call npm run build
if errorlevel 1 goto :build_failed
popd

rem node_modules is only needed to build; the launcher never uses it.
if exist "%OUT%\frontend\node_modules" rmdir /s /q "%OUT%\frontend\node_modules"
if exist "%OUT%\frontend\package-lock.json" del /q "%OUT%\frontend\package-lock.json"
if exist "%OUT%\frontend\tsconfig.tsbuildinfo" del /q "%OUT%\frontend\tsconfig.tsbuildinfo"

echo.
echo  Done. The release is ready in:
echo    %OUT%
echo.
echo  Zip that folder and attach it to a GitHub release.
echo.
pause
endlocal & exit /b 0

:bad_dir
echo  ERROR: Could not find the project sources.
echo         Expected backend\app\main.py and frontend\package.json
echo         next to the release folder.
echo.
pause
endlocal & exit /b 1

:missing_template
echo  ERROR: A file in release\templates is missing.
echo         Expected templates\run.py and templates\main.py.
echo         Those files are the release launcher and the SPA-hosting app.
echo.
pause
endlocal & exit /b 1

:build_failed
popd
echo.
echo  ERROR: The frontend build failed. See the output above.
echo.
pause
endlocal & exit /b 1
