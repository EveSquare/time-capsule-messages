from flask import Flask, request, abort, render_template, redirect, abort
import random
import sqlite3
import datetime as dt
from datetime import timedelta, timezone
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

path = "status.db"
JST = timezone(timedelta(hours=+9), 'JST')

def push_db(date:str, content:str, created_datetime:str, user_id:str, status:int):
    conn = sqlite3.connect(path)

    c = conn.cursor()
    # Insert a row of data
    c.execute(f"INSERT INTO stocks VALUES ('{date}','{content}', '', '{created_datetime}', '{user_id}', {status})")
 
    conn.commit()

    conn.close()

def where_date_db2(date:str):
    conn = sqlite3.connect(path)
    c = conn.cursor()

    where_list = []

    for i in c.execute(f'SELECT date, token, created_datetime, user_id, message FROM stocks where date < "{date}"'):
        where_list.append(i)

    conn.close()

    return where_list


# push_db("2021-01-03", "aiueo", "2021-01-04", "adadadadawda", 0)

date_dbs2 = where_date_db2(dt.datetime.now(JST) - dt.timedelta(days=10))


if date_dbs2 != []:
    for row in date_dbs2:
        print(row)

def all_data():
    conn = sqlite3.connect(path)
    c = conn.cursor()

    where_list = []

    for i in c.execute(f'SELECT * FROM stocks'):
        where_list.append(i)

    conn.close()

    print(where_list)

all_data()
#
#print((dt.datetime.now() - dt.timedelta(days=10)).strftime("%Y-%m-%d"))
# date_dbs2 = where_date_db2(dt.datetime.now() - dt.timedelta(days=10))