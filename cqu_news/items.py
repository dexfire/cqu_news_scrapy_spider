# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CquNewsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    time = scrapy.Field()
    title = scrapy.Field()
    abstract = scrapy.Field()
    link = scrapy.Field()
    cover = scrapy.Field()
    source = scrapy.Field()
    page = scrapy.Field()
    date = scrapy.Field()
    content = scrapy.Field()
    author = scrapy.Field()
    tags = scrapy.Field()
    hits = scrapy.Field()
    todayhits = scrapy.Field()
    weekhits = scrapy.Field()
    monthhits = scrapy.Field()
    block = scrapy.Field()
