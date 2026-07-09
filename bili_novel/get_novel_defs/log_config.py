import logging

class config:
    # 屏蔽selenium请求日志
    def silence_selenium(self):
        logging.getLogger("selenium").setLevel(logging.ERROR)
        logging.getLogger("selenium.webdriver.remote.remote_connection").setLevel(logging.ERROR)
        logging.getLogger("urllib3").setLevel(logging.ERROR)
        logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)