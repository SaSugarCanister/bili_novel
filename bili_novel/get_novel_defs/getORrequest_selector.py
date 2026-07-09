from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from scrapy.selector import Selector
from bili_novel.get_novel_defs.waitEle import waitEle

class getORrequest_selector:
    def __init__(self):
        self.waitEle = waitEle()

    #请求章节页以及下一页，加载所有目标元素
    def request_chapterORnextpage_text_Sel(self, url: str, driver,logger):
        driver.get(url)

        # 等待p、br、img元素
        self.waitEle.waitElements('img', scroll_flag=True, driver=driver,url=url)
        self.waitEle.waitElements('p', driver=driver)
        self.waitEle.waitElements('br', driver=driver)

        WebDriverWait(driver, 5).until(
            lambda d:
            d.find_elements(By.XPATH, '//div[@id="mlfy_main_text"]/h1')
            and
            (
                    d.find_elements(By.XPATH, '//a[text()="下一页"]')
                    or
                    d.find_elements(By.XPATH, '//a[text()="返回书页"]')
            )
        )

        logger.info(url + "---------章节内容加载完成---------")

    # 返回章节页以及下一页的Selector对象
    def get_chapterORnextpage_text_Sel(self, url: str, driver, logger) -> Selector:
        self.request_chapterORnextpage_text_Sel(url, driver=driver, logger=logger)

        sel = Selector(text=driver.page_source)

        return sel