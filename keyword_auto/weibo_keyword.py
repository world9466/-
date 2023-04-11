import requests,json,re,os,time
from bs4 import BeautifulSoup
from datetime import datetime
from fake_useragent import UserAgent


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


# 微博熱搜
weibo_url = 'https://s.weibo.com/top/summary?cate=realtimehot'

# 偽造 UserAgent
ua = UserAgent()

cookie = 'SUB=_2AkMUca9Zf8NxqwFRmPAUym_qbolzyAnEieKiLV6CJRMxHRl-yT92qnUEtRB6P_GBtm5byuQQnf0749GOOS2avFh2_318; _s_tentry=www.google.com; UOR=www.google.com,s.weibo.com,www.google.com; Apache=8099932117659.911.1681204540190; SINAGLOBAL=8099932117659.911.1681204540190; ULV=1681204540211:1:1:1:8099932117659.911.1681204540190:'

header = {
	'User-Agent': ua.random,
	'Host': 's.weibo.com',
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
	'Accept-Encoding': 'gzip, deflate, br',
	# 定期更换Cookie
	'Cookie':cookie 
}

def weibo_access():
    global soup_weibo
    res_weibo = requests.get(weibo_url, headers=header,timeout=(6.05, 15))
    soup_weibo = BeautifulSoup(res_weibo.content,'lxml')


# 加入try語法
try:

    # 連續嘗試存取
    try:
        weibo_access()
    except:
        print('存取失敗，10秒後重新抓取')
        time.sleep(11)
        try:
            weibo_access()
        except:
            print('存取失敗，20秒後重新抓取')
            time.sleep(21)
            try:
                weibo_access()
            except:
                print('存取失敗，30秒後重新抓取')
                time.sleep(29)
                try:
                    weibo_access()
                except:
                    print('抓不到我盡力了，88888')
                    today = datetime.now().strftime('%Y-%m-%d %H時')
                    message = '微博資料無法獲取有誤(可能需要更新cookie)，發生時間點：{}\n'.format(today)
                    lineNotifyMessage(token, message)
                    os._exit(0)


    print('weibo access ok')


    ################################################
    # 嘗試建立頁面

    # 擷取標題
    # 避免加入錯誤的標題，要洗多次標籤
    title_weibo = soup_weibo.select('body')[0].find_all('a',limit=55)
    #print(title_weibo)
    title_weibo_list = []
    for title in title_weibo:
        title = str(title)
        title = re.findall('/weibo?.*?</a>',title)
        if title !=[]:
            title = title[0]
            title = re.findall('">.*?</a>',title)
            if title !=[]:
                title = title[0]
                title = title[2:-4]
                title_weibo_list.append(title)
    title_len = len(title_weibo_list)
    print('獲取微博熱搜筆數：共 {} 筆(含廣告)'.format(title_len))

    # 擷取主要資料
    weibo_data = soup_weibo.select('body')[0]
    weibo_data = str(weibo_data)
    #print(weibo_data)

    # 擷取超連結
    title_url_weibo = re.findall('="/weibo.*?"',weibo_data)
    title_url_weibo_list = []
    for url in title_url_weibo:
        url = 'https://s.weibo.com/'+url[3:-1]
        title_url_weibo_list.append(url)
    #print(title_url_weibo_list)
    url_len = len(title_url_weibo_list)
    print('獲取微博熱搜超連結筆數：共 {} 筆'.format(url_len))


    # 擷取序號(要做廣告判斷)
    serial_weibo = re.findall('<strong class=.*?</strong>',weibo_data)
    serial_weibo_list = []
    for serial in serial_weibo:
        serial = re.findall('>.*?<',serial)
        serial = serial[0]
        serial = serial[1:-1]
        serial_weibo_list.append(serial)

    # 擷取熱、沸等標籤，flags=re.DOTALL 把換行當作字串
    tag_weibo = re.findall('<td class="td-03.*?</td>',weibo_data,flags=re.DOTALL)
    tag_weibo_list = []

    for tag in tag_weibo:
        if 'icon' in tag:
            tag = re.findall('icon.*?</td>',tag)
            tag = tag[0]
            tag = re.findall('">.*?</i>',tag)
            tag = tag[0]
            tag = tag[2:-4]
            if tag == '热':
                tag_weibo_list.append('🔥熱')
            elif tag == '新':
                tag_weibo_list.append('⭐新')
            elif tag == '沸':
                tag_weibo_list.append('🔥🔥沸')
            else:
                tag_weibo_list.append('useless')
        else:
            tag_weibo_list.append('')

    tag_len = len(tag_weibo_list)
    print('獲取微博熱搜加註標籤筆數：共 {} 筆'.format(tag_len))
    print('熱門程度判斷完成，其中商業廣告共 {} 筆'.format(tag_len-51))



    ################ 編寫網頁內容  ################

    rw = open('separate/weibo.html','w',encoding = 'utf8')
    # r 讀取
    # w 寫入(刪除原本內容)
    # a 追加寫入


    # 寫入新浪微博热搜榜
    title_weibo = '<h2 style="text-align:center;background: #f00; color: #fff; margin: 0 4px; border-radius: 4px;">新浪微博热搜榜</h2>'
    rw.write(title_weibo)

    # 寫入資料擷取時間
    time_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    time_news = '<div><h3 style="text-align:center;color:gray">資料擷取時間{}</h2></div>'.format(time_now)
    rw.write(time_news)

    data_len = len(title_weibo_list)
    serial_final = 0
    for num in range(data_len):
        # 除去 tag 是商業廣告的部分，然後只取到30筆
        if tag_weibo_list[num] != 'useless' and serial_final<30 and serial_final<=data_len:
            serial_final+=1
            weibo = (
                '<div style="text-align:left;font-size:18px;margin-bottom:25px;">'+
                '<span style="margin-left:20px;font-family:Lucida Console;color:#ff8c00;">({})</span>'.format(serial_final)+
                '<span style="margin-bottom:5px;margin-left:20px;">'+
                '<a href="{}" target="_blank" style="color:#000000;font-weight:bold;">'.format(title_url_weibo_list[num])+
                '{}&nbsp;</a></span>'.format(title_weibo_list[num])+
                '<span style="color:#ff0000;font-weight:bold;">{}</span></div>'.format(tag_weibo_list[num])
                )
            rw.write(weibo)

except Exception as errormsg:
    msg = '微博爬蟲資料有誤\n'
    lineNotifyMessage(token, msg+str(errormsg))
    os._exit(0)


rw.close()

