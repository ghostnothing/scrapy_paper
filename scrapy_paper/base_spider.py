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

TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
CURRENT_PATH = os.path.split(os.path.realpath(__file__))[0]
PAPER_TITLE = "paper_title"
PAPER_URL = "paper_url"
AUTHOR_NAME = "author_name"
AUTHOR_LINK = "author_link"
AUTHOR_IDENTITY = "author_identity"
PAPER_TIME = "paper_time"
PAPER_ABSTRACT = "paper_abstract"
PAPER_TAGS = "paper_tags"
PAPER_LOOK_NUMBER = "paper_look_number"
PAPER_LOOK_COMMENTS = "paper_look_comments"
PAPER_SPIDER = "paper_spider"
PAPER_FILE = "paper_file"
NAME_LIST = [PAPER_TITLE, PAPER_URL, AUTHOR_NAME, AUTHOR_LINK, AUTHOR_IDENTITY, PAPER_TIME, PAPER_ABSTRACT,
             PAPER_TAGS, PAPER_LOOK_NUMBER, PAPER_LOOK_COMMENTS, PAPER_SPIDER]

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
        """
        Article content processing
        :param response:
        :return:
        """
        log.debug("{} start parse url: {}".format(response.meta["item"]["paper_spider"], response.url))
        item = response.meta["item"]
        item["response"] = response
        return item

    def fetch_xpath(self, etree_, xpath_, default_="", node_=0):
        """
        Get node data via xpath
        :param etree_:
        :param xpath_:
        :param default_:
        :param node_:
        :return:
        """
        if etree_ and xpath_:
            node = etree_.xpath(xpath_)
            if node and len(node) > node_:
                return node[node_].extract()
        return default_

    def fix_url(self, response_, url_):
        """
        Fix the URI as a URL
        :param response_:
        :param url_:
        :return:
        """
        if url_ and not url_.startswith("http"):
            url = response_.urljoin(url_)
        else:
            url = url_
        return url

    def make_header(self, page_url_):
        """
        Generates an HTTP header
        :param page_url_:
        :return:
        """
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

    def check_param(self, response_, news_list_):
        """
        Check the parameters
        :param response_:
        :param news_list_:
        :return:
        """
        log.debug(u"start parse url: {}".format(response_.url))
        if response_.status != 200:
            log.warning("response code is {}".format(response_.status))
            return False
        news_list = response_.xpath(news_list_)
        if not news_list:
            log.warning("invalid news_list")
            return False
        return True

    def parse_tags(self, response, news_info_, tags_):
        paper_tags = []
        if not news_info_ or not tags_:
            return paper_tags
        for tag in news_info_.xpath(tags_):
            tag_name = self.fetch_xpath(tag, "text()")
            tag_url = self.fetch_xpath(tag, "@href")
            tag_url = self.fix_url(response, tag_url)
            tag_info = dict(tag_name=tag_name,
                            tag_url=tag_url)
            paper_tags.append(tag_info)
        return paper_tags

    def set_abstract_value(self, abstract_dict_, response, news_info, name_, xpath):
        if hasattr(self, name_):
            special_func = getattr(self, name_)
            abstract_dict_[name_] = special_func(response, news_info, xpath)
            return abstract_dict_

        if name_ == PAPER_SPIDER:
            abstract_dict_[name_] = xpath
        elif name_ == AUTHOR_IDENTITY:
            abstract_dict_[name_] = True if self.fetch_xpath(news_info, xpath) else False
        elif name_ == PAPER_TAGS:
            abstract_dict_[name_] = self.parse_tags(response, news_info, xpath)
        elif name_ == PAPER_LOOK_NUMBER or name_ == PAPER_LOOK_COMMENTS:
            abstract_dict_[name_] = self.fetch_xpath(news_info, xpath, default_="0")
            abstract_dict_[name_] = "".join(abstract_dict_[name_].split(","))
        else:
            abstract_dict_[name_] = self.fetch_xpath(news_info, xpath)
        return abstract_dict_

    def strip_item(self, item):
        """
        delete useless characters
        :param item:
        :return:
        """
        for key, value in item.items():
            if isinstance(value, str):
                item[key] = value.strip()
            if key == 'paper_abstract' and not item['paper_abstract']:
                log.warning(
                    "root url: {} url: {} paper_abstract is None ".format(item['response'].url, item['paper_url']))

    def make_item(self, response, news, news_info_x, dict_):
        """

        :param response:
        :param news:
        :param news_info_x:
        :param dict_:
        :return:
        """
        if news_info_x:
            news_info = news.xpath(news_info_x)
        else:
            news_info = news
        abstract_dict = dict()
        for key, value in dict_.items():
            self.set_abstract_value(abstract_dict, response, news_info, key, value)

        if abstract_dict[PAPER_URL]:
            abstract_dict[PAPER_URL] = self.fix_url(response, abstract_dict[PAPER_URL])
        if abstract_dict[AUTHOR_LINK]:
            abstract_dict[AUTHOR_LINK] = self.fix_url(response, abstract_dict[AUTHOR_LINK])

        item = ScrapyPaperItem(**abstract_dict)
        # delete useless characters
        self.strip_item(item)
        return item, abstract_dict[PAPER_URL]

    def make_paper_req(self, response, item, paper_url):
        """
        Generate article request parameters
        :param response:
        :param item:
        :param paper_url:
        :return:
        """
        spider_name = item[PAPER_SPIDER]
        if paper_url and not self.db.exist_sp_paper(paper_url):
            meta_tmp = response.meta.copy()
            meta_tmp["item"] = item
            headers = self.make_header(paper_url)
            return [paper_url, dict(meta=meta_tmp, callback=self.parse_paper, headers=headers)]
        elif paper_url and self.db.exist_sp_paper(paper_url, spider_name):
            msg = u"{} url: {} already in database".format(spider_name, paper_url)
            log.debug(msg)
            self.db.up_sp_abstract(**dict(item))
            return "continue"
        else:
            log.debug("{} paper_url is None".format(spider_name))
            return "continue"

    def make_next_req(self, next_page):
        pass