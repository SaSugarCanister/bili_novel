import logging
import os
import re
import random
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium import webdriver
from scrapy.selector import Selector

class DefS:
    #获取UA
    def get_UA(self) -> list:
        UA_list = []
        with open("UA.txt","r",encoding="utf-8") as f:
            for line in f:
                UA_list.append(line)

            return UA_list

    #选择随机UA
    def random_choice_UA(self,UA_lst:list) -> str:
        UA = random.choice(UA_lst)

        return UA

    # 判断目标路径下的文件夹是否存在，若不存在即创建对应的文件夹
    def deter_dir(self, aim: str, type: str,novel_name:str):
        if type == "novel":
            if not os.path.exists("novel/" + aim):
                os.mkdir("novel/" + aim)
        elif type == "imgs":
            if not os.path.exists("imgs/" + aim):
                os.mkdir("imgs/" + aim)
        elif type == "img_fail":
            if not os.path.exists("imgs/" + aim + ".txt"):
                open("imgs/" + novel_name + "/" + aim + ".txt", "w", encoding="utf-8").close()

    # 格式化名称
    def format_name(self, name: str, **kwargs) -> str:  # **kwargs用以传递p参数，p是正则表达式
        new_name = name.strip().replace(" ", "_")
        # 格式化下一页章节名
        if kwargs.get('p'):
            if not re.match(kwargs.get('p'), name) == None:
                # 例：喜欢你（1/3）格式化后-> 喜欢你（1_of_3）
                pattern = r'(.*?)(（\d+/\d+）)'
                pg = re.match(pattern, new_name)
                pg = pg.group(2)
                name_chip = re.sub(r'/', "_of_", pg)
                new_name = re.sub(r'（\d+/\d+）', name_chip, new_name)

        new_name = re.sub(r'\\/:*?"<>\|', "", new_name)

        return new_name

    # 等待章节内容中的p、img、br元素
    def waitElements(self, ele: str, driver, **kwargs):
        #scrolls 记录上滑处理的次数
        self.scrolls = 1
        #部分页面需要上滑操作，部分图片才能js渲染出来，但另一部分页面只要请求就能获取所有内容（包括图片），
        #所以针对需要上滑操作的页面进行相应处理即可
        if "/images/sloading.svg" in driver.page_source:
            # 此处页面滑动功能，解决了部分img元素不加载
            if kwargs.get('scroll_flag'):
                #每进行一次上滑处理就+1
                if kwargs.get("scrolls"):
                    self.scrolls = kwargs.get("scrolls") + 1
                #跳转至页面最上面
                driver.execute_script(f"window.scrollTo(0,0);")
                # 获取当前自动化浏览器窗口的高度
                driver_end_height = driver.execute_script("return document.body.scrollHeight")
                # scroll_times：设定滑动次数 滑动次数越多越像真人在滑动页面
                # 若高度很高就平分多，反之亦然
                rand_num = random.randint(0, 1)
                # 设置random.uniform的两个参数min、max
                # 当前页面过高时，就平分多些，等待长些，以保证页面元素加载完全(尤其是img元素)
                if driver_end_height >= 15000:
                    if rand_num == 0:
                        driver_end_height = round(driver_end_height / 100, 2)
                        scroll_times = 100
                    else:
                        driver_end_height = round(driver_end_height / 120, 2)
                        scroll_times = 120
                    min = 0.2
                    max = 0.5
                else:
                    if rand_num == 0:
                        driver_end_height = round(driver_end_height / 60, 2)
                        scroll_times = 60
                    else:
                        driver_end_height = round(driver_end_height / 80, 2)
                        scroll_times = 80
                    min = 0.1
                    max = 0.3

                for t in range(scroll_times):
                    # 模拟用户慢慢上滑页面
                    driver.execute_script(f"window.scrollBy(0,{driver_end_height});")
                    time.sleep(random.uniform(min, max))

        try:
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located(
                    (By.XPATH, f'//div[@id="mlfy_main_text"]/div[@id="TextContent"]/{ele}')
                )
            )

        except TimeoutException:
            pass

        #退出函数，防止死循环
        if self.scrolls > 3:
            print(kwargs.get("chapter_path") + " " + "!!!!!!!!此章节页存在未加载的图片!!!!!!!!")
            return 0

        if "/images/sloading.svg" in driver.page_source:
            time.sleep(random.uniform(3, 5))
            self.waitElements(ele=ele,driver=driver,scroll_flag=True,scrolls=self.scrolls)


    def request_chapterORnextpage_text_Sel(self, url: str, driver,logger,**kwargs):
        driver.get(url)

        # 等待p、br、img元素
        self.waitElements('img', scroll_flag=True, driver=driver,chapter_path=kwargs.get("chapter_path"))
        self.waitElements('p', driver=driver)
        self.waitElements('br', driver=driver)

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

    # 请求章节url和每页url，返回Selector对象
    def get_chapterORnextpage_text_Sel(self, url: str, driver,logger,service,options,**kwargs) -> Selector:
        try:
            self.request_chapterORnextpage_text_Sel(url, driver=driver,logger=logger,chapter_path=kwargs.get("chapter_path"))
        except:
            logger.info(url + "-------------章节请求出现错误-------------")
            # 重新请求，至多三次
            for i in range(3):
                try:
                    logger.info(url + f"---------尝试第{i + 1}次----------")
                    # 重启自动化浏览器
                    self.driver02.close()
                    self.driver02 = webdriver.Chrome(service=service, options=options)

                    self.request_chapterORnextpage_text_Sel(url, driver=driver,logger=logger,chapter_path=kwargs.get("chapter_path"))
                    break
                except:
                    logger.info(url + "-------------章节请求出现错误-------------")
                    if i == 2:
                        logger.info(url + "--------需检查此处问题--------")

        sel = Selector(text=driver.page_source)
        time.sleep(random.uniform(0.5, 3))

        return sel

    #获取当前章节页的小说正文内容
    def get_chapter_text(self,driver) -> list:
        text_lst = driver.execute_script(
            """
                // 先找到你要的那个元素，比如 id="TextContent" 的 div
                var container = document.querySelector('#TextContent');
                // 在这个元素下面找所有 p
                var ps = container.querySelectorAll('p,br,center,img');
                // 2. 准备一个空数组，用来装过滤后的结果
                var result = [];
                // 3. 循环遍历每个 <p> 标签
                for (var i = 0; i < ps.length; i++) {
                    // 4. 获取这个 <p> 在屏幕上实际渲染的尺寸和位置
                    var rect = ps[i].getBoundingClientRect();
                    //只有当前元素是p元素时，才执行以下逻辑
                    if (ps[i].tagName === 'P') {
                        // 5. 判断：宽度大于0 且 高度大于0
                        if (rect.width > 0 && rect.height > 0) {
                            result.push(ps[i].innerText);
                        } else {
                            result.push("")
                        }
                    } else {
                        result.push(ps[i])
                    }
                }
                return result
            """
        )

        return text_lst

    # 屏蔽selenium请求日志
    def silence_selenium(self):
        logging.getLogger("selenium").setLevel(logging.ERROR)
        logging.getLogger("selenium.webdriver.remote.remote_connection").setLevel(logging.ERROR)
        logging.getLogger("urllib3").setLevel(logging.ERROR)
        logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
