import os

class config:
    # 判断目标路径下的文件夹是否存在，若不存在即创建对应的文件夹
    def deter_dir(self, aim: str, t: str, img_fail_novel_name: str = ""):
        if t == "novel":
            if not os.path.exists("novel/" + aim):
                os.mkdir("novel/" + aim)
        elif t == "imgs":
            if not os.path.exists("imgs/" + aim):
                os.mkdir("imgs/" + aim)
        elif t == "img_fail":
            if not os.path.exists("imgs/" + aim + ".txt"):
                open("imgs/" + img_fail_novel_name + "/" + aim + ".txt", "w", encoding="utf-8").close()