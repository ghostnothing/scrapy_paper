#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    author:     small 
    date:       2017/8/21
    purpose:    爬取嘶吼资讯 "http://www.4hou.com"
"""

from scrapy_paper.base_spider import *

log = logging.getLogger(os.path.split(os.path.realpath(__file__))[1])
SELECTOR_NEWS_LIST = r"//div[@id='new-post']/*"
SELECTOR_NEWS_INFO = r".//div[@class='new_con']"
HOME_PAGE = "http://www.4hou.com"


class ClassifyTitle(BaseSpider, scrapy.Spider):

    name = 'sh_spider'

    def __init__(self):
        super(ClassifyTitle, self).__init__()

    def start_requests(self):

        urls = [
            HOME_PAGE
        ]
        for url in urls:
            yield scrapy.http.Request(url=url, callback=self.parse)

    def paper_time(self, response, news_info, xpath):
        """
        转换时间格式为TIME_FORMAT
        :param time_:       "8小时 前","2分钟 前", "2017年09月13日"
        :return:            TIME_FORMAT
        """
        time_ = self.fetch_xpath(news_info, xpath)
        if not time_:
            return time_

        now_time = datetime.now()
        key_time_minutes = "分钟"
        key_time_hours = "小时"
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
        else:
            time_format = "%Y年%m月%d日"
            try:
                time_ = datetime.strptime(time_, time_format).strftime(TIME_FORMAT)
            except Exception as e:
                pass
        log.debug("{} time:{}".format(self.name, time_))
        return time_

    def paper_tags(self, response, news_info, xpath):
        paper_tags = []
        news_info = news_info.xpath("../a[@class='new_img_title']")
        for tag in news_info.xpath(xpath):
            tag_info = dict(tag_name=tag.extract(),
                            tag_url="")
            paper_tags.append(tag_info)
        return paper_tags

    def parse(self, response):
        if not self.check_param(response, SELECTOR_NEWS_LIST):
            return

        news_list = response.xpath(SELECTOR_NEWS_LIST)
        for news in news_list:
            paper_title = r".//h1/text()"
            paper_url = r"./a/@href"
            paper_tags = r".//div[@class='new_img']/span/text()"
            author_name = r"./div[@class='avatar_box']/a/p/text()"
            author_link = r"./div[@class='avatar_box']/a/@href"
            author_identity = ""
            paper_time = r"./div[@class='new_bottom']/p[@class='newtime']/text()"
            paper_abstract = r"./p[@class='new_context']/text()"
            paper_look_number = r"./div[@class='new_bottom']//div[@class='read ']/span/text()"
            paper_look_comments = r"./div[@class='new_bottom']//div[@class='comment ']/span/text()"

            dict_ = dict(paper_title=paper_title, paper_url=paper_url, author_name=author_name, author_link=author_link,
                         author_identity=author_identity, paper_time=paper_time, paper_abstract=paper_abstract,
                         paper_tags=paper_tags, paper_look_number=paper_look_number,
                         paper_look_comments=paper_look_comments, paper_spider=self.name)

            item, paper_url = self.make_item(response, news, SELECTOR_NEWS_INFO, dict_)
            paper_req = self.make_paper_req(response, item, paper_url)
            if paper_req is None:
                return
            elif isinstance(paper_req, list):
                yield scrapy.http.Request(paper_req[0], **paper_req[1])

        next_page = "//div[@id='prm_btn']/a/@href"
        next_page = self.fetch_xpath(response, next_page)

        if next_page:
            yield scrapy.http.Request(next_page, callback=self.parse)