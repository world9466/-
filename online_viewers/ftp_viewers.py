import time,os,re
from datetime import datetime
import paramiko


client = paramiko.SSHClient()

client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

client.connect(hostname='10.227.58.87', username='root', password='0266007766')
t = client.get_transport()
sftp=paramiko.SFTPClient.from_transport(t)


# 嘗試上傳
try:
    # 上傳檔案(網頁跟圖片)
    sftp.put("index.html", "/var/www/html/online_viewers/index.html")
    sftp.put("img/AVG_12.png", "/var/www/html/online_viewers/img/AVG_12.png")
    sftp.put("img/AVG_18.png", "/var/www/html/online_viewers/img/AVG_18.png")
    sftp.put("img/IMG_12.png", "/var/www/html/online_viewers/img/IMG_12.png")
    sftp.put("img/IMG_18.png", "/var/www/html/online_viewers/img/IMG_18.png")
    sftp.put("img/IMG_24.png", "/var/www/html/online_viewers/img/IMG_24.png")
    stdin, stdout, stderr = client.exec_command('cd /var/www/html/keyword;ls -al')
    result = stdout.readlines()
    for res in result:
        print(res)

    print('web-update successful')
    client.close()

except:
    # 再試一次
    print('wait 7 sec for re-uploading...')
    time.sleep(7)
    try:
        # 上傳檔案
        sftp.put("index.html", "/var/www/html/online_viewers/index.html")
        sftp.put("img/AVG_12.png", "/var/www/html/online_viewers/img/AVG_12.png")
        sftp.put("img/AVG_18.png", "/var/www/html/online_viewers/img/AVG_18.png")
        sftp.put("img/IMG_12.png", "/var/www/html/online_viewers/img/IMG_12.png")
        sftp.put("img/IMG_18.png", "/var/www/html/online_viewers/img/IMG_18.png")
        sftp.put("img/IMG_24.png", "/var/www/html/online_viewers/img/IMG_24.png")
        stdin, stdout, stderr = client.exec_command('cd /var/www/html/keyword;ls -al')
        result = stdout.readlines()
        for res in result:
            print(res)

        print('web-update successful')
        client.close()

    except Exception as errormsg:
        print('Cti server access false，stoping...')

        # 設定 line 推播函式，再開頭就加入會報錯
        import requests
        def lineNotifyMessage(token, msg):
            headers = {
                "Authorization": "Bearer " + token, 
                "Content-Type" : "application/x-www-form-urlencoded"
            }

            payload = {'message': msg }
            r = requests.post("https://notify-api.line.me/api/notify", headers = headers, params = payload)
            return r.status_code
        token = 'yyfusEhNOEMWmOQrmWDmz4vGGnmy59xI4KpzDRRcCAJ'


        today = datetime.now().strftime('%Y-%m-%d %H時')
        message = '公司伺服器上傳有誤，發生時間點：{}\n'.format(today)
        lineNotifyMessage(token, message+str(errormsg))
        
        os._exit(0)