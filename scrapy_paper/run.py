#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    author:     small 
    date:       2017/8/29
    purpose:    
"""

from scrapy import cmdline

# base_cmd = "scrapy crawl {} -L WARNING"
# base_cmd = "scrapy crawl {}"
# eaq_spider_cmd = base_cmd.format("eaq_spider")
# cmdline.execute(eaq_spider_cmd.split())
base_cmd = "scrapy crawl -a wds=[\"机器学习\"] -a max_page=20 {} "
secp_spider_cmd = base_cmd.format("baidu_spider")
cmdline.execute(secp_spider_cmd.split())
