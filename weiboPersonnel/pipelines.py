# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from weiboPersonnel.items import SinaUserItem, SinaWeiboItem, SinaUserRelationItem


class WeibopersonnelPipeline(object):

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(mongo_uri=crawler.settings.get('MONGO_HOST'),
                   mongo_db=crawler.settings.get('MONGO_DB'))

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        self.db[SinaUserItem.collection].create_index([('id', pymongo.ASCENDING)])
        self.db[SinaWeiboItem.collection].create_index([('id', pymongo.ASCENDING)])

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        if isinstance(item, SinaUserItem) or isinstance(item, SinaWeiboItem):
            self.db[item.collection].update({'id': item.get('id')}, {'$set': item}, True)
        if isinstance(item, SinaUserRelationItem):
            self.db[item.collection].update(
                {'id': item.get('id')},
                {'$addToSet': {
                    'follows': {'$each': item['follows']},
                    'fans': {'$each': item['fans']}}
                }, True)
        return item