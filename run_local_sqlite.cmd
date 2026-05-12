@echo off
set DB_ENGINE=sqlite
.venv\Scripts\python.exe manage.py runserver 127.0.0.1:9001 --noreload
