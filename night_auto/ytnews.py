import pandas as pd
import requests,json,re,os
from bs4 import BeautifulSoup
from jsonpath import jsonpath
#pip install jsonpath
from datetime import datetime


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


# api金鑰
api_key = 'AIzaSyD-oHGuCUlAJtFQECU6V8-6mX3KVwR5v_I'
news_list = 'PL3ZQ5CpNulQkExTxjzlJ8zDo_U_1uMKJu'

# 使用try語法
try:
    # YT新聞
    ytnews_url = 'https://www.googleapis.com/youtube/v3/playlistItems?part=snippet,contentDetails,status&playlistId={}&key={}&maxResults=10'.format(news_list,api_key)

    res = requests.get(ytnews_url)

    # 轉換為json型式
    data = json.loads(res.text)

    #影片標題
    data_title = jsonpath(data,"$.items[*].snippet.title")

    #影片ID
    data_videoID = jsonpath(data,"$.items[*].contentDetails.videoId")

    #頻道
    data_channelTitle = jsonpath(data,"$.items[*].snippet.videoOwnerChannelTitle")

    #頻道ID
    data_channelId = jsonpath(data,"$.items[*].snippet.videoOwnerChannelId")

    # 把時間的 T 跟 Z 贅字去除
    data_publish_1 = jsonpath(data,"$.items[*].contentDetails.videoPublishedAt")
    data_publish = []
    for time in data_publish_1:
        if 'T' in time:
            time = time.replace('T',' ')
        if 'Z' in time:
            time = time.replace('Z',' ')
        data_publish.append(time)

    # 影片說明只取前幾個字，可以調整
    data_descri_1 = jsonpath(data,"$.items[*].snippet.description")

    data_descri = []
    for descri in data_descri_1:
        data_descri.append(descri[0:60]+'...')

    #縮圖
    data_img = jsonpath(data,"$.items[*].snippet.thumbnails.medium")
    data_img = pd.DataFrame(data_img)
    data_img = data_img['url']


    ################ 編寫網頁內容  ################


    rw = open('separate/ytnews.html','w',encoding = 'utf8')
    # r 讀取
    # w 寫入(刪除原本內容)
    # a 追加寫入


    # 寫入 head
    # 指定div1 inline-block 參數，可以做兩行並排(只要寬度夠，寬度可以調整)
    # 設定 item.special 為紅框，給中天的頻道上框用
    style = '''
            <head>
                <meta charset="utf-8">
                <style type="text/css">
                    #div1{
                        width: 500px;
                        display: inline-block;
                    }
                </style>
                <style>
                    .item.special {
                        border: 2px solid red;
                    }
                </style>
            </head>
            '''
    #rw.write(style)            # 已經寫在head.html內，單檔測試再寫入，避免跑版


    # 標題
    head =  '<div><h2 style="text-align:center">YT發燒榜-新聞類前10名</h2></div>'
    time_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    time_news = '<div><h3 style="text-align:center;color:gray">資料擷取時間{}</h2></div>'.format(time_now)
    rw.write(head+time_news)

    # 迭代10個影片資訊
    if len(data_channelTitle) < 10:
        num_video = range(len(data_channelTitle))
    else:
        num_video = range(10)

    for num in num_video:
        
        # _blank 參數表示另開視窗
        # a href 做超連結
        title = '<div style="font-weight:bold"><a href="https://youtu.be/{}" target="_blank"><font face="微軟正黑體">{}</font></a></div>'.format(data_videoID[num],data_title[num])

        # 把每個元素做成一行
        channelTitle = '<div>影片頻道：{}</div>'.format(data_channelTitle[num])

        publish = '<div>發布時間：{}</div>'.format(data_publish[num])

        descri = '<div>影片介紹：{}</div>'.format(data_descri[num])

        img = '<img src="{}">'.format(data_img[num])

        #把圖片呈現在左邊，其餘資訊呈現在右邊，item裡面再包左右兩個div
        cti_channel = ['UC-z9BI8hMHNPrvnccyWgjyg','UCNWYi-14c43fAug9IwQSQMg',
        'UCz_rK02a3hnmMOOUSmFQo2w','UC_5iXjMizQ8gxzbEIV3TKCQ','UCdp5pYDJCpl5WFk3jFEjWHw',
        'UChLnfgAqCNLvz5DSFcnngNQ','UC0UX_EK8-UuBi-OrkmWB6eA','UCpu3bemTQwAU8PqM4kJdoEQ',
        'UCCqASHJXWs5_Lst_jWp40dw','UC5l1Yto5oOIgRXlI4p4VKbw','UCj2hyNWnTkCuSa5DgAjPMIg',
        'UCqU5mtjVB4qwGqY1-K0CMQA','UCiwt1aanVMoPYUt_CQYCPQg']


        if data_channelId[num] in cti_channel:
            tag = "item special"
        else:
            tag = "item"
        # max-width:60%  用來調整中天頻道紅框的最大寬度
        item = (
            '<div class="{}" style="text-align:center;margin:auto;margin-bottom:15px;max-width:60%">'.format(tag)+
            '<a href="https://youtu.be/{}" target="_blank"><div id="div1">{}</div></a>'.format(data_videoID[num],img)+
            '<div id="div1" style="vertical-align:top;text-align:left">{}</div>'.format(title+channelTitle+publish+descri)+
            '</div>'
            )

        rw.write(item)

    img_sep = '<img src="../img/sep.png" style="display:block; margin:auto;">'
    rw.write(img_sep)

except Exception as errormsg:
    print('youtube hot_news access false，stoping')
    today = datetime.now().strftime('%Y-%m-%d %H時')
    message = 'YT發燒新聞資料獲取有誤，發生時間點：{}\n'.format(today)
    lineNotifyMessage(token, message+str(errormsg))
    os._exit(0)

    ################ bottom  ################

rw.close()


