# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ScrapyPaperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    response = scrapy.Field()
    paper_title = scrapy.Field()
    paper_url = scrapy.Field()
    author_name = scrapy.Field()
    author_link = scrapy.Field()
    author_identity = scrapy.Field()
    paper_time = scrapy.Field()
    paper_abstract = scrapy.Field()
    paper_tags = scrapy.Field()
    paper_look_number = scrapy.Field()
    paper_look_comments = scrapy.Field()
    paper_spider = scrapy.Field()
