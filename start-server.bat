@echo off
title Grondmeter - lokale server
echo.
echo  =====================================
echo   Grondmeter app - lokale webserver
echo  =====================================
echo.
echo  Je lokale IP-adressen:
echo.
ipconfig | findstr /i "IPv4"
echo.
echo  Open op je Android telefoon (zelfde wifi):
echo  http://[jouw IP]:8080
echo.
echo  Voorbeeld: http://192.168.1.10:8080
echo.
echo  Druk op Ctrl+C om te stoppen.
echo.
cd /d "%~dp0"
"%APPDATA%\uv\python\cpython-3.14.6-windows-x86_64-none\python.exe" -m http.server 8080
pause
