import requests
import os
import telegram
from bs4 import BeautifulSoup
import pymysql

token = '413482486:AAHdbEUmbQEiejyg--DVtOStHT-EDlwBKE0'
conn = pymysql.connect(host='localhost', user='telegram', password='*Whdg1839t', db='telegram_bot', charset='utf8')
curs = conn.cursor()

sql = 'select id, recent_update from bot where bot_id = \'' + token + '\''
curs.execute(sql)
rows = curs.fetchall()
botTableId = rows[-1][0]
recent_update = rows[-1][1]

bot = telegram.Bot(token=token)

# process commend
botUpdates = bot.getUpdates(offset=recent_update)
if botUpdates[-1].update_id != recent_update:
    for update in botUpdates:
        if update.update_id != recent_update:
            chatId = update.message.chat.id
            if str(update.message.text) == 'join':
                curs.execute('select * from user where chat_id =' + str(chatId))
                rows = curs.fetchall()
                if len(rows) == 0:
                    curs.execute('insert into user (chat_id, bot_id) values (' + str(chatId) + ', ' + str(botTableId) + ')')    
                    conn.commit()
                    bot.sendMessage(chat_id=chatId, text='enrollment success')
                else:
                    bot.sendMessage(chat_id=chatId, text='already enrolled')
            else:
                bot.sendMessage(chat_id=chatId, text='failure')

curs.execute('update bot set recent_update = ' + str(botUpdates[-1].update_id) + ' where id = ' + str(botTableId))
conn.commit()

# Get Users
curs.execute('select chat_id from user where is_deleted != 1 and bot_id = ' + str(botTableId))
chatIds = curs.fetchall()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

req = requests.get('http://cse.pusan.ac.kr/cse/14651/subview.do?enc=Zm5jdDf8QEB8JTJGYmJzJTJGY3NIJTJGMjYwNSUyRmFydGNsTGlzdC5kbyUzRg%3D%3D')
req.encoding = 'utf-8'

html = req.text
soup = BeautifulSoup(html, 'html.parser')

posts = soup.find_all('table')[0]
posts = posts.find_all('tr')

items = []
for tr in posts: 
    if tr.td and tr.td.text:
        if tr.td.text.isdigit():
            title = tr.select('td._artclTdTitle')[0].a.strong.text
            num = tr.td.text
            url = 'http://cse.pusan.ac.kr' + tr.select('td._artclTdTitle')[0].a['href']
            items.append((title, num, url))

with open(os.path.join(BASE_DIR, 'cse.txt'), 'r+') as f_read:
    beforeNum = f_read.readline()
    beforeTitle = f_read.readline()
    f_read.close()
    if beforeNum != items[0][1] or beforeTitle != items[0][0]:
        for item in items:
            title = item[0]
            num = item[1]
            url = item[2]
            if int(num) == int(beforeNum):
                if title != beforeTitle:
                    for chatId in chatIds:
                        bot.sendMessage(chat_id=chatId[0], text='[MODIFIED] No. ' + num + ' [Notice] ' + title + '\n' + url)
                break
            else:
                for chatId in chatIds:
                    bot.sendMessage(chat_id=chatId[0], text='No. ' + num + ' [Notice] ' + title + '\n' + url)
        with open(os.path.join(BASE_DIR, 'cse.txt'), 'w+') as f_write:
            f_write.write(items[0][1])
            f_write.write('\n')
            f_write.write(items[0][0])
            f_write.close()

req = requests.get('http://cse.pusan.ac.kr/cse/14655/subview.do')
req.encoding = 'utf-8'

html = req.text
soup = BeautifulSoup(html, 'html.parser')

posts = soup.find_all('table')[0]
posts = posts.find_all('tr')

items = []
for tr in posts: 
    if tr.td and tr.td.text:
        if tr.td.text.isdigit():
            title = tr.select('td._artclTdTitle')[0].a.strong.text
            num = tr.td.text
            url = 'http://cse.pusan.ac.kr' + tr.select('td._artclTdTitle')[0].a['href']
            items.append((title, num, url))

with open(os.path.join(BASE_DIR, 'cse_term.txt'), 'r+') as f_read:
    beforeNum = f_read.readline()
    beforeTitle = f_read.readline()
    f_read.close()
    if beforeNum != items[0][1] or beforeTitle != items[0][0]:
        for item in items:
            title = item[0]
            num = item[1]
            url = item[2]
            if int(num) == int(beforeNum):
                if title != beforeTitle:
                    for chatId in chatIds:
                        bot.sendMessage(chat_id=chatId[0], text='[MODIFIED] No. ' + num + ' [Term] ' + title + '\n' + url)
                break
            else:
                for chatId in chatIds:
                    bot.sendMessage(chat_id=chatId[0], text='No. ' + num + ' [Term] ' + title + '\n' + url)
        with open(os.path.join(BASE_DIR, 'cse_term.txt'), 'w+') as f_write:
            f_write.write(items[0][1])
            f_write.write('\n')
            f_write.write(items[0][0])
            f_write.close()




conn.close()
