from flask import Flask, request, abort, render_template, redirect, url_for
import os
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
import sqlite3
import datetime as dt
import schedule
import time
import secrets as se

app = Flask(__name__)
path = "status.db"

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
    print("Triger On")
    all_data()
    return render_template('index.html')

@app.errorhandler(404)
def error_handler(error):
    return render_template('error.html')

if __name__ == '__main__':
    app.run(debug=True)
    # schedule.every(1).minutes.do(hello)

    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)