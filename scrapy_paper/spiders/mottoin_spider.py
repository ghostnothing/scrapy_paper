#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
author:     small
date:       2017/9/8
purpose:    爬取http://www.mottoin.com/资讯
"""

from scrapy_paper.base_spider import *

log = logging.getLogger(os.path.split(os.path.realpath(__file__))[1])
SELECTOR_NEWS_LIST = r"//ul[@class='article-list tab-list active']/li[@class='item']"
SELECTOR_NEWS_INFO = r""
HOME_PAGE = "http://www.mottoin.com/"


class ClassifyTitle(BaseSpider, scrapy.Spider):

    name = 'mottoin_spider'

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
        key_time_minutes = "分钟前"
        key_time_hours = "小时前"
        key_time_days = "天前"
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
            # 2017年9月1日
            time_format = "%Y年%m月%d日"
            try:
                time_ = datetime.strptime(time_, time_format).strftime(TIME_FORMAT)
            except Exception as e:
                pass
        log.debug("{} time:{}".format(self.name, time_))
        return time_

    def paper_tags(self, response, news_info, xpath):
        paper_tags = []
        if xpath:
            tag_name = self.fetch_xpath(news_info, xpath[0])
            tag_url = self.fetch_xpath(news_info, xpath[1])
            tag_info = dict(tag_name=tag_name,
                            tag_url=tag_url)
            paper_tags.append(tag_info)
        return paper_tags

    def make_next_headers(self):
        next_page = "http://www.mottoin.com/wp-admin/admin-ajax.php"
        self.page += 1
        format_data = {"action": "wpcom_load_posts", "page": self.page}
        format_data = urlencode(format_data)
        headers = self.make_header(HOME_PAGE)
        headers["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"
        headers["X-Requested-With"] = "XMLHttpRequest"
        headers["Origin"] = "http://www.mottoin.com"
        headers["Host"] = "www.mottoin.com"
        return next_page, headers, format_data

    def gen_paper_req_(self, response, news):
        paper_title = "./div[@class='item-content']/h2[@class='item-title']/a/@title"
        paper_url = "./div[@class='item-content']/h2[@class='item-title']/a/@href"
        tag_name = "./div[@class='item-img']/a[@class='item-category']/text()"
        tag_url = "./div[@class='item-img']/a[@class='item-category']/@href"
        paper_tags = [tag_name, tag_url]
        author_name = "./div[@class='item-content']/div[@class='item-meta']/div[@class='item-meta-li author']/a[@class='nickname']/text()"
        author_link = "./div[@class='item-content']/div[@class='item-meta']/div[@class='item-meta-li author']/a[@class='nickname']/@href"
        author_identity = ""
        paper_time = "./div[@class='item-content']/div[@class='item-meta']/span[@class='item-meta-li date']/text()"  # 1天前
        paper_abstract = "./div[@class='item-content']/div[@class='item-excerpt']/p/text()"
        paper_look_number = "./div[@class='item-content']/div[@class='item-meta']/span[@class='item-meta-li views']/span/text()"
        paper_look_comments = "./div[@class='item-content']/div[@class='item-meta']/a[@class='item-meta-li comments']/span/text()"

        dict_ = dict(paper_title=paper_title, paper_url=paper_url, author_name=author_name, author_link=author_link,
                     author_identity=author_identity, paper_time=paper_time, paper_abstract=paper_abstract,
                     paper_tags=paper_tags, paper_look_number=paper_look_number,
                     paper_look_comments=paper_look_comments, paper_spider=self.name)

        paper_req = self.gen_paper_req(response, news, SELECTOR_NEWS_INFO, dict_)
        return paper_req

    def parse_next_page(self, response):
        if not self.check_param(response, "//li"):
            return

        news_list = response.xpath("//li")
        for news in news_list:
            paper_req = self.gen_paper_req_(response, news)
            if paper_req is None:
                return
            elif isinstance(paper_req, list):
                yield scrapy.http.Request(paper_req[0], **paper_req[1])
        next_page, headers, format_data = self.make_next_headers()
        yield scrapy.http.Request(next_page, method="POST", headers=headers, callback=self.parse_next_page,
                                  body=format_data)

    def parse(self, response):
        if not self.check_param(response, SELECTOR_NEWS_LIST):
            return

        news_list = response.xpath(SELECTOR_NEWS_LIST)
        for news in news_list:
            paper_req = self.gen_paper_req_(response, news)
            if paper_req is None:
                return
            elif isinstance(paper_req, list):
                yield scrapy.http.Request(paper_req[0], **paper_req[1])
        next_page, headers, format_data = self.make_next_headers()
        yield scrapy.http.Request(next_page, method="POST", headers=headers, callback=self.parse_next_page, body=format_data)
