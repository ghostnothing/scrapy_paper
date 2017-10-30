#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
author: small
date:   2017/8/22
purpose: 抓取安全牛资讯 http://www.aqniu.com/
"""

from scrapy_paper.base_spider import *

log = logging.getLogger(os.path.split(os.path.realpath(__file__))[1])
SELECTOR_NEWS_LIST = r"//div[@id='news']//div[@class='row post']"
SELECTOR_NEWS_INFO = r".//div[@class='col-md-7 col-sm-6']"
HOME_PAGE = "http://www.aqniu.com"


class ClassifyTitle(BaseSpider, scrapy.Spider):
    name = 'aqn_spider'

    def __init__(self):
        super(ClassifyTitle, self).__init__()

    def start_requests(self):

        urls = [
            HOME_PAGE
        ]
        # yield scrapy.http.Request(url="http://www.aqniu.com/page/175", callback=self.aqn_parse)
        for url in urls:
            yield scrapy.http.Request(url=url, callback=self.parse)

    def paper_time(self, response, news_info, xpath):
        """
        转换时间格式
        :param response:
        :param news_info:
        :param xpath:
        "星期四, 八月 31, 2017"
        :return:
        """
        time_ = self.fetch_xpath(news_info, xpath)
        if not time_:
            return time_
        map_num = {
            "一": 1,
            "二": 2,
            "三": 3,
            "四": 4,
            "五": 5,
            "六": 6,
            "七": 7,
            "八": 8,
            "九": 9,
            "十": 10,
            "十一": 11,
            "十二": 12,
        }
        month_day = time_.split(",")[1].strip()
        year = time_.split(",")[2].strip()
        month = map_num.get(month_day.split(" ")[0][:-1], datetime.now().month)
        day = month_day.split(" ")[1]
        date_obj = datetime(year=int(year), month=int(month), day=int(day))
        time_ = date_obj.strftime(TIME_FORMAT)
        log.debug("{} time:{}".format(self.name, time_))
        return time_

    def parse(self, response):
        if not self.check_param(response, SELECTOR_NEWS_LIST):
            return

        news_list = response.xpath(SELECTOR_NEWS_LIST)
        for news in news_list:
            paper_title = r"./h4/a/text()"
            paper_url = r"./h4/a/@href"
            paper_tags = r".//span[@class='cat']/a"
            author_name = r"./div[@class='meta']/span[@class='author']/a/text()"
            author_link = r"./div[@class='meta']/span[@class='author']/a/@href"
            author_identity = r""
            paper_time = r"./div[@class='meta']/span[@class='date']/text()"
            paper_abstract = r"./p/text()"
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
        next_page = r"//div[@id='news']//div[@class='navigation']/div[@class='nav-previous']/a/@href"
        next_page = self.fetch_xpath(response, next_page)
        log.debug("next_page: {}".format(next_page))
        if next_page:
            yield scrapy.http.Request(next_page, callback=self.parse)
