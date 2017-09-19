#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
author:     small
date:       2017/8/29
purpose:    抓取安全客资讯(http://bobao.360.cn/)
"""

from scrapy_paper.base_spider import *

log = logging.getLogger(os.path.split(os.path.realpath(__file__))[1])
SELECTOR_NEWS_LIST = r"//ul[@class='news-list']//li[@class='clearfix']"
SELECTOR_NEWS_INFO = r"./div[@class='news-msg-wr']"
HOME_PAGE = "http://bobao.360.cn/"


class ClassifyTitle(BaseSpider, scrapy.Spider):

    name = 'aqk_spider'

    def __init__(self):
        super(ClassifyTitle, self).__init__()

    def start_requests(self):

        urls = [
            "http://bobao.360.cn/learning/index",
            "http://bobao.360.cn/news/index",
        ]

        for url in urls:
            yield scrapy.http.Request(url=url, callback=self.parse)

    def paper_time(self, response, news_info, xpath):
        """
        :param response:
        :param news_info:
        :param xpath:
        | 发布时间: 55分钟前             |
        | 时间：15小时前                 |
        | 发布时间: 16小时前             |
        | 时间：10小时前                 |
        | 发布时间: 2017-08-30 14:26
        :return:
        # days=None, seconds=None, microseconds=None, milliseconds=None, minutes=None, hours=None, weeks=None
        """

        time_ = self.fetch_xpath(news_info, xpath)
        if not time_:
            return time_
        now_time = datetime.now()
        key_public_time_1 = "发布时间: "
        key_public_time_2 = "时间："
        key_time_minutes = "分钟前"
        key_time_hours = "小时前"
        key_time_days = "天前"
        if time_.find(key_public_time_1) != -1:
            time_ = time_[len(key_public_time_1):]
        if time_.find(key_public_time_2) != -1:
            time_ = time_[len(key_public_time_2):]
        if time_.find(key_time_minutes) != -1:
            minutes = time_[:time_.find(key_time_minutes)]
            pre_time = timedelta(minutes=int(minutes))
            time_ = now_time - pre_time
            time_ = time_.strftime(TIME_FORMAT)
        elif time_.find(key_time_hours) != -1:
            hours = time_[:time_.find(key_time_hours)]
            pre_time = timedelta(hours=int(hours))
            time_ = now_time - pre_time
            time_ = time_.strftime(TIME_FORMAT)
        elif time_.find(key_time_days) != -1:
            days = time_[:time_.find(key_time_days)]
            pre_time = timedelta(days=int(days))
            time_ = now_time - pre_time
            time_ = time_.strftime(TIME_FORMAT)
        else:
            time_format = "%Y-%m-%d %H:%M"
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
            paper_title = r"./a[@class='title']/text()"
            paper_url = r"./a[@class='title']/@href"
            paper_tags = r""
            author_name = r""
            author_link = r""
            author_identity = ""
            paper_time = r"./p[@class='other']/span[@class='time']/text()"
            paper_abstract = r"./p[@class='desc']/text()"
            paper_look_number = r""
            paper_look_comments = r""

            dict_ = dict(paper_title=paper_title, paper_url=paper_url, author_name=author_name, author_link=author_link,
                         author_identity=author_identity, paper_time=paper_time, paper_abstract=paper_abstract,
                         paper_tags=paper_tags, paper_look_number=paper_look_number,
                         paper_look_comments=paper_look_comments, paper_spider =self.name)

            item, paper_url = self.make_item(response, news, SELECTOR_NEWS_INFO, dict_)
            paper_req = self.make_paper_req(response, item, paper_url)
            if paper_req is None:
                return
            elif isinstance(paper_req, list):
                yield scrapy.http.Request(paper_req[0], **paper_req[1])

        next_page = r"//div[@class='page-wr']/ul[@class='page']/li[@class='cur']/a/@href"
        next_page = self.fetch_xpath(response, next_page)
        next_page = "{}={}".format(next_page.split("=")[0], int(next_page.split("=")[1])+1)

        if next_page and not next_page.startswith("http"):
            if response.url.find("news") != -1:
                # http://bobao.360.cn/news/&page=2
                next_page = "{}news/{}".format(HOME_PAGE, next_page)
            else:
                next_page = "{}{}".format(HOME_PAGE, next_page)
        if next_page:
            yield scrapy.http.Request(next_page, callback=self.parse)
        else:
            log.debug("next_page is invalid")