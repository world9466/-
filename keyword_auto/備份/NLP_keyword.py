'''時間要求 前天0:00 - 今天 01:00'''
from datetime import datetime,timedelta
yesterday = datetime.now() + timedelta(days = -1)
date = yesterday.strftime('%Y-%m-%d')
date2= datetime.now().strftime('%Y-%m-%d 01:00:00')

#pip install opencc
#pip install mysql-connector
#pip install wordcloud
#pip install chardet

# date = "2023-04-15"
# date2= "2023-04-16 01:00:00"


'''資料庫連結測試'''
import mysql.connector
import pandas as pd
import numpy as np
inhost = "ytdb1.ctitv.com.tw"
inuser = "dbuser"
inpwd  = "66007766"
# mydb = mysql.connector.connect(host = inhost,user = inuser,password = inpwd)
# mydb.close()


'''設定 line 推播函式'''
def lineNotifyMessage(token, msg):
    headers = {
        "Authorization": "Bearer " + token, 
        "Content-Type" : "application/x-www-form-urlencoded"
    }

    payload = {'message': msg }
    r = requests.post("https://notify-api.line.me/api/notify", headers = headers, params = payload)
    return r.status_code
token = 'm6uafWsyIziRWXaqYfTKJxNShGYlp3WM3RG9e0hP2OA'


'''主程式'''
try:
    from opencc import OpenCC
    import time,os,re,requests
    import re

    def LiveChat():
        mydb = mysql.connector.connect(host=inhost,user=inuser,password=inpwd)
        cursor = mydb.cursor()
        query = f"""
            SELECT * FROM dbYT_Chat.CTInewsMesg 
            WHERE tim between %s AND %s
            order by tim DESC;
        """
        value = ((date),(date2))
        cursor.execute(query, value)
        df2 = pd.DataFrame(cursor.fetchall())
        df2.columns=["iD", "tim", "nam", "authimg", "mess1", "type", "channel"]
        mydb.close()
        return df2

    data = LiveChat()
    data = data.sort_index(ascending=False)
    data = data.drop(columns=['iD','authimg','type','channel'])

    def clean(list_text):  
        list_text = re.sub(r"\{.+\}","", list_text)       # drop_url
        list_text = re.sub(r"\s+","", list_text)          # drop_blank
        return list_text

    data['mess2'] = data['mess1'].apply(clean)
    data.head()

    from collections import Counter
    import json
    import jieba

    all_words = []
    data['mess3'] = data['mess2']
    data['Association'] = data['mess2']
    jieba.load_userdict("NLP/NLP-CN_words.txt")  #lcut 自定義
    stop = [line.strip() for line in open("NLP/NLP-stopwords.txt",encoding="utf-8").readlines()]

    for i in range(len(data['mess2'])): 
        afterstop=[]
        a = jieba.lcut(data['mess2'][i])
        for seg in a:
            '''剃除停用字，且過濾大於1文字'''
            if seg not in stop and len(seg)>1:
                all_words.append(seg)
                afterstop.append(seg)

        data['mess3'][i] = str(afterstop)
        data['Association'][i] = np.array(afterstop)
        #print('過濾後',afterstop)

    jieba_word = sorted(dict(Counter(all_words)).items(), key=lambda d:d[1], reverse=True)  
    jiebaoutput = data.drop(columns=['mess1','mess2','Association'])
    sorted_list = []
    title = []
    counts = []
    for words in jieba_word:                     # List 內的 tuple 轉 List
        sorted_list += [list(words)]

    for j in range(len(sorted_list)):            # Counter 統計
        if len(sorted_list[j][0])> 1:            # only word >1 can in table count
            title.append(sorted_list[j][0])
            counts.append(sorted_list[j][1])

    dicts = dict(zip(title,counts))   # comvine List(No stopword)
    
    # WordsCloud
    #pip install chardet
    #pip install wordcloud
    import chardet 
    from matplotlib import pyplot as plt
    from wordcloud import WordCloud

    wc = WordCloud(background_color = 'white',                                    # Background 
                   #mask = np.array(Image.open(path.join(d, "wave.png"))),        # masked 
                   min_font_size = 8,    
                   scale = 9,                                                     # Scaling between computation and drawing.
                   font_path = 'C:\Windows\Fonts\Microsoft JhengHei\msjh.ttc',    # Chinese word path
                  ) .generate_from_frequencies(dicts)  
    plt.imshow(wc,interpolation='bilinear') 
    plt.axis('off') 
    plt.tight_layout() 

    plt.savefig('NLP/NLP-Cloud.png',dpi=100)
    #plt.show()
    
    # 選出前500筆大資料
    NLP_key= []
    NLP_val= []
    i = 0
    for key,values in dicts.items():
        NLP_key.append(key)
        NLP_val.append(values)
        i += 1 
        if i == 800:
            break
    print(date,date2)

    # 讀取 NLP-People.txt, NLP-Region.txt 和 NLP-Org.txt
    NLP_People = [line.strip() for line in open("NLP/NLP-People.txt", encoding="utf-8").readlines()]
    NLP_Region = [line.strip() for line in open("NLP/NLP-Region.txt", encoding="utf-8").readlines()]
    NLP_Org = [line.strip() for line in open("NLP/NLP-Org.txt", encoding="utf-8").readlines()]
    NLP_Event = [line.strip() for line in open("NLP/NLP-Event.txt", encoding="utf-8").readlines()]

    # 將 HTML 寫入 NLP.html 檔案
    with open('separate/NLP.html', 'w', encoding='utf8') as rw:
        NLPList = '<h2 style="text-align:center;background: #f00; color: #fff; margin: 0 4px; border-radius: 4px;">聊天室分析</h2>'
        rw.write(NLPList)

        # 寫入資料擷取時間
        time_news = '<div><h3 style="text-align:center;color:gray">資料擷取時間從{}至{}</h2></div>'.format(date, date2)
        rw.write(time_news)

        # 定義一個函數，用於處理熱門討論的部分
        def write_hot_topics(title, nlp_key, nlp_values, dictionary):
            rw.write('<div style="text-align:left;font-size:18px;margin-bottom:25px;">')
            rw.write('<div><h3 style="text-align:left;color:black">熱門討論：{}</h2></div>'.format(title))
            
            subnum = 0
            for num, (key, value) in enumerate(zip(nlp_key, nlp_values)):
                if key in dictionary:
                    subnum += 1
                    if subnum > 10:
                        break;
                    else:
                        
                        print(key, value)
                        NLPs = ('<br><span style="margin-left:20px;font-family:Lucida Console;color:#4169e1;">({})</span>'.format(subnum)+
                                '<span style="margin-bottom:5px;margin-left:20px;">'+
                                '<a target="_blank" style="color:#000000;font-weight:bold;">'+
                                '{} - 出現 {} 次&nbsp;</a></span>'.format(key, value))
                        rw.write(NLPs)
            rw.write('</div>')
            print("-----------")   

#         # 處理熱門討論的三個部分
#         write_hot_topics("人物", NLP_key, NLP_val,NLP_People)
#         write_hot_topics("區域", NLP_key, NLP_val,NLP_Region)
#         write_hot_topics("組織", NLP_key, NLP_val,NLP_Org)
#         write_hot_topics("事件", NLP_key, NLP_val,NLP_Event)
        
        # 左欄
        rw.write('<div style="width:50%;float:left;">')
        write_hot_topics("人物", NLP_key, NLP_val,NLP_People)
        write_hot_topics("區域", NLP_key, NLP_val,NLP_Region)
        rw.write('</div>')

        # 右欄
        rw.write('<div style="width:50%;float:right;">')
        write_hot_topics("組織", NLP_key, NLP_val,NLP_Org)
        write_hot_topics("事件", NLP_key, NLP_val,NLP_Event)
        rw.write('</div>')


        cloud_img = ('<br><div><h3 style="text-align:left;color:black">熱門討論：文字雲</h2></div>'+
                     '<img src="NLP/NLP-Cloud.png" alt="Cloud">')
        rw.write(cloud_img)
    
except Exception as errormsg:
    print('聊天室抓取有誤')
    lineNotifyMessage(token,str(errormsg))
    os._exit(0)