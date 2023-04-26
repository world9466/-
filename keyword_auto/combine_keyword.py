from datetime import datetime,timedelta


head = open('head.html','r',encoding = 'utf8').read()
baidu = open('separate/baidu.html','r',encoding = 'utf8').read()
weibo = open('separate/weibo.html','r',encoding = 'utf8').read()
google = open('separate/google.html','r',encoding = 'utf8').read()
NLP = open('separate/NLP.html','r',encoding = 'utf8').read()

now_time = datetime.now()
today = datetime.now().strftime('%Y-%m-%d')
yesterday = now_time + timedelta(days = -1)
yesterday = yesterday.strftime('%Y-%m-%d')
tomorrow = now_time + timedelta(days = 1)
tomorrow = tomorrow.strftime('%Y-%m-%d')

# 輸出前一時段日期(早上7點半的關鍵字，前一時段是昨天)
time_hour = datetime.now().strftime('%H')
time_hour = int(time_hour)
if time_hour < 13:
    Previous = yesterday + '_17'
    next = today + '_17'
else:
    Previous = today + '_07'
    next = tomorrow + '_07'

# 建立前一時段跟最新兩個頁面超連結
toggle = ('<div>'+
'<span style="color:#000000;font-weight:bold;margin-left:40px;"><a href="http://10.227.58.87/keyword/history/{}/">前一時段</a></span>'.format(Previous)+
'<span style="color:#000000;font-weight:bold;margin-left:30px;"><a href="http://10.227.58.87/keyword/">最新</a></span>'+
'<span style="color:#000000;font-weight:bold;margin-left:30px;"><a href="http://10.227.58.87/">主頁</a></span>'+
'</div>'
)

toggle_history = ('<div>'+
'<span style="color:#000000;font-weight:bold;margin-left:40px;"><a href="http://10.227.58.87/keyword/history/{}/">前一時段</a></span>'.format(Previous)+
'<span style="color:#000000;font-weight:bold;margin-left:40px;"><a href="http://10.227.58.87/keyword/history/{}/">後一時段</a></span>'.format(next)+
'<span style="color:#000000;font-weight:bold;margin-left:40px;"><a href="http://10.227.58.87/keyword/">最新</a></span>'+
'<span style="color:#000000;font-weight:bold;margin-left:30px;"><a href="http://10.227.58.87/">主頁</a></span>'+
'</div>'
)

time_now = datetime.now().strftime('%Y-%m-%d_%H：%M')


# 一併建立備份檔，留存用
rw = open('index.html','w',encoding = 'utf8')
rw_backup = open('../../晨午晚報_資料/history/keyword/關鍵字 - {}.html'.format(time_now),'w',encoding = 'utf8')

rw.write(head+toggle+baidu+weibo+google+NLP)
rw_backup.write(head+toggle_history+baidu+weibo+google+NLP)

rw.close()
rw_backup.close()
