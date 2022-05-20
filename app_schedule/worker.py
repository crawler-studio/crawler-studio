"""
@Description: 
@Usage: 
@Author: liuxianglong
@Date: 2022/2/1 下午11:04
"""
import datetime
import logging
import time
import requests
from elasticsearch import Elasticsearch
from utils.message_transmit import send_ding_message, send_mail
from utils.rabbitmq import RabbitMQ2
from app_scrapyd.models import SpiderStats, HourlyErrLogRate
from app_schedule.models import MonitorRules

logger = logging.getLogger(__name__)
mq = RabbitMQ2()


def log_alive(**kwargs):
    logger.info(f'log_alive worker收到任务 {kwargs}')
    ip = kwargs['ip']
    job_id = kwargs['job_id']
    project = kwargs['project']
    spider = kwargs['spider']
    alive_limit = kwargs['alive_limit']
    recipients = kwargs['recipients']

    es = Elasticsearch(['http://10.0.6.197', ], port=9200)
    body = {
      "size": 1,
      "query": {
          "bool": {
              "must": [
                  {
                      "term": {
                          "remote_ip.keyword": ip
                      }
                  },
                  {
                      "range": {
                          "@timestamp": {
                              "gte": "now-1d"
                          }
                      }
                  },
                  {
                     "match_phrase": {
                       "source": f'{job_id}.log'
                     }
                  }
              ]
          }
      },
      "aggs": {
          "last_access": {
              "max": {
                  "field": "@timestamp"
              }
          }
      }
    }
    search_result = es.search(
        index=f'ocean_log',
        body=body
    )
    logger.info(f'ES搜索结果 {search_result}')

    def alert(_seconds):
        report = f'- 爬虫服务器IP: {ip}'
        report += '\n'
        report += f'- 项目: {project}'
        report += '\n'
        report += f'- 爬虫: {spider}'
        report += '\n'
        report += f'- JOB ID: {job_id}'
        report += '\n'
        report += f'- 日志存活上限: {alive_limit} sec'
        report += '\n'
        report += f"- 当前存活时间: {_seconds} sec" if _seconds else f'- 一天内无爬虫日志信息'
        report += '\n'

        mail_rev = list()
        mail_name = list()
        ding_rev = list()
        ding_name = list()
        for name, addr in recipients.items():
            if '@' in addr:
                mail_name.append(name)
                mail_rev.append(addr)

            if 'dingtalk' in addr:
                ding_name.append(name)
                ding_rev.append(addr)

        if mail_rev:
            report += f"- 邮件收件人: {','.join(mail_name)}"
            report += '\n'
            send_mail(receiver=mail_rev, subject='爬虫存活日志预警', content=report)

        if ding_rev:
            report += f"- 钉钉收件人: {','.join(ding_name)}"
            report += '\n'
            for rev in ding_rev:
                send_ding_message(title='爬虫存活日志预警', content=report, ding_addr=rev)

    timestamp = search_result['aggregations']['last_access']['value']
    if not timestamp:
        alert(None)
    else:
        seconds = int(time.time() - timestamp // 1000)
        if seconds > int(alive_limit):
            alert(seconds)


def rabbitmq_task(**kwargs):
    queue = kwargs['queue']
    queue_params = kwargs['queue_params']
    queue_params['sendTime'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    mq.send(queue, queue_params)
    logger.info(f'发送定时任务成功，队列 {queue}, 参数 {queue_params}')


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
