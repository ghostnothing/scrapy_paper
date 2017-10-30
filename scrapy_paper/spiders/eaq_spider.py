#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
author:     small
date:       2017/9/8
purpose:    爬取 E安全 https://www.easyaq.com/资讯
"""

from scrapy_paper.base_spider import *

log = logging.getLogger(os.path.split(os.path.realpath(__file__))[1])
SELECTOR_NEWS_LIST = r"//div[@class='listnews_block select_block']/div[@class='listnews bt']"
SELECTOR_NEWS_INFO = r""
HOME_PAGE = "https://www.easyaq.com/"


class ClassifyTitle(BaseSpider, scrapy.Spider):

    name = 'eaq_spider'

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
            paper_title = "./div[@class='listdeteal']/h3/a/text()"
            paper_url = "./div[@class='listdeteal']/h3/a/@href"
            paper_tags = "./div[@class='listdeteal']/ul[@class='listword']/li/a"
            author_name = "./div[@class='listdeteal']/div[@class='source']/span/a/text()"
            author_link = "./div[@class='listdeteal']/div[@class='source']/span/a/@href"
            author_identity = ""
            paper_time = "./div[@class='listdeteal']/div[@class='source']/span/text()"
            paper_abstract = "./div[@class='listdeteal']/p/text()"
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

        max_page = "//input[@id='totalPage']/@value"
        max_page = self.fetch_xpath(response, max_page)
        if self.page <= int(max_page) and response.text:
            next_page = "{}{}.shtml".format(HOME_PAGE, self.page)
            response = urlopen(next_page)
            while not response.code == 200 and self.page <= int(max_page):
                self.page += 1
                next_page = "{}{}.shtml".format(HOME_PAGE, self.page)
                response = urlopen(next_page)
            self.page += 1
            log.debug("next_page: {}".format(next_page))
            yield scrapy.http.Request(next_page, callback=self.parse)
        else:
            log.debug("page: {}, max_page:{}".format(self.page, max_page))
