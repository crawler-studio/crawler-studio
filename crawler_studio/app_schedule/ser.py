"""
@Description: 
@Usage: 
@Author: liuxianglong
"""
import uuid
from apscheduler.triggers.interval import IntervalTrigger
from crawler_studio.app_schedule import worker
from crawler_studio.utils.timer_scheduler import scheduler
from crawler_studio.app_schedule.models import MonitorRules, MonitorRecipients
from rest_framework import serializers
from django_apscheduler.models import DjangoJob


class MonitorRecipientsSerializer(serializers.ModelSerializer):

    class Meta:
        model = MonitorRecipients
        exclude = ['create_time', 'update_time']


class MonitorRulesSerializer(serializers.ModelSerializer):

    recipients = serializers.SlugRelatedField(many=True, slug_field='rev_name', queryset=MonitorRecipients.objects.all())
    next_run_time = serializers.DateTimeField(source='timer_task.next_run_time', required=False, format='%Y-%m-%d %H:%M:%S')

    def create(self, validated_data):
        rev = validated_data.pop('recipients')
        task_id = str(uuid.uuid4())
        params = {
            "job_id": validated_data['spider_job_id'],
        }
        scheduler.add_job(
            worker.spider_monitor_task,
            id=task_id,
            trigger='interval',
            seconds=int(validated_data['monitor_freq']),
            kwargs=params,
            misfire_grace_time=1000
        )
        validated_data['timer_task'] = DjangoJob.objects.filter(id=task_id).first()
        rule = MonitorRules.objects.create(**validated_data)
        rule.recipients.set(rev)
        return rule

    def update(self, instance, validated_data):
        serializers.raise_errors_on_nested_writes('update', self, validated_data)
        rev = validated_data.pop('recipients')

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        params = {
            "job_id": validated_data['spider_job_id'],
        }
        scheduler.modify_job(
            job_id=validated_data['timer_task'].id,
            func=worker.spider_monitor_task,
            trigger=IntervalTrigger(seconds=int(validated_data['monitor_freq'])),
            kwargs=params,
            misfire_grace_time=1000
        )
        if MonitorRules.objects.filter(id=instance.id).first().monitor_freq != validated_data['monitor_freq']:
            scheduler.reschedule_job(
                job_id=validated_data['timer_task'].id,
                trigger=IntervalTrigger(seconds=int(validated_data['monitor_freq'])),
            )
        instance.save()
        instance.recipients.set(rev)
        return instance

    class Meta:
        model = MonitorRules
        exclude = ['create_time', 'update_time']


