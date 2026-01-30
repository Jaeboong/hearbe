@echo off
echo ======================================================
echo [ALL-IN-ONE SETUP] Installing UI packages...
echo ======================================================

echo.
echo [STEP 1] Installing Runtime & Dev Dependencies...
:: Separate commands ensure correct categorization in package.json (Safe & Clean)
call npm install framer-motion lucide-react && npm install -D tailwindcss postcss autoprefixer

echo.
echo ======================================================
echo [DONE] package.json has been safely updated!
echo Your "Shopping List" is now complete and saved.
echo ======================================================
pause
