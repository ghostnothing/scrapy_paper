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

    def transform_time(self, time_):
        """
        转换时间格式为TIME_FORMAT
        :param time_:       "8小时 前","2分钟 前", "2017年09月13日"
        :return:            TIME_FORMAT
        """
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
        log.debug("home: {} time:{}".format(HOME_PAGE, time_))
        return time_

    def parse(self, response):
        meta = response.meta
        news_list = response.xpath(SELECTOR_NEWS_LIST)
        if not news_list:
            return
        for news in news_list:
            if SELECTOR_NEWS_INFO:
                news_info = news.xpath(SELECTOR_NEWS_INFO)
            else:
                news_info = news

            paper_title = r".//h1/text()"
            paper_url = r"./a/@href"
            tags = r".//div[@class='new_img']/span/text()"
            author_name = r"./div[@class='avatar_box']/a/p/text()"
            author_link = r"./div[@class='avatar_box']/a/@href"
            paper_time = r"./div[@class='new_bottom']/p[@class='newtime']/text()"
            paper_abstract = r"./p[@class='new_context']/text()"
            paper_look_number = r"./div[@class='new_bottom']//div[@class='read ']/span/text()"
            paper_look_comments = r"./div[@class='new_bottom']//div[@class='comment ']/span/text()"

            paper_title = self.fetch_xpath(news_info, paper_title)
            paper_url = self.fetch_xpath(news_info, paper_url)
            author_name = self.fetch_xpath(news_info, author_name)
            author_link = self.fetch_xpath(news_info, author_link)
            author_identity = False
            paper_time = self.fetch_xpath(news_info, paper_time)
            paper_time = self.transform_time(paper_time)
            paper_abstract = self.fetch_xpath(news_info, paper_abstract)
            paper_tags = []
            for tag in news_info.xpath(tags):
                tag_info = dict(tag_name=tag.extract(),
                                tag_url="")
                paper_tags.append(tag_info)
            paper_look_number = self.fetch_xpath(news_info, paper_look_number, default_="0")
            paper_look_number = "".join(paper_look_number.split(","))
            paper_look_comments = self.fetch_xpath(news_info, paper_look_comments, default_="0")

            item = ScrapyPaperItem(paper_title=paper_title,
                                   paper_url=paper_url,
                                   author_name=author_name,
                                   author_link=author_link,
                                   author_identity=author_identity,
                                   paper_time=paper_time,
                                   paper_abstract=paper_abstract,
                                   paper_tags=paper_tags,
                                   paper_look_number=paper_look_number,
                                   paper_look_comments=paper_look_comments,
                                   paper_spider=self.name)

            if paper_url and not self.db.exist_sp_paper(paper_url):
                meta_tmp = meta.copy()
                meta_tmp["item"] = item
                yield scrapy.Request(paper_url, meta=meta_tmp, callback=self.parse_paper)
            elif paper_url and self.db.exist_sp_paper(paper_url, HOME_PAGE):
                msg = u"{} url: {} already in database".format(self.name, paper_url)
                log.debug(msg)
                return
            else:
                log.debug("{} paper_url is None".format(HOME_PAGE))

        next_page = "//div[@id='prm_btn']/a/@href"
        next_page = self.fetch_xpath(response, next_page)

        if next_page:
            yield scrapy.http.Request(next_page, callback=self.parse)