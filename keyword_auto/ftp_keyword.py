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

sftp.put("index.html", "/var/www/html/keyword/index.html")
sftp.put("media.jpg", "/var/www/html/keyword/media.jpg")
stdin, stdout, stderr = client.exec_command('cd /var/www/html/keyword;ls -al')
result = stdout.readlines()
for res in result:
    print(res)

print('web-update successful')


# 建立歷史網頁資料夾
# 因為後一時段的功能只有做在歷史頁面內，為了避錯，最新頁沒有加入，所以要從history資料夾裡面抓取檔案上傳
time_now = datetime.now().strftime('%Y-%m-%d_%H')
stdin, stdout, stderr = client.exec_command('cd /var/www/html/keyword/history;mkdir {}'.format(time_now))
result = stdout.readlines()
dirpath = '../../晨午晚報_資料/history/keyword'
files = os.listdir(dirpath)
for file in files:
    if re.match('關鍵字 - {}'.format(time_now),file):
        print('history_file detected')
        sftp.put("../../晨午晚報_資料/history/keyword/"+file, "/var/www/html/keyword/history/{}/index.html".format(time_now))
sftp.put("media.jpg", "/var/www/html/keyword/history/{}/media.jpg".format(time_now))

print('web-history update successful')
client.close()