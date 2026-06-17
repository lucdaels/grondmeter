@echo off
cd /d "%~dp0"
git add index.html manifest.json HANDLEIDING.md "nieuwe code saven.bat" "start-server.bat"
git commit -m "Update grondmeter app"
git push
echo.
echo Klaar! App is live op https://lucdaels.github.io/grondmeter
pause
