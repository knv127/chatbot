from flask import Flask, request, make_response, jsonify
import os
import sys
import urllib.request
import json
import re


client_id = "LEBsNjWeWyzm917Vl9Zw"
client_secret = "17ftF2T1ED"

idx = 0
display = 3
start = 1
end = 10

app = Flask(__name__)
@app.route('/', methods=['GET'])
def server():
    return 'Hello, World!'


@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    return make_response(food_r())

def food_r():
    req = request.get_json(silent=True, force=True)
    query_result = req.get('queryResult')
    food = query_result.get('parameters').get('category')

    query = urllib.parse.quote(str(food) + "밀키트")
    url = "https://openapi.naver.com/v1/search/shop?query=" + query \
          + "&display=" + str(display)
    r = urllib.request.Request(url)
    r.add_header("X-Naver-Client-Id", client_id)
    r.add_header("X-Naver-Client-Secret", client_secret)
    response = urllib.request.urlopen(r)
    rescode = response.getcode()

    if (rescode == 200):
        response_body = response.read()
        response_dict = json.loads(response_body.decode('utf-8'))
        items = response_dict['items']
        for item_index in range(0, len(items)):
            remove_tag = re.compile('<.*?>')
            title = re.sub(remove_tag, '', items[item_index]['title'])
            link = items[item_index]['link']
            image = items[item_index]['image']
            low_price = items[item_index]['lprice']

    else:
        print("Error Code:" + rescode)

    if query_result.get('action') == 'recommend.food':
        fulfillmentmessages = [
                {
                    "payload": {
                        "line": {
                            "altText": "this is a buttons template",
                            "template": {
                                "thumbnailImageUrl": image,
                                "title": title,
                                "type": "buttons",
                                "actions": [
                                    {
                                        "uri": link,
                                        "type": "uri",
                                        "label": "상세페이지 이동"
                                    },
                                    {
                                        "label": "위시리스트 저장",
                                        "type": "postback",
                                        "data": "action=add&itemid=123"
                                    },
                                    {
                                        "text": "시작",
                                        "type": "message",
                                        "label": "다시 시작"
                                    }
                                ],
                                "text": low_price+'원'
                            },
                            "type": "template"
                        }
                    },
                    "platform": "LINE"
                },
                {
                    "text": {
                        "text": [
                            ""
                        ]
                    }
                }
            ]

    return {
        "fulfillmentMessages": fulfillmentmessages
    }


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
