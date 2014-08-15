# !/usr/bin/env Python
# -*- coding:utf-8 -*-

import conf
import twitter

PROXY_SERVER = 'proxy.nagaokaut.ac.jp:8080'

class APIonProxy(twitter.Api):
    def _GetOpener(self, url, username=None, password=None):
        opener = twitter.Api._GetOpener(self, url, username, password)

        urllib2 = twitter.urllib2
        p_h = urllib2.ProxyHandler({'http': PROXY_SERVER})
        opener.add_handler(p_h)
        return opener

def main():
    config = conf.app_settings['twitter']

    api = APIonProxy(
            consumer_key=config["csm_key"],
            consumer_secret=config['csm_secret'],
            access_token_key=config["acs_key"],
            access_token_secret=config['acs_secret']
            )

    tweets = api.GetSearch("#NUTFes2014")
    print len(tweets)
    for tweet in tweets:
        print tweet

if __name__ == '__main__':
    main()

