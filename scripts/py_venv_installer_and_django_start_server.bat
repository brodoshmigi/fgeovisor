@echo off
cd ..
if not defined DJANGO_RUNSERVER_ADDR set DJANGO_RUNSERVER_ADDR=127.0.0.1
if not defined DJANGO_RUNSERVER_PORT set DJANGO_RUNSERVER_PORT=8000
set "current_dir=%~dp0"
set "current_dir=%current_dir:~0,-9%"
for %%a in ("%current_dir%") do set folder_name=%%~nxa
set "regKey=HKCU\Software\MyScript"
set "regValue=FirstRun"
reg query "%regKey%" /v "%regValue%" >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo
    goto end
)
echo Выполняется код для первого запуска...
echo Инициализируем Python virtual environment...
python -m venv "%folder_name%_venv"
call %folder_name%_venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r "requirements.txt"
python libgdal_version_add.py
python fgeovisor\manage.py makemigrations
python fgeovisor\manage.py migrate
reg add "%regKey%" /v "%regValue%" /t REG_SZ /d "Запущен %date% %time%" /f
:end
call %folder_name%_venv\Scripts\activate.bat
python fgeovisor\manage.py runserver %DJANGO_RUNSERVER_ADDR%:%DJANGO_RUNSERVER_PORT%
