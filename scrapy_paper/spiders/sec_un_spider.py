#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
author:     small
date:       2017/9/8
purpose:    爬取安全圈资讯(https://www.sec-un.org/)
"""

from scrapy_paper.base_spider import *

log = logging.getLogger(os.path.split(os.path.realpath(__file__))[1])
SELECTOR_NEWS_LIST = r"//article[@class='post_box']"
SELECTOR_NEWS_INFO = r""
HOME_PAGE = "https://www.sec-un.org/"


class ClassifyTitle(BaseSpider, scrapy.Spider):

    name = 'sec_un_spider'

    def __init__(self):
        super(ClassifyTitle, self).__init__()

    def start_requests(self):

        urls = [
            HOME_PAGE
        ]
        # yield scrapy.http.Request(url="https://www.sec-wiki.com/news?News_page=130", callback=self.sw_parse)
        for url in urls:
            yield scrapy.http.Request(url=url, callback=self.parse)

    def paper_time(self, response, news_info, xpath):
        """
        " / 2017-09-08"
        :param response:
        :param news_info:
        :param xpath:
        :return:
        # days=None, seconds=None, microseconds=None, milliseconds=None, minutes=None, hours=None, weeks=None
        """
        time_ = ""
        year = self.fetch_xpath(news_info, xpath, node_=0)
        month_day = self.fetch_xpath(news_info, xpath, node_=1)
        if not year or not month_day:
            return time_
        time_ = "{}-{}".format(year, month_day)
        time_ = time_.split()[-1]
        time_format = "%Y-%m-%d"
        try:
            time_ = datetime.strptime(time_, time_format).strftime(TIME_FORMAT)
        except Exception as e:
            pass
        log.debug("{} time:{}".format(self.name, time_))
        return time_

    def paper_abstract(self, response, news_info, xpath):
        paper_abstract = self.fetch_xpath(news_info, xpath)
        if not paper_abstract:
            paper_abstract = "./div[@class='c-con']/a/text()"
            paper_abstract = self.fetch_xpath(news_info, paper_abstract, node_=1)
        return paper_abstract

    def paper_tags(self, response, news_info, xpath):
        paper_tags = []
        if xpath:
            for tag in news_info.xpath(xpath):
                tag_name = self.fetch_xpath(tag, "text()")
                tag_url = self.fetch_xpath(tag, "@href")
                tag_url = self.fix_url(response, tag_url)
                tag_info = dict(tag_name=tag_name,
                                tag_url=tag_url)
                paper_tags.append(tag_info)
        return paper_tags

    def parse(self, response):
        if not self.check_param(response, SELECTOR_NEWS_LIST):
            return

        news_list = response.xpath(SELECTOR_NEWS_LIST)
        for news in news_list:
            paper_title = "./div[@class='c-top']/header[@class='tit']/h2/a/text()"
            paper_url = "./div[@class='c-top']/header[@class='tit']/h2/a/@href"
            paper_tags = "./div[@class='c-top']/header[@class='tit']/aside[@class='iititle']/span/a[@rel='category tag']"
            author_name = "./div[@class='c-top']/header[@class='tit']/aside[@class='iititle']/span/a[@rel='author']/text()"
            author_link = "./div[@class='c-top']/header[@class='tit']/aside[@class='iititle']/span/a[@rel='author']/@href"
            author_identity = ""
            paper_time = "./div[@class='c-top']/div[@class='datetime']/text()"
            paper_abstract = "./div[@class='c-con']/a/p/text()"
            paper_look_number = ""
            paper_look_comments = ""

            dict_ = dict(paper_title=paper_title, paper_url=paper_url, author_name=author_name, author_link=author_link,
                         author_identity=author_identity, paper_time=paper_time, paper_abstract=paper_abstract,
                         paper_tags=paper_tags, paper_look_number=paper_look_number,
                         paper_look_comments=paper_look_comments, paper_spider=self.name)

            paper_req = self.gen_paper_req(response, news, SELECTOR_NEWS_INFO, dict_)

            if paper_req is None:
                return
            elif isinstance(paper_req, list):
                yield scrapy.http.Request(paper_req[0], **paper_req[1])
        self.page += 1
        next_page = "https://www.sec-un.org/page/{}".format(self.page)
        log.debug("next_page: {}".format(next_page))
        yield scrapy.http.Request(next_page, callback=self.parse)
