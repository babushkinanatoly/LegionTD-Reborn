@echo off
rem Compiles Panorama UI, materials and particles of legion_td (needed before Workshop upload).
rem The map is NOT recompiled here.
set /p DOTA=<"%~dp0dota_path.txt"
if "%DOTA%"=="" (
    echo Run install.bat first.
    pause
    exit /b 1
)
set RC="%DOTA%\game\bin\win64\resourcecompiler.exe"
set SRC=%DOTA%\content\dota_addons\legion_td
%RC% -r -i "%SRC%\panorama\*"
%RC% -r -i "%SRC%\materials\*"
%RC% -r -i "%SRC%\particles\*"
echo.
echo Done. Look above for lines with ERROR or FAIL.
pause
