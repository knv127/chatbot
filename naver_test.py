from flask import Flask, request, make_response, jsonify
import os
import sys
import urllib.request
import pandas as pd
import json
import re

client_id = "LEBsNjWeWyzm917Vl9Zw"
client_secret = "17ftF2T1ED"

idx = 0
display = 3
start = 1
end = 10

shop_df = pd.DataFrame(columns=("Title", "Link", "image", "Low price"))

def food_r():
    query = urllib.parse.quote("떡볶이 밀키트")
    for start_index in range(start, end, display):
        url = "https://openapi.naver.com/v1/search/shop?query=" + query \
              + "&display=" + str(display)

        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id", client_id)
        request.add_header("X-Naver-Client-Secret", client_secret)
        response = urllib.request.urlopen(request)
        rescode = response.getcode()
        if (rescode == 200):
            response_body = response.read()
            response_dict = json.loads(response_body.decode('utf-8'))
            items = response_dict['items']
            return {'fulfillmentText':str(items[0]['title'])}
        else:
            print("Error Code:" + rescode)

app = Flask(__name__)
@app.route('/', methods=['GET'])
def server():
    return "hello world"

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    return make_response(jsonify(food_r()))

if __name__ == '__main__':
    app.run(debug=True, host="localhost", port = 5000)
