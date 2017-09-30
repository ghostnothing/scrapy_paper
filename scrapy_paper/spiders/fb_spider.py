#!/usr/bin/python
# coding: utf-8

"""
    author:     small 
    date:       17-3-25
    purpose:    爬取freebuf资讯(http://www.freebuf.com)
"""

from scrapy_paper.base_spider import *

log = logging.getLogger(os.path.split(os.path.realpath(__file__))[1])
SELECTOR_NEWS_LIST = "//div[@class='news_inner news-list']"
SELECTOR_NEWS_INFO = "./div[@class='news-info']"
HOME_PAGE = "http://www.freebuf.com"


class ClassifyTitle(BaseSpider, scrapy.Spider):

    name = 'fb_spider'

    def __init__(self):
        super(ClassifyTitle, self).__init__()

    def start_requests(self):
        """
        :return: 
        """
        urls = [
            HOME_PAGE
        ]

        for url in urls:
            yield scrapy.http.Request(url=url, callback=self.parse)

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

    def author_name(self, response, news_info, xpath):
        author_name = self.fetch_xpath(news_info, xpath)
        if not author_name:
            xpath = "./dl/dd/span[@class='name']/text()"
            author_name = self.fetch_xpath(news_info, xpath)
        if not author_name:
            xpath = "./dl/dd/span[@class='name-head']/text()"
            author_name = self.fetch_xpath(news_info, xpath)
        if not author_name:
            xpath = "./dl/dd/span[@class='name']/a/text()"
            author_name = self.fetch_xpath(news_info, xpath)
        return author_name

    def author_link(self, response, news_info, xpath):
        author_link = self.fetch_xpath(news_info, xpath)
        if not author_link:
            xpath = "./dl/dd/span[@class='name']/@href"
            author_link = self.fetch_xpath(news_info, xpath)
        if not author_link:
            xpath = "./dl/dd/span[@class='name-head']/@href"
            author_link = self.fetch_xpath(news_info, xpath)
        if not author_link:
            xpath = "./dl/dd/span[@class='name']/a/@href"
            author_link = self.fetch_xpath(news_info, xpath)
        return author_link

    def parse(self, response):
        if not self.check_param(response, SELECTOR_NEWS_LIST):
            return

        news_list = response.xpath(SELECTOR_NEWS_LIST)
        for news in news_list:
            paper_title = "./dl/dt/a/text()"
            paper_url = "./dl/dt/a/@href"
            author_name = "./dl/dd/span[@class='name-head']/a/text()"
            author_link = "./dl/dd/span[@class='name-head']/a/@href"
            author_identity = "./dl/dd/span[@class='identity']/a/@href"
            paper_abstract = "./dl/dd[@class='text']/text()"
            paper_time = "./dl/dd/span[@class='time']/text()"
            paper_tags = "./div[@class='news_bot']/span[@class='tags']/a"
            paper_look_number = "./div[@class='news_bot']/span[@class='look']/strong/text()"
            paper_look_comments = "./div[@class='news_bot']/span[@class='look']/strong/text()"

            dict_ = dict(paper_title=paper_title, paper_url=paper_url, author_name=author_name, author_link=author_link,
                         author_identity=author_identity, paper_time=paper_time, paper_abstract=paper_abstract,
                         paper_tags=paper_tags, paper_look_number=paper_look_number,
                         paper_look_comments=paper_look_comments, paper_spider=self.name)

            paper_req = self.gen_paper_req(response, news, SELECTOR_NEWS_INFO, dict_)

            if paper_req is None:
                return
            elif isinstance(paper_req, list):
                yield scrapy.http.Request(paper_req[0], **paper_req[1])

        next_page = "//div[@class='news-more']/a/@href"
        next_page = self.fetch_xpath(response, next_page)

        if next_page:
            yield scrapy.http.Request(next_page, callback=self.parse)