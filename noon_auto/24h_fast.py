import requests,json,re,os
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
token = 'm6uafWsyIziRWXaqYfTKJxNShGYlp3WM3RG9e0hP2OA'


# 加入try語法
try:
    # 24小時觀看數增加最快
    yt_fast_url = 'https://playboard.co/en/chart/video/most-viewed-news-videos-in-taiwan-daily'

    res = requests.get(yt_fast_url)
    soup = BeautifulSoup(res.content,'lxml')


    # 影片標題
    data_title = soup.select('body')[0].select('div')[0].select('div')[0].select('div')[0].select('div')[0].select('main')[0].select('table')[0].find_all('h3',limit=10)
    list_title = []
    for title in data_title:
        title = str(title)
        num = title.find('="">')            # 找到jpg" src=的位置，用在擷取完整的圖片連結
        title = title[num+4:-5]
        title = title.replace(u'\u3000',u'  ')   # \u3000 是全形空白，刪除或取代要用特殊參數 u
        list_title.append(title)


    # 日期
    data_date = soup.select('body')[0].select('div')[0].select('div')[0].select('div')[0].select('div')[0].select('main')[0].select('table')[0].find_all('div',class_='title__date',limit=10)
    list_date = []
    for date in data_date:
        date = str(date)[45:-19]
        list_date.append(date)


    # 圖片
    data_img = soup.select('body')[0].select('div')[0].select('div')[0].select('div')[0].select('div')[0].select('main')[0].select('table')[0].find_all('div',class_='thumb',limit=10)
    list_img = []
    for img in data_img:
        img = 'https://'+str(img)[44:-27]
        list_img.append(img)


    # 網址
    data_web = soup.select('body')[0].select('div')[0].select('div')[0].select('div')[0].select('div')[0].select('main')[0].select('table')[0].find_all('a',class_='title__label',limit=10)
    list_web = []
    for web in data_web:
        web = str(web)[49:70]
        web = 'https://playboard.co/'+web
        list_web.append(web)


    # 頻道名稱
    data_ch_name = soup.select('body')[0].select('div')[0].select('div')[0].select('div')[0].select('div')[0].select('main')[0].select('table')[0].find_all('span',class_='name',limit=10)
    list_ch_name = []
    for name in data_ch_name:
        name = str(name)[38:-7]
        list_ch_name.append(name)


    # 頻道圖片
    list_ch_img = []
    for ch in list_ch_name:  
        data_ch_img = soup.select('body')[0].select('div')[0].select('div')[0].select('div')[0].select('div')[0].select('main')[0].select('table')[0].find_all('img',alt = ch)
        data_ch_img = str(data_ch_img)
        data_ch_img = data_ch_img.replace(ch,'')   # 把頻道名稱取代為空，這樣要取值時前面的長度才會一樣，更好取出圖片超連結
        num = data_ch_img.find('jpg" src=')        # 找到jpg" src=的位置，用在擷取完整的圖片連結
        data_ch_img = data_ch_img[23:num+3]
        list_ch_img.append(data_ch_img)

    # 頻道觀看數增長量
    ch_view = soup.select('body')[0].select('div')[0].select('div')[0].select('div')[0].select('div')[0].select('main')[0].select('table')[0].find_all('span',class_ = 'fluc-label fluc-label--mono-font fluc-label--en fluc-label--symbol-math up',limit=10)
    list_ch_view = []
    ch_view = str(ch_view)
    ch_view = re.findall('"">.*?</',ch_view)
    for view in ch_view:
        view = view[3:-2]
        list_ch_view.append(view)

    # 頻道訂閱數
    ch_subs = soup.select('body')[0].select('div')[0].select('div')[0].select('div')[0].select('div')[0].select('main')[0].select('table')[0].find_all('span',class_ = 'subs__count',limit=10)
    list_ch_subs = []
    ch_subs = str(ch_subs)
    ch_subs = re.findall('<span.*?span>',ch_subs)     # 逐步縮小範圍，怕網站
    ch_subs = str(ch_subs)
    ch_subs = re.findall('">.*?</',ch_subs)
    for sub in ch_subs:
        sub = sub[2:-2]
        list_ch_subs.append(sub)


    ################ 編寫網頁內容  ################

    rw = open('separate/24h_fast.html','w',encoding = 'utf8')
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
                </style>
            </head>
            '''
    #rw.write(style)            # 已經寫在head.html內，單檔測試再寫入，避免跑版

    # 標題
    head =  '<div><a href="https://playboard.co/en/chart/video/most-viewed-news-videos-in-taiwan-daily" target="_blank"><h2 style="text-align:center">YT - 24 小時內觀看數增加最快的影片前十名</h2></a></div>'
    time_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    time_news = '<div><h3 style="text-align:center;color:gray">資料擷取時間{}</h2></div>'.format(time_now)
    rw.write(head+time_news)

    # 迭代10個影片資訊
    num_video = [0,1,2,3,4,5,6,7,8,9]
    for num in num_video:
        
        # _blank 參數表示另開視窗
        # a href 做超連結
        title = '<div style="font-weight:bold"><a href="{}" target="_blank"><font face="微軟正黑體">{}</font></a></div>'.format(list_web[num],list_title[num])

        # 把每個元素做成一行
        channelTitle = '<div>影片頻道：{}</div>'.format(list_ch_name[num])

        publish = '<div>發布時間：{}</div>'.format(list_date[num])

        img = '<img src="{}">'.format(list_img[num])

        ch_img = '<img src="{}">'.format(list_ch_img[num])

        video_views = '<div>24小時累計觀看次數：{} views</div>'.format(list_ch_view[num])

        channel_subs = '<div>頻道訂閱數：{} 🔔</div>'.format(list_ch_subs[num])

        #把圖片呈現在左邊，其餘資訊呈現在右邊，item裡面再包左右兩個div
        cti_channel = ['中天電視','中天新聞','我愛貓大','中天財經頻道','正常發揮',
        '來去CHECK IN','頭條開講','姐的星球','中天娛樂頻道','大新聞大爆卦','台灣大搜索',
        '毛球烏托邦','全球大視野']

        if list_ch_name[num] in cti_channel:
            tag = "item special"
        else:
            tag = "item"
        # max-width:60%  用來調整中天頻道紅框的最大寬度
        item = (
            '<div class="{}" style="text-align:center;margin:auto;margin-bottom:15px;max-width:60%">'.format(tag)+
            '<div id="div2" class="circle" style="vertical-align: middle;">{}</div>'.format(ch_img)+
            '<a href="{}" target="_blank"><div id="div1" style="vertical-align: middle;">{}</div></a>'.format(list_web[num],img)+
            '<div id="div1" style="vertical-align:top;text-align:left;">{}</div>'.format(title+channelTitle+publish+channel_subs+video_views)+
            '</div>')

        rw.write(item)

    img_sep = '<img src="../img/sep.png" style="display:block; margin:auto;">'
    rw.write(img_sep)

except Exception as errormsg:
    print('24小時觀看數累積最快資料獲取失敗')
    today = datetime.now().strftime('%Y-%m-%d %H時')
    message = '24小時觀看數累積最快資料獲取有誤，發生時間點：{}\n'.format(today)
    lineNotifyMessage(token, message+str(errormsg))
    os._exit(0)

################ bottom  ################

rw.close()
