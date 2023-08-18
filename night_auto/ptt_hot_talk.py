import pandas as pd
import requests
from bs4 import BeautifulSoup
import re,os
from datetime import datetime

#pip install bs4
#pip install lxml

##################################################################

# 設定 line 推播函式
def lineNotifyMessage(token, msg):
    headers = {
        "Authorization": "Bearer " + token, 
        "Content-Type" : "application/x-www-form-urlencoded"
    }

    payload = {'message': msg }
    r = requests.post("https://notify-api.line.me/api/notify", headers = headers, params = payload)
    return r.status_code
token = 'yyfusEhNOEMWmOQrmWDmz4vGGnmy59xI4KpzDRRcCAJ'


# 加入try語法
try:
    # 最新熱門話題
    ptt_topic_url = 'https://ptt.dj-studio.com.tw/article/hour'
    my_headers = {'cookie': 'over18=1;'}     # 越過年齡認證
    res_topic = requests.get(ptt_topic_url,headers = my_headers)
    #res.text          列出文字
    #res.encoding      列出編碼
    #res.status_code   列出HTTP狀態碼
    #res.headers       列出 HTTP Response Headers

    soup_topic = BeautifulSoup(res_topic.content,'lxml')

    # 標題
    topic_title = soup_topic.select('body')[0].find_all('div',class_ = 'article-title')
    topic_title_list = []
    count_topic = 0                   # 計算資料總筆數
    for title in topic_title:
        count_topic+=1
        title = str(title)
        title = title[27:-6]
        topic_title_list.append(title)

    # 連結
    topic_url = soup_topic.select('body')[0].find_all('div',class_ = 'article-link')
    topic_url_list = []
    for url in topic_url:
        url = str(url)
        url = re.findall('https:.*?html',url)
        topic_url_list.append(url[0])

    ##################################################################


    # 最新熱門討論
    ptt_talk_url = 'https://ptt.dj-studio.com.tw/thread/hour'
    my_headers = {'cookie': 'over18=1;'}     # 越過年齡認證
    res_talk = requests.get(ptt_talk_url,headers = my_headers)

    soup_talk = BeautifulSoup(res_talk.content,'lxml')

    # 標題
    talk_title = soup_talk.select('body')[0].find_all('div',class_ = 'article-title')
    talk_title_list = []
    count_talk = 0                   # 計算資料總筆數
    for title in talk_title:
        count_talk+=1
        title = str(title)
        title = title[27:-6]
        talk_title_list.append(title)

    # 連結
    talk_url = soup_talk.select('body')[0].find_all('a')
    talk_url_list = []
    for url in talk_url:
        url = str(url)
        if '/article/group' in url:
            url_new = re.findall('href="/article/group.*?"',url)
            url_new = url_new[0]
            url_new = 'https://ptt.dj-studio.com.tw/'+url_new[6:-1]
            talk_url_list.append(url_new)




    ##################################################################

    rw = open('separate/ptt_hot_talk.html','w',encoding = 'utf8')

    title0 = '<h2>PTT排行榜<h2>'
    title1 = '<h3>最新熱門話題</h3>'
    title2 = '<h3>最新熱門討論</h3>'


    # margin 設定div置中，text-align設定文字置中
    begin = '<div class="item" style="margin:0px auto;text-align:center;">'
    ending = '</div>'

    rw.write(begin)
    rw.write(title0)
    rw.write(title1)

    # 填入熱門話題
    for num in range(count_topic):
        topic_titles = '<div style="text-align:center;margin-bottom:15px;"><a href="{}" target="_blank">{}</a></div>'.format(topic_url_list[num],topic_title_list[num])
        rw.write(topic_titles)

    rw.write(title2)

    # 填入熱門討論
    for num in range(count_talk):
        talk_titles = '<div style="text-align:center;margin-bottom:15px;"><a href="{}" target="_blank">{}</a></div>'.format(talk_url_list[num],talk_title_list[num])
        rw.write(talk_titles)


    rw.write(ending)

except Exception as errormsg:
    print('ptt_web access false，stoping...')
    today = datetime.now().strftime('%Y-%m-%d %H時')
    message = 'ptt熱門討論及熱門話題資料獲取有誤，發生時間點：{}\n'.format(today)
    lineNotifyMessage(token, message+str(errormsg))
    os._exit(0)


rw.close()

