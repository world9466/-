from datetime import datetime


time_thisday = datetime.now().strftime('%Y-%m-%d')
title = '<h1 class="title-big" style="text-align:center">數據中心-晨報{}</h1>'.format(time_thisday)

rw = open('separate/title.html','w',encoding = 'utf8')

rw.write(title)

rw.close()

