"""
@Description: 
@Usage: 
@Author: liuxianglong
@Date: 2022/5/13 下午2:24
"""

from app_scrapyd.models import SpiderStats
from rest_framework import serializers


class SpiderStatsSer(serializers.ModelSerializer):

    class Meta:
        model = SpiderStats
        exclude = ['create_time', 'update_time']
