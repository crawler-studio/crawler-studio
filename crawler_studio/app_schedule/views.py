import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from crawler_studio.utils.exceptions import *
from crawler_studio.app_schedule.models import MonitorRecipients, MonitorRules
from crawler_studio.app_schedule.ser import MonitorRecipientsSerializer, MonitorRulesSerializer
from crawler_studio.utils.timer_scheduler import scheduler
from crawler_studio.app_scrapyd.models import SpiderStartParams


logger = logging.getLogger(__name__)


class MonitorRecipientsCRUD(APIView):
    def __init__(self):
        super(MonitorRecipientsCRUD, self).__init__()
        self.logger = logging.getLogger('MonitorRecipientsCRUD')

    def get(self, request, **kwargs):
        data = MonitorRecipients.objects.all()
        ser = MonitorRecipientsSerializer(data, many=True)
        res = {
            'code': 200,
            'data': {
                'data': ser.data
            },
            'message': 'ok'
        }
        return Response(res)

    def post(self, request, **kwargs):
        existed = MonitorRecipients.objects.filter(rev_addr=request.data['rev_addr']).first()
        recipients = MonitorRecipientsSerializer(instance=existed, data=request.data)
        if recipients.is_valid():
            recipients.save()
            if existed:
                res = {
                    'code': 200,
                    'data': None,
                    'message': '修改成功'
                }
                return Response(res)
            else:
                res = {
                    'code': 200,
                    'data': None,
                    'message': '添加成功'
                }
                return Response(res)
        else:
            logger.error(recipients.errors)
            res = {
                'code': 400,
                'data': None,
                'message': recipients.errors
            }
            return Response(res)

    def delete(self, request, **kwargs):
        MonitorRecipients.objects.filter(rev_addr=request.data['rev_addr']).delete()
        res = {
            'code': 200,
            'data': None,
            'message': '删除成功'
        }
        return Response(res)


class MonitorRulesCRUD(APIView):
    """
    Post方法由爬虫开启时调用，同步开启监控
    Put由设置界面中调用
    Delete由爬虫关闭或者界面中删除监控规则的时候调用
    """
    def __init__(self):
        super(MonitorRulesCRUD, self).__init__()
        self.logger = logging.getLogger('MonitorRulesCRUD')

    def get(self, request, **kwargs):
        ser = MonitorRulesSerializer(instance=MonitorRules.objects.all(), many=True)
        res = {
            'code': 200,
            'data': {
                'data': ser.data
            },
            'message': 'ok'
        }
        return Response(res)

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
                res = {
                    'code': 200,
                    'data': None,
                    'message': 'This jobid has monitor rule already'
                }
                return Response(res)
            else:
                obj = rule.save()
                res = {
                    'code': 200,
                    'data': None,
                    'message': f'增加成功 {obj.id}'
                }
                return Response(res)
        else:
            self.logger.error(rule.errors)
            return Response(rule.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, **kwargs):
        existed = MonitorRules.objects.filter(spider_job_id=request.data['spider_job_id']).first()
        rule = MonitorRulesSerializer(instance=existed, data=request.data)
        if rule.is_valid():
            rule.save()
            res = {
                'code': 200,
                'data': None,
                'message': f'修改成功'
            }
            return Response(res)
        else:
            self.logger.error(rule.errors)
            return Response(rule.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, **kwargs):
        rule = MonitorRules.objects.filter(spider_job_id=request.data['spider_job_id']).first()
        scheduler.remove_job(rule.timer_task.id)
        res = {
            'code': 200,
            'data': None,
            'message': f'删除成功 {rule.timer_task}'
        }
        self.logger.info(f'Delete timer task success {rule.timer_task}')
        return Response(res)


