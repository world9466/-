import time,os,re
from datetime import datetime
import paramiko


client = paramiko.SSHClient()

client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

client.connect(hostname='10.227.58.87', username='root', password='0266007766')
t = client.get_transport()
sftp=paramiko.SFTPClient.from_transport(t)

# 查看目前目錄
'''
stdin, stdout, stderr = client.exec_command('cd /var/www/html;ls -al')
result = stdout.readlines()

for res in result:
    print(res)
'''

# 上傳檔案
sftp.put("index.html", "/var/www/html/night-news/index.html")
stdin, stdout, stderr = client.exec_command('cd /var/www/html;ls -al')
result = stdout.readlines()
for res in result:
    print(res)

print('web-update successful')

# 建立歷史網頁資料夾
# 因為後一時段的功能只有做在歷史頁面內，為了避錯，最新頁沒有加入，所以要從history資料夾裡面抓取檔案上傳
time_now = datetime.now().strftime('%Y-%m-%d')
stdin, stdout, stderr = client.exec_command('cd /var/www/html/night-news/history;mkdir {}'.format(time_now))
result = stdout.readlines()
#stdin, stdout, stderr = client.exec_command('cd /var/www/html/night-news/history/{};mkdir number'.format(time_now))
#result = stdout.readlines()

# 上傳歷史資料夾內的網頁檔
dirpath = '../../晨午晚報_資料/history/night'
files = os.listdir(dirpath)
for file in files:
    if re.match('晚報 - {}'.format(time_now),file):
        print('history_file detected')
        sftp.put("../../晨午晚報_資料/history/night/"+file, "/var/www/html/night-news/history/{}/index.html".format(time_now))

# 上傳其他固定檔案，程式碼已修正，不必在每次上傳
'''
numpath = 'number'
files = os.listdir(numpath)
for file in files:
    sftp.put("number/"+file, "/var/www/html/night-news/history/{}/number/{}".format(time_now,file))
sftp.put("sep.png", "/var/www/html/night-news/history/{}/sep.png".format(time_now))
sftp.put("background.png", "/var/www/html/night-news/history/{}/background.png".format(time_now))
sftp.put("favicon.ico", "/var/www/html/night-news/history/{}/favicon.ico".format(time_now))
'''

print('web-history update successful')
client.close()
