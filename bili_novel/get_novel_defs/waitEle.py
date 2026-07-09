from selenium.common import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import random
import time

class waitEle:
    #等待指定元素
    def waitElement(self,driver,ele:str):
        #等待div[@class='tit fl']元素的出现
        WebDriverWait(driver,10).until(
            EC.presence_of_element_located(
                (By.XPATH,ele)
            )
        )

    # 等待章节内容中的p、img、br元素
    def waitElements(self, ele: str, driver, **kwargs):
        #scrolls 记录上滑处理的次数
        scrolls=1
        #部分页面需要上滑操作，部分图片才能js渲染出来，但另一部分页面只要请求就能获取所有内容（包括图片），
        #所以针对需要上滑操作的页面进行相应处理即可
        if "/images/sloading.svg" in driver.page_source:
            # 此处页面滑动功能，解决了部分img元素不加载
            if kwargs.get('scroll_flag'):
                #每进行一次上滑处理就+1
                if kwargs.get("scrolls"):
                    scrolls = kwargs.get("scrolls") + 1
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
        if scrolls > 3:
            print(kwargs.get("url") + " " + "!!!!!!!!此章节页存在未加载的图片!!!!!!!!")
            return 0

        if "/images/sloading.svg" in driver.page_source:
            if '<div id="hidden-images" style="display:none;">' in driver.page_source:
               if "/images/sloading.svg" not in driver.page_source.split('<div id="hidden-images" style="display:none;">')[0]:
                        return 0

            time.sleep(random.uniform(3, 5))
            self.waitElements(ele=ele, driver=driver, scroll_flag=True, scrolls=scrolls)
