# -*- coding: utf-8 -*-
import redis

from weiboMaster.sinauidspider import SinaUidSpider


class SinaUidRedisSpider(SinaUidSpider):

    def __init__(self, redis_db_name='sina_weibo:wait_spider_proxy',
                 redis_host="localhost", redis_port="6379", redis_password=''):
        super().__init__(init_uid='1906230597')
        self.redis = redis.Redis(host=redis_host, port=redis_port, password=redis_password)
        self.redis_db_name = redis_db_name
        self.user_url = 'https://m.weibo.cn/api/container/getIndex?uid={uid}&luicode=10000011&lfid=230413{uid}' \
               '_-_WEIBO_SECOND_PROFILE_WEIBO&type=uid&value={uid}&containerid=100505{uid}'

    def uid_collection_saver(self, uid):
        return self.redis.sadd('sina_weibo:uid_all_proxy', uid)

    def wait_for_collection_saver(self, uid):
        return self.redis.lpush('sina_weibo:wait_m_uid_proxy', uid)

    def wait_for_collection_remover(self, uid):
        return self.redis.lrem('sina_weibo:wait_m_uid_proxy', uid)

    def get_wait_for_collection(self):
        return self.redis.lrange('sina_weibo:wait_m_uid_proxy', 0, -1)

    def filter_data(self, data):
        if data:
            cards = data.get('cards')
            for card in cards:
                if card.get('card_style') is None:
                    card_group = card.get('card_group')
                    for cardgr in card_group:
                        user = cardgr.get('user')
                        uid = user.get('id')
                        screen_name = user.get('screen_name')
                        if self.uid_collection_saver(uid):
                            self.wait_for_collection_saver(uid)
                            self.redis.lpush(self.redis_db_name, self.user_url.format(uid=uid))
                        #print(uid, '   ', screen_name)
        else:
            print("ERROR data is None")


if __name__ == '__main__':
    sinaUidRedisSpider = SinaUidRedisSpider(redis_port='7379')
    sinaUidRedisSpider.spider_main(sinaUidRedisSpider)
