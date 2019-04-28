# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import random

import redis
from scrapy import signals
from scrapy.utils.project import get_project_settings


class WeibopersonnelSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class WeibopersonnelDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.
    def __init__(self):
        settings = get_project_settings()
        self.user_agents = settings.get('USER_AGENTS')
        self.redis_host = settings.get('REDIS_HOST')
        self.redis_port = settings.get('REDIS_PORT')
        self.redis_password = settings.get('REDIS_PASSWORD').get('password')
        self.redis_ip_proxy_name = settings.get('REDIS_IP_PROXY_NAME')
        self.redis = redis.Redis(host=self.redis_host, port=self.redis_port, password=self.redis_password)

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        ip = self.redis.srandmember(self.redis_ip_proxy_name)
        if isinstance(ip, str):
            request.meta['proxy'] = ip
        else:
            request.meta['proxy'] = ip.decode('utf-8')
        agent = random.choice(self.user_agents)
        referer = request.meta.get('referer', None)
        request.headers["User-Agent"] = agent
        request.headers["Referer"] = referer

    def process_response(self, request, response, spider):
        if response.status != 200:
            proxy = self.redis.srandmember(self.redis_ip_proxy_name)
            print("this is response ip:" + proxy)
            if isinstance(proxy, str):
                request.meta['proxy'] = proxy
            else:
                request.meta['proxy'] = proxy.decode('utf-8')
            return request
        return response

    def process_exception(self, request, exception, spider):
        self.redis.sadd("weibo_master:weibo_download_error_urls", request.url)

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
