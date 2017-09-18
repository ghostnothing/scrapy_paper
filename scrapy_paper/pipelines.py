# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import os
import re
import logging
import traceback
from scrapy_paper.db.db_base import DataBase
from scrapy_paper.base_spider import urlopen
log = logging.getLogger(os.path.split(os.path.realpath(__file__))[1])
CURRENT_PATH = os.path.split(os.path.realpath(__file__))[0]
FILE_PATH = os.path.realpath(os.path.join(CURRENT_PATH, "..\..\paper_file"))


class ScrapyPaperPipeline(object):

    def __init__(self):
        self.db = DataBase()

    def save_abstract(self, log_info):
        self.db.add_sp_abstract(**log_info)

    def gen_suffix(self, paper_url="", content_type=""):
        if isinstance(content_type, bytes):
            content_type = content_type.decode()

        paper_url = paper_url.lower()
        content_type = content_type.lower()

        if content_type.find("html") != -1 or paper_url.endswith("html"):
            suffix = ".html"
        elif paper_url.endswith(".txt"):
            suffix = ".txt"
        elif paper_url.endswith(".pdf") or content_type.find("pdf") != -1:
            suffix = ".pdf"
        else:
            suffix = ""
        return suffix

    def transform_title(self, paper_title):
        # 只保留中文字符、英文字母、数字
        pattern = re.compile(u'[a-zA-Z0-9\u4e00-\u9fa5]+')
        filter_data = re.findall(pattern, paper_title)
        paper_title = u''.join(filter_data)
        return paper_title

    def gen_file(self, paper_title, paper_url, content_type, spider_name):
        suffix = self.gen_suffix(paper_url, content_type)
        file_path = os.path.join(FILE_PATH, spider_name)
        if not os.path.isdir(file_path):
            os.mkdir(file_path)
        paper_title = self.transform_title(paper_title)
        paper_file = os.path.join(file_path, paper_title + suffix)
        return paper_file

    def strip_item(self, item):
        """
        delete useless characters
        :param item:
        :return:
        """
        for key, value in item.items():
            if isinstance(value, str):
                item[key] = value.strip()
            if key == 'paper_abstract' and not item['paper_abstract']:
                log.debug("root url: {} url: {} error paper_abstract is None ".format(item['response'].url, item['paper_url']))

    def write_file(self, paper_file, content):
        if not os.path.isfile(paper_file):
            with open(paper_file, "wb+") as fp:
                if isinstance(content, bytes):
                    fp.write(content)
                else:
                    fp.write(content.encode('utf-8'))

    def common_process(self, item, spider):
        # delete useless characters
        self.strip_item(item)

        # add database
        dic = dict(item)
        self.save_abstract(dic)

        # save file
        content = item['response'].body
        paper_title = item['paper_title']
        paper_url = item["paper_url"]
        content_type = item['response'].headers['Content-Type']
        spider_name = spider.name
        paper_file = self.gen_file(paper_title, paper_url, content_type, spider_name)
        self.write_file(paper_file, content)
        self.db.set_sp_file(paper_url_=paper_url, paper_file_=os.path.basename(paper_file))
        return item

    def sh_spider(self, item, spider):
        return self.common_process(item, spider)

    def process_item(self, item, spider):
        if not os.path.isdir(FILE_PATH):
            os.mkdir(FILE_PATH)
        if hasattr(self, spider.name):
            func = getattr(self, spider.name)
            return func(item, spider)
        else:
            return self.common_process(item, spider)

    def download_failed_file(self):
        papers = self.db.query_sp_paper(paper_file_="")
        for paper in papers:
            if not paper.paper_url:
                continue
            paper_title = paper.paper_title
            paper_url = paper.paper_url
            response = urlopen(paper_url)
            content = response.body
            content_type = response.headers['Content-Type']
            spider_name = paper.paper_spider
            paper_file = self.gen_file(paper_title, paper_url, content_type, spider_name)
            self.write_file(paper_file, content)
            self.db.set_sp_file(paper_url_=paper_url, paper_file_=paper_file)
