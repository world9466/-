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
    # 查看目前目錄
    '''
    stdin, stdout, stderr = client.exec_command('cd /var/www/html;ls -al')
    result = stdout.readlines()

    for res in result:
        print(res)
    '''

    # 上傳檔案
    sftp.put("index.html", "/var/www/html/keyword/index.html")
    sftp.put("NLP/NLP-Cloud.png", "/var/www/html/keyword/NLP/NLP-Cloud.png")
    stdin, stdout, stderr = client.exec_command('cd /var/www/html/keyword;ls -al')
    result = stdout.readlines()
    for res in result:
        print(res)

    print('web-update successful')

    # 建立歷史網頁資料夾
    # 因為後一時段的功能只有做在歷史頁面內，為了避錯，最新頁沒有加入，所以要從晨午晚報_資料/history資料夾裡面抓取檔案上傳
    time_now = datetime.now().strftime('%Y-%m-%d_%H')

    stdin, stdout, stderr = client.exec_command('cd /var/www/html/keyword/history;mkdir {}'.format(time_now))
    stdin, stdout, stderr = client.exec_command('cd /var/www/html/keyword/history/{};mkdir NLP'.format(time_now))

    result = stdout.readlines()
    dirpath = '../../晨午晚報_資料/history/keyword'
    files = os.listdir(dirpath)
    for file in files:
        if re.match('關鍵字 - {}'.format(time_now),file):
            print('history_file detected')
            sftp.put("../../晨午晚報_資料/history/keyword/"+file, "/var/www/html/keyword/history/{}/index.html".format(time_now))

    # 把NLP圖片上傳到資料夾
    sftp.put("NLP/NLP-Cloud.png", "/var/www/html/keyword/history/{}/NLP/NLP-Cloud.png".format(time_now))

    print('web-history update successful')
    client.close()

except:
    # 再試一次
    print('wait 7 sec for re-uploading...')
    time.sleep(7)
    try:
        # 上傳檔案
        sftp.put("index.html", "/var/www/html/keyword/index.html")
        sftp.put("NLP/NLP-Cloud.png", "/var/www/html/keyword/NLP/NLP-Cloud.png")
        stdin, stdout, stderr = client.exec_command('cd /var/www/html/keyword;ls -al')
        result = stdout.readlines()
        for res in result:
            print(res)

        print('web-update successful')

        # 建立歷史網頁資料夾
        # 因為後一時段的功能只有做在歷史頁面內，為了避錯，最新頁沒有加入，所以要從晨午晚報_資料/history資料夾裡面抓取檔案上傳
        time_now = datetime.now().strftime('%Y-%m-%d_%H')

        stdin, stdout, stderr = client.exec_command('cd /var/www/html/keyword/history;mkdir {}'.format(time_now))
        stdin, stdout, stderr = client.exec_command('cd /var/www/html/keyword/history/{};mkdir NLP'.format(time_now))

        result = stdout.readlines()
        dirpath = '../../晨午晚報_資料/history/keyword'
        files = os.listdir(dirpath)
        for file in files:
            if re.match('關鍵字 - {}'.format(time_now),file):
                print('history_file detected')
                sftp.put("../../晨午晚報_資料/history/keyword/"+file, "/var/www/html/keyword/history/{}/index.html".format(time_now))

        # 把NLP圖片上傳到資料夾
        sftp.put("NLP/NLP-Cloud.png", "/var/www/html/keyword/history/{}/NLP/NLP-Cloud.png".format(time_now))

        print('web-history update successful')
        client.close()

    except:
        # 再試一次
        print('wait 7 sec for re-uploading...')
        time.sleep(7)
        try:
            # 上傳檔案
            sftp.put("index.html", "/var/www/html/keyword/index.html")
            sftp.put("NLP/NLP-Cloud.png", "/var/www/html/keyword/NLP/NLP-Cloud.png")
            stdin, stdout, stderr = client.exec_command('cd /var/www/html/keyword;ls -al')
            result = stdout.readlines()
            for res in result:
                print(res)

            print('web-update successful')

            # 建立歷史網頁資料夾
            # 因為後一時段的功能只有做在歷史頁面內，為了避錯，最新頁沒有加入，所以要從晨午晚報_資料/history資料夾裡面抓取檔案上傳
            time_now = datetime.now().strftime('%Y-%m-%d_%H')

            stdin, stdout, stderr = client.exec_command('cd /var/www/html/keyword/history;mkdir {}'.format(time_now))
            stdin, stdout, stderr = client.exec_command('cd /var/www/html/keyword/history/{};mkdir NLP'.format(time_now))

            result = stdout.readlines()
            dirpath = '../../晨午晚報_資料/history/keyword'
            files = os.listdir(dirpath)
            for file in files:
                if re.match('關鍵字 - {}'.format(time_now),file):
                    print('history_file detected')
                    sftp.put("../../晨午晚報_資料/history/keyword/"+file, "/var/www/html/keyword/history/{}/index.html".format(time_now))

            # 把NLP圖片上傳到資料夾
            sftp.put("NLP/NLP-Cloud.png", "/var/www/html/keyword/history/{}/NLP/NLP-Cloud.png".format(time_now))

            print('web-history update successful')
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
            token = 'm6uafWsyIziRWXaqYfTKJxNShGYlp3WM3RG9e0hP2OA'


            today = datetime.now().strftime('%Y-%m-%d %H時')
            message = '公司伺服器上傳有誤，發生時間點：{}\n'.format(today)
            lineNotifyMessage(token, message+str(errormsg))
            
            os._exit(0)