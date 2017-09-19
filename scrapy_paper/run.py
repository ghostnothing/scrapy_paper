#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    author:     small 
    date:       2017/8/29
    purpose:    
"""

from scrapy import cmdline

# base_cmd = "scrapy crawl {} -L WARNING"
base_cmd = "scrapy crawl {}"
# eaq_spider_cmd = base_cmd.format("eaq_spider")
# cmdline.execute(eaq_spider_cmd.split())
secp_spider_cmd = base_cmd.format("secp_spider")
cmdline.execute(secp_spider_cmd.split())
# sec_un_spider_cmd = base_cmd.format("sec_un_spider")
# cmdline.execute(sec_un_spider_cmd.split())
# mottoin_spider_cmd = base_cmd.format("mottoin_spider")
# cmdline.execute(mottoin_spider_cmd.split())
# seebug_spider_cmd = base_cmd.format("seebug_spider")
# cmdline.execute(seebug_spider_cmd.split())
# fb_spider_cmd = base_cmd.format("fb_spider")
# cmdline.execute(fb_spider_cmd.split())
# bb_spider_cmd = base_cmd.format("aqk_spider")
# cmdline.execute(bb_spider_cmd.split())
# sh_spider_cmd = base_cmd.format("sh_spider")
# cmdline.execute(sh_spider_cmd.split())
# aqn_spider_cmd = base_cmd.format("aqn_spider")
# cmdline.execute(aqn_spider_cmd.split())
# sw_spider_cmd = base_cmd.format("sw_spider")
# cmdline.execute(sw_spider_cmd.split())
