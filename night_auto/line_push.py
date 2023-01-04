import requests
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

# token 根據發送頻道不同有不同的密鑰
token = 'ZGBI0dIu8Yr00txZHfbfmFvcXBX8hc36vAGZ4fncsxw'
today = datetime.now().strftime('%Y-%m-%d')
message = '({})今日晚報已更新\n公司內部網站：\nhttp://10.227.58.87/night-news/\n公司外部網路連結：\nhttp://60.251.107.160:8100/night-news/\n※非公司內部網路請點擊外網連結'.format(today)
lineNotifyMessage(token, message)



# 發行新token
# https://access.line.me/oauth2/v2.1/login?loginState=aF7qMuO8ssZLVlLjQcf93m&loginChannelId=1476232700&returnUri=%2Foauth2%2Fv2.1%2Fauthorize%2Fconsent%3Fscope%3Dprofile%2Bopenid%2Bbot.add%26response_type%3Dcode%26redirect_uri%3Dhttps%253A%252F%252Fnotify-bot.line.me%252Flogin%252Fcallback%26state%3DYdjEfPIAz3JaBbkXJMgfOd%26nonce%3DE9jCXTkpS9CsFqbU2UYuQi%26client_id%3D1476232700#/