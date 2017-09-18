#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    author:     small 
    date:       2017/8/22
    purpose:    
"""


import os
import sys
import scrapy
import logging
import traceback
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from scrapy_paper.items import ScrapyPaperItem
from scrapy_paper.db.db_base import DataBase

TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
CURRENT_PATH = os.path.split(os.path.realpath(__file__))[0]


if sys.version >= '3':
    PYTHON3 = True
    import urllib
    from urllib.request import urlopen
    from urllib import parse
    from urllib.parse import urlencode
else:
    PYTHON3 = False
    import urllib
    from urllib import urlopen, urlencode

log = logging.getLogger(os.path.split(os.path.realpath(__file__))[1])


class BaseSpider(object):

    def __init__(self):
        super(BaseSpider, self).__init__()
        self.page = 2
        self.db = DataBase()

    def fetch_list(self, list_, index_):
        if index_ < len(list_):
            return list_[index_]
        return None

    def parse_paper(self, response):
        log.debug("{} start parse url: {}".format(response.meta["item"]["paper_spider"], response.url))
        item = response.meta["item"]
        item["response"] = response
        return item

    def fetch_xpath(self, etree_, xpath_, default_="", node_=0):
        if etree_ and xpath_:
            node = etree_.xpath(xpath_)
            if node:
                return node[node_].extract()
        return default_

    def fix_url(self, response_, url_):
        if url_ and not url_.startswith("http"):
            url = response_.urljoin(url_)
        else:
            url = url_
        return url

    def make_header(self, page_url_):
        # python2 use
        if not PYTHON3:
            type, rest = urllib.splittype(page_url_)
            host, path = urllib.splithost(rest)
        # python3 use
        else:
            host = parse.urlsplit(parse.unquote(page_url_)).netloc

        headers = {
            "Host": host,
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Referer": page_url_,
            "Connection": "keep-alive"
        }
        return headers

    def prettify_html(self, html_):
        return BeautifulSoup(html_, 'lxml').prettify()
