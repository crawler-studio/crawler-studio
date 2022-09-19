"""
@Description: 
@Usage: 
@Author: liuxianglong
@Date: 2022/5/12 下午10:13
"""
import json
import logging
import datetime
from twisted.internet import task
from .core import BaseInfo

logger = logging.getLogger(__name__)


class SpiderStats(BaseInfo):
    def __init__(self, crawler, spider):
        BaseInfo.__init__(self, crawler, spider)
        self.task = None
        self.interval = 60

    def spider_open(self, spider):
        self.stats.set_value('host', self.host)
        self.stats.set_value('project', self.project)
        self.stats.set_value('spider', self.spider)
        self.stats.set_value('job_id', self.job_id)
        self.task = task.LoopingCall(self.send, spider)
        self.task.start(self.interval)

    def spider_close(self, spider, reason):
        if self.task and self.task.running:
            self.send(spider, finish_reason=reason, close=True)
            self.task.stop()

    def send(self, spider, finish_reason=None, close=False):
        stats = self.stats.get_stats()
        new_stats = {}
        for k, v in stats.items():
            if k == 'start_time' and type(v) != str:
                v = str(stats[k] + datetime.timedelta(hours=8))

            if k == 'finish_time' and type(v) != str:
                v = str(stats[k] + datetime.timedelta(hours=8))

            if k.startswith('memusage') and type(v) != str:
                v = str(round(v/(1024*1024), 1)) + 'MB'

            new_stats[k] = v

        d = dict()
        d['host'] = self.host
        d['project'] = self.project
        d['spider'] = self.spider
        d['job_id'] = self.job_id
        d['record_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        d['log_debug_count'] = new_stats.get('log_count/DEBUG', 0)
        d['log_info_count'] = new_stats.get('log_count/INFO', 0)
        d['log_warn_count'] = new_stats.get('log_count/WARNING', 0)
        d['log_error_count'] = new_stats.get('log_count/ERROR', 0)
        d['log_critical_count'] = new_stats.get('log_count/CRITICAL', 0)

        log_total_count = new_stats.get('log_count/log_hourly_total_count', 0)
        log_error_count = new_stats.get('log_count/log_hourly_error_count', 0)
        if log_total_count != 0:
            d['log_hourly_error_rate'] = round(log_error_count/log_total_count, 4)
        else:
            d['log_hourly_error_rate'] = 0
        d['memory_use'] = float(new_stats.get('memusage/max', '0MB').replace('MB', '').strip())
        d['start_time'] = new_stats.get('start_time')
        d['finish_time'] = new_stats.get('finish_time', None)
        d['finish_reason'] = finish_reason
        d['elapsed_time'] = new_stats.get('elapsed_time_seconds', None)
        d['state'] = 1 if not close else 0
        d['stats'] = json.dumps(new_stats, ensure_ascii=False)
        self.api.send_stats_data(raw_json=d)
