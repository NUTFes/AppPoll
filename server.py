# !/usr/bin/env Python
# -*- coding:utf-8 -*-
import sys
# sys.path.append('~/.local/bin')
sys.path.append('~/.local/lib/python2.7/site-packages') 

import os
import json

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

path = {
    'd_sample_quiz': 'system/question',
    'd_sample_story':'system/text',
    'sample_txt' : 'cgi-bin/merosu.txt',
    'sample_quiz' : 'sample_quiz.txt',
    'input'       : 'system/story/sample.txt',
    'output'      : 'system/question/sample.txt',
    'quiz_maker'  : 'system/py/main.py',
}

def roundrobin(*iterables):
    "roundrobin('ABC', 'D', 'EF') --> A D E B F C"
    # Recipe credited to George Sakkis
    pending = len(iterables)
    nexts = cycle(iter(it).next for it in iterables)
    while pending:
        try:
            for next in nexts:
                yield next()
        except StopIteration:
            pending -= 1
            nexts = cycle(islice(nexts, pending))

class MainHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("index.html")


class Word2VecHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        words = self.get_argument('body', 'No data reveived')
        self.render("demo_word2vec.html")
        # # data = w2v.vectorize(words)
        # out = dict()
        # for word, x, y in data:
        #     p = {'x' : x, 'y' : y}
        #     out[word] = p
        # else:
        #     self.write(json.dumps(out))

class ReadingQuizHandler(tornado.web.RequestHandler):
    def initialize(self):
        root, dirnames, filenames = os.walk(path['d_sample_story']).next()
        self.cache_files = filenames

    @tornado.web.asynchronous
    def post(self):
        text = self.get_argument('story_box')
        fname = self.get_argument('file')

        if fname in self.cache_files:
            f_quiz =  os.path.join(path['d_sample_story'], fname)
            self.quiz_path = os.path.join(path['d_sample_quiz'], fname)
            with open(f_quiz) as fin:
                self.text = fin.read().strip().replace('\n', '<br>')
        else:
            self.text = self.get_argument('story_box').strip().replace('\n','<br>')
            self.quiz_path = path['sample_quiz']
            if not self.text:
                with open(path['sample_txt']) as fin:
                    self.text = fin.read().strip().replace('\n', '<br>')
            with open(path['input'], 'w') as fout:
                fout.write(self.text.encode('utf-8'))
            # quiz_maker.run()

        qz = self.load_quizzes(self.quiz_path)
        self.render("demo_reading.html"
                , story=self.text, n_quizzes=5, quizzes=self.quizzes)

    def load_quizzes(self, path):
        self.quizzes = list()
        # qa[0] = ["メロスのは激怒しましたか？", "はい", "いいえ","", "",
        template = 'qa[{num}] = ["{quiz}", "{0}", "{1}","{2}", "{3}", {ans}]'
        num2kind = [[] for x in xrange(4)]
        with open(path) as fin:
            for idx, line in enumerate(fin):
                cols = line.strip().split('\t')
                if cols[0] == '1':
                    ans = '1' if 'y' == cols[2] else '2'
                    quiz = template.format(
                            'はい', 'いいえ', '', '',
                            num=idx, quiz=cols[1], ans=ans)
                    idx = 0
                elif cols[0] == '2':
                    quiz = cols[1]
                    slct = cols[3:]
                    ans = slct.index(cols[2]) + 1
                    quiz = template.format(
                            slct[0], slct[1], slct[2], slct[3],
                            num=idx, quiz=quiz, ans=ans)
                    idx = 1
                elif cols[0] == '3':
                    quiz = cols[1]
                    slct = cols[3:7]
                    ans = slct.index(cols[2]) + 1
                    quiz = template.format(
                            slct[0], slct[1], slct[2], slct[3],
                            num=idx, quiz=quiz, ans=ans)
                    idx = 2
                else:
                    quiz = ""
                if idx > -1:
                    num2kind[idx].append(quiz)
                self.quizzes.append(quiz)

        return [ q for q in roundrobin(num2kind)]


class Application(tornado.web.Application):
    def __init__(self):
        settings = dict(
            debug=True,
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static")
        )
        handlers = [
            (r"/", MainHandler),
            (r"/quiz",ReadingQuizHandler),
            (r"/w2v", Word2VecHandler),
            ]
        tornado.web.Application.__init__(self, handlers, **settings)


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()

