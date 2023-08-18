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

# 使用try語法
try:
    # YT發燒前五名(一頁只有5個結果，所以會有前五名跟後五名兩個url)
    ythot10_url_1 = 'https://youtube.googleapis.com/youtube/v3/videos?part=snippet%2CcontentDetails%2Cstatistics&chart=mostPopular&regionCode=TW&key={}'.format(api_key)

    # YT發燒後五名
    ythot10_url_2 = 'https://youtube.googleapis.com/youtube/v3/videos?part=snippet%2CcontentDetails%2Cstatistics&chart=mostPopular&regionCode=TW&key={}&pageToken=CAUQAA'.format(api_key)

    # YT發燒第三頁(有時候前兩頁不滿10個)
    ythot10_url_3 = 'https://youtube.googleapis.com/youtube/v3/videos?part=snippet%2CcontentDetails%2Cstatistics&chart=mostPopular&regionCode=TW&key={}&pageToken=CAoQAA'.format(api_key)

    res1 = requests.get(ythot10_url_1)
    res2 = requests.get(ythot10_url_2)
    res3 = requests.get(ythot10_url_3)

    #res.text          列出文字
    #res.encoding      列出編碼
    #res.status_code   列出 HTTP 狀態碼
    #res.headers       列出 HTTP Response Headers

    # 轉換為json型式
    data1 = json.loads(res1.text)
    data2 = json.loads(res2.text)
    data3 = json.loads(res3.text)

    # 從json檔裡用jsonpath指定特定的元素(標題、影片ID、觀看數...等等)
    #影片標題
    data_title_1 = jsonpath(data1,"$.items[*].snippet.title")
    data_title_2 = jsonpath(data2,"$.items[*].snippet.title")
    data_title_3 = jsonpath(data3,"$.items[*].snippet.title")
    data_title = data_title_1 + data_title_2 + data_title_3

    #影片ID
    data_videoID_1 = jsonpath(data1,"$.items[*].id")
    data_videoID_2 = jsonpath(data2,"$.items[*].id")
    data_videoID_3 = jsonpath(data3,"$.items[*].id")
    data_videoID = data_videoID_1 + data_videoID_2 + data_videoID_3

    #頻道
    data_channelTitle_1 = jsonpath(data1,"$.items[*].snippet.channelTitle")
    data_channelTitle_2 = jsonpath(data2,"$.items[*].snippet.channelTitle")
    data_channelTitle_3 = jsonpath(data3,"$.items[*].snippet.channelTitle")
    data_channelTitle = data_channelTitle_1 + data_channelTitle_2 + data_channelTitle_3

    #頻道ID
    data_channelId_1 = jsonpath(data1,"$.items[*].snippet.channelId")
    data_channelId_2 = jsonpath(data2,"$.items[*].snippet.channelId")
    data_channelId_3 = jsonpath(data3,"$.items[*].snippet.channelId")
    data_channelId = data_channelId_1 + data_channelId_2 + data_channelId_3

    #觀看數，超過一萬作處理
    data_views_1 = jsonpath(data1,"$.items[*].statistics.viewCount")
    data_views_2 = jsonpath(data2,"$.items[*].statistics.viewCount")
    data_views_3 = jsonpath(data3,"$.items[*].statistics.viewCount")
    data_views_total = data_views_1 + data_views_2 + data_views_3
    data_views = []
    for view in data_views_total:
        if int(view) >= 10000:
            view_new = str(int(int(view)/10000))+'萬'
            data_views.append(view_new)
        else:
            data_views.append(view)

    # 把時間的 T 跟 Z 贅字去除
    data_publish_1 = jsonpath(data1,"$.items[*].snippet.publishedAt")
    data_publish_2 = jsonpath(data2,"$.items[*].snippet.publishedAt")
    data_publish_3 = jsonpath(data3,"$.items[*].snippet.publishedAt")
    data_publish_total = data_publish_1 + data_publish_2 + data_publish_3
    data_publish = []
    for time in data_publish_total:
        if 'T' in time:
            time = time.replace('T',' ')
        if 'Z' in time:
            time = time.replace('Z',' ')
        data_publish.append(time)

    # 影片說明只取前幾個字，可以調整
    data_descri_1 = jsonpath(data1,"$.items[*].snippet.description")
    data_descri_2 = jsonpath(data2,"$.items[*].snippet.description")
    data_descri_3 = jsonpath(data3,"$.items[*].snippet.description")
    data_descri_total = data_descri_1 + data_descri_2 + data_descri_3
    data_descri = []
    for descri in data_descri_total:
        data_descri.append(descri[0:60]+'...')

    #縮圖
    data_img_1 = jsonpath(data1,"$.items[*].snippet.thumbnails.medium")
    data_img_2 = jsonpath(data2,"$.items[*].snippet.thumbnails.medium")
    data_img_3 = jsonpath(data3,"$.items[*].snippet.thumbnails.medium")
    data_img = data_img_1 + data_img_2 + data_img_3
    data_img = pd.DataFrame(data_img)
    data_img = data_img['url']


    ################ 編寫網頁內容  ################


    rw = open('separate/ythot10.html','w',encoding = 'utf8')
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
    head =  '<div><h2 style="text-align:center">YT發燒影片排行榜前10名</h2></div>'
    time_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    time_news = '<div><h3 style="text-align:center;color:gray">資料擷取時間{}</h2></div>'.format(time_now)
    rw.write(head+time_news)



    # 迭代10個影片資訊
    num_video = [0,1,2,3,4,5,6,7,8,9]
    for num in num_video:
        
        # _blank 參數表示另開視窗
        # a href 做超連結
        title = '<div style="font-weight:bold"><a href="https://youtu.be/{}" target="_blank"><font face="微軟正黑體">{}</font></a></div>'.format(data_videoID[num],data_title[num])

        # 把每個元素做成一行
        channelTitle = '<div>影片頻道：{}</div>'.format(data_channelTitle[num])

        publish = '<div>發布時間：{}</div>'.format(data_publish[num])

        descri = '<div>影片介紹：{}</div>'.format(data_descri[num])

        img = '<img src="{}">'.format(data_img[num])

        view = '<div>觀看次數：{} views</div>'.format(data_views[num])

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
            '<div id="div1" style="vertical-align:top;text-align:left">{}</div>'.format(title+channelTitle+publish+view+descri)+
            '</div>'
            )    

        rw.write(item)

    # display:block 把標籤屬性改為區塊，方便調整位置，也會自動換行
    img_sep = '<img src="../img/sep.png" style="display:block; margin:auto;">'
    rw.write(img_sep)

except Exception as errormsg:
    print('youtube hot video access false，stoping...')
    today = datetime.now().strftime('%Y-%m-%d %H時')
    message = 'YT發燒影片資料獲取有誤，發生時間點：{}\n'.format(today)
    lineNotifyMessage(token, message+str(errormsg))
    os._exit(0)

################ bottom  ################

rw.close()


