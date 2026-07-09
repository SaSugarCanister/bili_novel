import requests

headers = {
    "user-agent":"Opera/9.80 (Windows NT 6.1; U; en) Presto/2.9.181 Version/12.00",
    "referer":"https://www.linovelib.com/"
}
proxy = {
    "https": "socks5h://127.0.0.1:7890"
}
img = requests.get("https://img3.readpai.com/cover/3768/317543.jpg",headers=headers,proxies=proxy).content
with open("img.jpg","wb") as f:
    f.write(img)