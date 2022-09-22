"""
@Description: 
@Usage: 
@Author: liuxianglong
@Date: 2022/9/23 上午1:08
"""
from rest_framework import serializers
from .models import DailyErrLogRate, HourlyErrLogRate, ErrorLog


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