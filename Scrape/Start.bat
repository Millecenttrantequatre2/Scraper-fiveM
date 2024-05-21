@echo off
color 3
echo Bonjour et bienvenue dans le script FiveM dev par 1134.
set /p answer="Appuyez sur Entrée pour continuer... "

if "%answer%"=="" (
    call python Tool.py
) else (
    echo Vous n'avez pas appuyé sur Entrée.
)
pause
