#!/usr/bin/python
# coding: utf-8

"""
    author:     small
    date:       17-10-18
    purpose:    爬取CSDN blog(http://blog.csdn.net/)
"""

from scrapy_paper.base_spider import *

log = logging.getLogger(os.path.split(os.path.realpath(__file__))[1])
SELECTOR_NEWS_LIST = "//dl[@class='blog_list clearfix']"
SELECTOR_NEWS_INFO = ""
HOME_PAGE = "http://blog.csdn.net"


class ClassifyTitle(BaseSpider, scrapy.Spider):

    name = 'csdn_spider'

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
        :param response:
        :param news_info:
        :param xpath:
        | 2小时前                |
        | 昨天 17:07             |
        | 前天 19:04             |
        | 4天前 10:16            |
        | 2017-10-09 15:25       |
        :return:
        # days=None, seconds=None, microseconds=None, milliseconds=None, minutes=None, hours=None, weeks=None
        """
        time_ = self.fetch_xpath(news_info, xpath)
        if not time_:
            return time_
        now_time = datetime.now()
        key_time_minutes = "分钟前"
        key_time_hours = "小时前"
        key_time_yesterday = "昨天"
        key_time_yesterday_2 = "前天"
        key_time_yesterday_3 = "天前"
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
        elif time_.find(key_time_yesterday) != -1:
            times = time_.split(" ")[1]
            times = times.strip()
            pre_time = timedelta(days=int(1))
            time_ = now_time - pre_time
            time_ = time_.strftime(TIME_FORMAT)
            time_ = "{} {}".format(time_.split(" ")[0], times)
            time_format = "%Y-%m-%d %H:%M"
            try:
                time_ = datetime.strptime(time_, time_format).strftime(TIME_FORMAT)
            except Exception as e:
                pass
        elif time_.find(key_time_yesterday_2) != -1:
            times = time_.split(" ")[1]
            times = times.strip()
            pre_time = timedelta(days=int(2))
            time_ = now_time - pre_time
            time_ = time_.strftime(TIME_FORMAT)
            time_ = "{} {}".format(time_.split(" ")[0], times)
            time_format = "%Y-%m-%d %H:%M"
            try:
                time_ = datetime.strptime(time_, time_format).strftime(TIME_FORMAT)
            except Exception as e:
                pass
        elif time_.find(key_time_yesterday_3) != -1:
            days = time_[:time_.find(key_time_yesterday_3)]
            times = time_.split(" ")[1]
            times = times.strip()
            pre_time = timedelta(days=int(days))
            time_ = now_time - pre_time
            time_ = time_.strftime(TIME_FORMAT)
            time_ = "{} {}".format(time_.split(" ")[0], times)
            time_format = "%Y-%m-%d %H:%M"
            try:
                time_ = datetime.strptime(time_, time_format).strftime(TIME_FORMAT)
            except Exception as e:
                pass
        else:
            # 2017年9月1日
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
            paper_title = "./dd/h3/a/text()"
            paper_url = "./dd/h3/a/@href"
            author_name = "./dt/a[@class='nickname']/text()"
            author_link = "./dt/a[@class='nickname']/@href"
            author_identity = False
            paper_abstract = "./dd/div[@class='blog_list_c']/text()"
            paper_time = "./dd/div[@class='blog_list_b clearfix']/div[@class='blog_list_b_r fr']/label/text()"
            paper_tags = "./dd/div[@class='blog_list_b clearfix']/div[@class='blog_list_b_l fl']/span/a"
            paper_look_number = "./dd/div[@class='blog_list_b clearfix']/div[@class='blog_list_b_r fr']/span/em/text()"
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
        next_page = "{}/?&page={}".format(HOME_PAGE, self.page)
        log.debug("next_page: {}".format(next_page))
        if next_page:
            yield scrapy.http.Request(next_page, callback=self.parse)
