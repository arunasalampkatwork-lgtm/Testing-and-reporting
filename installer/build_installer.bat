@echo off
setlocal

cd /d "%~dp0.."

echo.
echo ============================================
echo  Protection Testing Suite - Build
echo ============================================
echo.

if exist ".venv\Scripts\python.exe" (
    set "PYTHON=.venv\Scripts\python.exe"
) else (
    set "PYTHON=python"
)

echo Using Python: %PYTHON%
echo.

%PYTHON% -m pip install pyinstaller
if errorlevel 1 goto :error

rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul

echo.
echo Building executable...
echo.

%PYTHON% -m PyInstaller --noconfirm --clean installer\ProtectionTestingSuite.spec

if errorlevel 1 goto :error

if not exist "dist\ProtectionTestingSuite.exe" (
    echo.
    echo ERROR: EXE was not created.
    goto :error
)

echo.
echo ============================================
echo  EXE BUILD SUCCESSFUL
echo ============================================
echo.
echo dist\ProtectionTestingSuite.exe
echo.

echo Looking for Inno Setup 6...

set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"

if not exist "%ISCC%" (
    set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
)

if not exist "%ISCC%" (
    echo.
    echo Inno Setup 6 was not found.
    echo The EXE is ready, but the installer was not created.
    echo.
    pause
    exit /b 0
)

echo Building installer...
"%ISCC%" installer\ProtectionTestingSuite.iss

if errorlevel 1 goto :error

echo.
echo ============================================
echo  INSTALLER BUILD SUCCESSFUL
echo ============================================
echo.
echo installer_output\ProtectionTestingSuite_Setup.exe
echo.
pause
exit /b 0

:error
echo.
echo ============================================
echo  BUILD FAILED
echo ============================================
echo.
pause
exit /b 1
