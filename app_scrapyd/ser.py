"""
@Description: 
@Usage: 
@Author: liuxianglong
@Date: 2022/5/13 下午2:24
"""
from app_scrapyd.models import SpiderStats, DailyErrLogRate, HourlyErrLogRate, ErrorLog, \
    SpiderStartParams
from rest_framework import serializers
from crawler_studio_be.custom_field import Str2IntSerializerField, Str2ListSerializerField, Str2DictSerializerField


class SpiderStatsSer(serializers.ModelSerializer):

    class Meta:
        model = SpiderStats
        exclude = ['create_time', 'update_time']


class SpiderStartParamsSer(serializers.ModelSerializer):

    params = serializers.CharField(allow_blank=True)
    monitor_recipients = Str2ListSerializerField()
    monitor_freq = Str2IntSerializerField()
    params = Str2DictSerializerField()

    class Meta:
        model = SpiderStartParams
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
        exclude = ['create_time', 'update_time']
