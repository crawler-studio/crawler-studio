import json
import re
import logging
from scrapyd_api import ScrapydAPI
from django.http import HttpResponse, JsonResponse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from app_schedule.models import MonitorRules
from django.forms.models import model_to_dict
from .ser import SpiderStatsSer, HourlyErrLogRateSer, DailyErrLogRateSer, ErrorLogSer, \
    SpiderStartParamsSer
from .models import SpiderStats, HourlyErrLogRate, DailyErrLogRate, ErrorLog, \
     SpiderStartParams


logger = logging.getLogger(__name__)
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
                monitor_rule = MonitorRules.objects.filter(spider_job_id=running['id']).first()
                item = dict()
                item['project'] = p
                item['job_id'] = running['id']
                item['spider'] = running['spider']
                item['pid'] = running['pid']
                item['start_time'] = running['start_time'].split('.')[0]
                item['schedule_type'] = 'Unknown' if stats is None else stats.run_type
                item['trigger'] = 'Unknown' if stats is None else stats.trigger
                item['last_run'] = 'Unknown' if stats is None else stats.last_run
                item['memory_use'] = 0 if stats is None else stats.memory_use
                item['memory_use_limit'] = 'Unknown' if monitor_rule is None else monitor_rule.memory_use_limit
                item['log_hourly_error_rate'] = 'Unknown' if stats is None else stats.log_hourly_error_rate
                item['log_hourly_error_limit'] = 'Unknown' if monitor_rule is None else monitor_rule.errlog_rate_limit
                running_info.append(item)
        running_info.sort(key=lambda _: _['start_time'], reverse=True)
        return Response(running_info)

    def post(self, request, **kwargs):
        pass

    def delete(self, request, **kwargs):
        for task in request.data['checked_data']:
            addr = request.data['host']
            project = task['project']
            job_id = task['job_id']
            ins = ScrapydAPI(target=addr)
            ins.cancel(project, job_id)
        return Response(f'删除{len(request.data["checked_data"])}个任务成功')


class NewTaskCRUD(APIView):

    def get(self, request, **kwargs):
        """
        获取所有项目的所有爬虫及其启动参数，先获取默认参数，再获取此爬虫的参数
        test url: http://127.0.0.1:8000/api/v1/scrapyd/newTask/?addr=http://10.0.4.150:6800
        """
        host = request.query_params['host']
        scrapyd = ScrapydAPI(target=host)
        projects = scrapyd.list_projects()
        info = []
        default_params = SpiderStartParams.objects.filter(project='__default', spider='__default').first()
        for project in projects:
            if project not in ('.DS_Store', 'default'):
                try:
                    spiders = scrapyd.list_spiders(project)
                    for spider in spiders:
                        spider_params = SpiderStartParams.objects.filter(project=project, spider=spider).first()
                        if spider_params:
                            ser = SpiderStartParamsSer(spider_params)
                            item = ser.data
                        else:
                            ser = SpiderStartParamsSer(default_params)
                            item = ser.data
                            item.update({
                                'project': project,
                                'spider': spider
                            })
                        info.append(item)
                except Exception as e:
                    logger.error(e)
        return Response(info, status=status.HTTP_200_OK)

    def post(self, request, **kwargs):
        """
        启动爬虫，并且传递设置参数
        """
        data = request.data
        setting = {}
        if data['run_type'] == 'interval':
            setting['LOOP_INTERVAL'] = int(data['trigger'])
        if data['run_type'] == 'crontab':
            setting['LOOP_CRONTAB'] = data['trigger']
        setting['CS_ENABLE_MONITOR_RULE'] = data['enable_monitor_rule']
        setting['CS_ENABLE_SEND_ERR_TEXT'] = data['enable_send_error_log']
        setting['CS_MONITOR_FREQ'] = int(data['monitor_freq'])
        setting['CS_ERRLOG_RATE_LIMIT'] = float(data['errlog_rate_limit'])
        setting['CS_MEMORY_USE_LIMIT'] = int(data['memory_use_limit'])
        logger.info(f'Start spider, spider settings {setting}')
        ins = ScrapydAPI(target=data['host'])
        job_id = ins.schedule(data['project'], data['spider'], settings=setting)
        return Response(job_id, status=status.HTTP_200_OK)


class SpiderStartParamsCRUD(APIView):

    def get(self, request, **kwargs):
        project = request.query_params.get('project', '__default')
        data = SpiderStartParams.objects.filter(project=project).first()
        ser = SpiderStartParamsSer(data)
        return Response(ser.data)

    def post(self, request, **kwargs):
        existed = SpiderStartParams.objects.filter(project=request.data['project'], spider=request.data['spider']).first()
        params = SpiderStartParamsSer(instance=existed, data=request.data)
        if params.is_valid():
            params.save()
            if existed:
                return Response(f"update success", status=status.HTTP_200_OK)
            else:
                return Response(f"create success", status=status.HTTP_200_OK)
        else:
            logger.error(params.errors)
            return Response(params.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, **kwargs):
        pass


class SpiderStatsCRUD(APIView):

    def get(self, request, **kwargs):
        """
        获取爬虫运行状态，从`SpiderStats`表中取stats字段
        :param request:
        :param kwargs:
        :return:
        """
        job_id = request.query_params['jobId']
        existed = SpiderStats.objects.filter(job_id=job_id).first()
        if existed:
            d = json.loads(existed.stats)
            d = [{'key': k, 'value': v} for k, v in d.items()]
            return Response(d, status=status.HTTP_200_OK)
        else:
            return Response('jobid not existed', status=status.HTTP_200_OK)

    def post(self, request, **kwargs):
        """
        在`SpiderStats`表中创建或更新爬虫状态
        :param request:
        :param kwargs:
        :return:
        """
        job_id = request.data['job_id']
        existed = SpiderStats.objects.filter(job_id=job_id).first()
        stats = SpiderStatsSer(instance=existed, data=request.data)
        if stats.is_valid():
            stats.save()
            if existed:
                return Response(f'update success {job_id}', status=status.HTTP_200_OK)
            else:
                return Response(f'create success {job_id}', status=status.HTTP_200_OK)
        else:
            logger.error(stats.errors)
            return Response(stats.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, **kwargs):
        pass


class ErrorLogRateCRUD(APIView):

    def get(self, request, **kwargs):
        pass

    def post(self, request, **kwargs):
        if request.data.get('log_hour'):        # hourly api
            job_id = request.data['job_id']
            log_date = request.data['log_date']
            log_hour = request.data['log_hour']
            existed = HourlyErrLogRate.objects.filter(job_id=job_id, log_date=log_date, log_hour=log_hour).first()
            data = HourlyErrLogRateSer(instance=existed, data=request.data)
            if data.is_valid():
                data.save()
                if existed:
                    return Response(f'update success {job_id} {log_date}-{log_hour}', status=status.HTTP_200_OK)
                else:
                    return Response(f'create success {job_id} {log_date}-{log_hour}', status=status.HTTP_200_OK)
            else:
                logger.error(data.errors)
                return Response(data.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            job_id = request.data['job_id']             # daily api
            log_date = request.data['log_date']
            existed = DailyErrLogRate.objects.filter(job_id=job_id, log_date=log_date).first()
            data = DailyErrLogRateSer(instance=existed, data=request.data)
            if data.is_valid():
                data.save()
                if existed:
                    return Response(f'update success {job_id} {log_date}', status=status.HTTP_200_OK)
                else:
                    return Response(f'create success {job_id} {log_date}', status=status.HTTP_200_OK)
            else:
                logger.error(data.errors)
                return Response(data.errors, status=status.HTTP_400_BAD_REQUEST)                # daily api


class ErrorLogContentCRUD(APIView):
    def get(self, request, **kwargs):
        pass

    def post(self, request, **kwargs):
        data = ErrorLogSer(data=request.data)
        if data.is_valid():
            data.save()
            return Response(f'create success', status=status.HTTP_200_OK)
        else:
            logger.error(data.errors)
            return Response(data.errors, status=status.HTTP_400_BAD_REQUEST)


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
