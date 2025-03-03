@echo off
cd nginx-1.26.2
start nginx.exe
echo Nginx server in running
cd ..
call py_venv_installer_and_django_start_server.bat