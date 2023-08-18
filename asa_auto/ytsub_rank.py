import pandas as pd
import requests,os,re
from bs4 import BeautifulSoup
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



# 嘗試讀取
try:
    # 政治新聞類排名
    yt_sub_url = 'https://playboard.co/en/youtube-ranking/most-subscribed-news-channels-in-taiwan-total'

    res = requests.get(yt_sub_url)
    soup = BeautifulSoup(res.content,'lxml')

    title_list = []
    subs_list = []
    images_list = []

    # 影片標題
    tr_elements = soup.select('tr.chart__row[data-v-03380aca]')

    for tr_element in tr_elements:
        # 迭代這個標籤抓到的內容，取出標題、訂閱數、頻道圖片
        data = str(tr_element).replace("\n", " ")

        # 抓標題
        title = re.findall('img alt=".*?"',data)
        if len(title) > 0:
            title = title[0][9:-1]
            title_list.append(title)
        
        # 抓訂閱數
        subs = re.findall('</a></li></ul></td>.*?</td>',data)
        if len(subs) > 0:
            subs = subs[0][73:-20]
            subs = int(subs.replace(",", ""))  # 去掉千分位，轉成整數型態
            subs_list.append(subs)

        # 抓圖片網址
        img = re.findall('data-src="https://i.playboard.app/p/.*?.jpg',data)
        if len(img) > 0:
            img = img[0][10:]
            images_list.append(img)

    # 將從api取得的資料轉成 dataframe
    ch_list = {'name':title_list,'subs':subs_list,'img':images_list}
    ch_list = pd.DataFrame(ch_list)


    # 強制轉換為整數型態(不然會有小數點)，除以1萬，再轉成字串格式加上"萬"來顯示
    ch_list['subs'] = (ch_list['subs']/10000).astype(int)
    ch_list['subs'] = ch_list['subs'].astype(str) + ' 萬'


    ################ 編寫網頁內容  ################

    rw = open('separate/ytsubs_rank.html','w',encoding = 'utf8')
    # r 讀取
    # w 寫入(刪除原本內容)
    # a 追加寫入

    style = '''
            <head>
                <meta charset="utf-8">
                <style type="text/css">
                    #div1{
                        width: 500px;
                        display: inline-block;
                    }
                    #div2{
                        width: 100px;
                        display: inline-block;
                    }
                    #div3{
                        width: 700px;
                        display: inline-block;
                    }
                    #div4{
                        width: 60px;
                        display: inline-block;
                    }
                    #div5{
                        width: 200px;
                        display: inline-block;
                    }
                </style>
                <style>
                    .item.special {
                        border: 2px solid red;
                    }
                    .circle{
                        width:100px; 
                        height:100px; 
                        border-radius:100%; 
                        overflow:hidden;
                    }
                    .circle > img{
                        width: 100%;
                        height: 100%;
                    }
                    .circle-small{
                        width:60px; 
                        height:60px; 
                        border-radius:100%; 
                        overflow:hidden;
                    }
                    .circle-small > img{
                        width: 100%;
                        height: 100%;
                    }
                </style>
            </head>
            '''
    #rw.write(style)            # 已經寫在head.html內，單檔測試再寫入，避免跑版

    # 標題
    title =  '<div><a href="https://tw.noxinfluencer.com/youtube-channel-rank/top-100-tw-news%20%26%20politics-youtuber-sorted-by-subs-weekly" target="_blank"><h2 style="text-align:center">YT - 訂閱戶排行榜</h2></a></div>'
    time_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    time_news = '<div><h3 style="text-align:center;color:gray">資料擷取時間{}</h2></div>'.format(time_now)
    rw.write(title+time_news)


    table_title = (
        '<div class="item" style="text-align:center;margin:auto;margin-bottom:15px;">'+
        '<div id="div1" style="vertical-align: middle;text-align:center;font-size:20px;margin:1px;font-family:Microsoft JhengHei;font-weight:bold;">🦉頻道</div>'+
        '<div id="div5" style="vertical-align: middle;font-size:20px;text-align:right;margin:5px;font-family:Microsoft JhengHei;font-weight:bold;">🙆粉絲數</div>'+
        '</div>')

    rw.write(table_title)


    # 迭代10個影片資訊
    for num in range(10):
        
        # _blank 參數表示另開視窗
        # a href 做超連結
        # 把每個元素做成一行
        channetitle = '<div style="font-weight:bold"><font face="微軟正黑體">{}</font></div>'.format(ch_list["name"][num])

        channel_subs = '<div>{}</div>'.format(ch_list["subs"][num])

        img = '<img src="{}">'.format(ch_list["img"][num])


        item = (
            '<div class="item" style="text-align:center;margin:auto;margin-bottom:15px;">'+
            '<div id="div4" class="circle-small" style="vertical-align: middle;">{}</div>'.format(img)+
            '<div id="div1" style="vertical-align: middle;text-align:left;font-size:20px;margin:15px">{}</div>'.format(channetitle)+
            '<div id="div2" style="vertical-align: middle;font-size:24px;text-align:right;margin:5px">{}</div>'.format(channel_subs)+
            '</div>')

        rw.write(item)

    img_sep = '<img src="../img/sep.png" style="display:block; margin:auto;">'
    rw.write(img_sep)


except Exception as errormsg:
    print('YT排名資料獲取失敗')
    today = datetime.now().strftime('%Y-%m-%d %H時')
    message = 'YT排名資料獲取有誤，發生時間點：{}\n'.format(today)
    lineNotifyMessage(token, message+str(errormsg))
    os._exit(0)


################ bottom  ################

rw.close()