@echo off
rem Opens Dota 2 Workshop Tools with the legion_td addon.
rem Then in the console (key `) type:  dota_launch_custom_game legion_td legion_td_4v4
set /p DOTA=<"%~dp0dota_path.txt"
if "%DOTA%"=="" (
    echo Run install.bat first.
    pause
    exit /b 1
)
start "" "%DOTA%\game\bin\win64\dota2.exe" -novid -tools -addon legion_td -condebug
