"""
@Description: 
@Usage: 
@Author: liuxianglong
@Date: 2022/5/13 下午2:24
"""
from app_scrapyd.models import SpiderStats, DailyErrLogRate, HourlyErrLogRate, ErrorLog
from rest_framework import serializers


class SpiderStatsSer(serializers.ModelSerializer):

    class Meta:
        model = SpiderStats
        exclude = ['create_time', 'update_time']


class DailyErrLogRateSer(serializers.ModelSerializer):

    class Meta:
        model = DailyErrLogRate
        fields = '__all__'


class HourlyErrLogRateSer(serializers.ModelSerializer):

    class Meta:
        model = HourlyErrLogRate
        fields = '__all__'


class ErrorLogSer(serializers.ModelSerializer):

    class Meta:
        model = ErrorLog
        fields = '__all__'
