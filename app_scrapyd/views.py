import logging
import time
import re
import logging
import requests
import tldextract
from scrapyd_api import ScrapydAPI
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from crawler_studio_be.settings import get_redis_from_name
from urllib.parse import urlparse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from app_schedule.models import MonitorRules
from .ser import SpiderStatsSer
from .models import SpiderStats


redis_cli = get_redis_from_name('pac2')
logger = logging.getLogger()
scrapyd_container = dict()


class RunningTaskCRUD(APIView):

    def __init__(self):
        super(RunningTaskCRUD, self).__init__()
        self.logger = logging.getLogger('RunningTaskCRUD')
        self.key = f'crawler_studio_be:scrapyd:setting'
        from rest_framework.test import APIClient
        self.client = APIClient()

    def get(self, request, **kwargs):
        """
        test url: http://127.0.0.1:8000/api/v1/scrapyd/runningTask/?addr=http://10.0.4.150:6800
        """
        addr = request.GET['addr']
        ins = ScrapydAPI(target=addr)

        running_info = list()
        for p in ins.list_projects():
            j = ins.list_jobs(p)
            for running in j['running']:
                stats = SpiderStats.objects.filter(job_id=running['id']).first()
                item = dict()
                item['project'] = p
                item['job_id'] = running['id']
                item['spider'] = running['spider']
                item['pid'] = running['pid']
                item['start_time'] = running['start_time'].split('.')[0]
                item['schedule_type'] = stats.run_type
                item['trigger'] = stats.trigger
                item['last_run'] = stats.last_run
                running_info.append(item)
        running_info.sort(key=lambda _: _['start_time'], reverse=True)
        return Response(running_info)

    def post(self, request, **kwargs):
        data = request.data
        ins = ScrapydAPI(target=data['addr'])
        job_id = ins.schedule(data['project'], data['spider'])
        # monitor = redis_cli.hgetall(self.key)
        # recipients = [] if not monitor['recipients'] else monitor['recipients'].split(',')
        # monitor_log_alive = True if int(monitor['monitor_log_alive']) else False
        # monitor_log_err_rate = True if int(monitor['monitor_log_err_rate']) else False
        # if monitor_log_alive:
        #     body = {
        #         "recipients": recipients,
        #         "spiderHost": tldextract.extract(data['addr']).domain,
        #         "spiderProject": data['project'],
        #         "spiderName": data['spider'],
        #         "spiderJobId": job_id,
        #         "monitorType": "日志存活时间",
        #         "monitorFreq": int(monitor['monitor_freq']),
        #         "threshold": int(monitor['log_alive_limit']),
        #     }
        #     res = self.client.post('/api/v1/schedule/monitorRules/', body, format='json')
        #     self.logger.info(f'添加日志监控规则 {res}')
        return Response('ok')

    def delete(self, request, **kwargs):
        for task in request.data['checked_data']:
            addr = request.data['host']
            project = task['project']
            job_id = task['job_id']
            ins = ScrapydAPI(target=addr)
            ins.cancel(project, job_id)
            rule = MonitorRules.objects.filter(spider_job_id=task['job_id']).first()
            if rule:
                res = self.client.delete('/api/v1/schedule/monitorRules/', data={'id': rule.id}, format='json')
                self.logger.info(f'删除日志监控规则 {res}')
        return Response(f'删除{len(request.data["checked_data"])}个任务成功')


class SpiderSettingCRUD(APIView):

    def __init__(self):
        super(SpiderSettingCRUD, self).__init__()
        self.key = f'crawler_studio_be:scrapyd:setting'
        data = redis_cli.hgetall(self.key)
        if not data:
            data = {
                'monitor_log_alive': '1',
                'log_alive_limit': '70',
                'monitor_log_err_rate': '1',
                'log_err_rate_limit': '5',
                'monitor_freq': '1800',
                'recipients': '',
            }
            for k, v in data.items():
                redis_cli.hset(self.key, k, v)

    def get(self, request, **kwargs):
        data = redis_cli.hgetall(self.key)
        data['recipients'] = [] if not data['recipients'] else data['recipients'].split(',')
        data['monitor_log_alive'] = True if int(data['monitor_log_alive']) else False
        data['monitor_log_err_rate'] = True if int(data['monitor_log_err_rate']) else False
        return Response(data)

    def post(self, request, **kwargs):
        data = request.data
        data['recipients'] = ','.join(data['recipients'])
        data['monitor_log_alive'] = '1' if data['monitor_log_alive'] else '0'
        data['monitor_log_err_rate'] = '1' if data['monitor_log_err_rate'] else '0'
        redis_cli.hmset(self.key, request.data)
        return Response('保存成功')

    def put(self, request, **kwargs):
        pass


class SpiderStatsCRUD(APIView):

    def get(self, request, **kwargs):
        return Response('ok')

    def post(self, request, **kwargs):
        job_id = request.data['job_id']
        existed = SpiderStats.objects.filter(job_id=job_id).first()
        stats = SpiderStatsSer(instance=existed, data=request.data)
        if stats.is_valid():
            stats.save()
            if existed:
                return Response(f'更新成功 {job_id}', status=status.HTTP_200_OK)
            else:
                return Response(f'添加成功 {job_id}', status=status.HTTP_200_OK)
        else:
            logger.error(stats.errors)
            return Response(stats.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, **kwargs):
        pass


def list_finished(request):
    """
    获取跑完的爬虫信息
    test url: http://127.0.0.1:8000/api/v1/scrapyd/spider_finished/?addr=http://10.0.4.150:6800
    """
    addr = request.GET['addr']
    if addr not in scrapyd_container:
        scrapyd_container[addr] = ScrapydAPI(target=addr)

    finished_info = list()
    for p in scrapyd_container[addr].list_projects():
        j = scrapyd_container[addr].list_jobs(p)
        for finished in j['finished']:
            item = dict()
            item['project'] = p
            item['job_id'] = finished['id']
            item['spider'] = finished['spider']
            item['start_time'] = finished['start_time'].split('.')[0]
            item['end_time'] = finished['end_time'].split('.')[0]
            finished_info.append(item)
    finished_info.sort(key=lambda _: _['end_time'], reverse=True)
    return JsonResponse(finished_info, safe=False)


def list_spiders(request):
    """
    获取所有项目的所有爬虫
    test url: http://127.0.0.1:8000/api/v1/scrapyd/spider_all/?addr=http://10.0.4.150:6800
    """
    addr = request.GET['addr']
    if addr not in scrapyd_container:
        scrapyd_container[addr] = ScrapydAPI(target=addr)

    projects = scrapyd_container[addr].list_projects()
    info = []
    for project in projects:
        if project not in ('.DS_Store', 'default'):
            try:
                spiders = scrapyd_container[addr].list_spiders(project)
                for spider in spiders:
                    item = {
                        'project': project,
                        'spider': spider
                    }
                    info.append(item)
            except Exception as e:
                logger.error(f'异常: {e}', exc_info=True)

    return JsonResponse(info, safe=False)


def project_info(request):
    """
    获取项目信息
    test url: http://127.0.0.1:8000/api/v1/scrapyd/project_all/?addr=http://10.0.4.150:6800
    """
    addr = request.GET['addr']
    if addr not in scrapyd_container:
        scrapyd_container[addr] = ScrapydAPI(target=addr)

    projects = scrapyd_container[addr].list_projects()
    info = []
    for project in projects:
        if project not in ('.DS_Store', 'default'):
            try:
                spiders = scrapyd_container[addr].list_spiders(project)
                item = {
                    'project': project,
                    'spider_num': len(spiders),
                    'spider_list': ', '.join(spiders),
                    'available': True
                }
            except:
                item = {
                    'project': project,
                    'spider_num': 0,
                    'spider_list': '',
                    'available': False
                }
            info.append(item)
    return JsonResponse(info, safe=False)


def cancel_spider(request):
    """
    停止单个爬虫
    test url: http://127.0.0.1:8000/api/v1/scrapyd/cancel_spider/?addr=http://10.0.4.150:6800&project=twitter&job_id=1087dc6456a611ec9f2d00163e290a0d
    """
    addr = request.GET['addr']
    project = request.GET['project']
    job_id = request.GET['jobId']
    if addr not in scrapyd_container:
        scrapyd_container[addr] = ScrapydAPI(target=addr)

    result = scrapyd_container[addr].cancel(project, job_id)
    return JsonResponse(result, safe=False)


def stats(request):
    """
    获取爬虫状态
    test url: http://127.0.0.1:8000/api/v1/scrapyd/stats/?addr=http://10.0.4.150:6800&project=twitter&job_id=1087dc6456a611ec9f2d00163e290a0d&spider=twitter_loop
    """
    addr = request.GET['addr']
    host = urlparse(addr).netloc.split(':')[0]
    project = request.GET['project']
    job_id = request.GET['job_id']
    spider = request.GET['spider']
    stats_key = f'scrapy_box:stats:{job_id}'
    stats = redis_cli.hgetall(stats_key)
    result = [{'key': k, 'value': v} for k, v in stats.items()]
    return JsonResponse(result, safe=False)


def check_cancel(request):
    """
    检查job_id是否在还在运行列表中
    test url: http://127.0.0.1:8000/api/v1/scrapyd/check_cancel/?addr=http://10.0.4.150:6800&project=twitter&job_id=0fd0e2f45c9911ec9f2d00163e290a0d
    """
    addr = request.GET['addr']
    if addr not in scrapyd_container:
        scrapyd_container[addr] = ScrapydAPI(target=addr)

    project = request.GET['project']
    job_id = request.GET['jobId']
    jobs = scrapyd_container[addr].list_jobs(project)
    running_jobs = [_['id'] for _ in jobs['running']]
    if job_id not in running_jobs:
        return JsonResponse({'status': 0}, safe=False)
    else:
        return JsonResponse({'status': 1}, safe=False)
