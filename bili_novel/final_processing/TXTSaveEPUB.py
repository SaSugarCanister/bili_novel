import os
import re
from ebooklib import epub
import sys

class SaveEPUB:
    toc = []
    def saveEPUB(self,novel_name:str,novel_author:str,EPUB_cover_mode):
        #创建用于存储该小说的所有EPUB书籍的文件夹
        EPUB_novel_name = f"EPUB/{novel_name}"
        if not os.path.exists(EPUB_novel_name):
            os.mkdir(EPUB_novel_name)

        #获取当前大小说目录下的所有直接目录和文件
        start_dir = f"novel/{novel_name}"
        dir_txt_list = os.listdir(start_dir)
        for item in dir_txt_list:
            #路径拼接->完整的相对目录/文件路径
            #例：novel/novel_name/novel_title
            relative_path_s_novel = os.path.join(start_dir,item)
            if os.path.isdir(relative_path_s_novel):
                novel_title = item
                #根据小说名获取小说的ID
                ID = novel_title.strip().replace(" ","_").rsplit("_",1)[1]
                #创建一个EPUB书籍
                self.create_EPUB(ID,novel_name,novel_author,novel_title,EPUB_cover_mode)
                #将小说中的所有图片保存于EPUB中
                self.save_img_to_EPUB(novel_name,novel_title)

                #获取当前小说目录下的所有章节目录
                chapter_dir_lst = os.listdir(relative_path_s_novel)

                #记录当前章节编号
                chapter_num = 1

                while True:
                    #记录的当前章节编号 > 实际总章节目录数量 时，即已经对所有章节做了相应操作 此时可以退出while循环了
                    if chapter_num > len(chapter_dir_lst):
                        #添加目录
                        self.book.toc = self.toc
                        #添加导航文件
                        self.book.add_item(epub.EpubNcx())
                        self.book.add_item(epub.EpubNav())
                        #设置阅读顺序（第一章->第二章->第三章）
                        self.book.spine = ["nav"] + self.toc
                        # 初始化toc列表
                        self.toc = []
                        # 保存EPUB书籍
                        epub.write_epub(f"{EPUB_novel_name + '/' + novel_title}.epub", self.book)
                        print(f"{novel_title} 已保存为EPUB书籍！！！")

                        break

                    #遍历章节目录
                    for chapter_name in chapter_dir_lst:
                        if chapter_name.split("_")[-1] == str(chapter_num):
                            chapter_num += 1
                            #格式化章节名
                            chapter_name_format = chapter_name.rsplit("_",1)[0]
                            #获取当前章节目录下的所有txt文件
                            # 例：novel/novel_name/novel_title/chapter_dir
                            chapter_dir_path = os.path.join(relative_path_s_novel,chapter_name)
                            txt_lst = os.listdir(chapter_dir_path)
                            #创建空列表，用于对同章节下的txt文件排序
                            txt_order_lst = [""] * len(txt_lst)

                            pattern = f'.*?（(\d+)_of_\d+）.txt'

                            for txt in txt_lst:
                                re_match = re.match(pattern,txt)
                                if re_match:
                                    txt_order = int(re_match.group(1).strip())
                                    #章节内容txt是章节中的第几页，那么就是该列表中的第几个元素
                                    txt_order_lst[txt_order - 1] = txt
                                else:
                                    #若匹配失败，即当前章节页是第一页
                                    txt_order_lst[0] = txt

                            #用于保存当前章节内容
                            content = ""
                            #遍历重新排列的txt列表，从第一页到最后一页
                            for txt in txt_order_lst:
                                if txt == txt_order_lst[0]:
                                    self.create_chapter(chapter_name_format)
                                    c = self.create_content(novel_name,novel_title,chapter_name,txt,True,chapter_name_format)
                                    content += c
                                else:
                                    c = self.create_content(novel_name,novel_title,chapter_name,txt,False,chapter_name_format)
                                    content += c

                            # 将章节内容写入EPUB章节中
                            self.chapter.content = content
                            # 将EPUB章节加入EPUB书籍中
                            self.book.add_item(self.chapter)
                            #终结此次for循环
                            break

    # --创建EPUB书籍 一本小说 -> 一本EPUB书籍
    def create_EPUB(self,ID:str,novel_name:str,novel_author:str,novel_title:str,EPUB_cover_mode):
        #创建EPUB书籍对象
        self.book = epub.EpubBook()
        # --设置EPUB书籍的封面
        # 存储在EPUB中的封面图片的名称
        cover_name = f"{novel_title}.jpg"
        EPUB_cover_path = self.set_cover(EPUB_cover_mode, novel_name, novel_title)
        try:
            with open(EPUB_cover_path, "rb") as f:
                img = f.read()
            self.book.set_cover(cover_name, img)
            # --设置EPUB书籍的信息
            # EPUB书籍的ID号
            self.book.set_identifier(ID)
            # 书名
            self.book.set_title(novel_title)
            # 语言
            self.book.set_language("zh-CN")
            # 作者
            self.book.add_author(novel_author)
        except TypeError:
            print("===无插图章节，无法生成封面===")

    # --创建章节
    def create_chapter(self,chapter_name:str):
        #当前章节页为该章节的第一页时，才创建EPUB章节
        self.chapter = epub.EpubHtml(
            title=chapter_name,
            file_name=chapter_name + ".xhtml",
            lang="zh-CN"
        )
        chapter = self.chapter
        # 将章节对象存储在列表中用于后需创建EPUB目录
        self.toc.append(chapter)

    # --创建章节内容
    def create_content(self,novel_name:str,novel_title:str,chapter_name:str,txt:str,content_title_flag:bool,chapter_name_format:str):
        # 读取相应的TXT文件
        with open('novel/' + novel_name + '/' + novel_title + '/' + chapter_name + '/' + txt, "r",encoding="utf-8") as f:
            # 用于存储章节内容（文本、图片）
            content = ""

            # 为章节中添加标题
            if content_title_flag:
                title = f"<h1>{chapter_name_format}</h1>"

                content += title

            for line in f:

                # 除去字符串中最后一个字符，即"\n"换行符
                line = line[:-1]

                # --为章节中插入文本或图片
                # 插入对应图片
                if "http://" in line or "https://" in line:
                    # 获取图片名称
                    img_name = line.split("/")[-1].split(".")[0]
                    # --从imgs文件夹中获取对应图片
                    # 例：imgs/novel_name/novel_title/chapter_name/img.jpg
                    img_path = f"images/{novel_title + '_' + chapter_name + '_' + img_name + '.jpg'}"
                    # 为章节中插入图片
                    img = f"<img src='{img_path}' alt='{img_name}'/>"

                    content += img

                # 插入空行
                elif line == "<br/>":
                    content += line

                # 插入文本
                else:
                    ptext = f"<p>{line}</p>"

                    content += ptext

            return content

    #获得EPUB书籍封面
    def set_cover(self,EPUB_cover_mode,novel_name:str,novel_title:str):
        #--通过找到每个小说目录下的“插图”目录下的最小名称图片，
        # (指图片名称是数字形式时，字符串数字转为整型数字时，最小的整形数字)
        # 以该图作为封面
        if EPUB_cover_mode:
            if EPUB_cover_mode == "illustration":
                path = f"imgs/{novel_name}/{novel_title}"
                for d in os.listdir(path):
                    if re.match("插图_\\d+",d):
                        name_min = 1
                        for t_min in os.listdir(path + "/" + d):
                            new = int(t_min.split(".")[0])
                            if name_min == 1:
                                name_min = new
                            elif new < name_min:
                                name_min = new

                        cover_path = path + "/" + d + "/" + f"{name_min}.jpg"

                        return cover_path

    #将当前小说中的所有图片保存在EPUB的images中
    def save_img_to_EPUB(self,novel_name:str,novel_title:str):
        path = f"imgs/{novel_name}/{novel_title}"
        for d in os.listdir(path):
            chapter_dir = path + "/" + d

            for c in os.listdir(chapter_dir):
                img_path = chapter_dir + '/' + c
                with open(img_path,"rb") as f:
                    img_content = f.read()

                # 创建存储图片对象
                img_item = epub.EpubImage()

                img_item.file_name = f"images/{novel_title}_{d}_{c}"
                img_item.content = img_content

                # 将存储图片的对象传入book对象中
                self.book.add_item(img_item)




if __name__ == '__main__':
    save_epub = SaveEPUB()
    save_epub.saveEPUB(sys.argv[1],sys.argv[2],sys.argv[3])

    #备用方案
    # save_epub.saveEPUB("书名","书本作者名","illustration")
