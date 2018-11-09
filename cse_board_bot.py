import requests
import os
import telegram
from bs4 import BeautifulSoup
import pymysql

token = '413482486:AAHdbEUmbQEiejyg--DVtOStHT-EDlwBKE0'
conn = pymysql.connect(host='localhost', user='telegram', password='', db='telegram_bot', charset='utf8')
curs = conn.cursor()

bot = telegram.Bot(token=token)

sql = "select id, recent_update from bot where bot_id = '{}'".format(token) 
curs.execute(sql)
rows = curs.fetchall()
botTableId = rows[-1][0]
recent_update = rows[-1][1]

def getNewMessage():
    # Get new message from telegram
    # Message is only available in 24 hours
    botUpdates = bot.getUpdates(offset=recent_update)
    if botUpdates[-1].update_id != recent_update:
        for update in botUpdates:
            if update.update_id != recent_update:
                chatId = update.message.chat.id
                def checkUserInDB(chatId):
                    curs.execute('select * from user where chat_id = {}'.format(str(chatId)))
                    rows = curs.fetchall()
                    return len(rows) != 0
                if str(update.message.text) == 'join':
                    if not checkUserInDB(chatId):
                        curs.execute('insert into user (chat_id, bot_id) values ({}, {})'.format(str(chatId), str(botTableId)))
                        conn.commit()
                        raise bot.sendMessage(chat_id=chatId, text='You\'ve been sucessfully enrolled')
                    else:
                        raise bot.sendMessage(chat_id=chatId, text='You are already part of us') 
                elif str(update.message.text) == 'bye':
                    if checkUserInDB(chatId):
                        try:
                            curs.execute('delete from user where chat_id = {}'.format(str(chatId)))
                            conn.commit()
                            raise bot.sendMessage(chat_id=chatId, text='Bye~')
                        except:
                            raise bot.sendMessage(chat_id=chatId, text='Fail...')
                    else:
                        raise bot.sendMessage(chat_id=chatId, text='You are not enrolled')
                else:
                    raise bot.sendMessage(chat_id=chatId, text='I do not know what you mean')

        curs.execute('update bot set recent_update = {} where id = {}'.format(str(botUpdates[-1].update_id), str(botTableId)))
        conn.commit()
    return

try:
    getNewMessage()
except:
    pass

# Get Users
curs.execute('select chat_id from user where is_deleted != 1 and bot_id = {}'.format(str(botTableId)))
chatIds = curs.fetchall()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def cseBot(baseurl, suburl, boardType):
    print('Request to {}{}'.format(baseurl, suburl)) 
    print('Type: {}'.format(boardType))
    req = requests.get(baseurl + suburl)
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
                url = baseurl + tr.select('td._artclTdTitle')[0].a['href']
                items.append((title, num, url))

    record = 'cse_{}.txt'.format(boardType)
    with open(os.path.join(BASE_DIR, record), 'r+') as f_read:
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
                            try: 
                                bot.sendMessage(chat_id=chatId[0], text='[MODIFIED] No. {} [{}] {} \n{}'.format(num, boardType, title, url))
                            except:
                                pass

                    break
                else:
                    for chatId in chatIds:
                        try: 
                            bot.sendMessage(chat_id=chatId[0], text='No. {} [{}] {} \n{}'.format(num, boardType, title, url))
                        except:
                            pass
            with open(os.path.join(BASE_DIR, record), 'w+') as f_write:
                print('Write {} {}'.format(items[0][1], items[0][0]))
                f_write.write(items[0][1])
                f_write.write('\n')
                f_write.write(items[0][0])
                os.fsync(f_write)
                f_write.close()
    print('Done')
    return

conn.close()

cseBot('http://cse.pusan.ac.kr', '/cse/14651/subview.do', 'Notice')
cseBot('http://cse.pusan.ac.kr', '/cse/14655/subview.do', 'Term')
cseBot('http://cse.pusan.ac.kr', '/cse/14667/subview.do', 'Job')
cseBot('http://swedu.pusan.ac.kr', '/swedu/31630/subview.do', 'SW_Membership')
cseBot('http://cse.pusan.ac.kr', '/cse/14666/subview.do', 'Class')
cseBot('http://cse.pusan.ac.kr', '/cse/14668/subview.do', 'Event')
cseBot('http://cse.pusan.ac.kr', '/cse/14669/subview.do', 'Free')
cseBot('http://cse.pusan.ac.kr', '/cse/14670/subview.do', 'Wall')
cseBot('http://cse.pusan.ac.kr', '/cse/14657/subview.do', 'QNA')

