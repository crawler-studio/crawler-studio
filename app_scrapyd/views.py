import json
import logging
from scrapyd_api import ScrapydAPI
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from dateutil import parser as dt_parser
from utils.time import seconds_to_dhms_zh
from .ser import SpiderStatsSer, \
    SpiderStartParamsSer
from .models import SpiderStats, \
     SpiderStartParams


logger = logging.getLogger(__name__)


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


class RunningTaskCRUD(APIView):

    def __init__(self):
        super(RunningTaskCRUD, self).__init__()
        self.logger = logging.getLogger('RunningTaskCRUD')

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
                item['schedule_type'] = 'Unknown' if stats is None else stats.run_type
                item['trigger'] = 'Unknown' if stats is None else stats.trigger
                item['last_run'] = 'Unknown' if stats is None else stats.last_run
                item['memory_use'] = 0 if stats is None else stats.memory_use
                item['log_hourly_error_rate'] = 'Unknown' if stats is None else stats.log_hourly_error_rate
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


class FinishTaskCRUD(APIView):
    """
    获取跑完的爬虫信息
    test url: http://127.0.0.1:8000/api/v1/scrapyd/spiderFinished/?addr=http://10.0.4.150:6800
    """

    def get(self, request, **kwargs):
        scrapyd = ScrapydAPI(target=request.query_params['host'])
        finished_info = list()
        for p in scrapyd.list_projects():
            j = scrapyd.list_jobs(p)
            for finished in j['finished']:
                item = dict()
                item['project'] = p
                item['job_id'] = finished['id']
                item['spider'] = finished['spider']
                item['start_time'] = finished['start_time'].split('.')[0]
                item['end_time'] = finished['end_time'].split('.')[0]
                start = dt_parser.parse(item['start_time'])
                end = dt_parser.parse(item['end_time'])
                item['elapsed_time'] = seconds_to_dhms_zh((end-start).seconds)
                finished_info.append(item)
        finished_info.sort(key=lambda _: _['end_time'], reverse=True)
        return Response(finished_info)

    def post(self, request, **kwargs):
        pass


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
            return Response(status=status.HTTP_204_NO_CONTENT)

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
