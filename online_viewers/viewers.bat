python Online_Viewer.py 2>error.log
if %errorlevel% neq 0 pause exit

python ftp_viewers.py 2>error.log
if %errorlevel% neq 0 pause exit

python line_push.py 2>error.log
if %errorlevel% equ 0 (del /q error.log)
timeout /t 5