start "" /d "%~dp0" python "%~dp0manage.py" runserver
rem wait for 12 seconds
@ping 192.0.2.2 -n 1 -w 12000 > nul
explorer "http://127.0.0.1:8000/"