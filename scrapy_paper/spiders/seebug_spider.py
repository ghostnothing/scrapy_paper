#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
author:     small
date:       2017/9/6
purpose:    爬取seebug资讯文章(https://paper.seebug.org/)
"""

from scrapy_paper.base_spider import *

log = logging.getLogger(os.path.split(os.path.realpath(__file__))[1])
SELECTOR_NEWS_LIST = r"//article[@class='post']"
SELECTOR_NEWS_INFO = r""
HOME_PAGE = "https://paper.seebug.org/"


class ClassifyTitle(BaseSpider, scrapy.Spider):

    name = 'seebug_spider'

    def __init__(self):
        super(ClassifyTitle, self).__init__()

    def start_requests(self):

        urls = [
            HOME_PAGE
        ]
        # yield scrapy.http.Request(url="https://www.sec-wiki.com/news?News_page=130", callback=self.sw_parse)
        for url in urls:
            yield scrapy.http.Request(url=url, callback=self.parse)

    def fetch_author_name(self, author_and_abstract):
        author_feature = u"作者："
        if author_and_abstract.find(author_feature) != -1:
            # 存在作者处理
            author = author_and_abstract.split()[0][len(author_feature):]
            abstract = " ".join(author_and_abstract.split()[1:])
            return author, abstract
        else:
            return "", author_and_abstract

    def author_name(self, response, news_info, xpath):
        paper_abstract = self.fetch_xpath(news_info, xpath)
        author_name, paper_abstract = self.fetch_author_name(paper_abstract)
        return author_name

    def paper_abstract(self, response, news_info, xpath):
        paper_abstract = self.fetch_xpath(news_info, xpath)
        author_name, paper_abstract = self.fetch_author_name(paper_abstract)
        return paper_abstract

    def paper_time(self, response, news_info, xpath):
        """
        "2017-09-08"
        :param response:
        :param news_info:
        :param xpath:
        :return:
        # days=None, seconds=None, microseconds=None, milliseconds=None, minutes=None, hours=None, weeks=None
        """
        time_ = self.fetch_xpath(news_info, xpath)
        if not time_:
            return time_
        time_ = time_.split()[-1]
        time_format = "%Y-%m-%d"
        try:
            time_ = datetime.strptime(time_, time_format).strftime(TIME_FORMAT)
        except Exception as e:
            pass
        log.debug("{} time:{}".format(self.name, time_))
        return time_

    def parse(self, response):
        if not self.check_param(response, SELECTOR_NEWS_LIST):
            return

        news_list = response.xpath(SELECTOR_NEWS_LIST)
        for news in news_list:
            paper_title = r"./header[@class='post-header']/h5[@class='post-title']/a/text()"
            paper_url = r"./header[@class='post-header']/h5[@class='post-title']/a/@href"
            paper_tags = r"./header[@class='post-header']/section[@class='post-meta']/a"
            author_name = r"./section[@class='post-content']/text()"
            author_link = r""
            author_identity = r""
            paper_time = r"./header[@class='post-header']/section[@class='post-meta']/span/time[@class='fulldate']/@datetime"
            paper_abstract = r"./section[@class='post-content']/text()"
            paper_look_number = r""
            paper_look_comments = r""

            dict_ = dict(paper_title=paper_title, paper_url=paper_url, author_name=author_name, author_link=author_link,
                         author_identity=author_identity, paper_time=paper_time, paper_abstract=paper_abstract,
                         paper_tags=paper_tags, paper_look_number=paper_look_number,
                         paper_look_comments=paper_look_comments, paper_spider=self.name)

            paper_req = self.gen_paper_req(response, news, SELECTOR_NEWS_INFO, dict_)

            if paper_req is None:
                return
            elif isinstance(paper_req, list):
                yield scrapy.http.Request(paper_req[0], **paper_req[1])

        next_page = r"//nav[@class='pagination']/a[@class='older-posts']/@href"
        next_page = self.fetch_xpath(response, next_page)
        next_page = self.fix_url(response, next_page)
        log.debug("next_page: {}".format(next_page))
        if next_page:
            yield scrapy.http.Request(next_page, callback=self.parse)
