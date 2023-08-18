import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests,os

mpl.rc("font", family="Microsoft JhengHei")  # 增加中文字體

"""時間要求 前天0:00 - 今天 01:00"""
from datetime import datetime, timedelta

yesterday = datetime.now() + timedelta(days=-1)
date = yesterday.strftime("%Y-%m-%d 06:00")
date2 = datetime.today().strftime("%Y-%m-%d 00:00")

# date = yesterday.strftime("2023-08-09 06:00")
# date2 = datetime.today().strftime("2023-08-10 00:00")

print(date, "between", date2)


try:
    """資料庫連結測試"""
    import mysql.connector

    inhost = "ytdb1.ctitv.com.tw"
    inuser = "dbuser"
    inpwd = "66007766"
    query = f"""Select * from dbLiveStreamListViewers.ytLiveStreamListViewers 
            where 資料時間 BETWEEN %s AND %s AND 觀看量 >3 AND 影片類別 NOT LIKE "YT清單" 
            ORDER BY 資料時間 ASC;"""
    value = ((date), (date2))

    def onlineview():
        mydb = mysql.connector.connect(host=inhost, user=inuser, password=inpwd)
        cursor = mydb.cursor()
        cursor.execute(query, value)
        df = pd.DataFrame(cursor.fetchall())
        df.columns = ["iD", "資料時間", "頻道ID", "PIC連結", "標題", "觀看量", "頻道名稱", "影片類別"]
        mydb.close()
        return df

    df = onlineview()
    df["小時"] = df["資料時間"]

    for i in range(len(df["資料時間"])):
        df.loc[i, "資料時間"] = datetime.strptime(df["資料時間"][i][:16], "%Y-%m-%d %H:%M")
        df.loc[i, "小時"] = df["資料時間"][i].hour
    #df.head()


    # ###  將所有頻道的資料製作成圖表
    ## 切割各頻道在線人數
    CTI = df[(df["頻道名稱"] == "中天電視") & (df["影片類別"] == "大直播")].reset_index(drop=True)
    CTI2 = df[df["頻道名稱"] == "中天新聞"].reset_index(drop=True)
    TTV = df[(df["頻道名稱"] == "台視新聞 TTV NEWS") & (df["影片類別"] == "大直播")].reset_index(drop=True)
    SET = df[(df["頻道名稱"] == "三立LIVE新聞") & (df["影片類別"] == "大直播")].reset_index(drop=True)
    FTV = df[(df["頻道名稱"] == "民視新聞網 Formosa TV News network") & (df["影片類別"] == "大直播")].reset_index(drop=True)
    EBC = df[(df["頻道名稱"] == "東森新聞 CH51") & (df["影片類別"] == "大直播")].reset_index(drop=True)
    TVBS = df[(df["頻道ID"] == "m_dhMSvUCIc") & (df["影片類別"] == "大直播")].reset_index(drop=True)
    FIN = df[(df["頻道名稱"] == "57東森財經新聞") & (df["影片類別"] == "大直播")].reset_index(drop=True)
    CTV = df[(df["頻道名稱"] == "中視新聞 HD直播頻道｜Taiwan CTV news HD Live") & (df["影片類別"] == "大直播")].reset_index(drop=True)

    # 全球大視野	大新聞大爆卦 頭條開講
    Global_Vision = df[(df["頻道名稱"] == "全球大視野") & (df["影片類別"] == "全球大視野")].reset_index(drop=True)
    HotNewsTalk = df[(df["頻道名稱"] == "大新聞大爆卦") & (df["影片類別"] == "大新聞大爆卦")].reset_index(drop=True)
    HeadlinesTalk = df[(df["頻道名稱"] == "頭條開講") & (df["影片類別"] == "頭條開講")].reset_index(drop=True)
    CTI2_combine = (
        pd.concat([CTI2, Global_Vision, HotNewsTalk, HeadlinesTalk])
        .reset_index()
        .sort_values("資料時間", ascending=True)
    )
    All_Channel = pd.concat(
        [CTI, CTI2_combine, TTV, SET, FTV, EBC, TVBS, FIN, CTV]
    ).reset_index()


    def Channels(x1, y1, labels, color, label="Y", linestyle = "solid"):
        x = x1.tolist()
        y = y1.tolist()
        ax.plot(x1, y1, label=labels, color=color , linestyle=linestyle)

        ymax = max(y)
        xpos = y.index(ymax)
        xmax = x[xpos]
        ax.plot(xmax, ymax, "ro")
        if label != "N":
            ax.text(xmax, ymax + 200, "" + str(ymax))


    fig, ax = plt.subplots(figsize=(12, 4), layout="constrained")
    Channels(CTI["資料時間"], CTI["觀看量"], "中天電視", "royalblue", "N")
    Channels(CTI2_combine["資料時間"], CTI2_combine["觀看量"], "中天子頻", "dodgerblue", "N")

    cdf = mpl.dates.ConciseDateFormatter(ax.xaxis.get_major_locator())
    ax.xaxis.set_major_formatter(cdf)
    ax.set_xlabel("時間")
    ax.set_ylabel("同時在線人數")
    ax.set_title("平均小時 | 同時在線觀看人數")
    ax.legend()
    plt.savefig("img/IMG_24.png", bbox_inches="tight")



    # In[4]:


    pivot = pd.pivot_table(
        All_Channel,
        values=["觀看量"],
        index=["頻道名稱"],
        columns=["小時"],
        aggfunc="mean",
        fill_value=0,
        margins=False,
        dropna=True,
        margins_name="All",
        observed=False,
        sort=True,
    ).astype(
        int
    )
    pivot = pivot.rename_axis(None)



    with open("index.html", "w", encoding="utf8") as rw:
        # head
        rw.write('<head>')
        rw.write('<meta charset="UTF-8">')
        rw.write('<link rel="stylesheet" type="text/css" href="df_style.css"/>')
        rw.write('<link rel="icon" href="img/favicon.ico">')
        rw.write('<title>同時在線觀看人數</title>')
        rw.write('</head>')

        # Title
        rw.write('<h1 class="title-big" style="text-align:center">同時在線觀看人數</h1>')
        # Time
        time_news = (
            '<div><h3 style="text-align:center;color:gray">資料擷取時間從{}至{}</h2></div>'.format(date, date2)
        )
        rw.write(time_news)
        ### All Time
        IMG_24 = "<br>" + '<img src="img/IMG_24.png" width="60% alt="Avg">'
        rw.write(IMG_24)
        result = pivot.to_html(classes="mystyle")
        rw.write(result)
        rw.write("<hr>")


    # ### 午晚報

    def LineChart(time):
        CTI_noon = noon(CTI,time)
        CTI2_noon = noon(CTI2,time)
        TTV_noon = noon(TTV,time)
        SET_noon = noon(SET,time)
        FTV_noon = noon(FTV,time)
        EBC_noon = noon(EBC,time)
        TVBS_noon = noon(TVBS,time)
        FIN_noon = noon(FIN,time)
        CTV_noon = noon(CTV,time)
        return [CTI_noon,CTI2_noon,TTV_noon,SET_noon,FTV_noon,EBC_noon,TVBS_noon,FIN_noon,CTV_noon]

    def noon(cahnnel,time_noon):
        return cahnnel.loc[
            (cahnnel["小時"] == time_noon[0])
            | (cahnnel["小時"] == time_noon[1])
            | (cahnnel["小時"] == time_noon[2])
        ]

    def piv(time,x):
        All_noon = pd.concat(x).reset_index()
        pivot = pd.pivot_table(
            All_noon,
            values=["觀看量"],
            index=["小時"],
            columns=["頻道名稱"],
            aggfunc="mean",
            fill_value=0,
            margins=False,
            dropna=True,
            margins_name="All",
            sort=True,
        ).astype(int)["觀看量"]  # astype 轉換為列表
        pivot = pivot.rename_axis(None) 
        
        i, j, k = time[1], time[2], "時段平均"
        ans = pd.DataFrame(
            {
                "Hour": [str(i) + "點", str(j) + "點", k],
                "中天電視": [
                    pivot.loc[i, "中天電視"],
                    pivot.loc[j, "中天電視"],
                    (pivot.loc[i, "中天電視"] + pivot.loc[j, "中天電視"]) / 2,
                ],
                "中天新聞": [
                    pivot.loc[i, "中天新聞"],
                    pivot.loc[j, "中天新聞"],
                    (pivot.loc[i, "中天新聞"] + pivot.loc[j, "中天新聞"]) / 2,
                ],
                "台視": [
                    pivot.loc[i, "台視新聞 TTV NEWS"],
                    pivot.loc[j, "台視新聞 TTV NEWS"],
                    (pivot.loc[i, "台視新聞 TTV NEWS"] + pivot.loc[j, "台視新聞 TTV NEWS"]) / 2,
                ],
                "三立LIVE": [
                    pivot.loc[i, "三立LIVE新聞"],
                    pivot.loc[j, "三立LIVE新聞"],
                    (pivot.loc[i, "三立LIVE新聞"] + pivot.loc[j, "三立LIVE新聞"]) / 2,
                ],
                "民視": [
                    pivot.loc[i, "民視新聞網 Formosa TV News network"],
                    pivot.loc[j, "民視新聞網 Formosa TV News network"],
                    (pivot.loc[i, "民視新聞網 Formosa TV News network"] + pivot.loc[j, "民視新聞網 Formosa TV News network"]) / 2,
                ],
                "東森": [
                    pivot.loc[i, "東森新聞 CH51"],
                    pivot.loc[j, "東森新聞 CH51"],
                    (pivot.loc[i, "東森新聞 CH51"] + pivot.loc[j, "東森新聞 CH51"]) / 2,
                ],
                "TVBS": [
                    pivot.loc[i, "TVBS NEWS"],
                    pivot.loc[j, "TVBS NEWS"],
                    (pivot.loc[i, "TVBS NEWS"] + pivot.loc[j, "TVBS NEWS"]) / 2,
                ],
                "中視": [
                    pivot.loc[i, "中視新聞 HD直播頻道｜Taiwan CTV news HD Live"],
                    pivot.loc[j, "中視新聞 HD直播頻道｜Taiwan CTV news HD Live"],
                    (pivot.loc[i, "中視新聞 HD直播頻道｜Taiwan CTV news HD Live"] + pivot.loc[j, "中視新聞 HD直播頻道｜Taiwan CTV news HD Live"]) / 2,
                ],
                "東森財經": [
                    pivot.loc[i, "57東森財經新聞"],
                    pivot.loc[j, "57東森財經新聞"],
                    (pivot.loc[i, "57東森財經新聞"] + pivot.loc[j, "57東森財經新聞"]) / 2,
                ],
            }
        )
        ans.set_index("Hour", inplace=True)
        ans = ans.rename_axis(None)
        ans = ans.astype(int)
        return ans


    # In[7]:


    # 午報 
    x = LineChart([11, 12, 13])
    fig, ax = plt.subplots(figsize=(12, 6), layout="constrained")
    Channels(x[0]["資料時間"], x[0]["觀看量"], "中天電視", "royalblue")
    Channels(x[1]["資料時間"], x[1]["觀看量"], "中天新聞", "dodgerblue")
    Channels(x[2]["資料時間"], x[2]["觀看量"], "台視", "orange")
    Channels(x[3]["資料時間"], x[3]["觀看量"], "三立LIVE", "green")
    Channels(x[4]["資料時間"], x[4]["觀看量"], "民視", "limegreen")
    Channels(x[5]["資料時間"], x[5]["觀看量"], "東森", "purple")
    Channels(x[6]["資料時間"], x[6]["觀看量"], "TVBS", "gray")
    Channels(x[7]["資料時間"], x[7]["觀看量"], "東森財經", "orchid")
    Channels(x[8]["資料時間"], x[8]["觀看量"], "中視", "red","Y","dashed")
    cdf = mpl.dates.ConciseDateFormatter(ax.xaxis.get_major_locator())
    ax.xaxis.set_major_formatter(cdf)
    ax.set_xlabel("時間")
    ax.set_ylabel("同時在線人數")
    ax.set_title("午報平均小時 | 同時在線觀看人數")
    ax.legend()
    plt.savefig("img/IMG_12.png", bbox_inches="tight")


    ### 繪圖
    df_moon = piv([11, 12, 13],x)
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(10, 3), layout="constrained")  # 拉寬畫布
    x = list(df_moon.columns)
    h = df_moon.iloc[1].tolist()
    x2 = list(df_moon.columns)
    h2 = df_moon.iloc[2].tolist()
    bar1 = ax.bar(x, h, color="lightcoral", width=0.3, align="edge")  # 第一組數據靠左邊緣對齊
    bar2 = ax.bar(x2, h2, color="cornflowerblue", width=0.2)  # 第二組數據置中對齊
    plt.savefig("img/AVG_12.png", bbox_inches="tight")


    ## Web
    with open("index.html", "a", encoding="utf8") as rw:
        rw.write("<br>" + '<img src="img/IMG_12.png" width="50% alt="Avg">')
        rw.write("<br>" + '<img src="img/AVG_12.png" width="50% alt="Avg">')
        result = df_moon.to_html(classes="mystyle")
        rw.write(result)
        rw.write("<hr>")

    #df_moon.head()


    # In[8]:


    # 晚報 
    x = LineChart([17, 18, 19])
    fig, ax = plt.subplots(figsize=(12, 6), layout="constrained")
    Channels(x[0]["資料時間"], x[0]["觀看量"], "中天電視", "royalblue")
    Channels(x[1]["資料時間"], x[1]["觀看量"], "中天新聞", "dodgerblue")
    Channels(x[2]["資料時間"], x[2]["觀看量"], "台視", "orange")
    Channels(x[3]["資料時間"], x[3]["觀看量"], "三立LIVE", "green")
    Channels(x[4]["資料時間"], x[4]["觀看量"], "民視", "limegreen")
    Channels(x[5]["資料時間"], x[5]["觀看量"], "東森", "purple")
    Channels(x[6]["資料時間"], x[6]["觀看量"], "TVBS", "gray")
    #Channels(x[7]["資料時間"], x[7]["觀看量"], "東森財經", "orchid")
    Channels(x[8]["資料時間"], x[8]["觀看量"], "中視", "red","Y","dashed")
    cdf = mpl.dates.ConciseDateFormatter(ax.xaxis.get_major_locator())
    ax.xaxis.set_major_formatter(cdf)
    ax.set_xlabel("時間")
    ax.set_ylabel("同時在線人數")
    ax.set_title("晚報平均小時 | 同時在線觀看人數")
    ax.legend()
    plt.savefig("img/IMG_18.png", bbox_inches="tight")



    ### 繪圖
    df_night = piv([17, 18, 19],x)
    df_night = df_night.drop(['東森財經'], axis=1)
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(10, 3), layout="constrained")  # 拉寬畫布
    x = list(df_night.columns)
    h = df_night.iloc[1].tolist()
    x2 = list(df_night.columns)
    h2 = df_night.iloc[2].tolist()
    bar1 = ax.bar(x, h, color="lightcoral", width=0.3, align="edge")  # 第一組數據靠左邊緣對齊
    bar2 = ax.bar(x2, h2, color="cornflowerblue", width=0.2)  # 第二組數據置中對齊
    plt.savefig("img/AVG_18.png", bbox_inches="tight")


    ## Web
    with open("index.html", "a", encoding="utf8") as rw:
        rw.write("<br>" + '<img src="img/IMG_18.png" width="50% alt="Avg">')
        rw.write("<br>" + '<img src="img/AVG_18.png" width="50% alt="Avg">')
        result = df_night.to_html(classes="mystyle")
        rw.write(result)
        rw.write("<hr>")
        #df_night.head()

except Exception as errormsg:

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

    print('在線人數資料獲取失敗')
    today = datetime.now().strftime('%Y-%m-%d %H時')
    message = '在線人數資料獲取有誤，發生時間點：{}\n'.format(today)
    lineNotifyMessage(token, message+str(errormsg))
    os._exit(0)


