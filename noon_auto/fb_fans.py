import pandas as pd
import numpy as np
import requests,re,time,os
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


# 新文易數
fb_fabs_url = 'https://tag.analysis.tw/event/'

# 確認網站是否已更新資料，固定時間檢查一次
# 若檢查次數達標則抓取前一小時，都沒有的話顯示無法抓取資料並跳過此程序

# 加入try語法
try:
    checktimes = 0
    while True:
        res = requests.get(fb_fabs_url)
        soup = BeautifulSoup(res.content,'lxml')
        web_content_check = str(soup)
        if '<th>10</th>' in web_content_check:
            break
        elif checktimes == 3:
            time_now = datetime.now().strftime('%Y-%m-%d')
            # 取前一個小時的資料
            fb_fabs_url_11 = 'https://tag.analysis.tw/event/{}/11/'.format(time_now)
            res = requests.get(fb_fabs_url_11)
            soup = BeautifulSoup(res.content,'lxml')
            web_content_check_2 = str(soup)
            if '<th>10</th>' in web_content_check_2:
                break
            else:
                print('無法抓取資料，跳過此程序')
                rw = open('separate/fb_fans.html','w',encoding = 'utf8')
                title = '<h1 style="text-align:center"><a href="https://tag.analysis.tw/event/" target="_blank">現在FB 新聞粉專最重要事件 - 前10 名</a></h1>'
                nodata = '<div><h3 style="text-align:center">網站尚未更新，無法抓取資料</h3></div>'
                img_sep = '<img src="../img/sep.png" style="display:block; margin:auto;">'
                rw.write(title+nodata+img_sep)
                rw.close()
                os._exit(0)
        else:
            checktimes+=1
            print('網站尚未更新，等待12秒後重新確認，來源確認第{}次，最多確認3次'.format(checktimes))
            time.sleep(12)


    ################ 編寫網頁內容  ################

    rw = open('separate/fb_fans.html','w',encoding = 'utf8')
    title = '<h1 style="text-align:center"><a href="https://tag.analysis.tw/event/" target="_blank">現在FB 新聞粉專最重要事件 - 前10 名</a></h1>'
    rw.write(title)


    rank_num = [1,2,3,4,5,6,7,8,9,10]
    for num in rank_num:

        content = str(soup)

        start = content.index('<th>{}</th>'.format(num))
        end = content.index('<tr class="trs"><th>{}</th>'.format(num+1))

        new_content = content[start:end]


        # 擷取tag(關鍵字)
        tag_list = re.findall('tag/.*?/',new_content)
        # .   匹配除了 \n 換行符號的任意一個字元
        # *   匹配在*前面的字元出現到再次出現的內容
        # .*  開始到結束的所有內容
        # .*? 遇到開始及結束就擷取

        # 擷取標題
        title_list = re.findall('colspan="3">.*?<a',new_content)

        # 擷取標題超連結
        titleHyp_list = re.findall('<a class="like_href" href=".*?">',new_content)

        # 關鍵字
        videokeyword = []
        for tag in tag_list:
            tag = tag[4:-1]
            videokeyword.append(tag)

        # 標題
        videotitle = []
        for title in title_list:
            title = title[12:-3]
            videotitle.append(title)

        # 標題超連結
        titleHyp = []
        for Hyp in titleHyp_list:
            Hyp = Hyp[27:-2]
            titleHyp.append(Hyp)
        # 有時候超連結的標籤會不一樣，如果抓不到就給dataframe填空值避免報錯
        while True:
            if len(titleHyp) == len(videotitle):
                break
            elif len(titleHyp)>30:
                break
            else:
                titleHyp.append(np.NAN)


        img = '<img src="../img/number/{}.png">'.format(num)

        # 把關鍵字弄成紅底白字水平排列
        keyword ='<div>'
        for key in videokeyword:
            key_span = '<span style="background: #f00; color: #fff; margin: 0 4px; border-radius: 4px; ">{}</span>'.format(key)
            keyword = keyword + key_span
        keyword = keyword + '</div>'

        video_table = {"title":videotitle,'hyperlink':titleHyp}
        video_table = pd.DataFrame(video_table)
        
        #標題用白底比較看得清楚，<span>讓單純標題白底，不會整格都白底
        title = ''
        for video in video_table.values:
            # 如果網址沒抓到是空值，就變成用google搜尋標題
            if type(video[1]) != type('字串測試'):
                video[1] = 'https://www.google.com/search?q={}'.format(video[0])
            tit = '<a href="{}" target="_blank"><div style="margin:5px;"><span style="background: #fff;">{}</sapn></div></a>'.format(video[1],video[0])
            title = title + tit


        item = (
            '<div class="item" style="text-align:center;margin:50px">'+
            '<div id="div2" style="vertical-align: middle;margin:15px;font-size:18px;">{}</div>'.format(img)+
            '<div id="div3" style="vertical-align:middle;text-align:left;font-size:18px;">'+keyword+title+'</div>'+
            '</div>')

        rw.write(item)

    img_sep = '<img src="../img/sep.png" style="display:block; margin:auto;">'
    rw.write(img_sep)

except Exception as errormsg:
    print('新文易數資料獲取失敗')
    today = datetime.now().strftime('%Y-%m-%d %H時')
    message = '新文易數資料獲取有誤，發生時間點：{}\n'.format(today)
    lineNotifyMessage(token, message+str(errormsg))
    os._exit(0)


################ bottom  ################

rw.close()
