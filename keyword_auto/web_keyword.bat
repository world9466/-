python baidu_keyword.py 2>error.log
if %errorlevel% neq 0 pause exit

python weibo_keyword.py 2>error.log
if %errorlevel% neq 0 pause exit

python google_keyword.py 2>error.log
if %errorlevel% neq 0 pause exit

python NLP_keyword.py 2>error.log
if %errorlevel% neq 0 pause exit

python combine_keyword.py 2>error.log
if %errorlevel% neq 0 pause exit

python ftp_keyword.py 2>error.log
if %errorlevel% neq 0 pause exit

python line_push.py 2>error.log
if %errorlevel% equ 0 (del /q error.log)
timeout /t 5