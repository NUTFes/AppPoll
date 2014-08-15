# !/usr/bin/env Python
# -*- coding:utf-8 -*-
import os
import json
import conf
import twitter

import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket

from tornado.options import define, options

from collections import namedtuple
from itertools import islice, cycle
# from word2vector import Word2Vec

define( "port", default=8888, help="run on the given port", type=int)
PROXY_SERVER = 'proxy.nagaokaut.ac.jp:8080'
config = conf.app_settings['twitter']
api = APIonProxy(
        consumer_key=config["csm_key"],
        consumer_secret=config['csm_secret'],
        access_token_key=config["acs_key"],
        access_token_secret=config['acs_secret']
        )
connections = []

class APIonProxy(twitter.Api):
    def _GetOpener(self, url, username=None, password=None):
        opener = twitter.Api._GetOpener(self, url, username, password)

        urllib2 = twitter.urllib2
        p_h = urllib2.ProxyHandler({'http': PROXY_SERVER})
        opener.add_handler(p_h)
        return opener

 
class MainHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("index.html")

class TweetWebSocket(tornado.websocket.WebSocketHandler):

    class CosplayCandidate(object):
        def __init__(self, name="JohnDo", hashtag="#entry01", init_cnt=0):
            self.name = name
            self.hashtag = hashtag
            self.cnt = init_cnt

    def open(self):
        self.add_connection()
        self.wait_message()
        self.setup()

    def setup(self):
        self.candidate = [ CosplayCandidate() for x in xrange(10)]

    def tweet_callback(self):
        tweets = api.GetSearch(config['anchored_hashtag'])
        for tweet in tweets:
            # TODO: idごとにツイートを管理し、逐次更新していく
            # update_tweets()
        # coutup_vote()
        # write_message()

        tornado.ioloop.IOLoop.call_later(10, self.tweet_callback)

    def add_connection(self):
        if not (self in connections):
            connections.append(self)

    @tornado.web.asynchronous
    def on_message(self, message):
        cols = message.split(',', 7)
        capacity[int(cols[0])] = 1
        cols[1]  = str(cnt)
        message = ','.join(cols)
        for con in connections:
            try:
                con.write_message(message)
            except:
                connections.remove(con)
        self.wait_message()

    def on_connection_close(self):
        self.del_connection()
        self.close()

    def del_connection(self):
        if self in connections:
            connections.remove(self)


class Application(tornado.web.Application):
    def __init__(self):
        settings = dict(
            debug=True,
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static")
        )
        handlers = [
            (r"/", MainHandler),
            ]
        tornado.web.Application.__init__(self, handlers, **settings)


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()

