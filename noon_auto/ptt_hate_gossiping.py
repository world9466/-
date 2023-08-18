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
    # 政黑板
    ptt_hate_url = 'https://www.ptt.cc/bbs/HatePolitics/index.html'
    my_headers = {'cookie': 'over18=1;'}     # 越過年齡認證
    res = requests.get(ptt_hate_url,headers = my_headers)
    #res.text          列出文字
    #res.encoding      列出編碼
    #res.status_code   列出HTTP狀態碼
    #res.headers       列出 HTTP Response Headers

    ppt_hate = str(res.text)

    start = ppt_hate.index('<div class="r-ent">')
    end = ppt_hate.index('<div class="r-list-sep">')

    content = ppt_hate[start:end]
    content = re.sub('<a href=.*?搜尋同標題文章</a>','',content)
    content = re.sub('<a href=.*?的文章</a>','',content)

    content = re.findall('<a href=".*?</a>',content)

    # 標題
    hate_title_list = []
    count_hate = 0 
    for title in content:
        count_hate+=1
        title_new = re.findall('>.*?</a>',title)
        title_new = title_new[0]
        title_new = title_new[1:-4]
        hate_title_list.append(title_new)

    # 連結
    hate_url_list = []
    for url in content:
        url_new = re.findall('/bbs.*?html',url)
        url_new = 'https://www.ptt.cc'+url_new[0]
        hate_url_list.append(url_new)



    ##################################################################

    # 八卦版
    ptt_Gossiping_url = 'https://www.ptt.cc/bbs/Gossiping/index.html'
    my_headers = {'cookie': 'over18=1;'}     # 越過年齡認證
    res = requests.get(ptt_Gossiping_url,headers = my_headers)

    ptt_Gossiping = str(res.text)

    start = ptt_Gossiping.index('<div class="r-ent">')
    end = ptt_Gossiping.index('<div class="r-list-sep">')

    content = ptt_Gossiping[start:end]

    content = re.sub('<a href=.*?搜尋同標題文章</a>','',content)
    content = re.sub('<a href=.*?的文章</a>','',content)

    content = re.findall('<a href=".*?</a>',content)

    # 標題
    Gos_title_list = []
    count_Gos = 0
    for title in content:
        count_Gos+=1
        title_new = re.findall('>.*?</a>',title)
        title_new = title_new[0]
        title_new = title_new[1:-4]
        Gos_title_list.append(title_new)

    # 連結
    Gos_url_list = []
    for url in content:
        url_new = re.findall('/bbs.*?html',url)
        url_new = 'https://www.ptt.cc'+url_new[0]
        Gos_url_list.append(url_new)



    ##################################################################

    rw = open('separate/ptt_hate.html','w',encoding = 'utf8')

    title0 = '<h2>PTT排行榜<h2>'
    title1 = '<h3>政黑板</h3>'
    title2 = '<h3>八卦板</h3>'

    # margin 設定div置中，text-align設定文字置中
    begin = '<div class="item" style="margin:0px auto;text-align:center;">'
    ending = '</div>'

    rw.write(begin)
    rw.write(title0)
    rw.write(title1)

    # 填入黑特版
    for num in range(count_hate):
        topic_titles = '<div style="text-align:center;margin-bottom:15px;"><a href="{}" target="_blank">{}</a></div>'.format(hate_url_list[num],hate_title_list[num])
        rw.write(topic_titles)

    rw.write(title2)

    # 填入八卦版
    for num in range(count_Gos):
        talk_titles = '<div style="text-align:center;margin-bottom:15px;"><a href="{}" target="_blank">{}</a></div>'.format(Gos_url_list[num],Gos_title_list[num])
        rw.write(talk_titles)


    rw.write(ending)

except Exception as errormsg:
    print('ptt_web access false，stoping...')
    today = datetime.now().strftime('%Y-%m-%d %H時')
    message = 'ptt黑特板及八卦板資料獲取有誤，發生時間點：{}\n'.format(today)
    lineNotifyMessage(token, message+str(errormsg))
    os._exit(0)

rw.close()

