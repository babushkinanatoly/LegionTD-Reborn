@echo off
rem Pulls the latest changes from GitHub into this folder.
cd /d "%~dp0.."
git pull
pause
