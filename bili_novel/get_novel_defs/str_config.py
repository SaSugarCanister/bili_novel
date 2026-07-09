import re

class str_format:
    # 格式化名称
    def format_name(self, name: str, **kwargs) -> tuple:  # **kwargs用以传递p参数，p是正则表达式
        new_name = name.strip().replace(" ", "_")
        two_num_lst = []
        # 格式化下一页章节名
        if kwargs.get('p'):
            if not re.match(kwargs.get('p'), name) == None:
                # 例：喜欢你（1/3）格式化后-> 喜欢你（1_of_3）
                pattern = r'(.*?)(（\d+/\d+）)'
                pg = re.match(pattern, new_name)
                pg = pg.group(2)
                two_num_lst = pg.replace("（","").replace("）","").split("/")
                name_chip = re.sub(r'/', "_of_", pg)
                new_name = re.sub(r'（\d+/\d+）', name_chip, new_name)

        new_name = re.sub(r'\\/:*?"<>\|', "", new_name)

        return (new_name,two_num_lst)
