"""
@Description: 
@Usage: 
@Author: liuxianglong
@Date: 2022/5/14 下午9:06
"""
import socket
import requests
from .api import API


class BaseInfo(object):

    def __init__(self, crawler, spider):
        ip_type = crawler.settings.get('CS_HOST_IP_TYPE', 'internal')
        if ip_type == 'internal':
            get_ip = self.get_internal_ip
        else:
            get_ip = self.get_external_ip
        self.host = get_ip()
        self.project = crawler.settings.get('BOT_NAME')
        self.spider = spider.name
        self.job_id = getattr(spider, '_job', '000000')
        self.stats = crawler.stats
        self.api = API.from_crawler(crawler)
        self.enable_send_err_text = crawler.settings.getbool('CS_ENABLE_SEND_ERR_TEXT', True)

    @staticmethod
    def get_internal_ip():
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
            return ip

    @staticmethod
    def get_external_ip():
        ip = requests.get('https://api.ipify.org').text
        return ip
