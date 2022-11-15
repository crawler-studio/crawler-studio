"""
@Description: 
@Usage: 
@Author: liuxianglong
"""
from crawler_studio.app_scrapyd.models import SpiderStats, SpiderStartParams
from rest_framework import serializers
from crawler_studio.crawler_studio.custom_field import Str2IntSerializerField, Str2ListSerializerField, Str2DictSerializerField


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
