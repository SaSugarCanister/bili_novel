import requests
from bili_novel.get_novel_defs.waitEle import waitEle
from bili_novel.get_novel_defs.getORrequest_selector import getORrequest_selector
from scrapy.selector import Selector

class requests_url:
    def __init__(self):
        self.waitEle = waitEle()
        self.getORrequest_selector = getORrequest_selector()

    def request_novel(self,driver,url:str):
        driver.get(url)

        self.waitEle.waitElement(driver=driver, ele="//div[@class='tit fr']/a")
        self.waitEle.waitElement(driver=driver, ele="//div[@class='tit fl']/a")

        return Selector(text=driver.page_source)

    def request_chapter(self,driver,url:str,logger):
        sel = self.getORrequest_selector.get_chapterORnextpage_text_Sel(url=url,driver=driver,logger=logger)

        return sel

    def request_img(self,img_url,start_url):
        headers = {
            "user-agent": "Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Mobile Safari/537.36",
            "Referer": start_url
        }
        proxies = {
            "https": "socks5h://127.0.0.1:7890"
        }

        b_img = requests.get(img_url, timeout=10, headers=headers, proxies=proxies).content
        print(img_url + "----------下载图片中----------")

        return b_img
