from flask import Flask, request, abort, render_template, redirect, abort
import random
import sqlite3
import datetime as dt
import secrets as se
import re
import requests
 
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, MessageTemplateAction,
    TemplateSendMessage, ConfirmTemplate, PostbackTemplateAction,
    StickerMessage, StickerSendMessage, ButtonsTemplate,
    PostbackAction, MessageAction, URIAction
)
import os
import schedule
import time


app = Flask(__name__)
path = "status.db"

line_bot_api = LineBotApi("PydKcB4ohoGs3rq3aCj53UYhHUA7Qam1UwnMnkRQdDXsqByYOokMIIXXkYAKJTji5pf7T2LFj+8299innh1yVgNo7uGwi8WnrwaMxUMVeuWoxhBjDvY9uNbeGfhoCwNa6bo8+L1fVSnT73e2nMA3gwdB04t89/1O/w1cDnyilFU=")
handler = WebhookHandler("ec4b4f750316feb4d1984a52cb8d3f37")


@app.route('/')
def top_page():
    return render_template('index.html')

def push_db(date:str, content:str, created_datetime:str, user_id:str, status:int):
    conn = sqlite3.connect(path)

    c = conn.cursor()
    # Insert a row of data
    c.execute(f"INSERT INTO stocks VALUES ('{date}','{content}', '{se.token_hex()}', '{created_datetime}', '{user_id}', {status})")
 
    conn.commit()

    conn.close()

def all_data():
    conn = sqlite3.connect(path)
    c = conn.cursor()

    where_list = []

    for i in c.execute(f'SELECT * FROM stocks'):
        where_list.append(i)

    conn.close()

    print(where_list)

def delete_db(token:str):
    conn = sqlite3.connect(path)
    c = conn.cursor()

    c.execute(f'DELETE from stocks WHERE token = "{token}"')

    conn.commit()

    conn.close()

def user_all_data(user_id:str):
    conn = sqlite3.connect(path)
    c = conn.cursor()

    where_list = []

    for i in c.execute(f'SELECT * FROM stocks WHERE user_id = "{user_id}"'):
        where_list.append(i)

    conn.close()

    return where_list

def message_data(token:str):
    conn = sqlite3.connect(path)
    c = conn.cursor()

    where_list = []

    for i in c.execute(f'SELECT message FROM stocks WHERE token = "{token}"'):
        where_list.append(i)

    conn.close()

    return where_list


def send_message(user_id:str, message:str):
    line_bot_api.multicast([user_id], TextSendMessage(text=message))


def pattern_math(date):
    date_type = re.compile(r"""(
        (^\d{4})        # First 4 digits number
        (\D)            # Something other than numbers
        (\d{1,2})       # 1 or 2 digits number
        (\D)            # Something other than numbers
        (\d{1,2})       # 1 or 2 digits number
        )""",re.VERBOSE)

    try:
        hit_date = date_type.search(date)
        bool_value = bool(hit_date)
        if bool_value is True:
            split = hit_date.groups()

            # Tuple unpacking
            year, month, day = int(split[1]),int(split[3]),int(split[5])

        nows = now().split("-")

        if dt.datetime(int(nows[0]), int(nows[1]), int(nows[2])) > dt.datetime(year, month, day):
            return False

        if year>3000 or month >12 or day > 31:
            return False
        else:
            if month <= 9:
                month = '0' + str(month)
            if day <= 9:
                day = '0' + str(day)
            return [str(year), str(month), str(day)]

    except:
        return False

def now():
    return dt.datetime.now().strftime("%Y-%m-%d")

# return :list
def where_date_db(date:str):
    conn = sqlite3.connect(path)
    c = conn.cursor()

    where_list = []

    for i in c.execute(f'SELECT date, token, created_datetime, user_id, message FROM stocks where date = "{date}"'):
        where_list.append(i)

    conn.close()

    return where_list

def where_date_db2(date:str):
    conn = sqlite3.connect(path)
    c = conn.cursor()

    where_list = []

    for i in c.execute(f'SELECT date, token, created_datetime, user_id, message FROM stocks where date < "{date}"'):
        where_list.append(i)

    conn.close()

    return where_list

@app.route('/data/')
def data():
    date             = request.args.get('d', None)
    message          = request.args.get('m', None)
    created_datetime = request.args.get('c', None)
    user_id          = request.args.get('u', None)

    if date is not None and message is not None and created_datetime is not None and user_id is not None:
        push_db(date, message, created_datetime, user_id, 2)
    
    return render_template("index.html")

@app.route('/triger')
def triger():
    send_url = "https://time-capsule-messages.herokuapp.com/future/"

    date_dbs = where_date_db(now())

    if date_dbs != []:
        for row in date_dbs:
            token = row[1]
            created_date = row[2].split('-')
            user_id = row[3]
            message = row[4]
            send_message(user_id, f"{created_date[0]}年{created_date[1]}月{created_date[2]}日のあなたからのメッセージです。 {send_url + token}")
    
    date_dbs2 = where_date_db2(dt.datetime.now() - dt.timedelta(days=10))


    if date_dbs2 != []:
        for row in date_dbs2:
            delete_db(row[1])

    return render_template('index.html')

@app.route('/future/<token>')
def future(token):

    m = message_data(token)[0]

    if m == []:
        abort(404)
    else:
        message = m[0]

    return render_template('index.html',
                            message=message) 

@app.errorhandler(404)
def error_handler(error):
    return render_template('error.html')

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)