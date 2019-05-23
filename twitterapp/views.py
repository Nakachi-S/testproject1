# from django.shortcuts import render
# from django.http import HttpResponse

# # Create your views here.
# def index(request):
#     return HttpResponse("Hello World!")

from django.shortcuts import render
from .forms import TestForm

# 以下追加
import json
from requests_oauthlib import OAuth1Session
from time import sleep
import emoji
import sys
import io
import json
import csv
from janome.tokenizer import Tokenizer
import matplotlib.pyplot as plt
# from wordcloud1 import WordCloud
from bs4 import BeautifulSoup
import wordcloud
from collections import Counter, defaultdict
import os

#####################################################################
# 多分これが最初にひょうじするための処理。
#####################################################################


def index(request):
    # static内の画像を削除
    if (os.path.exists('./static/images/wordcloud_result.png') == True):
        os.remove('./static/images/wordcloud_result.png')

    my_dict = {
        'form': TestForm(),
        'insert_forms': 'ユーザー名を入力',
        'insert_result': '/static/images/first_img.png'
    }
    if (request.method == 'POST'):
        # my_dict['insert_forms'] = '文字列:' + request.POST['text'] + '<br>整数型:' + request.POST['num']
        my_dict['insert_forms'] = 'ユーザー名:' + request.POST['text']
        my_dict['form'] = TestForm(request.POST)
        print(request.POST['text'])
        gen_wordcloud(request.POST['text'])
        my_dict['insert_result'] = '/static/images/wordcloud_result.png'
    return render(request, './index.html', my_dict)


# 不本意だがimportでつまづいたので
# 直接、このファイルに処理を書く
#####################################################################
#  twitterのapiを使う処理
#####################################################################

# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
# sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')

# 絵文字を除去する


def remove_emoji(src_str):
    return ''.join(c for c in src_str if c not in emoji.UNICODE_EMOJI)


# 名詞だけ抽出、単語をカウント
def counter(texts):
    t = Tokenizer()
    words_count = defaultdict(int)
    words = []
    for text in texts:
        tokens = t.tokenize(text)
        for token in tokens:
            # 品詞から名詞だけ抽出
            pos = token.part_of_speech.split(',')[0]
            if pos in ['名詞']:
                # 必要ない単語を省く(実際の結果を見てから不必要そうな単語を記載しました)
                if token.base_form not in ["こと", "よう", "そう", "これ", "それ"]:
                    words_count[token.base_form] += 1
                    words.append(token.base_form)
    return words_count, words


def gen_wordcloud(username):
    # APIキー設定(別ファイルのconfig.pyで定義しています)
    CK = 'UjCD4Ttbap6ltvF1YSRYD0X7N'
    CS = 'K5r5sAUQubUjdZORQ7L6j7PJltHmkQ9PaSela8y82TSGsxGcsC'
    AT = '1107188613458984960-1ZfMVbGx0kxFaRLeqZYWZcMXxhOmN3'
    ATS = 'H8kSOXpORXPa75jDNZUYjv06yzkVDyXDmWROmARKnwtjq'

    # 認証処理
    twitter = OAuth1Session(CK, CS, AT, ATS)

    # タイムライン取得エンドポイント
    url = "https://api.twitter.com/1.1/statuses/user_timeline.json"

    # パラメータの定義
    params = {'screen_name': username,
              'exclude_replies': True,
              'include_rts': False,
              'count': 200}

    # 出力先ファイル
    # f_out = open('./output/tweet_data', 'w')

    #　保存用配列
    tweet = []
    for j in range(10):
        res = twitter.get(url, params=params)
        if res.status_code == 200:
            # API残り回数
            limit = res.headers['x-rate-limit-remaining']
            print("API remain: " + limit)
            if limit == 1:
                sleep(60 * 15)

            n = 0
            timeline = json.loads(res.text)
            # 各ツイートの本文を表示
            for i in range(len(timeline)):
                if i != len(timeline) - 1:
                    # 絵文字があると、wordcloudが使用できないため、削除する
                    tmp = remove_emoji(timeline[i]['text'])

                    # f_out.write(tmp + '\n')
                    tweet.append(tmp)
                else:
                    # 絵文字があると、wordcloudが使用できないため、削除する
                    # f_out.write(remove_emoji(timeline[i]['text']) + '\n')
                    tmp = remove_emoji(timeline[i]['text'])
                    tweet.append(tmp)
                    # 一番最後のツイートIDをパラメータmax_idに追加
                    params['max_id'] = timeline[i]['id'] - 1

    # f_out.close()

    ##########################################

    texts = []
    for row in tweet:
        if (len(row) > 0):
            text = row.split('http')[0]
            texts.append(text)
    # print(texts)

    words_count, words = counter(texts)
    text = ' '.join(words)

    # fontは自分の端末にあるものを使用する
    fpath = "~/Library/Fonts/RictyDiscord-Bold.ttf"
    wordcloud1 = wordcloud.WordCloud(background_color="white",
                                     font_path=fpath, width=900, height=500).generate(text)

    wordcloud1.to_file("./static/images/wordcloud_result.png")
