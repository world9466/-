import requests,json,re,os,time
from bs4 import BeautifulSoup
from datetime import datetime
from jsonpath import jsonpath
from fake_useragent import UserAgent
import paramiko
#pip install jieba
#pip install BeautifulSoup4
#pip install jsonpath
#pip install fake-useragent

# Google Trend
# 教學網址 https://tlyu0419.github.io/2020/02/18/Crawl-GoogleTrends/


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


#### 下載NLP字詞庫  ####

# 建立連線
client = paramiko.SSHClient()

client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

client.connect(hostname='10.227.58.87', username='root', password='0266007766')
t = client.get_transport()
sftp=paramiko.SFTPClient.from_transport(t)

try:
    file_list = ['NLP-Audience.txt','NLP-CN_words.txt','NLP-Event.txt','NLP-Org.txt','NLP-People.txt','NLP-Region.txt','NLP-stopwords.txt']
    for file in file_list:
        print('downloading {}'.format(file))
        sftp.get('/var/www/html/keyword/NLP/{}'.format(file), 'NLP/{}'.format(file))

except Exception as errormsg:
    print('downloading failed...')
    print(errormsg)
    pass

#### 下載NLP字詞庫-完成  ####




#### 擷取google關鍵字  ####

time_trend = datetime.now().strftime('%Y%m%d')
time_trend = str(time_trend)

# 嘗試編碼擷取資料，若出現錯誤就中斷執行

try:
    # 修改網址為目前時間
    trends_url = 'https://trends.google.com.tw/trends/api/dailytrends?hl=zh-TW&tz=-480&ed={}&geo=TW&ns=15'.format(time_trend)

    res_trends = requests.get(trends_url)

    # 把干擾文字 )]}',\n 刪除 
    res_trends = re.sub(r'\)\]\}\',\n', '', res_trends.text)

    # 轉碼，不然不能看

    trends = res_trends.encode('utf-8').decode('unicode_escape')


    # 把json檔再轉成字串開始做正則處理
    trends_str = str(trends)
    trends_str = trends_str.replace('\"','\'')

    trends_content = re.findall("'query'.*?'snippet':",trends_str)

    trends_title_list = []
    trends_search_list = []
    trends_articles_list = []
    trends_url_list = []
    count_trends = 0

    for content in trends_content:
        count_trends+=1
        # 洗出標題
        trends_title = re.findall("'query'.*?,",content)
        trends_title = trends_title[0]
        trends_title = trends_title[9:-2]
        trends_title_list.append(trends_title)

        # 洗出搜尋量
        trends_search = re.findall("formattedTraffic.*?,",content)
        trends_search = trends_search[0]
        trends_search = trends_search[19:-2]
        trends_search_list.append(trends_search)    

        # 洗出第一則文章
        trends_articles = re.findall("'articles.*?timeAgo",content)
        trends_articles = trends_articles[0]
        trends_articles = trends_articles[22:-10]
        trends_articles_list.append(trends_articles)
        
        # 洗出文章超連結，抓不到就用google搜尋替代
        if 'newsUrl' or '\'Url' in content:
            trends_url = re.findall("newsUrl.*?',|'url':.*?',",content)
            trends_url = trends_url[0]
            trends_url = re.findall("http.*?',",content)
            trends_url = trends_url[0]
            trends_url = trends_url[:-2]
            trends_url_list.append(trends_url)
        else:
            trends_url = 'https://www.google.com/search?q='+trends_title
            trends_url_list.append(trends_url)


    print('google access ok')

    print('獲取標題筆數共： {} 筆'.format(len(trends_title_list)))
    print('獲取搜尋量筆數共： {} 筆'.format(len(trends_search_list)))
    print('獲取內文筆數共： {} 筆'.format(len(trends_articles_list)))
    print('獲取超連結筆數共： {} 筆'.format(len(trends_url_list)))


    ################ 編寫網頁內容  ################

    rw = open('separate/google.html','w',encoding = 'utf8')
    # r 讀取
    # w 寫入(刪除原本內容)
    # a 追加寫入


    # 寫入google trends
    title_trends = '<h2 style="text-align:center;background: #f00; color: #fff; margin: 0 4px; border-radius: 4px;">Google搜尋趨勢</h2>'
    rw.write(title_trends)

    # 寫入資料擷取時間
    time_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    time_news = '<div><h3 style="text-align:center;color:gray">資料擷取時間{}</h2></div>'.format(time_now)
    rw.write(time_news)

    for num in range(10):
        begin = '<item>'
        trends_title = (
            '<div style="text-align:left;font-size:20px;">'+
            '<span style="margin-left:20px;font-family:Lucida Console;color:#008000;">({})</span>'.format(num+1)+
            '<span style="margin-left:50px;margin-bottom:5px;font-weight:bold;">{}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>'.format(trends_title_list[num])+
            '<span>🔥&nbsp;{}筆搜尋</span></div>'.format(trends_search_list[num])
            )
        news = '<div style="text-align:left;margin-bottom:25px;margin-left:50px;font-size:20px;"><a href="{}" target="_blank">{}</a></div>'.format(trends_url_list[num],trends_articles_list[num])
        end = '</item>'
        rw.write(begin+trends_title+news+end)
        
except Exception as errormsg:
    print('google資料獲取失敗')
    today = datetime.now().strftime('%Y-%m-%d %H時')
    message = 'google資料獲取有誤，發生時間點：{}\n'.format(today)
    lineNotifyMessage(token, message+str(errormsg))
    time.sleep(5)
    os._exit(0)

rw.close()


### NLP字庫更新 ###
try:
    '''把排名前100大寫進詞庫內'''
    document = set([line.strip() for line in open("NLP/NLP-CN_words.txt",encoding="utf-8").readlines()])

    '''檢查文字是否包含在 Stop 內'''
    def wirte_in_doc(path):
        with open(path, 'a',encoding='utf-8') as f:
            for i in trends_title_list:
                if i not in document:
                    f.write("\n"+i)
        f.close()

    wirte_in_doc('NLP/NLP-CN_words.txt')
    wirte_in_doc('NLP/NLP-Event.txt')
except:
    print("Jerry 詞庫執行失敗")



#### 上傳更新的NLP字詞庫  ####

try:
    file_list = ['NLP-Audience.txt','NLP-CN_words.txt','NLP-Event.txt','NLP-Org.txt','NLP-People.txt','NLP-Region.txt','NLP-stopwords.txt']
    for file in file_list:
        print('uploading {}'.format(file))
        sftp.put('NLP/{}'.format(file) , '/var/www/html/keyword/NLP/{}'.format(file))

except Exception as errormsg:
    print('uploading failed...')
    print(errormsg)
    pass

#### 上傳更新的NLP字詞庫-完成  ####