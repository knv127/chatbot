from flask import Flask, request, make_response, jsonify
import os
import sys
import urllib.request
import json
import re
import requests
from pyairtable import Table

'''base_id = 'appreJgmpfprndwhr'
table_name = "table-2"
url = "https://api.airtable.com/v0/" + base_id + "/" + table_name
api_key = "keyRW3GozNgE4IAPI"
headers = {"Authorization": "Bearer" + api_key}'''


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

    if query_result.get('action') == 'start':
        fulfillmentMessages = [
          {
            "card": {
              "title": "안녕하세요. 밀키트 추천 봇 입니다.",
              "subtitle": "원하시는 기능을 선택해주세요.",
              "buttons": [
                {
                  "text": "밀키트 추천 받기",
                  "postback": "밀키트 추천 받기"
                },
                {
                  "text": "내 위시리스트 보기",
                  "postback": "내 위시리스트 보기"
                }
              ]
            },
            "platform": "LINE"
          }
        ]

    if query_result.get('action') == 'recommend.food':
        fulfillmentMessages = [
          {
            "card": {
              "title": title,
              "subtitle": low_price+'원',
              "imageUri": image,
              "buttons": [
                {
                  "text": "상세페이지 이동",
                  "postback": link
                },
                {
                  "text": "다시 시작",
                  "postback": "시작"
                },
                {
                  "text": "위시리스트 저장",
                  "postback": title + ' ' + link

                }
              ]
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

    if query_result.get('action') == 'wishlist_save':
        req = request.get_json(silent=True, force=True)
        result = save_to_db(req)
        return {
            'fulfillmentText': str(result)
        }

    if query_result.get('action') == 'wishlist_view':
        table = Table('keyRW3GozNgE4IAPI', 'appreJgmpfprndwhr', 'table-2')
        result = table.all()
        sr = '내 위시리스트: '+'\n'
        for i in range(len(result)):
            sr += str(result[i]['createdTime'][0:10] +' '+ result[i]['fields']['Name'] + ' '+ result[i]['fields']['link']+'\n'+'\n')
        #date = result[0]['createdTime'][0:10]
        #name = result[0]['fields']['Name']
        #link = result[0]['fields']['link']
        print(sr)
        return {
            'fulfillmentText': sr
        }

    return {
        "fulfillmentMessages": fulfillmentMessages,
        "source": "webhookdata"
    }

def save_to_db(req):
    try:
        query_result = req.get('queryResult')
        title = query_result.get('parameters').get('title')
        url = query_result.get('parameters').get('url')

        table = Table('keyRW3GozNgE4IAPI', 'appreJgmpfprndwhr', 'table-2')
        result = table.create({'Name': title, 'link': url})
        return '위시리스트에 저장되었습니다.'
    except Exception as e:
        error_str = str(e)
        return 'Something went wrong. Please try again later'


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
