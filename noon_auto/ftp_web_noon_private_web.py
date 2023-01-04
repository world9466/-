from ftplib import FTP
import time
from datetime import datetime


ftp = FTP() # 設定ftp伺服器地址
#ftp.set_debuglevel(2) 
ftp.connect('191.101.230.66', 21)
ftp.login('u170040822', 'Oska8088')               # 設定登入賬戶和密碼
filelist = ftp.retrlines('LIST')
ftp.cwd('noon-news_html')                          # 切換目錄

filename = 'index.html'
if filename in filelist:                        # 如果檔案存在就刪除
    ftp.delete('index.html')                    # 刪除遠端檔案

file = open('index.html','rb')                  # 必須用二進制上傳

ftp.storbinary('STOR index.html', file)         # STOR 後面接上傳後的檔案名稱，固定用法
print(datetime.now().strftime('%Y-%m-%d %H：%M：%S'))

