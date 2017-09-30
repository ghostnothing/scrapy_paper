# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import os
import logging
import traceback
from scrapy_paper.db.db_base import DataBase
from scrapy_paper.base_spider import urlopen, Config
log = logging.getLogger(os.path.split(os.path.realpath(__file__))[1])
CURRENT_PATH = os.path.split(os.path.realpath(__file__))[0]
FILE_PATH = os.path.realpath(os.path.join(CURRENT_PATH, "..{}..{}paper_file".format(os.sep, os.sep)))


class ScrapyPaperPipeline(object):

    def __init__(self):
        self.db = DataBase()
        self.cfg = Config()
        self.file_path = None
        self.init_env()

    def init_env(self):
        cfg_file_path = self.cfg.get_setting_option("save_paper_file", "paper_path")
        if cfg_file_path:
            self.file_path = os.path.abspath(os.path.join(CURRENT_PATH, cfg_file_path.strip("\"")))
        else:
            self.file_path = FILE_PATH

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

    def gen_file(self, paper_title, paper_url, content_type, spider_name):
        suffix = self.gen_suffix(paper_url, content_type)
        file_path = os.path.join(self.file_path, spider_name)
        if not os.path.isdir(file_path):
            os.mkdir(file_path)
        paper_file = os.path.join(file_path, paper_title + suffix)
        return paper_file

    def save_paper(self, paper_file, content):
        if not os.path.isfile(paper_file):
            with open(paper_file, "wb+") as fp:
                if isinstance(content, bytes):
                    fp.write(content)
                else:
                    fp.write(content.encode('utf-8'))

    def common_process(self, item, spider):
        # save paper file
        content = item['response'].body
        paper_title = item['paper_title']
        paper_url = item["paper_url"]
        content_type = item['response'].headers['Content-Type']
        spider_name = spider.name
        paper_file = self.gen_file(paper_title, paper_url, content_type, spider_name)
        self.save_paper(paper_file, content)
        self.db.up_sp_abstract(paper_url=paper_url, paper_file=os.path.basename(paper_file))
        return item

    def sh_spider(self, item, spider):
        return self.common_process(item, spider)

    def process_item(self, item, spider):
        if not os.path.isdir(self.file_path):
            os.mkdir(self.file_path)
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
            self.save_paper(paper_file, content)
            self.db.up_sp_abstract(paper_url=paper_url, paper_file=paper_file)
