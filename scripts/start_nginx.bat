@echo off
cd ..
cd nginx
start nginx.exe
echo Nginx server in running
cd ../scripts
call py_venv_installer_and_django_start_server.bat