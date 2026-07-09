# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import os

class BiliNovelOriginalDataSavePipeline:
    def process_item(self, item, spider):
        #初始化logger
        self.logger = spider.logger

        #保存图片
        if item.get("t"):
            print("==t=====")
            self.save_img(
                item["img_path"],
                item["img_name"],
                item["t"],
                item["b_img"]
            )

        #在目标章节文件夹下创建文件以写入内容 如下的if elif语句创建文件方式是为了区分同一章节下的不同页的内容
        # --若目前内容的标题与章节名同名，就执行if语句
        if item.get('chapter_text'):
            self.deter_file(
                chapter_dir_path=item['chapter_dir_path'],
                chapter_title=item['chapter_title'],
                chapter_text=item['chapter_text']
            )

    def deter_file(self,chapter_dir_path:str,chapter_title,chapter_text:list):
        # 例：novel/大小说名/小说名/章节名/text.txt
        file_path = 'novel/' + chapter_dir_path + '/' + chapter_title + '.txt'
        #没有目标文件就创建,并写入内容
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as f:
                for t in chapter_text:
                    if t != "":
                        f.write(t + '\n')
            self.logger.info(file_path + "-----文件写入完成-----")
        else:
            self.logger.info(file_path + "-----文件存在-----")

    def save_img(self,img_path:str,img_name:str,t:str,b_img):
        # 在imgs文件夹下创建存储图片的对应文件夹
        with open(img_path + "/" + img_name, "wb") as f:
            f.write(b_img)

        self.logger.info(t + "---------图片下载完成---------")
