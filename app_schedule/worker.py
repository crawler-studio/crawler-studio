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


