# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ZhiweiItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass
    cityDate = scrapy.Field()
    date_time = scrapy.Field()
    company = scrapy.Field()
    positionName = scrapy.Field()
    subSelector = scrapy.Field()
    workYear = scrapy.Field()
    education = scrapy.Field()
    jobNature = scrapy.Field()
    city = scrapy.Field()
    salary = scrapy.Field()
    businessZones = scrapy.Field()
    companyLabelList = scrapy.Field()
    companySize = scrapy.Field()
    financeStage = scrapy.Field()
    industryField = scrapy.Field()
    positionId = scrapy.Field()
    responseJob = scrapy.Field()
