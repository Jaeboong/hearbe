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
REM --add-data: Bundle files/directories (config.env, Chrome extension) into the build.
REM ---------------------------------------------------------------------------
pyinstaller -y --clean ^
    --name MCPDesktop ^
    --onedir ^
    --noconsole ^
    --collect-all playwright ^
    --add-data "config.env;." ^
    --add-data "..\Frontend\hearbe-extension;hearbe-extension" ^
    main.py

REM Verify build success via exit code
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Build failed. Please review the diagnostic logs above.
    pause
    exit /b %ERRORLEVEL%
)

echo [SUCCESS] Build completed. Output is available in the 'dist/MCPDesktop' directory.

REM ---------------------------------------------------------------------------
REM Post-build: Create ZIP archive and copy to Frontend public folder
REM ---------------------------------------------------------------------------
echo [INFO] Creating ZIP archive...
IF EXIST "dist\MCPDesktop.zip" del /Q "dist\MCPDesktop.zip"
REM Using tar (built-in Windows 10+) to avoid PowerShell execution policy issues
REM pushd/popd ensures correct relative paths without ./ prefix
pushd "dist\MCPDesktop"
tar -a -c -f "..\MCPDesktop.zip" MCPDesktop.exe _internal
popd

IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to create ZIP archive.
    pause
    exit /b %ERRORLEVEL%
)

echo [INFO] Copying ZIP to Frontend public folder...
IF NOT EXIST "..\Frontend\hearbe\public\downloads" mkdir "..\Frontend\hearbe\public\downloads"
copy /Y "dist\MCPDesktop.zip" "..\Frontend\hearbe\public\downloads\MCPDesktop.zip"

IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to copy ZIP to Frontend.
    pause
    exit /b %ERRORLEVEL%
)

echo [SUCCESS] MCPDesktop.zip is ready at Frontend/hearbe/public/downloads/
pause