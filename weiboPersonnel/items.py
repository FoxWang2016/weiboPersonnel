# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class WeibopersonnelItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class SinaUserItem(scrapy.Item):
    collection = 'users'
    id = scrapy.Field()
    name = scrapy.Field()  #名字
    avatar = scrapy.Field()
    cover = scrapy.Field()
    gender = scrapy.Field()
    description = scrapy.Field()
    fans_count = scrapy.Field()
    follows_count = scrapy.Field()
    weibos_count = scrapy.Field()
    verified = scrapy.Field()
    verified_reason = scrapy.Field()
    verified_type = scrapy.Field()
    follows = scrapy.Field()
    fans = scrapy.Field()
    crawled_at = scrapy.Field()


class SinaUserRelationItem(scrapy.Item):
    collection = 'users'
    id = scrapy.Field()
    follows = scrapy.Field()
    fans = scrapy.Field()


class SinaWeiboItem(scrapy.Item):
    collection = 'weibos'
    id = scrapy.Field()
    attitudes_count = scrapy.Field() #点赞数
    comments_count = scrapy.Field() #回复数
    reposts_count = scrapy.Field() #转发数
    picture = scrapy.Field() #首图
    pictures = scrapy.Field() #微博图片
    source = scrapy.Field() #信息发送终端
    text = scrapy.Field() #微博内容
    raw_text = scrapy.Field() #发表内容
    thumbnail = scrapy.Field() #缩略图
    user = scrapy.Field()     #用户信息
    created_at = scrapy.Field() #发布时间
    scheme = scrapy.Field() #微博链接
    crawled_at = scrapy.Field()


