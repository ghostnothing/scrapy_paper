# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import os
import logging
import mimetypes
from scrapy_paper.db.db_base import DataBase
from scrapy_paper.base_spider import Config
log = logging.getLogger(os.path.split(os.path.realpath(__file__))[1])
CURRENT_PATH = os.path.split(os.path.realpath(__file__))[0]
FILE_PATH = os.path.realpath(os.path.join(CURRENT_PATH, "..{}..{}paper_file".format(os.sep, os.sep)))


class SaveFile(object):

    def __init__(self):
        self.name = "save_file"
        self.db = DataBase()
        self.cfg = Config()
        self.file_path = None
        self.init_env()

    def init_env(self):
        cfg_file_path = self.cfg.get_setting_option("save_file", "paper_path")
        if cfg_file_path:
            self.file_path = os.path.abspath(os.path.join(CURRENT_PATH, cfg_file_path.strip("\"")))
        else:
            self.file_path = FILE_PATH
        if not os.path.isdir(self.file_path):
            os.mkdir(self.file_path)

    def gen_file(self, spider_name, paper_title, suffix):
        file_path = os.path.join(self.file_path, spider_name)
        if not os.path.isdir(file_path):
            os.mkdir(file_path)
        paper_file = os.path.join(file_path, paper_title + suffix)
        return paper_file

    def save_paper(self, paper_file, paper_content):
        if not os.path.isfile(paper_file):
            with open(paper_file, "wb+") as fp:
                if isinstance(paper_content, bytes):
                    fp.write(paper_content)
                else:
                    fp.write(paper_content.encode('utf-8'))

    def guess_extension(self, content_type):
        if content_type:
            suffix = mimetypes.guess_extension(content_type.lower())
        else:
            suffix = ""
        return suffix

    def process_item(self, item, spider):
        # save paper file
        paper_url = item["paper_url"]
        paper_content = item['response'].body
        paper_title = item['paper_title']
        content_type = item['response'].headers['Content-Type']
        spider_name = spider.name
        paper_file = self.gen_file(spider_name, paper_title, self.guess_extension(content_type))
        self.save_paper(paper_file, paper_content)
        self.db.up_sp_abstract(paper_url=paper_url, paper_file=os.path.basename(paper_file))
        return


class ScrapyPaperPipeline(object):

    def __init__(self):
        self.cfg = Config()
        self.obj = self.init_obj(self.cfg)

    def init_obj(self, cfg):
        item_processor = cfg.get_option("settings", "item_processor")
        if item_processor == "save_file":
            item_processor = SaveFile()
        else:
            item_processor = None
        return item_processor

    def process_item(self, item, spider):
        if self.obj:
            return self.obj.process_item(item, spider)
        else:
            return item
