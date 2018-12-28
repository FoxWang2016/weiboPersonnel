# -*- coding: utf-8 -*-
import json

import redis as redis
from scrapy import Request
from scrapy_redis.spiders import RedisSpider
from weiboPersonnel.items import SinaUserItem, SinaUserRelationItem, SinaWeiboItem
from scrapy.conf import settings


class WeibospiderSpider(RedisSpider):
    name = 'weiboSpider'
    redis_key = 'sina_weibo:wait_spider_proxy'
    user_url = 'https://m.weibo.cn/api/container/getIndex?uid={uid}&luicode=10000011&lfid=230413{uid}' \
               '_-_WEIBO_SECOND_PROFILE_WEIBO&type=uid&value={uid}&containerid=100505{uid}'
    follow_url = 'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_followers_-_{uid}&page={page}'
    fans_url = 'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_fans_-_{uid}&page={page}'
    weibo_url = 'https://m.weibo.cn/api/container/getIndex?type=uid&value={uid}&containerid=107603{uid}'
    redis = redis.Redis(host=settings['REDIS_HOST'], port=settings['REDIS_PORT'], password=settings['REDIS_PASSWORD'])

    # allowed_domains = ['m.weibo.com']
    # start_urls = ['http://m.weibo.com/']

    def parse(self, response):
        result = json.loads(response.text)
        if result.get('ok'):
            user_info = result.get('data').get('userInfo')
            self.get_user(user_info)

            uid = user_info.get('id')
            yield Request(self.follow_url.format(uid=uid, page=1), callback=self.pares_follows, meta={'page': 1,
                                                                                                      'uid': uid})
            yield Request(self.fans_url.format(uid=uid, page=1), callback=self.pares_fans, meta={'page': 1, 'uid': uid})
            yield Request(self.weibo_url.format(uid=uid), callback=self.pares_sina_weibo, meta={'uid': uid})

    def pares_follows(self, response):
        result_follows = json.loads(response.text)
        if result_follows.get('ok') and result_follows.get('data').get('cards'):
            follows = result_follows.get('data').get('cards')[-1]
            cards_group = follows.get('card_group')
            self.add_for_wait_spider_proxy(cards_group)

            uid = response.meta.get('uid')
            follow_array = [{'id': card.get('user').get('id'),
                             'name': card.get('user').get('screen_name')} for card in cards_group]
            user_relation_item = SinaUserRelationItem()
            user_relation_item['id'] = uid
            user_relation_item['follows'] = follow_array
            user_relation_item['fans'] = []
            yield user_relation_item

            page = response.meta.get('page')+1
            yield Request(self.follow_url.format(uid=uid, page=page), callback=self.pares_follows, meta={'uid': uid,
                                                                                                         'page': page})

    def pares_fans(self, response):
        result_fans = json.loads(response.text)
        if result_fans.get('ok') and result_fans.get('data').get('cards'):
            fans = result_fans.get('data').get('cards')[-1]
            cards_group = fans.get('card_group')
            self.add_for_wait_spider_proxy(cards_group)

            uid = response.meta.get('uid')
            fans_array = [{'id': card.get('user').get('id'),
                           'name': card.get('user').get('screen_name')} for card in cards_group]
            user_relation_item = SinaUserRelationItem()
            user_relation_item['id'] = uid
            user_relation_item['follows'] = []
            user_relation_item['fans'] = fans_array
            yield user_relation_item

            page = response.meta.get('page') + 1
            yield Request(self.fans_url.format(uid=uid, page=page), callback=self.pares_fans, meta={'uid': uid,
                                                                                                    'page': page})

    def pares_sina_weibo(self, response):
        result_weibos = json.loads(response.text)
        if result_weibos.get('ok'):
            #反页抓取
            since_id = result_weibos.get('data').get('cardlistInfo').get('since_id')
            if since_id:
                uid = response.meta.get('uid')
                yield Request(self.weibo_url.format(uid)+'&since_id='+since_id, callback=self.pares_sina_weibo,
                              meta={'uid': uid})
            #内容抓取
            cards = result_weibos.get('data').get('cards')
            if cards:
                weibo_item = SinaWeiboItem()
                field_map = {'id': 'id', 'attitudes_count': 'attitudes_count', 'comments_count': 'comments_count',
                             'reposts_count': 'reposts_count', 'picture': 'original_pic', 'pictures': 'pics',
                             'created_at': 'created_at', 'source': 'source', 'text': 'text', 'raw_text': 'raw_text',
                             'thumbnail': 'thumbnail_pic'}
                for card in cards:
                    mblog = card.get('mblog')
                    scheme = card.get('scheme')
                    if mblog and scheme:
                        weibo_item['scheme'] = scheme
                        for field, attr in field_map.items():
                            weibo_item[field] = mblog.get(attr)
                        yield weibo_item

    def get_user(self, user_info):
        user_item = SinaUserItem()
        field_map = {'id': 'id', 'name': 'screen_name', 'avatar': 'profile_image_url', 'cover': 'cover_image_phone',
                     'gender': 'gender', 'description': 'description', 'fans_count': 'followers_count',
                     'follows_count': 'follow_count', 'weibos_count': 'statuses_count', 'verified': 'verified',
                     'verified_reason': 'verified_reason', 'verified_type': 'verified_type'}

        for field, attr in field_map.items():
            user_item[field] = user_info.get(attr)
        yield user_item

    def add_for_wait_spider_proxy(self, cards_group):
        for card in cards_group:
            user_info = card.get('user')
            if user_info:
                uid = user_info.get('id')
                if self.redis.sadd('sina_weibo:uid_all_proxy', uid):
                    self.redis.lpush('sina_weibo:wait_spider_proxy', self.user_url.format(uid=uid))
