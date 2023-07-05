# A very simple Flask Hello World app for you to get started with...

from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

import os
import requests
import pandas as pd
import io

def get_data_frame():
    response = requests.get('https://chouseisan.com/schedule/List/createCsv?h=0802c13d816b468fa531dc5c6c831cc4&charset=sjis&row=choice')

    # f = open('myfile.csv', 'w')
    # f.write(response.text)
    # f.close()

    return pd.read_csv(io.StringIO(response.text), encoding = "shift-jis", header=1, index_col=0)

def extract_by_position_and_data(position, data, df):
    df = df.filter(like=data, axis=0)
    df = df.filter(like=position, axis=1)
    df = df.loc[:, df.isin(['◯']).any()]
    list = [s.replace(position, '') for s in df.columns.values]
    return ','.join(list)

def extract_triangle(data, df):
    df = df.filter(like=data, axis=0)
    df = df.loc[:, df.isin(['△']).any()]
    list = [s for s in df.columns.values]
    return ','.join(list)

def extract_nan(data, df):
    df = df.filter(like=data, axis=0)
    df = df.loc[:, df.isnull().any()]
    list = [s for s in df.columns.values]
    return ','.join(list)

def output_member(data):
    member_list = '参加者\n\n'
    df = get_data_frame()
    for position in ['AT', 'MF', 'LG', 'GL', 'FO', 'MG']:
        member_list = member_list + position + '\n'
        member_list = member_list + extract_by_position_and_data(position, data, df) + '\n' + '\n'

    member_list = member_list + '△' + '\n'
    member_list = member_list + extract_triangle(data, df) + '\n' + '\n'

    member_list = member_list + '未記入' + '\n'
    member_list = member_list + extract_nan(data, df) + '\n' + '\n'

    return member_list

LINE_CHANNEL_ACCESS_TOKEN = "DzPdVXZn/ijwJv4n01qKRaxQGovO5reAxK+2SpwQlG2/Ody2+wF8jm6jURmHdbImYRfRDBuZDWaInholwEX1xLwcVOQiROa8qaD3OrmheZCEuSrSg5gmZnXEu6oBp40EDFc6jzNKr5jy3ft8/eeKwgdB04t89/1O/w1cDnyilFU="
LINE_CHANNEL_SECRET = "01e29ccbbfa49956c8d8af674d6dc5fb"

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "hello world!"

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    reply_message = output_member(data=event.message.text)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_message))

if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
