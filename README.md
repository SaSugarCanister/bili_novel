# 哔哩轻小说获取小说，并转为EPUB

[![License](https://img.shields.io/badge/license-MIT-red.svg)](https://github.com/SaSugarCanister/bili_novel/blob/main/LICENSE)

## 特性：

•99%稳定性获取小说内容与图片
•提供参数选项，适用不同需求

## 安装：

•python版本：
3.11
•依赖安装：
pip install -r requirements.txt

## 参数说明：

•无参数：仅获取小说的txt格式以及图片
•"illustration"：若获取的小说中存在“插图”章节，该模式在转化EPUB时，会生成带封面的EPUB

## 使用示例:

进入cmd，并切换至项目根目录下（即bili_novel），然后运行如下命令：
•scrapy crawl get_novel
•scrapy crawl get_novel -a "illustration"

## 待优化：

•添加其它参数项，满足更多小说的带封面EPUB转化
•添加报错日志，如selenium请求失败、requests请求失败等
•添加报错处理，如driver重启、requests重试
•若小说名存在规律之外的命名，可能就不清楚该本小说的原来阅读顺序，需添加小说编号等