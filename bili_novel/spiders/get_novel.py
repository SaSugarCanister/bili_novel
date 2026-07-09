import scrapy
from scrapy.selector import Selector
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from queue import Queue
from bili_novel.get_novel_defs.file_config import config as fc
from bili_novel.get_novel_defs.log_config import config as lc
from bili_novel.get_novel_defs.request_config import config as rc
from bili_novel.get_novel_defs.get_text import get_text
from bili_novel.get_novel_defs.getORrequest_selector import getORrequest_selector
from bili_novel.get_novel_defs.str_config import str_format
from bili_novel.get_novel_defs.waitEle import waitEle

class GetNovelSpider(scrapy.Spider):

    name = "get_novel"
    allowed_domains = [
        "www.linovelib.com",
        "img3.readpai.com"
    ]
    start_urls = ["https://www.linovelib.com"]
    # 小说编号 若想爬取其它小说，就在此处传入相应url片段
    novel_index = "/novel/XXX.html"

    #--通过 -a 关键字，定义EPUB书籍的封面设置方式
    # "illustration"：通过从“插图”文件夹中找到命名数字最小的那张图作为封面
    def __init__(self,EPUB_cover_mode=None,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.EPUB_cover_mode = EPUB_cover_mode
        # 初始化各个方法
        self.fc = fc()
        self.lc = lc()
        self.rc = rc()
        self.get_text = get_text()
        self.getORrequest_selector = getORrequest_selector()
        self.str_format = str_format()
        self.waitEle = waitEle()

        # 创建自动化浏览器
        self.service = Service(r"C:\chromedriver-win64\chromedriver-win64\chromedriver.exe")
        options = webdriver.ChromeOptions()
        # selenium自动化浏览器配置
        self.options = options.add_argument("socks5://127.0.0.1:7890")

        #创建driver
        self.driver01 = webdriver.Chrome(service=self.service,options=self.options)
        self.driver02 = webdriver.Chrome(service=self.service, options=self.options)
        self.driver03 = webdriver.Chrome(service=self.service, options=self.options)

        #创建队列
        self.q = Queue()
        self.q.put(self.driver02)
        self.q.put(self.driver03)

    #获取每个章节的url和名称，并准备请求 创建小说总文件夹 创建每本小说的文件夹
    def start_requests(self):
        # 跳转至目标大小说页面
        self.driver01.get(self.start_urls[0] + self.novel_index)
        self.waitEle.waitElement(self.driver01,"//div[@class='book-vol-chapter']/a/div/h4")
        # 创建Selector对象
        sel = Selector(text=self.driver01.page_source)
        #获取大小说名
        novel_name = sel.xpath('//h1[@class="book-name"]/text()').extract_first()
        # 获取大小说的作者名
        self.novel_author = sel.xpath('//div[@class="au-name"]/a/text()').extract_first()
        # 获取每本小说的url片段 列表
        novel_hrefs = sel.xpath('//div[@class="tit fl"]/parent::*/@href').extract()
        # 获取每本小说的名 列表
        novel_titles = sel.xpath('//div[@class="tit fl"]/h4/text()').extract()

        self.q.put(self.driver01)

        #为大小说创建文件夹
        self.novel_name = self.str_format.format_name(novel_name)[0]
        self.fc.deter_dir(aim=self.novel_name,t="novel")
        self.fc.deter_dir(aim=self.novel_name, t="imgs")

        for nh,nt in zip(novel_hrefs,novel_titles):
            #为每本小说创建对应文件夹
            novel_title = self.str_format.format_name(nt)[0]
            aim = self.novel_name + "/" + novel_title
            self.fc.deter_dir(aim=aim,t="novel")
            self.fc.deter_dir(aim=aim, t="imgs")
            #小说完整url
            novel_url = self.start_urls[0] + nh

            yield scrapy.Request(
                novel_url,
                meta={
                    "q":self.q,
                    "aim":aim,
                    "flag":"novel_url",
                },
                callback=self.novel_parse
            )

    def novel_parse(self,response):
        chapter_chips = response.meta["chapter_chips"]
        chapter_names = response.meta["chapter_names"]
        aim = response.meta["aim"]

        # 保存章节imgs文件夹路径
        chapter_dir_path_lst = []
        # 记录章节序号
        chapter_identifier = 1
        #为每个章节创建对应文件夹
        for cn in chapter_names:
            chapter_name = self.str_format.format_name(cn)[0]
            chapter_dir_path = aim + "/" + chapter_name + "_" + str(chapter_identifier)
            chapter_dir_path_lst.append(chapter_dir_path)
            self.fc.deter_dir(aim=chapter_dir_path,t="novel")
            self.fc.deter_dir(aim=chapter_dir_path, t="imgs")

            chapter_identifier += 1

        # 爬取章节内容
        for chapter_chip,chapter_dir_path in zip(chapter_chips,chapter_dir_path_lst):
            #存储当前章节页的所有图片url
            imgs_url = []
            #记录当前章节“下一页”页数
            page_num = 2
            #章节完整url
            chapter_url = self.start_urls[0] + chapter_chip

            yield scrapy.Request(
                chapter_url,
                meta={
                    "q": self.q,
                    "logger":self.logger,
                    "chapter_dir_path":chapter_dir_path,
                    "page_num":page_num,
                    "imgs_url": imgs_url,
                    "origin_chapter_url":chapter_url,
                    "execute_imgs":True,
                    "execute_next_url":True,
                    "execute_txt":True,
                    "flag":"chapter_url"
                },
                callback=self.chapter_parseORnext_request
            )

    def chapter_parseORnext_request(self,response):
        chapter_dir_path = response.meta.get("chapter_dir_path")
        chapter_title = response.meta.get("chapter_title")
        text = response.meta.get("text")
        page_num = response.meta.get("page_num")
        imgs_url = response.meta.get("imgs_url")
        execute_imgs = response.meta.get("execute_imgs")
        execute_next_url = response.meta.get("execute_next_url")
        execute_txt = response.meta.get("execute_txt")
        origin_chapter_url = response.meta.get("origin_chapter_url")
        chapter_next_url = response.url

        #保存章节页图片
        if execute_imgs:
            for img_url in imgs_url:
                yield scrapy.Request(
                    img_url[1],
                    meta={
                        "start_url":self.start_urls[0],
                        "chapter_dir_path":chapter_dir_path,
                        "img_name":img_url[0],
                        "flag":"img_url"
                    },
                    callback=self.save_img
                )

        # 保存章节页内容为txt
        if execute_txt:
            yield {
                "chapter_text":text,
                "chapter_dir_path":chapter_dir_path,
                "chapter_title":chapter_title
            }

        # 请求当前章节下一页url
        if execute_next_url:
            imgs_url = []
            yield scrapy.Request(
                chapter_next_url,
                meta={
                    "q": self.q,
                    "logger":self.logger,
                    "chapter_dir_path":chapter_dir_path,
                    "page_num":page_num,
                    "origin_chapter_url":origin_chapter_url,
                    "imgs_url":imgs_url,
                    "execute_imgs": execute_imgs,
                    "execute_next_url":execute_next_url,
                    "execute_txt":execute_txt,
                    "flag":"chapter_url",
                    "next_flag":"chapter_next_url"
                },
                callback=self.chapter_parseORnext_request
            )

    def save_img(self,response):
        chapter_dir_path = response.meta.get("chapter_dir_path")
        img_name = response.meta.get("img_name")
        b_img = response.meta.get("b_img")
        img_url = response.url
        img_path = "imgs/" + chapter_dir_path

        yield {
            "img_path": img_path,
            "img_name": img_name,
            "t": img_url,
            "b_img": b_img
        }

