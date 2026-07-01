# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import os

class BiliNovelOriginalDataSaveTXTPipeline:
    def process_item(self, item, spider):
        #初始化logger
        self.logger = spider.logger

        #保存图片
        if item.get("t"):
            self.save_img(
                item["img_path1"],
                item["img_name"],
                item["t"],
                item["b_img"]
            )

        #保存下载失败的图片url
        if item.get("img_fail"):
            self.save_fail_img(
                item["t"],
                item["novel_name"],
                item["img_path1"]
            )

        #在目标章节文件夹下创建文件以写入内容 如下的if else语句创建文件方式是为了区分同一章节下的不同页的内容
        # --若目前内容的标题与章节名同名，就执行if语句
        if item.get('next_title') == '' and type(item.get('next_title')) == str:
            self.deter_file(
                item['novel_name'],
                item['novel_title'],
                file_name=item['title'],
                chapter_dir=item['chapter_name'],
                text=item['text']
            )

        #--若目前内容的标题与章节名相似，就执行else语句
        elif item.get('next_title') != '' and type(item.get('next_title')) == str:
            self.deter_file(
                item['novel_name'],
                item['novel_title'],
                file_name=item['next_title'],
                chapter_dir=item['chapter_name'],
                text=item['text']
            )

    def deter_file(self,novel_name:str,novel_title:str,file_name:str=None,chapter_dir:str=None,text=None):
        # 例：novel/大小说名/小说名/章节名/text.txt
        file_path = 'novel/' + novel_name + '/' + novel_title + '/' + chapter_dir + '/' + file_name + '.txt'
        #没有目标文件就创建,并写入内容
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as f:
                for t in text:
                    if t != "":
                        f.write(t + '\n')
            self.logger.info(file_path + "-----文件写入完成-----")
        else:
            self.logger.info(file_path + "-----文件存在-----")

    def save_img(self,img_path1:str,img_name:str,t:str,b_img):

        # 在imgs文件夹下创建存储图片的对应文件夹
        with open(img_path1 + "/" + img_name, "wb") as f:
            f.write(b_img)

        self.logger.info(t + "---------图片下载完成---------")

    #保存下载失败的图片url
    def save_fail_img(self,t:str,novel_name:str,img_path1:str):
        self.logger.info(t + "---------图片url下载失败---------")
        with open("imgs/" + novel_name + "/" + "img_fail.txt", "a", encoding="utf-8") as f:
            f.write(img_path1 + "--&*&--")
            f.write(t + "\n")











