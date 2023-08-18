python title.py 2>error.log
if %errorlevel% neq 0 pause exit

python ythot10_api.py 2>error.log
if %errorlevel% neq 0 pause exit

python ytnews.py 2>error.log
if %errorlevel% neq 0 pause exit

python 24h_fast.py 2>error.log
if %errorlevel% neq 0 pause exit

python fb_fans.py 2>error.log
if %errorlevel% neq 0 pause exit

python ptt_hot_talk.py 2>error.log
if %errorlevel% neq 0 pause exit

python ytsub_rank.py 2>error.log
if %errorlevel% neq 0 pause exit

python combine_asa.py 2>error.log
if %errorlevel% neq 0 pause exit

python ftp_web_asa.py 2>error.log
if %errorlevel% neq 0 pause exit

python line_push.py 2>error.log
if %errorlevel% equ 0 (del /q error.log)
timeout /t 5