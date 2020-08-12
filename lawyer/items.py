# -*- coding: utf-8 -*-

import scrapy

#省级地域
class DistrictItem(scrapy.Item):
    name = scrapy.Field()#省级地域名称
    code = scrapy.Field()#省级地域编号

#市级地域
class CityDistrictItem(scrapy.Item):
    name = scrapy.Field()#市级地域名称
    city_code = scrapy.Field()#市级地域编号
    english_name = scrapy.Field()#英文名
    code = scrapy.Field()#省级地域编号

#律师事务所
class LawFirmItem(scrapy.Item):
    lsswsmc = scrapy.Field()#律师事务所名称
    zyzh = scrapy.Field()#执业证号
    ZSDH = scrapy.Field()#电话
    pzslsj = scrapy.Field()#成立时间
    city_district = scrapy.Field()#市级地域名称
    city_code = scrapy.Field()#市级地域编号
    zsd = scrapy.Field()#具体地址
    xzqh = scrapy.Field()#行政区号

#律师
class LawyerItem(scrapy.Item):
    pic = scrapy.Field()#律师图片
    xzqh = scrapy.Field()#行政区号
    lsswsmc = scrapy.Field()#律师事务所名称
    zyzh = scrapy.Field()#执业证号
    xm = scrapy.Field()#姓名
    years = scrapy.Field()#执业年限