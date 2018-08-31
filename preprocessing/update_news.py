#!/usr/bin/env python3

# coding: utf-8

import feedparser
import requests
import re
import hashlib
import pytz
from bs4 import BeautifulSoup
from tqdm import tqdm
from time import mktime
from datetime import datetime
from pymongo import MongoClient
from bson.codec_options import CodecOptions

def get_digest(string):
    return int(hashlib.sha256(string.encode("UTF-8")).hexdigest()[0:7], 16)


def crawl_channel(channel, tz):
    channel_id = channel['_id']
    link = channel['feed_link']
    feeds = feedparser.parse(channel['feed_link'])['entries']
    news_ = []
    for feed in feeds:
        try:
            news = {}
            news['_id'] = get_digest(feed['title'] + str(channel_id))
            news['channel_id'] = channel_id
            news['title'] = feed['title']
            news['summary'] = feed['summary']
            news['author'] = feed['author']
            news['pubdate'] = tz.localize(datetime.fromtimestamp(mktime(feed['published_parsed'])))
            news['link'] = feed['link']
            news_.append(news)
        except KeyError:
            continue
    return news_

def unique(seq, idfun=None):
    if idfun is None:
        def idfun(x): return x
    seen = {}
    result = []
    for item in seq:
        marker = idfun(item)
        if marker not in seen:
            seen[marker] = 1
            result.append(item)
    return result


def crawl_all_news(tz, db):
    channels_col = db['Channels']
    news_col = db['News'].with_options(
        codec_options=CodecOptions(tz_aware=True,tzinfo=tz)
    )

    number = 0
    all_news = []
    for channel in channels_col.find():
        print("Crawling channel {} {}".format(channel['_id'], channel['name']))
        news = crawl_channel(channel, tz)
        print("Get {} news".format(len(news)))
        all_news = all_news + news
    print("Get {} news in total".format(len(all_news)))
    
    insert_news = []
    for one_news in all_news:
        old_news = news_col.find_one({'_id': one_news['_id']})
        if old_news == None:
            insert_news.append(one_news)
            number = number + 1
        else:
            insert_news.append(old_news)
    insert_news.sort(key=lambda item:item['pubdate'], reverse=True)
    insert_news = unique(insert_news, lambda item:item['_id'])
    news_col.delete_many({})
    news_col.insert_many(insert_news)
    print("Inserted {} new news in total".format(number))


def update_news_picture(db, news):
    try:
        news_content = BeautifulSoup(requests.get(news['link']).text)
        main_img = news_content.find('div', {'id': 'Main-Article-QQ'}).find('p', {'align': 'center'}).find('img')
        img_url = main_img['src']
        if img_url[0:2] == '//':
            img_url = 'http:' + img_url
    except:
        img_url = ""
    
    db.update_one({
        '_id': news['_id']
    }, {'$set': {
        'picture': img_url
    }})


def update_news_pictures(db):
    no_pic_news = []
    for news in db.find():
        if 'picture' not in news.keys():
            no_pic_news.append(news)
    print('Currently news with no pictures: {}'.format(len(no_pic_news)))
    for news in tqdm(no_pic_news):
        update_news_picture(db, news)

if __name__ == '__main__':
	tz = pytz.timezone('Asia/Shanghai')
	client = MongoClient('localhost', 27017)
	db = client['trivial_news']
	
	crawl_all_news(tz, db)
	update_news_pictures(db['News'])

