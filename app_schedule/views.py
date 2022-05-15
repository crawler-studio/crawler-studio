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


class TimerScheduler(APIView):
    """
    Method: POST
        type:
        desc: 发布一条定时任务
        url: http://localhost:8000/api/v1/schedule/
        body:
        {
            'taskId': '',
            'ScheduleType': 'cron'/'date'/'interval'/,
            'ScheduleExp': '* * 1 * *',
            'worker': 'monitor_task',
            'Params': {
                sourceId: '',
                sourceName: '',
                sourcePath: '',
            }
        }
    """
    def __init__(self):
        super(TimerScheduler, self).__init__()
        self.logger = logging.getLogger('TimerScheduler')

    def post(self, request, **kwargs):
        """添加后台定时任务"""
        body = request.data
        try:
            if DjangoJob.objects.filter(id=str(body['task_id'])):
                raise ItemExistedException

            if body['schedule_type'] == 'cron':
                scheduler.add_job(
                    rabbitmq_task,
                    CronTrigger.from_crontab(body['schedule_exp']),
                    kwargs=body['params']
                )
            elif body['schedule_type'] == 'date':
                pass
            elif body['schedule_type'] == 'interval':
                task_info = scheduler.add_job(
                    getattr(worker, body['worker']),
                    id=str(body['task_id']),
                    trigger='interval',
                    seconds=body['schedule_exp'],
                    kwargs=body['params'],
                    misfire_grace_time=1000
                )
                return Response(f'添加定时任务成功 {task_info}', status=status.HTTP_200_OK)
            else:
                raise ValueError('type参数错误')
        except ItemExistedException:
            return Response('任务ID已存在', status=status.HTTP_208_ALREADY_REPORTED)
        except Exception as e:
            return Response(f'异常 {e}', status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, **kwargs):
        job_id = request.data['job_id']
        if DjangoJob.objects.filter(id=job_id):
            scheduler.remove_job(job_id)
            return Response('删除成功')
        else:
            return Response(f'jobId {job_id} 不存在')


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
            print(recipients.errors)
            return Response(recipients.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, **kwargs):
        MonitorRecipients.objects.filter(rev_addr=request.data['rev_addr']).delete()
        return Response('删除成功', status=status.HTTP_200_OK)


class MonitorRulesCRUD(APIView):
    def __init__(self):
        super(MonitorRulesCRUD, self).__init__()
        self.logger = logging.getLogger('MonitorRulesCRUD')

    def get(self, request):
        ser = MonitorRulesSerializer(instance=MonitorRules.objects.all(), many=True)
        return Response(ser.data)

    def post(self, request, **kwargs):
        if 'recipients' not in request.data:       # add default recipients
            rev = MonitorRecipients.objects.filter(is_default=1).all()
            request.data['recipients'] = [_.rev_name for _ in rev]

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
