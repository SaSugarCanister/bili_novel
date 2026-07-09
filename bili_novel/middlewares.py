from scrapy import signals
from twisted.internet import threads
from bili_novel.get_novel_defs.waitEle import waitEle
from bili_novel.get_novel_defs.log_config import config
from bili_novel.get_novel_defs.requests_url import requests_url
from bili_novel.get_novel_defs.responses_url import responses_url
from bili_novel.get_novel_defs.get_text import get_text
import time
import random

class BiliNovelSpiderMiddleware:
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

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class BiliNovelDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def __init__(self):
        self.waitEle = waitEle()
        self.requests_url = requests_url()
        self.responses_url = responses_url()
        self.get_text = get_text()
        config().silence_selenium()

    def process_request(self, request, spider):
        q = request.meta.get("q")
        logger = request.meta.get("logger")
        chapter_dir_path = request.meta.get("chapter_dir_path")
        flag = request.meta.get("flag")
        next_flag = request.meta.get("next_flag")
        page_num = request.meta.get("page_num")
        imgs_url = request.meta.get("imgs_url")
        start_url = request.meta.get("start_url")
        origin_chapter_url = request.meta.get("origin_chapter_url")
        url = request.url
        d = ""
        driver = ""
        if not (q is None):
            driver = q.get()

        time.sleep(random.uniform(0.5, 3))

        if flag == "novel_url":
            d = threads.deferToThread(self.requests_url.request_novel,driver=driver,url=url)
            d.addCallback(self.responses_url.response_novel,request=request,driver=driver,q=q,url=url)
        elif flag == "chapter_url":
            d = threads.deferToThread(self.requests_url.request_chapter,driver=driver,url=url,logger=logger)
            d.addCallback(self.responses_url.response_chapter,next_flag=next_flag,request=request,driver=driver,logger=logger,chapter_dir_path=chapter_dir_path,page_num=page_num,imgs_url=imgs_url,origin_chapter_url=origin_chapter_url,q=q)
        elif flag == "img_url":
            d = threads.deferToThread(self.requests_url.request_img,img_url=url,start_url=start_url)
            d.addCallback(self.responses_url.response_img,request=request,img_url=url)
        return d

    def process_response(self, request, response, spider):
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


