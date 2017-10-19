#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
author:     small
date:       2017/10/19
purpose:    抓取阿里云博客(https://yq.aliyun.com/articles/type_all?spm=5176.100239.bloglist.4.cdkKHM)
"""

from scrapy_paper.base_spider import *

log = logging.getLogger(os.path.split(os.path.realpath(__file__))[1])
SELECTOR_NEWS_LIST = "//div[contains(@class, 'yq-new-item item')]"
SELECTOR_NEWS_INFO = ""
HOME_PAGE = "https://yq.aliyun.com/articles/type_all"


class ClassifyTitle(BaseSpider, scrapy.Spider):

    name = 'aliyun_spider'

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

    def author_name(self, response, news_info, xpath):
        author_name = self.fetch_xpath(news_info, xpath, node_=0)
        return author_name

    def paper_look_number(self, response, news_info, xpath):
        locate = "人浏览"
        paper_look_number = self.fetch_xpath(news_info, xpath, node_=-1)
        paper_look_number = paper_look_number[:paper_look_number.find(locate)]
        return paper_look_number

    def parse(self, response):
        if not self.check_param(response, SELECTOR_NEWS_LIST):
            return

        news_list = response.xpath(SELECTOR_NEWS_LIST)
        for news in news_list:
            paper_title = "./h3/a/text()"
            paper_url = "./h3/a/@href"
            author_name = "./div[@class='new-content']/p[@class='user-info']/span[@class='info-text']/text()"
            author_link = ""
            author_identity = ""
            paper_abstract = "./div[@class='new-content']/p[@class='new-desc-two']/text()"
            paper_time = ""
            paper_tags = "./div[@class='new-content']/p[@class='tags']/a"
            paper_look_number = "./div[@class='new-content']/p[@class='user-info']/span[@class='info-text']/text()"
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

        next_page = "{}-order_createtime-page_{}".format(HOME_PAGE, self.page)
        self.page += 1
        if next_page:
            yield scrapy.http.Request(next_page, callback=self.parse)

