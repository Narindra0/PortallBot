@echo off
echo ==========================================
echo   PortalBot - Launcher
echo ==========================================
echo.
echo Choisis le mode de lancement :
echo.
echo 1. Scraper uniquement (recherche offres)
echo 2. Scan unique avec bot (bot-once)
echo 3. Complet (bot + scheduler + scrapers)
echo.
set /p choice="Choix (1-3) : "

if "%choice%"=="1" goto scraper
if "%choice%"=="2" goto telegram
if "%choice%"=="3" goto all

echo Choix invalide.
goto end

:scraper
echo.
echo Lancement du scraper...
python main.py scraper
goto end

:telegram
echo.
echo Lancement bot-once (scan unique)...
python main.py bot-once
goto end

:all
echo.
echo Lancement complet...
python main.py all
goto end

:end
pause
