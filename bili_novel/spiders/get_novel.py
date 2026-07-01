import scrapy
from scrapy.selector import Selector
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import time
import random
import os
import re
from bili_novel.get_novel_defs.defs import DefS

class GetNovelSpider(scrapy.Spider):

    name = "get_novel"
    allowed_domains = [
        "www.linovelib.com",
        "example.com"
    ]
    start_urls = ["https://www.linovelib.com"]

    #--通过 -a 关键字，定义EPUB书籍的封面设置方式
    # "illustration"：通过从“插图”文件夹中找到命名数字最小的那张图作为封面
    def __init__(self,EPUB_cover_mode=None,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.EPUB_cover_mode = EPUB_cover_mode

    def start_requests(self):
        #初始化各个方法
        defs = DefS()
        # 屏蔽selenium请求日志
        defs.silence_selenium()
        # 格式化名称
        self.format_name = defs.format_name
        # 判断目标路径下的文件夹是否存在，若不存在即创建对应的文件夹
        self.deter_dir = defs.deter_dir
        # 请求章节url和每页url，返回Selector对象
        self.get_chapterORnextpage_text_Sel = defs.get_chapterORnextpage_text_Sel
        # 获取当前章节页的小说正文内容
        self.get_chapter_text = defs.get_chapter_text
        #获取UA列表
        self.get_UA = defs.get_UA
        self.UA_lst = self.get_UA()
        #随机获取UA
        self.random_choice_UA = defs.random_choice_UA
        #创建自动化浏览器
        self.service = Service(r"C:\chromedriver-win64\chromedriver-win64\chromedriver.exe")
        options = webdriver.ChromeOptions()
        #不自动加载图片
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
        self.options = options.add_argument("socks5://127.0.0.1:7890")
        #负责获取每本小说中的每个章节url 之后用于获取章节内容
        self.driver01 = webdriver.Chrome(service=self.service,options=self.options)
        #用于获取章节内容
        self.driver02 = webdriver.Chrome(service=self.service, options=self.options)
        #小说编号 若想爬取其它小说，就在此处传入相应url片段
        self.novel_index = "/novel/xxxx.html"

        #保存小说页面的html
        # with open("html.txt","w",encoding="utf-8") as f:
        #     f.write(driver.page_source)

        # "handle_httpstatus_all":True：允许scrapy请求发生任何错误，且parse方法仍继续执行
        yield scrapy.Request(
            url="https://example.com/",
            meta={
                "handle_httpstatus_all":True
            },
            callback=self.parse
        )

    #请求大小说url 获取每个章节的url和名称，并准备请求 创建小说总文件夹 创建每本小说的文件夹
    def parse(self, response):
        # 跳转至目标大小说页面
        self.driver01.get(self.start_urls[0] + self.novel_index)
        # 创建Selector对象
        sel = Selector(text=self.driver01.page_source)
        #等待div[@class='tit fl']元素的出现
        WebDriverWait(self.driver01,10).until(
            EC.presence_of_element_located(
                (By.XPATH,"//div[@class='tit fl']")
            )
        )
        time.sleep(random.uniform(1.5,3))
        # 获取每本小说的url片段
        novel_hrefs = sel.xpath('//div[@class="tit fl"]/parent::*/@href').extract()
        #获取大小说的作者名
        novel_author = sel.xpath('//div[@class="au-name"]/a/text()').extract_first()
        #格式化作者名
        self.novel_author = self.format_name(novel_author)
        #获取大小说名
        novel_name = sel.xpath('//h1[@class="book-name"]/text()').extract_first()
        # 格式化大小说名，以作为对应文件夹名
        self.novel_name = self.format_name(novel_name)
        # 判断将要创建的大小说文件夹是否存在，不存在就创建
        self.deter_dir(self.novel_name,"novel",self.novel_name)
        self.deter_dir(self.novel_name,"imgs",self.novel_name)
        #创建存储下载失败的图片url的文件
        self.deter_dir("img_fail","img_fail",self.novel_name)
        # 获取每本小说的名
        novel_titles = sel.xpath('//div[@class="tit fl"]/h4/text()').extract()
        #存储每本小说的信息（小说名、每个章节url片段、每个章节的名字）
        novels_chapters_info = []
        #进入每本小说，获取该本小说中的所有章节url、章节名称 创建每本小说的文件夹
        for novel_href,novel_title in zip(novel_hrefs,novel_titles):
            #格式化小说名，以作为对应文件夹名
            novel_title = self.format_name(novel_title)
            # 判断将要创建的小说文件夹是否存在，不存在就创建
            self.deter_dir(self.novel_name + "/" + novel_title,"novel",self.novel_name)
            self.deter_dir(self.novel_name + "/" + novel_title, "imgs",self.novel_name)

            #完整小说url
            novel_url = self.start_urls[0] + novel_href

            #请求小说url
            try:
                self.driver01.get(novel_url)
            except:
                for i in range(3):
                    try:
                        self.logger.info(novel_url + f"---------尝试第{i + 1}次----------")
                        self.driver01.get(novel_url)
                        break
                    except:
                        self.logger.info(novel_url + "-------------小说请求出现错误-------------")
                        if i == 2:
                            self.logger.info(novel_url + "--------需检查此处问题--------")

            WebDriverWait(self.driver01, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[@class='tit fr']/a")
                )
            )
            time.sleep(random.uniform(0.5,1))

            sel = Selector(text=self.driver01.page_source)
            #获取每个章节的url片段
            chapter_chips = sel.xpath('//div[@class="tit fr"]/a/@href | //div[@class="tit fl"]/a/@href').extract()
            #获取每个章节的名字
            chapter_names = sel.xpath('//div[@class="tit fr"]/a/text() | //div[@class="tit fl"]/a/text()').extract()

            #存储当前小说的信息
            novels_chapters_info.append(
                {
                    'novel_title':novel_title,
                    'chapter_chips':chapter_chips,
                    'chapter_names':chapter_names
                }
            )

        #储存所有小说的所有章节信息
        novels_chapters_info_2 = []
        for novel_chapters_info in novels_chapters_info:
            # 记录章节序号
            chapter_identifier = 1
            #请求每个章节的url
            for chapter_chip,chapter_name in zip(novel_chapters_info['chapter_chips'],novel_chapters_info['chapter_names']):
                chapter_url = self.start_urls[0] + chapter_chip
                #格式化章节名
                chapter_name = self.format_name(chapter_name) + "_" + str(chapter_identifier)
                #创建对应文件夹，分别用于存储小说内容和图片
                self.deter_dir(self.novel_name + "/" + novel_chapters_info['novel_title'] + "/" + chapter_name, "novel",self.novel_name)
                self.deter_dir(self.novel_name + "/" + novel_chapters_info['novel_title'] + "/" + chapter_name,"imgs",self.novel_name)

                novels_chapters_info_2.append(
                    {
                        "chapter_url":chapter_url,
                        "novel_title":novel_chapters_info['novel_title'],
                        "chapter_name":chapter_name
                    }
                )

                chapter_identifier += 1

        #记录当前爬取进度
        self.crawl_num = 0
        #总进度
        self.crawl_all_num = len(novels_chapters_info_2)

        for novel_chapters_info_2 in novels_chapters_info_2:
            yield scrapy.Request(
                url="https://example.com/",
                meta={
                    "handle_httpstatus_all": True,
                    "url":novel_chapters_info_2["chapter_url"],
                    "novel_title":novel_chapters_info_2["novel_title"],
                    "chapter_name":novel_chapters_info_2["chapter_name"]
                },
                callback=self.chapter_parse
            )

    #获取每个章节的内容（小说文本、插图）
    def chapter_parse(self,response):
        self.crawl_num += 1
        #章节在网站中的路径名
        chapter_path = response.meta["novel_title"] + "/" + response.meta["chapter_name"] + "/" + response.meta["url"]
        #请求目标章节url
        self.logger.info(chapter_path + f"--------- 开始请求章节 {self.crawl_num}/{self.crawl_all_num} ---------")
        sel = self.get_chapterORnextpage_text_Sel(response.meta["url"],driver=self.driver02,logger=self.logger,service=self.service,options=self.options,chapter_path=chapter_path)

        #保存下一页标题名
        outer_format_next_title = ''

        #创建请求会话对象
        session = requests.Session()

        #chapter_flag用以判断当前章节是否获取完所有内容
        chapter_flag = True

        while True:
            if chapter_flag:
                # 获取内容块
                novel_main = sel.xpath("//div[@id='mlfy_main_text']")
                #标题名/章节名
                title = novel_main.xpath("./h1/text()").extract_first()
                #格式化标题名/章节名
                format_title = self.format_name(title)
                # 获取正文块
                text_context = novel_main.xpath("./div[@id='TextContent']")
                # 获取"下一页"url
                next_href = sel.xpath('//a[text()="下一页"]/@href').extract_first()
                if next_href == None:
                    next_url = ""
                else:
                    next_url = self.start_urls[0] + next_href
                    chapter_path = response.meta["novel_title"] + "/" + response.meta["chapter_name"] + "/" + next_url
                # 正文（包含文本、br元素、center元素、图片url）
                text = text_context.xpath('./p/text() | ./br | ./center/text() | ./img/@src').extract()
                # 获取解决了本文投毒的正文（仅包含文本）
                solve_poison_text = self.get_chapter_text(self.driver02)
                #--遍历获取到的正文列表，遍历到图片url时，对其进行下载保存
                #--遍历获取到的正文列表，遍历到<br>时，将其改为<br/>
                #用于记录遍历元素的对应下标
                lst_num = 0
                for t,spt in zip(text,solve_poison_text):
                    #判断文本是不是图片元素
                    if ("http://" in t or "https://" in t) and ("creativesurvey." not in t):

                        # 获取图片名称
                        img_name = t.split("/")[-1]

                        #--检测图片是否存在
                        img_path1 = "imgs/" + self.novel_name + "/" + response.meta['novel_title'] + "/" + response.meta['chapter_name']
                        img_path2 = img_path1 + "/" + img_name

                        #不存在就请求图片url
                        if not os.path.exists(img_path2):
                            time.sleep(random.uniform(1,5))

                            #下载图片 由于会检测Refer参数，这里通过requests下载
                            try:

                                self.get_session(session)

                                b_img = session.get(t,timeout=10).content

                                yield {
                                    "img_path1":img_path1,
                                    "img_name":img_name,
                                    "t":t,
                                    "b_img":b_img
                                }

                            except:
                                for i in range(3):
                                    self.logger.info(t + "---------图片url重新请求中---------")
                                    #重启session
                                    session.close()
                                    session = requests.Session()
                                    self.get_session(session)
                                    time.sleep(random.uniform(4,5))
                                    try:
                                        #重试下载
                                        b_img = session.get(t, timeout=10).content

                                        yield {
                                            "img_path1": img_path1,
                                            "img_name": img_name,
                                            "t": t,
                                            "b_img": b_img
                                        }

                                        break

                                    except:
                                        if i == 2:

                                            yield {
                                                "t":t,
                                                "novel_name":self.novel_name,
                                                "img_path1":img_path1,
                                                "img_fail":True
                                            }

                        else:
                            self.logger.info(img_path2 + "---------图片已存在---------")

                    elif t == "<br>":
                        text[lst_num] = "<br/>"

                    else:
                        if type(spt) == str:
                            text[lst_num] = spt

                    lst_num += 1

                yield {
                    "novel_name": self.novel_name,
                    "novel_title": response.meta["novel_title"],
                    "chapter_name":response.meta["chapter_name"],
                    "title": format_title,
                    "next_title": outer_format_next_title,
                    "text": text
                }

                if next_url == "":
                    chapter_flag = False
                else:
                    # 请求下一页
                    sel = self.get_chapterORnextpage_text_Sel(next_url,driver=self.driver02,logger=self.logger,service=self.service,options=self.options,chapter_path=chapter_path)
                    #获取下一页的标题名
                    next_title = sel.xpath('//div[@id="mlfy_main_text"]/h1/text()').extract_first()
                    #格式化下一页的标题名(去除左右两边空格)
                    format_next_title1 = next_title.strip()
                    format_next_title2 = format_next_title1.replace(" ","")

                    #判断该标题名是否为本章节名，是即该页的内容需要爬取，否即亦然
                    #例：喜欢你（1/2）匹配格式—> 喜欢你（/）
                    pattern = f'.*?（\d+/\d+）'
                    if re.match(pattern,format_next_title2) == None:
                        chapter_flag = False

                    #对下一页的标题名，再次格式化用以文件命名
                    outer_format_next_title = self.format_name(format_next_title1,p=pattern)

            else:
                #结束当前章节内容的获取 一般是当前章节内容已获取完
                self.logger.info(response.meta["chapter_name"] + "-----章节内容全部获取完成-----")
                session.close()
                break

    #配置session
    def get_session(self,session):
        # 获取随机UA
        UA = self.random_choice_UA(self.UA_lst)
        self.headers = {
            "user-agent": UA,
            "Referer": self.start_urls[0]
        }
        session.headers.update(self.headers)
        # 配置sessioon
        session.proxies = {
            "https": "socks5h://127.0.0.1:7890"
        }
