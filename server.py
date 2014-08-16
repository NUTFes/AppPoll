# !/usr/bin/env Python
# -*- coding:utf-8 -*-
import os
import json
import conf
import twitter
import csv

import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.log

from tornado.options import define, options

from collections import namedtuple
from itertools import islice, cycle
# from word2vector import Word2Vec

define( "port", default=8888, help="run on the given port", type=int)
PROXY_SERVER = 'proxy.nagaokaut.ac.jp:8080'
config = conf.app_settings["twitter"]
tweet_data = {}
candidates = {}
connections = []

class CosplayCandidate(object):
    def __init__(self, name="John", hashtag="#entry01", init_cnt=0):
        self.name = name
        self.hashtag = hashtag
        self.cnt = init_cnt
        self.init_cnt = init_cnt

    def reset_count(self):
        self.cnt = self.init_cnt


class APIonProxy(twitter.Api):
    def _GetOpener(self, url, username=None, password=None):
        opener = twitter.Api._GetOpener(self, url, username, password)
        urllib2 = twitter.urllib2
        p_h = urllib2.ProxyHandler({'http': PROXY_SERVER})
        opener.add_handler(p_h)
        return opener

api = APIonProxy(
        consumer_key=config["csm_key"],
        consumer_secret=config['csm_secret'],
        access_token_key=config["acs_key"],
        access_token_secret=config['acs_secret']
        )

class MainHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("index.html")


class TweetWebSocket(tornado.websocket.WebSocketHandler):
    def open(self):
        self.add_connection()

    def add_connection(self):
        if not (self in connections):
            connections.append(self)

    def on_close(self):
        if self in connections:
            connections.remove(self)

class MainHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("index.html")

class Application(tornado.web.Application):
    def __init__(self):
        settings = dict(
            debug=True,
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static")
        )
        handlers = [
            (r"/", MainHandler),
            (r"/data", TweetWebSocket),
            ]
        tornado.web.Application.__init__(self, handlers, **settings)

def tweet_callback():
    tweets = api.GetSearch(config['anchored_hashtag'])
    print "Received Tweets:({0})".format(len(tweets))
    c_hashtags = [ candidates[c].hashtag for c in candidates]
    for tweet in tweets:
        print tweet
        tid = tweet.id
        print [ tag.text for tag in tweet.hashtags]
        hashtags = set([ tag.text for tag in tweet.hashtags if tag.text in candidates])
        n_fav = tweet.favorite_count
        n_rt = tweet.retweet_count
        global tweet_data
        tweet_data[tid] = {"tags": hashtags, "fav":n_fav, "rt":n_rt}
    countup_vote()
    # write_message()
    update_data()
    tornado.ioloop.IOLoop.instance().call_later(5, tweet_callback)

def countup_vote():
    #データの初期化
    for hashtag in candidates:
        candidates[hashtag].reset_count()

    ratio = 1.0
    print tweet_data
    for tw in tweet_data:
        d = tweet_data[tw]
        for hashtag in d['tags']:
            score = ratio * d['fav'] + (1.0 - ratio) * d['rt']
            candidates[hashtag].cnt += score

    for c in candidates:
        print "Candiadte(hashtag:{0}, cnt:{1})".format(
                candidates[c].hashtag,
                candidates[c].cnt
                )

def update_data():
    print "Send data to all connections"
    data = []
    for hashtag in candidates:
        c = candidates[hashtag]
        d = {}
        d['count'] = c.cnt
        d['name'] = c.name
        data.append(d)

    for con in connections:
        con.write_message(json.dumps(data, ensure_ascii=False))
    return

def init():
    with open(conf.app_settings['entry_file']) as fin:
        reader = csv.DictReader(fin, delimiter = '\t')
        for entry in reader:
            candidates[entry['hash_tag'].strip('#')] = CosplayCandidate(
                    entry['resist_name'],
                    entry['hash_tag'],
                    int(entry['points'])
            )
            print entry

    print conf.app_settings

def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(8888)
    tornado.ioloop.IOLoop.instance().call_later(3, tweet_callback)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    init()
    main()

