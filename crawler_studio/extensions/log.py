"""
@Description: 
@Usage: 
@Author: liuxianglong
@Date: 2022/5/14 上午11:52
"""
import datetime
import logging
from twisted.internet import task
from .core import BaseInfo

logger = logging.getLogger(__name__)


class LogHandler(logging.Handler, BaseInfo):
    """Record log levels count into a crawler stats"""

    def __init__(self, crawler, spider, *args, **kwargs):
        super().__init__(*args, **kwargs)
        BaseInfo.__init__(self, crawler, spider)
        self.now_date = None
        self.now_hour = None

    def emit(self, record):
        today = datetime.datetime.now().date().strftime('%Y-%m-%d')
        if today != self.now_date:
            self.now_date = today
            self.stats.set_value('log_count/log_daily_total_count', 0)
            self.stats.set_value('log_count/log_daily_error_count', 0)

        hour = datetime.datetime.now().hour
        if hour != self.now_hour:
            self.now_hour = hour
            self.stats.set_value('log_count/log_hourly_total_count', 0)
            self.stats.set_value('log_count/log_hourly_error_count', 0)

        self.stats.inc_value('log_count/log_daily_total_count')
        self.stats.inc_value('log_count/log_hourly_total_count')

        if record.levelname in ('ERROR', 'CRITICAL'):
            self.stats.inc_value('log_count/log_daily_error_count')
            self.stats.inc_value('log_count/log_hourly_error_count')

            if self.enable_send_err_text:
                d = {
                    "host": self.host,
                    "project": self.project,
                    "spider": self.spider,
                    "job_id": self.job_id,
                    "record_time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "content": record.message,
                    "level": record.levelname,
                    "log_time": str(record.asctime),
                    "module": record.name,
                    "lineno": record.lineno,
                    "exc_info": record.exc_info,
                    "func_name": record.funcName,
                }
                self.api.send_errlog_content(raw_json=d)


class ErrorLogRate(BaseInfo):

    def __init__(self, crawler, spider):
        BaseInfo.__init__(self, crawler, spider)
        self.task = None
        self.interval = 60

    def spider_open(self, spider):
        self.task = task.LoopingCall(self.send, spider)
        self.task.start(self.interval)

    def spider_close(self, spider, reason):
        if self.task and self.task.running:
            self.send(spider)
            self.task.stop()

    def send(self, spider):
        today = datetime.datetime.now().date().strftime('%Y-%m-%d')
        hour = datetime.datetime.now().hour

        d = dict()
        d['host'] = self.host
        d['project'] = self.project
        d['spider'] = self.spider
        d['job_id'] = self.job_id
        d['log_date'] = today
        d['record_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        d['log_total_count'] = self.stats.get_value('log_count/log_daily_total_count', 0)
        d['log_error_count'] = self.stats.get_value('log_count/log_daily_error_count', 0)
        if d['log_total_count'] != 0:
            d['log_error_rate'] = round(d['log_error_count']/d['log_total_count'], 4)
        else:
            d['log_error_rate'] = 0
        self.api.send_errlog_rate(raw_json=d)

        d['log_total_count'] = self.stats.get_value('log_count/log_hourly_total_count', 0)
        d['log_error_count'] = self.stats.get_value('log_count/log_hourly_error_count', 0)
        if d['log_total_count'] != 0:
            d['log_error_rate'] = round(d['log_error_count']/d['log_total_count'], 4)
        else:
            d['log_error_rate'] = 0
        d['log_hour'] = hour
        self.api.send_errlog_rate(raw_json=d)

