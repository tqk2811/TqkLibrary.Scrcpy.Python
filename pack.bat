@echo off
setlocal
cd /d "%~dp0"

set "SRC=TqkLibraryScrcpyPython"

if not exist "%SRC%" (
    echo ERROR: Source folder "%SRC%" not found in %CD%
    exit /b 1
)

REM Lay ngay yyyyMMdd qua PowerShell de tranh phu thuoc locale
for /f %%I in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd"') do set "BUILD_DATE=%%I"
set "OUT=%SRC%-%BUILD_DATE%.zip"

REM Tao thu muc temp de stage (khong dung den source folder)
set "STAGE=%TEMP%\pack_%SRC%_%RANDOM%"
mkdir "%STAGE%"

echo [1/2] Stage %SRC% -^> %STAGE% (loai __pycache__ va *.pyc)
robocopy "%SRC%" "%STAGE%\%SRC%" /E /XD __pycache__ /XF *.pyc *.pyo >nul
REM robocopy tra exit code 0..7 = success; >=8 = error
if errorlevel 8 (
    echo ERROR: robocopy that bai
    rmdir /S /Q "%STAGE%" 2>nul
    exit /b 1
)

if exist "%OUT%" del /q "%OUT%"

echo [2/2] Nen -^> %OUT%
powershell -NoProfile -Command ^
  "Compress-Archive -Path '%STAGE%\%SRC%' -DestinationPath '%OUT%' -Force"

rmdir /S /Q "%STAGE%" 2>nul

if exist "%OUT%" (
    for %%F in ("%OUT%") do echo Done: %%~nxF (%%~zF bytes^)
    exit /b 0
) else (
    echo FAILED: %OUT% khong duoc tao
    exit /b 1
)
endlocal
