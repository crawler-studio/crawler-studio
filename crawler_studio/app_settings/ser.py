"""
@Description: 
@Usage: 
@Author: liuxianglong
@Date: 2022/9/20 上午11:02
"""
from .models import ScrapydServer
from rest_framework import serializers


class ScrapydServerSer(serializers.ModelSerializer):

    class Meta:
        model = ScrapydServer
        exclude = ['create_time', 'update_time']
