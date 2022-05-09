"""
@Description: 
@Usage: 
@Author: liuxianglong
@Date: 2022/2/23 下午9:31
"""
import uuid
from apscheduler.triggers.interval import IntervalTrigger
from app_schedule import worker
from utils.timer_scheduler import scheduler
from app_env.models import EnvVariable
from rest_framework import serializers
from django_apscheduler.models import DjangoJob


class EnvVariableSerializer(serializers.ModelSerializer):

    class Meta:
        model = EnvVariable
        exclude = ['create_time', 'update_time']
