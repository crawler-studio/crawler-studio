"""
@Description: 
@Usage: 
@Author: liuxianglong
@Date: 2022/1/21 下午8:51
"""
import uuid
from apscheduler.triggers.interval import IntervalTrigger
from app_schedule import worker
from utils.timer_scheduler import scheduler
from app_schedule.models import MonitorRules, MonitorRecipients
from rest_framework import serializers
from django_apscheduler.models import DjangoJob


class MonitorRecipientsSerializer(serializers.ModelSerializer):

    class Meta:
        model = MonitorRecipients
        exclude = ['create_time', 'update_time']


class MonitorRulesSerializer(serializers.ModelSerializer):

    recipients = serializers.SlugRelatedField(many=True, slug_field='rev_name', queryset=MonitorRecipients.objects.all())

    def create(self, validated_data):
        rev = validated_data.pop('recipients')
        task_id = str(uuid.uuid4())
        params = {
            "ip": validated_data['spider_host'],
            "project": validated_data['spider_project'],
            "spider": validated_data['spider_name'],
            "job_id": validated_data['spider_job_id'],
            "alive_limit": validated_data['threshold'],
            "recipients": {_.rev_name: _.rev_addr for _ in rev},
        }
        scheduler.add_job(
            getattr(worker, 'log_alive'),
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
            "ip": validated_data['spider_host'],
            "job_id": validated_data['spider_job_id'],
            "alive_limit": validated_data['threshold'],
            "recipients": [_.rev_addr for _ in rev],
        }
        scheduler.modify_job(
            job_id=validated_data['timer_task'].id,
            func=getattr(worker, 'log_alive'),
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


