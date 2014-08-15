# !/usr/bin/env Python
# -*- coding:utf-8 -*-
import os
import json
import conf 

import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket

from tornado.options import define, options

from collections import namedtuple
from itertools import islice, cycle
# from word2vector import Word2Vec

define( "port", default=8888, help="run on the given port", type=int)
Point = namedtuple('Point', ['x', 'y'])
connections = []
# w2v = Word2Vec()

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
            ]
        tornado.web.Application.__init__(self, handlers, **settings)

class ChatWebSocket(tornado.websocket.WebSocketHandler):

    def open(self):
        self.add_connection()
        self.wait_message()

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

def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()

