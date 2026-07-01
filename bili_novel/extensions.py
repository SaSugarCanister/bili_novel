from scrapy import signals
import subprocess

class RunAfterSpiderClosed:
    @classmethod
    def from_crawler(cls, crawler):
        ext = cls()
        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)
        return ext

    def spider_closed(self, spider, reason):
        spider.logger.info("------爬虫结束，执行外部脚本------")

        spider.driver01.quit()
        spider.driver02.quit()

        #对获取的所有小说转化为EPUB书籍
        subprocess.run(
            [
                "python",
                "bili_novel/final_processing/TXTSaveEPUB.py",
                spider.novel_name,
                spider.novel_author,
                spider.EPUB_cover_mode
            ]
        )

        spider.logger.info("---------scrapy爬虫执行完毕---------")


