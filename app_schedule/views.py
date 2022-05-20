import logging

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.models import DjangoJob, DjangoJobExecution
from utils.exceptions import *
from rest_framework.parsers import JSONParser
from django.forms.models import model_to_dict
from app_schedule.models import MonitorRecipients, MonitorRules
from app_schedule.ser import MonitorRecipientsSerializer, MonitorRulesSerializer
from app_schedule import worker
from utils.timer_scheduler import scheduler
from app_scrapyd.models import SpiderStartParams


logger = logging.getLogger(__name__)


class MonitorRecipientsCRUD(APIView):
    def __init__(self):
        super(MonitorRecipientsCRUD, self).__init__()
        self.logger = logging.getLogger('MonitorRecipientsCRUD')

    def get(self, request, **kwargs):
        data = MonitorRecipients.objects.all()
        ser = MonitorRecipientsSerializer(data, many=True)
        content = {'code': 0, 'data': ser.data}
        return Response(content)

    def post(self, request, **kwargs):
        existed = MonitorRecipients.objects.filter(rev_addr=request.data['rev_addr']).first()
        recipients = MonitorRecipientsSerializer(instance=existed, data=request.data)
        if recipients.is_valid():
            recipients.save()
            if existed:
                return Response('更新成功', status=status.HTTP_200_OK)
            else:
                return Response('添加成功', status=status.HTTP_200_OK)
        else:
            logger.error(recipients.errors)
            return Response(recipients.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, **kwargs):
        MonitorRecipients.objects.filter(rev_addr=request.data['rev_addr']).delete()
        return Response('删除成功', status=status.HTTP_200_OK)


class MonitorRulesCRUD(APIView):
    """
    Post方法由爬虫开启时调用，同步开启监控
    Put由设置界面中调用
    Delete由爬虫关闭或者界面中删除监控规则的时候调用
    """
    def __init__(self):
        super(MonitorRulesCRUD, self).__init__()
        self.logger = logging.getLogger('MonitorRulesCRUD')

    def get(self, request):
        ser = MonitorRulesSerializer(instance=MonitorRules.objects.all(), many=True)
        return Response(ser.data)

    def post(self, request, **kwargs):
        if 'recipients' not in request.data:       # add default recipients
            start_params = SpiderStartParams.objects.filter(
                project=request.data['spider_project'],
                spider=request.data['spider_name']
            ).first()
            if start_params:
                logger.info('使用启动参数中的收件人')
            else:
                if start_params is None:
                    start_params = SpiderStartParams.objects.filter(
                        project='__default',
                        spider='__default'
                    ).first()
                    logger.info('使用默认启动参数中的收件人')

            request.data['recipients'] = start_params.monitor_recipients.split(',')

        rule = MonitorRulesSerializer(data=request.data)
        if rule.is_valid():
            if MonitorRules.objects.filter(spider_job_id=rule.validated_data['spider_job_id']):
                return Response('This jobid has monitor rule already')
            else:
                obj = rule.save()
                return Response(f'Create success {obj.id}', status=status.HTTP_200_OK)
        else:
            self.logger.error(rule.errors)
            return Response(rule.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, **kwargs):
        existed = MonitorRules.objects.filter(spider_job_id=request.data['spider_job_id']).first()
        rule = MonitorRulesSerializer(instance=existed, data=request.data)
        if rule.is_valid():
            rule.save()
            return Response('Update success', status=status.HTTP_200_OK)
        else:
            self.logger.error(rule.errors)
            return Response(rule.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, **kwargs):
        rule = MonitorRules.objects.filter(spider_job_id=request.data['spider_job_id']).first()
        scheduler.remove_job(rule.timer_task.id)
        self.logger.info(f'Delete timer task success {rule.timer_task}')
        return Response('Delete success', status=status.HTTP_200_OK)
