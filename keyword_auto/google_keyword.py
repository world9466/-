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
token = 'm6uafWsyIziRWXaqYfTKJxNShGYlp3WM3RG9e0hP2OA'


#### 下載NLP字詞庫  ####

# 建立連線
client = paramiko.SSHClient()

client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

client.connect(hostname='10.227.58.87', username='root', password='0266007766')
t = client.get_transport()
sftp=paramiko.SFTPClient.from_transport(t)

try:
    file_list = ['NLP-CN_words.txt','NLP-Event.txt','NLP-Org.txt','NLP-People.txt','NLP-Region.txt','NLP-stopwords.txt']
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


###寫入關鍵字至 txt - trends_title_list

'''把 Google 資料拆分後 放入字典'''
import jieba
import jieba.posseg as pseg


try:
    for i in range(len(trends_title_list)): 
        text = trends_title_list[i]
        words = pseg.cut(text)
        print(f'text:{text}')
        for word, flag in words:
            #基本字典
            if len(word) > 1:
                with open('NLP/NLP-CN_words.txt', 'a',encoding='utf-8') as f:
                    f.write(word+"\n")

            #個人字典
            if flag == 'nr' or flag == 'nrfg':
                if len(word) > 2:
                    print("人名：", word)
                    with open('NLP/NLP-People.txt', 'a',encoding='utf-8') as f:
                        f.write(word+"\n")

            elif flag == 'ns' or flag == 'nrt':
                if len(word) >1:
                    print("地名：", word)
                    with open('NLP/NLP-Region.txt', 'a',encoding='utf-8') as f:
                        f.write(word+"\n")

            elif flag == 'nt':
                if len(word) >1:
                    print("組織：", word)
                    with open('NLP/NLP-Org.txt', 'a',encoding='utf-8') as f:
                        f.write(word+"\n")
            else:
                if len(word) >1:
                    print("事件：", word)
                    with open('NLP/NLP-Event.txt', 'a',encoding='utf-8') as f:
                        f.write(word+"\n")
    f.close()


    ### 剔除已有單字
    stopList = ["NLP/NLP_People.txt","NLP/NLP_Region.txt","NLP_Org"]
    stop = [line.strip() for line in open("NLP/NLP-stopwords.txt",encoding="utf-8").readlines()]
    with open('NLP/NLP-Event.txt', 'a',encoding='utf-8') as f:
                        f.write(word+"\n")


    ''' 重複內容過濾'''
    StopList = ['NLP/NLP-Region.txt','NLP/NLP-Org.txt','NLP/NLP-People.txt']

    with open('NLP/NLP-Event.txt', 'r', encoding='utf-8') as f1:
        nlp_event = set(f1.read().splitlines())


    for i in range(len(StopList)):
        with open(StopList[i], 'r', encoding='utf-8') as f2:
            nlp_stop = set(f2.read().splitlines())


        overlap = nlp_event.intersection(nlp_stop)
        if overlap:
            print("有重複的內容：", overlap)
            with open('NLP/NLP-Event.txt', 'r+', encoding='utf-8') as f5:
                lines = f5.readlines()
                f5.seek(0)
                for line in lines:
                    if line.strip() not in overlap:
                        f5.write(line)
                f5.truncate()
            print("重複的內容已自動刪除")
        else:
            print("沒有重複的內容")

    ### 刪除重複字元
    def overwrite(txt):  
        with open(txt, 'r',encoding="utf-8") as f:
            lines = f.readlines()
        lines = list(set(lines))
        with open(txt, 'w',encoding="utf-8") as f:
            f.writelines(lines)

    overwrite('NLP/NLP-People.txt')
    overwrite('NLP/NLP-Region.txt')
    overwrite('NLP/NLP-Event.txt')
    overwrite('NLP/NLP-Org.txt')
    overwrite('NLP/NLP-CN_words.txt')
    overwrite('NLP/NLP-stopwords.txt')    
    
except:
    print('寫入關鍵字失敗')
    time.sleep(5)
    os._exit(0)



#### 上傳更新的NLP字詞庫  ####

try:
    file_list = ['NLP-CN_words.txt','NLP-Event.txt','NLP-Org.txt','NLP-People.txt','NLP-Region.txt','NLP-stopwords.txt']
    for file in file_list:
        print('uploading {}'.format(file))
        sftp.put('NLP/{}'.format(file) , '/var/www/html/keyword/NLP/{}'.format(file))

except Exception as errormsg:
    print('uploading failed...')
    print(errormsg)
    pass

#### 上傳更新的NLP字詞庫-完成  ####