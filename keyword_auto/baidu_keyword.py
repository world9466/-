from selenium import webdriver
from selenium.webdriver.common.by import By             #用來特定id,class等標籤
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import datetime
import time,os,re,requests


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


url = 'https://top.baidu.com/board?tab=realtime'

# 以下 options 用來取消網頁中的彈出視窗，可加可不加
options = Options()
options.add_argument("--disable-notifications")

count = 0

# 嘗試讀取網頁
try:
    while True:
        # 傳入同資料夾內的 chromedriver 驅動程式
        chrome = webdriver.Chrome('chromedriver', options=options)

        # 開啟要爬取資料的網頁
        chrome.get(url)

        # 使用BeautifulSoup爬出頁面中的原始碼，之後步驟就跟傳統爬蟲一樣
        soup_baidu = BeautifulSoup(chrome.page_source,'lxml')

        # 關閉網頁
        chrome.close()

        # 等待網頁讀取
        print('網頁讀取中...')

        # 如果沒有讀取到資料就重來
        title_baidu = soup_baidu.select('body')[0].find_all('div',class_ = 'c-single-text-ellipsis',limit=30)
        if len(title_baidu) > 0:
            break
        elif count > 5 :
            print('抓不到資料，繼續下一步')
            rw = open('separate/baidu.html','w',encoding = 'utf8')
            title_baidu = '<h2 style="text-align:center;background: #f00; color: #fff; margin: 0 4px; border-radius: 4px;">百度熱搜</h2>'
            nogomes = '<div>程式多次存取百度資料未果，無法爬取網站資料</div>'
            rw.write(title_baidu+nogomes)
            rw.close()
            os._exit(0)
        else:
            count+=1
            print('資料爬取失敗，5秒後再試')
            time.sleep(5)

    # 退出驅動程式，不然批次檔會卡住導致其他py檔執行失敗
    chrome.quit()


    print('baidu access successful')


    ################################################
    # 嘗試建立頁面

    # 擷取標題
    title_baidu = soup_baidu.select('body')[0].find_all('div',class_ = 'c-single-text-ellipsis',limit=30)
    title_baidu_list = []
    count_baidu = 0
    for name in title_baidu:
        count_baidu+=1
        name = str(name)
        name = name[34:-10]
        name = re.findall('>.*?<',name)
        name = name[0]
        name = name[3:-2]
        title_baidu_list.append(name)
    title_len = len(title_baidu_list)
    print('獲取百度標題筆數：共 {} 筆'.format(title_len))

    # 擷取超連結
    title_url_baidu = soup_baidu.select('body')[0].find_all('a',class_ = 'title_dIF3B',limit=30)
    title_url_baidu_list = []
    for url in title_url_baidu:
        url = str(url)
        url = re.findall('https.*?"',url)
        url = url[0]
        url = url[:-1]
        title_url_baidu_list.append(url)
    url_len = len(title_url_baidu_list)
    print('獲取百度超連結筆數：共 {} 筆'.format(url_len))

    #  判斷熱、沸等標籤 re.compile 很好用，可以在很多時候直接判斷某個值
    tag_baidu = soup_baidu.select('body')[0].find_all('div',{'class': re.compile("c-text.*?")},limit=30)
    tag_baidu_list = []
    for tag in tag_baidu:
        tag = str(tag)
        tag = re.findall('">.*?</',tag)
        tag = tag[0]
        tag = tag[2:-2]
        if len(tag) > 0 :
            tag_baidu_list.append('🔥'+tag)
        else:
            tag_baidu_list.append('')
    print('熱門程度判斷完成')


    ################ 編寫網頁內容  ################

    rw = open('separate/baidu.html','w',encoding = 'utf8')
    # r 讀取
    # w 寫入(刪除原本內容)
    # a 追加寫入


    # 寫入百度熱搜
    title_baidu = '<h2 style="text-align:center;background: #f00; color: #fff; margin: 0 4px; border-radius: 4px;">百度熱搜</h2>'
    rw.write(title_baidu)

    # 寫入資料擷取時間
    time_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    time_news = '<div><h3 style="text-align:center;color:gray">資料擷取時間{}</h2></div>'.format(time_now)
    rw.write(time_news)

    # 按順序寫入熱搜數據，設定迴圈次數為資料筆數的list長度，避免錯誤

    for num in range(title_len):
        baidu = (
            '<div style="text-align:left;font-size:18px;margin-bottom:25px;">'+
            '<span style="margin-left:20px;font-family:Lucida Console;color:#4169e1;">({})</span>'.format(num+1)+
            '<span style="margin-bottom:5px;margin-left:20px;">'+
            '<a href="{}" target="_blank" style="color:#000000;font-weight:bold;">'.format(title_url_baidu_list[num])+
            '{}&nbsp;</a></span>'.format(title_baidu_list[num])+
            '<span style="color:#ff0000;font-weight:bold;">{}</span></div>'.format(tag_baidu_list[num])
            )
        rw.write(baidu)
except Exception as errormsg:
    print('baidu access false，stoping...')
    today = datetime.now().strftime('%Y-%m-%d %H時')
    message = '百度資料獲取有誤，發生時間點：{}\n'.format(today)
    lineNotifyMessage(token, message+str(errormsg))
    os._exit(0)


rw.close()