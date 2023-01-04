import requests,json,re,cloudscraper,time,os
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
    # 訂閱戶排名
    yt_sub_url = 'https://tw.noxinfluencer.com/youtube-channel-rank/top-100-tw-news%20%26%20politics-youtuber-sorted-by-subs-weekly'


    # 連續訪問，若無法抓取就跳出
    check_time = 0
    while True:
        res = cloudscraper.create_scraper().get(yt_sub_url)
        soup = BeautifulSoup(res.content,'lxml')
        content = soup.select('body')[0].find_all('div',class_ = 'table-line clearfix',limit=10)
        content = str(content)
        title_data = re.findall('<span class="title pull-left ellipsis">.*?</span>',content)
        if title_data !=[]:
            print('正常取得資料')
            break
        elif check_time == 20 :
            print('無法取得資料')
            os._exit(0)
        else:
            check_time+=1
            print('未取得資料，5秒後嘗試第{}次重新抓取'.format(check_time))
            time.sleep(5)


    # 取出頻道名稱    
    title_data = re.findall('<span class="title pull-left ellipsis">.*?</span>',content)
    title_list = []
    for title in title_data:
        title = title[39:-7]
        title_list.append(title)

    # 取出頻道圖片
    img_data = re.findall('src=".*?"',content)
    img_list = []
    for img in img_data:
        img = img[5:-1]
        img_list.append(img)


    # 取出頻道訂閱數
    sub_data = re.findall('rank-subs.*?</s',content)
    sub_list = []
    for sub in sub_data:
        sub = sub[32:-3]
        sub_list.append(sub)


    # 取出平均觀看量
    views_data = re.findall('rank-cell pull-left rank-avg-view.*?</s',content)
    views_list = []
    for view in views_data:
        view = view[57:-3]
        views_list.append(view)


    # 取出變化量，要做多層迭代，直到洗出list內容為訂閱數及觀看量的漲跌幅
    channel_data = re.findall('<div.*?</div>',content)
    change_sub_data = []
    change_views_data = []
    for channel in channel_data:
        change = re.findall('rank-cell pull-left rank-subs.*?</span>.</span>',channel)
        for cha in change:
            cha = re.findall('class="change.*?</span>.</span>',cha)
            for ch in cha:
                ch = re.findall('class="change.*?</span>.?</span>',ch)
                sub = ch[0]
                views = ch[1]
                change_sub_data.append(sub)
                change_views_data.append(views)


    # 取出訂閱數變化量
    change_sub = []
    for sub in change_sub_data:
        #print(sub)
        if 'change up' in sub:
            sub = float(sub[67:-17])
            change_sub.append(sub)
        elif 'change none' in sub:
            sub = 0
            change_sub.append(sub)
        elif 'change down' in sub:
            sub = float('-'+sub[71:-17])
            change_sub.append(sub)



    # 取出觀看數變化量
    change_views = []
    for views in change_views_data:

        if 'change up' in views:
            views = float(views[67:-18])
            change_views.append(views)
        elif 'change none' in views:
            views = 0
            change_views.append(views)
        elif 'change down' in views:
            views = float('-'+views[71:-19])
            change_views.append(views)


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
    rw.write(style)            # 已經寫在head.html內，單檔測試再寫入，避免跑版

    # 標題
    title =  '<div><a href="https://tw.noxinfluencer.com/youtube-channel-rank/top-100-tw-news%20%26%20politics-youtuber-sorted-by-subs-weekly" target="_blank"><h2 style="text-align:center">YT - 訂閱戶排行榜</h2></a></div>'
    time_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    time_news = '<div><h3 style="text-align:center;color:gray">資料擷取時間{}</h2></div>'.format(time_now)
    rw.write(title+time_news)



    table_title = (
        '<div class="item" style="text-align:center;margin:auto;margin-bottom:15px;">'+
        '<div id="div5" style="vertical-align: middle;text-align:center;font-size:20px;margin:1px;font-family:Microsoft JhengHei;font-weight:bold;">🦉頻道</div>'+
        '<div id="div5" style="vertical-align: middle;font-size:20px;text-align:center;margin:5px;font-family:Microsoft JhengHei;font-weight:bold;">🙆粉絲數</div>'+
        '<div id="div2" style="vertical-align: middle;font-size:20px;text-align:right;margin:15px;font-family:Microsoft JhengHei;font-weight:bold;">平均觀看量</div>'+
        '</div>')

    rw.write(table_title)


    # 迭代10個影片資訊
    num_video = [0,1,2,3,4,5,6,7,8,9]
    for num in num_video:
        
        # _blank 參數表示另開視窗
        # a href 做超連結
        # 把每個元素做成一行
        channetitle = '<div style="font-weight:bold"><font face="微軟正黑體">{}</font></div>'.format(title_list[num])

        img = '<img src="{}">'.format(img_list[num])

        #rank_img = '<img src="{}">'.format(list_ch_img[num])  #排名圖片

        channel_subs = '<div>{}</div>'.format(sub_list[num])

        channel_views = '<div>{}</div>'.format(views_list[num])

        # 判斷變化量大小跟正負值，做箭頭跟紅綠色區隔
        if change_sub[num] > 0:
            change_sub_value = '<div id="div4" style="vertical-align: middle;margin:1px;text-align:left;color: #EA0000;font-size:20px;">▲{}%</div>'.format(change_sub[num])
        elif change_sub[num] == 0:
            change_sub_value = '<div id="div4" style="vertical-align: middle;margin:1px;text-align:left;font-size:20px;"> - </div>'
        elif change_sub[num] < 0:
            change_sub_value = '<div id="div4" style="vertical-align: middle;margin:1px;text-align:left;color: #00DB00;font-size:20px;">▼{}%</div>'.format(change_sub[num])
        else:
            change_sub_value = '<div id="div4" style="vertical-align: middle;margin:1px;text-align:left;font-size:20px;"> - </div>'

        if change_views[num] > 0:
            change_views_value = '<div id="div4" style="vertical-align: middle;margin:1px;text-align:left;color: #EA0000;font-size:20px;">▲{}%</div>'.format(change_views[num])
        elif change_views[num] == 0:
            change_views_value = '<div id="div4" style="vertical-align: middle;margin:1px;text-align:left;font-size:20px;"> - </div>'
        elif change_views[num] < 0:
            change_views_value = '<div id="div4" style="vertical-align: middle;margin:1px;text-align:left;color: #00DB00;font-size:20px;">▼{}%</div>'.format(change_views[num])
        else:
            change_views_value = '<div id="div4" style="vertical-align: middle;margin:1px;text-align:left;font-size:20px;"> - </div>'



        item = (
            '<div class="item" style="text-align:center;margin:auto;margin-bottom:15px;">'+
            '<div id="div4" class="circle-small" style="vertical-align: middle;">{}</div>'.format(img)+
            '<div id="div5" style="vertical-align: middle;text-align:left;font-size:20px;margin:15px">{}</div>'.format(channetitle)+
            '<div id="div2" style="vertical-align: middle;font-size:20px;text-align:right;margin:5px">{}</div>'.format(channel_subs)+
            change_sub_value+
            '<div id="div2" style="vertical-align: middle;font-size:20px;text-align:right;margin:15px">{}</div>'.format(channel_views)+
            change_views_value+
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