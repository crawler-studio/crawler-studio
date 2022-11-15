"""
@Description: 
@Usage: 
@Author: liuxianglong
"""
import datetime
import logging
from crawler_studio.utils.message_transmit import send_ding_message, send_mail
from crawler_studio.app_scrapyd.models import SpiderStats
from crawler_studio.app_logs.models import HourlyErrLogRate
from crawler_studio.app_schedule.models import MonitorRules

logger = logging.getLogger(__name__)


def spider_monitor_task(**kwargs):
    logger.info(f'Spider_monitor_task worker rev task {kwargs}')
    running_task = HourlyErrLogRate.objects.filter(job_id=kwargs['job_id']).order_by('-record_time').first()
    monitor_rule = MonitorRules.objects.filter(spider_job_id=kwargs['job_id']).first()
    spider_stats = SpiderStats.objects.filter(job_id=kwargs['job_id']).first()

    error_status = False
    if running_task is None:
        error_status = True
        report = f'- 爬虫开启监控后未上报运行状态，请检查～'
    else:
        report = f'- 日志错误率异常爬虫如下'
        report += '\n'
        report += f'- 主机 {running_task.host}'
        report += '\n'
        report += f'- 项目 {running_task.project}'
        report += '\n'
        report += f'- 爬虫 {running_task.spider}'
        report += '\n'
        report += f'- JOBID {running_task.job_id}'
        report += '\n'
        report += f'- 最近上报时间: {running_task.record_time}'
        report += '\n'

        alive = (datetime.datetime.now()-running_task.record_time).seconds
        if alive >= monitor_rule.log_alive_limit:
            report += f'- 日志存活时间上限: {monitor_rule.log_alive_limit} sec'
            report += '\n'
            report += f'- 当前日志存活时间: {alive} sec'
            report += '\n'
            error_status = True

        if running_task.log_error_rate >= monitor_rule.errlog_rate_limit:
            report += f'- 日志错误率上限: {monitor_rule.errlog_rate_limit*100}%'
            report += '\n'
            report += f'- 当前日志错误率: {round(running_task.log_error_rate*100, 2)}%'
            report += '\n'
            error_status = True

        if spider_stats.memory_use > monitor_rule.memory_use_limit:
            report += f'- 内存占用上限: {monitor_rule.memory_use_limit}MB'
            report += '\n'
            report += f'- 当前内存占用: {spider_stats.memory_use}MB'
            report += '\n'
            error_status = True

    if error_status:
        for rev in monitor_rule.recipients.all():
            if '@' in rev.rev_addr:         # mail receiver
                send_mail(receiver=rev.rev_addr, subject='爬虫日志预警', content=report)

            if 'dingtalk' in rev.rev_addr:      # dingding receiver
                send_ding_message(title='爬虫日志预警', content=report, ding_addr=rev.rev_addr)
