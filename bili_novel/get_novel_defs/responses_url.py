import os
from scrapy.http import HtmlResponse
from bili_novel.get_novel_defs.str_config import str_format
from bili_novel.get_novel_defs.get_text import get_text
from bili_novel.get_novel_defs.requests_url import requests_url

class responses_url:
    def __init__(self):
        self.str_format = str_format()
        self.get_text = get_text()
        self.requests_url = requests_url()

    def response_novel(self,sel,request,driver,q,url):
        # 获取每个章节的url片段
        chapter_chips = sel.xpath('//div[@class="tit fr"]/a/@href | //div[@class="tit fl"]/a/@href').extract()
        # 获取每个章节的名字
        chapter_names = sel.xpath('//div[@class="tit fr"]/a/text() | //div[@class="tit fl"]/a/text()').extract()

        # 储存url片段与章节名至meta中
        request.meta["chapter_chips"] = chapter_chips
        request.meta["chapter_names"] = chapter_names

        q.put(driver)

        return HtmlResponse(
            url=url
        )

    def response_chapter(self,sel,next_flag,request,driver,logger,chapter_dir_path,page_num,imgs_url,origin_chapter_url,q):
        #获取内容块
        novel_main = sel.xpath("//div[@id='mlfy_main_text']")
        #标题名
        title = novel_main.xpath("./h1/text()").extract_first()
        #格式化标题名
        tuple_data = self.str_format.format_name(title, p=f'.*?（\\d+/\\d+）')
        format_title = tuple_data[0]
        two_num_lst = tuple_data[1]

        if next_flag:
            if int(two_num_lst[0]) > int(two_num_lst[1]):
                request.meta["execute_imgs"] = False
                request.meta["execute_next_url"] = False
                request.meta["execute_txt"] = False

                q.put(driver)

                return HtmlResponse(
                    url=""
                )

        # 获取解决了本文投毒的正文（包含文本、br元素、center元素、图片url）
        solve_poison_text = self.get_text.get_chapter_text(driver)

        # 用于记录遍历元素的对应下标
        lst_num = 0
        for spt in solve_poison_text:
            #判断文本是不是图片元素
            if ("http://" in spt or "https://" in spt) and ("creativesurvey." not in spt):

                # 获取图片名称
                img_name = spt.split("/")[-1]

                #--检测图片是否存在
                img_path1 = "imgs/" + chapter_dir_path
                img_path2 = img_path1 + "/" + img_name

                #不存在就保存该图片url
                if not os.path.exists(img_path2):
                    imgs_url.append((img_name,spt))

                else:
                    logger.info(img_path2 + "---------图片已存在---------")

            #判断是否为br元素
            elif spt == "<br>":
                solve_poison_text[lst_num] = "<br/>"

            lst_num += 1

        #获取当前章节的下一页url
        next_url = origin_chapter_url.split(".html")[0] + f"_{page_num}.html"
        page_num += 1

        request.meta["text"] = solve_poison_text
        request.meta["chapter_title"] = format_title
        request.meta["page_num"] = page_num
        request.meta["imgs_url"] = imgs_url

        q.put(driver)

        return HtmlResponse(
            url=next_url
        )

    def response_img(self,b_img,request,img_url):
        request.meta["b_img"] = b_img

        return HtmlResponse(
            url=img_url
        )