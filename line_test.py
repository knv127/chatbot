from flask import Flask, request, abort, make_response, jsonify

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, SourceUser, ButtonsTemplate, URITemplateAction, PostbackTemplateAction, MessageTemplateAction, TemplateSendMessage
)

import os
import sys
import urllib.request
import json
import re

client_id = "LEBsNjWeWyzm917Vl9Zw"
client_secret = "17ftF2T1ED"

app = Flask(__name__)

line_bot_api = LineBotApi('4BJMu6M4eDqga+PzYOvYuYDwJNdXJEac/YIfdaMY7KndoYEHoLvhHqY8GVCwDW7cuwx697LFU5N8bBw+/sM9AmY3AlobZWu+rprmtlNrYNN9XQxMIfLwvUpoldrCr40HLZ/ct3QRlx7G87tacK2EcwdB04t89/1O/w1cDnyilFU=')  #Channel access token
handler = WebhookHandler('4943de348d0107fcc159756f0ca399bf')  #Channel secret

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
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

def uri():
    req = request.get_json(silent=True, force=True)
    query_result = req.get('queryResult')
    food = query_result.get('parameters').get('category')

    query = urllib.parse.quote(str(food) + "밀키트")
    url = "https://openapi.naver.com/v1/search/shop?query=" + query
    r = urllib.request.Request(url)
    r.add_header("X-Naver-Client-Id", client_id)
    r.add_header("X-Naver-Client-Secret", client_secret)
    response = urllib.request.urlopen(r)
    rescode = response.getcode()

    if (rescode == 200):
        response_body = response.read()
        response_dict = json.loads(response_body.decode('utf-8'))
        items = response_dict['items']
        return str(items[0]['link'])

    else:
        print("Error Code:" + rescode)


user = {}
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text
    if text == '시작':
        buttons_template = ButtonsTemplate(
            type = 'buttons', text="안녕하세요. 밀키트 추천 봇 입니다. 원하시는 기능을 선택해주세요. 이 메시지를 다시 보고 싶으시다면 '시작'을 입력해주세요",
            actions=[
                URITemplateAction(
                    label='상세페이지 이동', uri=uri()),
                PostbackTemplateAction(label='밀키트 추천받기', data='ping', text='추천 받고 싶은 밀키트를 입력해주세요.'),
                PostbackTemplateAction(
                    label='내 위시리스트 보기', data='wish list',),
                MessageTemplateAction(label='Translate Rice', text='米')
            ])
        template_message = TemplateSendMessage(
            alt_text='Buttons alt text', template=buttons_template)
        line_bot_api.reply_message(event.reply_token, template_message)
    else:
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=event.message.text))

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)