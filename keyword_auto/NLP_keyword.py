#!/usr/bin/env python
# coding: utf-8

# In[1]:


'''時間要求 前天0:00 - 今天 01:00'''
from datetime import datetime,timedelta

yesterday = datetime.now() + timedelta(days = -1)
date = yesterday.strftime('%Y-%m-%d')
date2= datetime.now().strftime('%Y-%m-%d 01:00:00')
# date = "2023-05-04"
# date2= "2023-05-05 01:00:00"

'''資料庫連結測試'''
import mysql.connector,requests,os
import pandas as pd
import numpy as np
inhost = "ytdb1.ctitv.com.tw"
inuser = "dbuser"
inpwd  = "66007766"

'''設定 line 推播函式'''
def lineNotifyMessage(token, msg):
    headers = {
        "Authorization": "Bearer " + token, 
        "Content-Type" : "application/x-www-form-urlencoded"
    }

    payload = {'message': msg }
    r = requests.post("https://notify-api.line.me/api/notify", headers = headers, params = payload)
    return r.status_code
token = 'yyfusEhNOEMWmOQrmWDmz4vGGnmy59xI4KpzDRRcCAJ'


'''主程式'''
try:
    from opencc import OpenCC
    import time,os,re,requests
    import re

    query = f"""SELECT tim,nam,mess1 FROM dbYT_Chat.CTInewsMesg 
            WHERE tim between %s AND %s
            order by tim DESC;"""
    value = ((date),(date2))
    
    def LiveChat():
        mydb = mysql.connector.connect(host=inhost,user=inuser,password=inpwd)
        cursor = mydb.cursor()
        cursor.execute(query, value)
        df2 = pd.DataFrame(cursor.fetchall())
        df2.columns=["tim", "nam", "mess1"]
        mydb.close()
        return df2

    def clean(list_text):  
        list_text = re.sub(r"\{.+\}","", list_text)       # drop_url
        list_text = re.sub(r"\s+","", list_text)          # drop_blank
        return list_text

    data = LiveChat()
    data = data.drop_duplicates(subset=["mess1"]).reset_index(drop=True) 
    data['mess1'] = data['mess1'].apply(clean)
    data.head()
    
    
    freq = data['nam'].value_counts().to_frame()
    AudienceName = freq.index.values.tolist()
    AudienceName = [i.replace(" ","") for i in AudienceName if i] ## 
    document = set([line.strip() for line in open("NLP/NLP-CN_words.txt",encoding="utf-8").readlines()])
    audience_fifty = int(len(AudienceName)*0.3)   #前30%觀眾會被納入辭庫中

    def wirte_in_doc(path):
        with open(path, 'a',encoding='utf-8') as f:
            for i in AudienceName[0:audience_fifty]:
                f.write("\n"+i)
    wirte_in_doc('NLP/NLP-CN_words.txt')
    wirte_in_doc('NLP/NLP-Audience.txt')


    import json
    import jieba
    word_count = []
    data['mess2'] = data['mess1']
    jieba.load_userdict("NLP/NLP-CN_words.txt")  #lcut 自定義
    stop = [line.strip() for line in open("NLP/NLP-stopwords.txt",encoding="utf-8").readlines()]

    for i in range(len(data['mess1'])): 
        jiebawords = jieba.lcut(data['mess1'][i])

        char_to_sentence = []
        for chars in jiebawords:
            #檢查文字是否包含在 Stop 內
            if chars not in stop and len(chars)>1:
                char_to_sentence.append(chars)
                word_count.append(chars)
        data['mess2'][i] = char_to_sentence

        
    from collections import Counter
    sorted_list = []
    title = []
    counts = []
    jieba_word = Counter(word_count).most_common() 

    for j in range(len(jieba_word)): 
        title.append(jieba_word[j][0])
        counts.append(jieba_word[j][1])

    dicts = dict(zip(title,counts))   # comvine List(No stopword)
    
    #把排名前100大寫進詞庫內
    top100 = dict(zip(title[0:100],counts[0:100]))   # comvine List(No stopword)
    document = set([line.strip() for line in open("NLP/NLP-CN_words.txt",encoding="utf-8").readlines()])
    def wirte_in_doc(path):
        with open(path, 'a',encoding='utf-8') as f:
            for i in top100:
                if i not in document:
                    f.write("\n"+i)

    wirte_in_doc('NLP/NLP-CN_words.txt')
    wirte_in_doc('NLP/NLP-Event.txt')
    
    # WordsCloud
    import chardet 
    from matplotlib import pyplot as plt
    from wordcloud import WordCloud

    wc = WordCloud(background_color = 'white', 
               max_words=100,
               min_font_size = 12,   
               max_font_size = 160,
               scale = 9, 
               width=800, 
               height=400,
               font_path = 'C:\Windows\Fonts\Microsoft JhengHei\msjh.ttc',    # Chinese word path
               colormap = "Dark2_r"
              ).generate_from_frequencies(dicts)  

    plt.figure(figsize=(20,10))
    plt.imshow(wc) 
    plt.axis('off') 
    plt.tight_layout(pad=0) 

    plt.savefig('NLP/NLP-Cloud.png',bbox_inches='tight')
    #plt.show()    #先遮蔽
    
    # 選出前500筆大資料
    NLP_key= []
    NLP_val= []
    limite = 30
    for key,values in dicts.items():
        NLP_key.append(key)
        NLP_val.append(values)
        if values < limite : break

    def remove_duplicate(path):
        lines_seen = set()    
        doc = [line.strip() for line in open(path, encoding="utf-8").readlines()]
        doc = [Noblank for Noblank in doc if Noblank] ##
        with open(path, 'w',encoding='utf-8') as f:
            for line in doc:
                if line not in lines_seen:  # not a duplicate
                    f.write(line+"\n")
                    lines_seen.add(line)
    remove_duplicate('NLP/NLP-CN_words.txt')
    remove_duplicate('NLP/NLP-Audience.txt')
    remove_duplicate('NLP/NLP-Event.txt')
    remove_duplicate('NLP/NLP-Org.txt')
    remove_duplicate('NLP/NLP-People.txt')
    remove_duplicate('NLP/NLP-Region.txt')
    remove_duplicate('NLP/NLP-stopwords.txt')        
    
    # 將 HTML 寫入 NLP.html 檔案
    with open('separate/NLP.html', 'w', encoding='utf8') as rw:
        NLPList = '<h2 style="text-align:center;background: #f00; color: #fff; margin: 0 4px; border-radius: 4px;">聊天室分析</h2>'
        rw.write(NLPList)

        # 寫入資料擷取時間
        time_news = '<div><h3 style="text-align:center;color:gray">資料擷取時間從{}至{}</h2></div>'.format(date, date2)
        rw.write(time_news)
    
        # 定義一個函數，用於處理熱門討論的部分
        def write_hot_topics(title, nlp_key, nlp_values, dictionary,limite=10):
            rw.write('<div style="text-align:left;font-size:18px;margin-bottom:25px;">')
            rw.write('<div><h3 style="text-align:left;color:black">熱門討論：{}</h2></div>'.format(title))
            
            subnum = 0
            for num, (key, value) in enumerate(zip(nlp_key, nlp_values)):
                if key in dictionary:
                    subnum += 1
                    if subnum > limite: 
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
        
        def NLP_doc(doc):
            return [line.strip() for line in open(doc, encoding="utf-8").readlines()]

        # 左欄
        rw.write('<div style="width:30%;float:left;">')
        write_hot_topics("人物", NLP_key, NLP_val, NLP_doc("NLP/NLP-People.txt"))
        write_hot_topics("區域", NLP_key, NLP_val, NLP_doc("NLP/NLP-Region.txt"))
        
        rw.write('</div>')

        # 右欄
        rw.write('<div style="width:30%;float:left;">')
        write_hot_topics("組織", NLP_key, NLP_val, NLP_doc("NLP/NLP-Org.txt"))
        write_hot_topics("觀眾", NLP_key, NLP_val, NLP_doc("NLP/NLP-Audience.txt"))
        rw.write('</div>')

        # 右欄
        rw.write('<div style="width:40%;float:left;">')
        write_hot_topics("事件", NLP_key, NLP_val, NLP_doc("NLP/NLP-Event.txt"),24)
        rw.write('</div>')
        cloud_img = ('<br>'+'<img src="NLP/NLP-Cloud.png" width="65% alt="Cloud">')
        rw.write(cloud_img)
        
except Exception as errormsg:
    msg = '聊天室抓取有誤\n'
    lineNotifyMessage(token, msg+str(errormsg))
    os._exit(0)
