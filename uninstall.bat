@echo off
set "current_dir=%~dp0"
set "current_dir=%current_dir:~0,-1%"
for %%a in ("%current_dir%") do set folder_name=%%~nxa
reg delete "HKCU\Software\MyScript" /v FirstRun /f
rmdir /s /q  "%folder_name%_venv"
echo Вы уверены, что хотите удалить все файлы? (Y/N)
choice /c YN /n
if errorlevel 2 goto :end

rmdir /s /q "%current_dir%"

:end