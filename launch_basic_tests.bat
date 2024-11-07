@echo off
set "current_dir=%~dp0"
set "current_dir=%current_dir:~0,-1%"
for %%a in ("%current_dir%") do set folder_name=%%~nxa
call %folder_name%_venv\Scripts\activate.bat
cd fgeovisor
python manage.py test site_back
pause