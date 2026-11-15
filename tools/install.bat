@echo off
rem Double-click to link this repo into Dota 2 as addon "legion_td".
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1" %*
pause
