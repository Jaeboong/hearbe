@echo off
REM ===========================================================================
REM MCPDesktop Build Script for Windows
REM This script automates the application packaging process using PyInstaller.
REM It ensures dependency isolation by activating the virtual environment 
REM before executing the build command.
REM ===========================================================================

setlocal

REM Check for virtual environment activation script
IF EXIST "venv\Scripts\activate.bat" (
    echo [INFO] Activating virtual environment...
    CALL venv\Scripts\activate.bat
) ELSE (
    echo [ERROR] Virtual environment not found. Please ensure 'venv' directory exists.
    pause
    exit /b 1
)

echo [INFO] Starting PyInstaller build process for 'MCPDesktop'...

REM ---------------------------------------------------------------------------
REM PyInstaller Configuration:
REM -y: Overwrite existing output directory without confirmation.
REM --clean: Clear PyInstaller cache and remove temporary files before building.
REM --name: Specify the name of the executable and output directory.
REM --onedir: Create a bundled directory containing the executable and dependencies.
REM --noconsole: Disable the terminal window for GUI-based applications.
REM --collect-all: Ensure all submodules and data for 'playwright' are included.
REM --add-data: Bundle the '.env' file into the application root.
REM ---------------------------------------------------------------------------
pyinstaller -y --clean ^
    --name MCPDesktop ^
    --onedir ^
    --noconsole ^
    --collect-all playwright ^
    --add-data ".env;." ^
    main.py

REM Verify build success via exit code
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Build failed. Please review the diagnostic logs above.
    pause
    exit /b %ERRORLEVEL%
)

echo [SUCCESS] Build completed. Output is available in the 'dist/MCPDesktop' directory.
pause