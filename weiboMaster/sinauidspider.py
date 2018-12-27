# -*- coding: utf-8 -*-

import json
import random
import time

import urllib3


class SinaUidSpider(object):

    def __init__(self, init_uid='1906230597'):
        self.uid_set = self.init_uid_collection()
        self.wait_for_set = self.init_uid_collection()
        self.init_uid = init_uid
        self.home = 'https://m.weibo.cn/'
        self.user_home = 'https://m.weibo.cn/u/'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
        }
        self.__http = urllib3.PoolManager(headers=self.headers)

    def downloader(self, obj, url):
        obj.spider_sleep()
        return self.__http.request('GET', url)

    def get_request_cookieset(self, request):
        header = request.getheaders()
        set_cookie = header.get('Set-Cookie')
        return set_cookie[set_cookie.find('fid%3D') + 6:set_cookie.find('%26uicode')]

    def spider_main(self, obj):
        if obj.uid_collection_saver(self.init_uid):
            obj.wait_for_collection_saver(self.init_uid)
        for uid in obj.get_wait_for_collection():
            if not isinstance(uid, str):
                uid = uid.decode('utf-8')
            obj.wait_for_collection_remover(uid)
            start_url = self.user_home + uid
            request = obj.downloader(obj, start_url)
            obj.get_user_all_friends_url(obj, uid, obj.get_request_cookieset(request))

    def get_user_all_friends_url(self, obj, uid, containerid):
        follow_url = 'https://m.weibo.cn/api/container/getIndex?contahttps://m.weibo.cn/api/container/getIndex?containeridinerid=231051_-_followers_-_{}' \
                     '&luicode=10000011&lfid={}'.format(uid, containerid)
        fans_url = 'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_fans_-_{}' \
                   '&luicode=10000011&lfid={}'.format(uid, containerid)
        obj.get_follow(obj, uid, containerid, 1, follow_url)
        obj.get_fans(obj, uid, containerid, 1, fans_url)

    def get_follow(self, obj, uid, containerid, page, url):
        follow_json = json.loads(obj.downloader(obj, url).data)
        if follow_json.get('ok'):
            obj.filter_data(follow_json.get('data'))
            page = page+1
            follow_url = 'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_followers_-_{}' \
                         '&luicode=10000011&lfid={}&page={}'.format(uid, containerid, page)
            obj.get_follow(obj, uid, containerid, page, follow_url)

    def get_fans(self, obj, uid, containerid, page, url):
        obj.spider_sleep()
        fans_json = json.loads(obj.downloader(obj, url).data)
        if fans_json.get('ok'):
            obj.filter_data(fans_json.get('data'))
            page = page + 1
            fans_url = 'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_fans_-_{}' \
                       '&luicode=10000011&lfid={}&since_id={}'.format(uid, containerid, page)
            obj.get_fans(obj, uid, containerid, page, fans_url)

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
                        print(uid, '   ', screen_name)
        else:
            print("ERROR data is None")

    def get_wait_for_collection(self):
        return self.wait_for_set.copy()

    def uid_collection_saver(self, uid):
        raw_length = len(self.uid_set)
        self.uid_set.add(uid)
        now_length = len(self.uid_set)
        return raw_length < now_length

    def wait_for_collection_saver(self, uid):
        return self.wait_for_set.add(uid)

    def wait_for_collection_remover(self, uid):
        return self.wait_for_set.discard(uid)

    # 容器初始化
    def init_uid_collection(self):
        return set()

    # 随机睡眠或按照制定秒数睡眠
    def spider_sleep(self, second=random.randint(5, 15)):
        time.sleep(second)


if __name__ == "__main__":
    sinaUidSpider = SinaUidSpider()
    sinaUidSpider.spider_main(sinaUidSpider)
