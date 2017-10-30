#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    author:     small 
    date:       2017/8/22
    purpose:    
"""


import os
import re
import sys
import json
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
    import configparser as ConfigParser
else:
    PYTHON3 = False
    import urllib
    import ConfigParser
    from urllib import urlopen, urlencode

TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
CURRENT_PATH = os.path.split(os.path.realpath(__file__))[0]
PAPER_RESPONSE = "response"
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


class Dictionary(dict):
    """custom dict."""

    def __getattr__(self, key):
        return self.get(key, None)

    def __hasattr__(self, key):
        if key in self:
            return True
        else:
            return False

    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class Config(object):
    """Configuration file parser."""

    def __init__(self, cfg_file_="scrapy_paper.cfg", encoding_='utf-8'):
        """
        @param cfg_file_: config file name.
        @param encoding_: config file encoding, default utf-8.
        """
        self.file_config(os.path.join(CURRENT_PATH, cfg_file_), encoding_)

    def file_config(self, file_name_, encoding_):
        config = ConfigParser.ConfigParser()
        config.read(file_name_, encoding=encoding_)

        for section in config.sections():
            setattr(self, section, Dictionary())
            for name, raw_value in config.items(section):
                try:
                    # Ugly fix to avoid '0' and '1' to be parsed as a
                    # boolean value.
                    # We raise an exception to goto fail^w parse it
                    # as integer.
                    if config.get(section, name) in ["0", "1"]:
                        raise ValueError

                    value = config.getboolean(section, name)
                except ValueError:
                    try:
                        value = config.getint(section, name)
                    except ValueError:
                        try:
                            value = config.get(section, name).decode(encoding_)
                        except Exception as e:
                            value = config.get(section, name)

                setattr(getattr(self, section), name, value)

    def get(self, section_name_):
        """Get option.
        @param section_name_: section to fetch.
        @return: option value.
        """
        if not hasattr(self, section_name_):
            return None
        else:
            return getattr(self, section_name_)

    def get_option(self, section_name_, option_name_, default_=None):
        """Get option.
        @param section_name_: section to fetch.
        @param option_name_: option name to fetch.
        @param default_: The default value returned when it does not exist
        @return: option value.
        """
        section_dict = self.get(section_name_)
        if not section_dict:
            return default_
        else:
            return section_dict.get(option_name_, default_)

    def enabled(self, section_name_, default_=False):
        """
        Determine if the configuration is enabled
        @param section_name_: section to fetch.
        @param default_: The default value returned when it does not exist
        @return: True | False.
        """
        return self.get_option("settings", section_name_, default_)

    def get_setting_option(self, section_name_, option_name_, default_=None):
        """Get option.
        @param section_name_: section to fetch.
        @param option_name_: option name to fetch.
        @param default_: The default value returned when it does not exist
        @return: option value.
        """
        enabled = self.get_option("settings", section_name_)
        if not enabled:
            return default_
        else:
            return self.get_option(section_name_, option_name_, default_)


class BaseSpider(object):

    def __init__(self, *args, **kwargs):
        super(BaseSpider, self).__init__()
        self.page = 1
        self.db = DataBase()
        self.cfg = Config()
        self.init_var(**kwargs)

    def init_var(self, *args, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

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
        log.debug("{} start parse url: {}".format(response.meta["item"][PAPER_SPIDER], response.url))
        item = response.meta["item"]
        item[PAPER_RESPONSE] = response
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

    def transform_title(self, paper_title):
        # 只保留中文字符、英文字母、数字
        pattern = re.compile(u'[a-zA-Z0-9\u4e00-\u9fa5]+')
        filter_data = re.findall(pattern, paper_title)
        paper_title = u' '.join(filter_data)
        return paper_title

    def strip_item(self, item):
        """
        delete useless characters
        :param item:
        :return:
        """
        for key, value in item.items():
            if isinstance(value, str):
                item[key] = value.strip()

            if key in [PAPER_TITLE, PAPER_ABSTRACT]:
                item[key] = self.transform_title(value)

            if key == 'paper_abstract' and not item['paper_abstract']:
                log.warning(
                    "item {} paper_abstract is None ".format(dict(item)))

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

        return item

    def stop_crawling(self, item):
        """
        To determine whether to continue to crawl：
        1. If the crawler did not crawl the paper, continue to crawl;
        2. In the crawl date condition, continue to crawl;
        :param item:
        :return:
        """
        forced_crawling = self.cfg.get_option("settings", "forced_crawl")
        if forced_crawling:
            if item[PAPER_TIME]:
                paper_time = datetime.strptime(item[PAPER_TIME], TIME_FORMAT)
                paper_tge = self.cfg.get_option("forced_crawl", "paper_time_ge")
                if paper_tge and paper_time >= datetime.strptime(paper_tge.strip("\""), TIME_FORMAT):
                    return False
                else:
                    return True
            else:
                return False
        elif not self.db.exist_sp_paper(paper_url=item[PAPER_URL], paper_spider=item[PAPER_SPIDER]):
            return False
        else:
            return True

    def make_paper_req(self, response, item):
        """
        Generate article request parameters
        :param response:
        :param item:
        :return:        None: stop spider;  "continue": continue next paper; [paper_url, dict]: crawl paper
        """
        continue_str = "continue"
        paper_url = item[PAPER_URL]
        if not paper_url:
            return continue_str

        if self.stop_crawling(item):
            return None
        elif not self.db.exist_sp_paper(paper_url=paper_url):
            # add paper abstract info to database
            self.db.add_sp_abstract(**dict(item))
            # crawl paper
            if self.cfg.enabled("crawl_paper"):
                meta_tmp = response.meta.copy()
                meta_tmp["item"] = item
                headers = self.make_header(paper_url)
                return [paper_url, dict(meta=meta_tmp, callback=self.parse_paper, headers=headers)]
        else:
            # forced_crawling is True, update paper abstract info to database
            msg = u"{} url: {} already in database".format(item[PAPER_SPIDER], paper_url)
            log.debug(msg)
            self.db.up_sp_abstract(**dict(item))
            return continue_str

    def gen_paper_req(self, response, news, news_info_x, dict_):
        log.debug("gen_paper_req: {}".format(dict_.get("paper_url")))
        item = self.make_item(response, news, news_info_x, dict_)
        paper_req = self.make_paper_req(response, item)
        return paper_req

    def make_next_req(self, next_page):
        pass