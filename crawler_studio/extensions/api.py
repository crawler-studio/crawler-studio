"""
@Description: 
@Usage: 
@Author: liuxianglong
@Date: 2022/5/13 上午1:11
"""
import logging
import requests

logger = logging.getLogger(__name__)


def cs_api(func):

    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            logger.warning(f'API {func.__name__} error, {e}')

    return wrapper


class API(object):

    def __init__(self, settings):
        self._settings = settings
        self._host = settings.get('CS_BACKEND', 'http://localhost:8000')
        self._spider_stats_end_point = f"{self._host}/api/v1/scrapyd/spiderStats/"
        self._errlog_rate_end_point = f"{self._host}/api/v1/scrapyd/errorLogRate/"
        self._errlog_content_end_point = f"{self._host}/api/v1/scrapyd/errorLogContent/"
        self._api_token = settings.get('CS_API_TOKEN', '')

    @classmethod
    def from_crawler(cls, crawler):
        o = cls(crawler.settings)
        return o

    @property
    def headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Token {self._api_token}'
        }

    @cs_api
    def send_stats_data(self, raw_json):
        response = requests.post(self._spider_stats_end_point, headers=self.headers, json=raw_json)
        logger.info(f'Send scrapy stats success, {response.text}')

    @cs_api
    def send_errlog_rate(self, raw_json):
        response = requests.post(self._errlog_rate_end_point, headers=self.headers, json=raw_json)
        logger.info(f'Send errlog rate success, {response.text}')

    @cs_api
    def send_errlog_content(self, raw_json):
        response = requests.post(self._errlog_content_end_point, headers=self.headers, json=raw_json)
        logger.info(f'Send errlog content success, {response.text}')

